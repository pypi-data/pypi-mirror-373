from __future__ import annotations

import io
import re
import sys
import tempfile
import warnings
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import google.protobuf as protobuf
from pydantic import BaseModel, Field

from ._bpln_proto.commander.service.v2 import common_pb2 as common_pb
from ._bpln_proto.commander.service.v2 import get_logs_pb2 as get_logs_pb
from ._bpln_proto.commander.service.v2 import job_context_pb2 as job_context_pb
from ._bpln_proto.commander.service.v2 import runner_events_pb2 as runner_events_pb

T = TypeVar('T')
RT = TypeVar('RT')

# TODO: this alias is for backwards compatibility, but I would like to remove it
JobLog: TypeAlias = 'JobLogEvent'
DateRange: TypeAlias = tuple[Optional[datetime], Optional[datetime]]


REF_REGEX = r'^(.*?)(:?@([^@]+))?$'


# Safely convert proto timestamp fields to native Python datetime
def proto_datetime_to_py_datetime(
    ts: protobuf.timestamp_pb2.Timestamp,
) -> Optional[datetime]:
    if not ts.seconds and not ts.nanos:
        return None
    return ts.ToDatetime()


class _BauplanData(BaseModel):
    def __str__(self) -> str:
        return self.__repr__()


class Ref(_BauplanData):
    """A branch or a tag"""

    name: str
    hash: str | None = None
    type: str | None = None

    def __str__(self) -> str:
        if self.hash:
            return f'{self.name}@{self.hash}'
        return self.name

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        return cls(**data)

    @classmethod
    def from_string(cls, ref: str) -> Self:
        matched = re.match(REF_REGEX, ref)
        if not matched:
            raise ValueError(f'invalid ref format: {ref}')
        name = matched.group(1).strip()
        hash = matched.group(3) or None
        if not name:
            raise ValueError(f'invalid ref format: {ref}')
        return cls(name=name, hash=hash)


class Branch(Ref):
    type: Literal['BRANCH'] = 'BRANCH'


class Tag(Ref):
    type: Literal['TAG'] = 'TAG'


class DetachedRef(Ref):
    type: Literal['DETACHED'] = 'DETACHED'


APIRef: TypeAlias = Annotated[
    Union[Branch, Tag, DetachedRef],
    Field(discriminator='type'),
]


class APIMetadata(_BauplanData):
    status_code: int
    ref: Optional[APIRef] = None
    username: Optional[str] = None
    error: Optional[str] = None
    pagination_token: Optional[str] = None
    request_id: str
    request_ts: int
    request_ms: int


class APIError(_BauplanData):
    code: int
    type: str
    message: str
    context: dict[str, Any]


class APIResponse(_BauplanData):
    metadata: APIMetadata
    ref: Optional[APIRef] = None


class APIResponseWithData(APIResponse):
    data: Any
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class APIResponseWithError(APIResponse):
    error: APIError
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class Namespace(_BauplanData):
    name: str
    ref: Optional[APIRef] = None


class Entry(_BauplanData):
    name: str
    namespace: str
    kind: str

    @property
    def fqn(self) -> str:
        return f'{self.namespace}.{self.name}'


class TableField(_BauplanData):
    id: int
    name: str
    required: bool
    type: str


class PartitionField(_BauplanData):
    name: str
    transform: str


class Table(Entry):
    kind: str = 'TABLE'


class TableWithMetadata(Table):
    id: str
    records: Optional[int]
    size: Optional[int]
    last_updated_ms: int
    fields: List[TableField]
    snapshots: Optional[int]
    partitions: List[PartitionField]
    metadata_location: str
    current_snapshot_id: Optional[int]
    current_schema_id: Optional[int]
    raw: Optional[Dict]


class Commit(_BauplanData):
    ref: APIRef
    message: Optional[str]
    authors: List[Actor]
    authored_date: datetime
    committer: Actor
    committed_date: datetime
    parent_ref: APIRef
    parent_hashes: List[str]
    properties: Dict[str, str]
    signed_off_by: List[Actor]

    @property
    def author(self) -> Actor:
        return self.authors[0]

    @property
    def subject(self) -> Optional[str]:
        if self.message is None:
            return None
        subject = self.message.strip().split('\n')[0].strip()
        return subject or None

    @property
    def body(self) -> Optional[str]:
        if self.message is None:
            return None
        body = '\n'.join(self.message.strip().split('\n')[1:]).strip()
        return body or None

    @property
    def parent_merge_ref(self) -> Optional[Branch]:
        if len(self.parent_hashes) > 1:
            return Branch(name=self.parent_ref.name, hash=self.parent_hashes[1])
        return None


class Actor(_BauplanData):
    name: str
    email: str | None


@dataclass
class _BauplanIteratorContext:
    page_idx: int = 0
    page_item_idx: int = 0
    idx: int = 0
    finished: bool = False

    def next_page(self) -> None:
        self.page_idx = self.page_idx + 1
        self.page_item_idx = 0

    def next_item(self, limit: int | None) -> None:
        self.page_item_idx = self.page_item_idx + 1
        self.idx = self.idx + 1
        self.finished = True if limit and self.idx >= limit else False


class _BauplanIterableCatalogAPIResponse(Generic[T, RT]):
    responses: List[APIResponse]

    def __init__(
        self,
        data_fetcher: Callable[[int, Optional[str]], APIResponse],
        data_mapper: Callable[[Dict[str, Any]], T],
        itersize: int,
        limit: int | None = None,
    ) -> None:
        self.responses = []

        self._response_ref: RT = None  # type: ignore
        self._limit = limit
        self._itersize = itersize
        self._data_fetcher = data_fetcher
        self._data_mapper = data_mapper
        self._iter = _BauplanIteratorContext()
        self._has_next_page = True
        self._fetch_next_page()

    def values(self) -> List[T]:
        return list(self)

    def __iter__(self) -> _BauplanIterableCatalogAPIResponse[T, RT]:
        # We need to reset the iterator context
        self._iter = _BauplanIteratorContext()
        return self

    def __getitem__(self, idx: int) -> T:
        if idx < 0:
            raise ValueError('Negative indexing is not supported')
        # TODO: this is not efficient
        pos = 0
        for res in self:
            if pos == idx:
                return res
            pos += 1
        raise IndexError('Index out of range')

    def __next__(self) -> T:
        if self._iter.finished:
            raise StopIteration
        # Get the current page
        page = self.responses[self._iter.page_idx]
        if self._iter.page_item_idx >= len(page.data):
            # We've reached the end of the current page
            self._fetch_next_page()
            self._iter.next_page()
            self._iter.finished = self._iter.page_idx >= len(self.responses)
            return self.__next__()
        # Get the current item
        item = page.data[self._iter.page_item_idx]
        self._iter.next_item(self._limit)
        return self._data_mapper(item)

    def __len__(self) -> int:
        while self._has_next_page:
            self._fetch_next_page()
        return self._response_data_len()

    def __str__(self) -> str:
        ref = '' if not hasattr(self, 'ref') else f'ref={str(self.ref)!r}, '
        return f'{self.__class__.__name__}({ref}iterator={self.responses[0].metadata.request_id!r})'

    def _response_data_len(self) -> int:
        # Actual number of items fetched over all pages
        return sum(len(page.data) for page in self.responses)

    @property
    def _next_pagination_token(self) -> Optional[str]:
        if not self._has_next_page:
            return None
        if self.responses:
            return self.responses[-1].metadata.pagination_token
        return None

    def _fetch_next_page(self) -> None:
        if not self._has_next_page:
            return
        if self._limit:
            # We should fetch only the remaining items, without exceeding the setted itersize
            missing_items = min(self._itersize, self._limit - self._response_data_len())
        else:
            # Without an explicit limit, we should fetch the itersize
            missing_items = self._itersize
        page = self._data_fetcher(missing_items, self._next_pagination_token)
        self.responses.append(page)
        if page.ref and not self._response_ref:
            self._response_ref = cast(RT, page.ref)
        # We need to use the private __len method to prevent an infinite loop
        tot_items = self._response_data_len()
        if self._limit and tot_items >= self._limit:
            # We should stop fetching pages when we have enough items
            self._has_next_page = False
            # and remove the extra items from the last page
            if tot_items > self._limit:
                page.data = page.data[: self._limit - tot_items]
        else:
            # We should stop fetching pages when there are no more pages
            self._has_next_page = self._next_pagination_token is not None


class _BauplanIterableCatalogAPIResponseWithRef(_BauplanIterableCatalogAPIResponse[T, RT]):
    @property
    def ref(self) -> RT:
        return self._response_ref


class GetCommitsResponse(_BauplanIterableCatalogAPIResponseWithRef[Commit, Union[Branch, Tag]]): ...


class GetTablesResponse(_BauplanIterableCatalogAPIResponseWithRef[TableWithMetadata, Union[Branch, Tag]]): ...


class GetNamespacesResponse(_BauplanIterableCatalogAPIResponseWithRef[Namespace, Union[Branch, Tag]]): ...


class GetBranchesResponse(_BauplanIterableCatalogAPIResponse[Branch, None]): ...


class GetTagsResponse(_BauplanIterableCatalogAPIResponse[Tag, None]): ...


class JobState(Enum):
    UNSPECIFIED = common_pb.JobStateType.JOB_STATE_TYPE_UNSPECIFIED
    NOT_STARTED = common_pb.JobStateType.JOB_STATE_TYPE_NOT_STARTED
    RUNNING = common_pb.JobStateType.JOB_STATE_TYPE_RUNNING
    COMPLETE = common_pb.JobStateType.JOB_STATE_TYPE_COMPLETE
    ABORT = common_pb.JobStateType.JOB_STATE_TYPE_ABORT
    FAIL = common_pb.JobStateType.JOB_STATE_TYPE_FAIL
    OTHER = common_pb.JobStateType.JOB_STATE_TYPE_OTHER

    def __str__(self) -> str:
        return {
            JobState.UNSPECIFIED: 'Unspecified',
            JobState.NOT_STARTED: 'Not Started',
            JobState.RUNNING: 'Running',
            JobState.COMPLETE: 'Complete',
            JobState.ABORT: 'Abort',
            JobState.FAIL: 'Fail',
            JobState.OTHER: 'Other',
        }[self]


class Job(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    Job is a model for a job in the Bauplan system. It is tracked as a result
    of a code snapshot run.

    """

    id: str
    kind: str
    user: str
    human_readable_status: str
    created_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: JobState

    @classmethod
    def from_proto(cls, job_pb: common_pb.JobInfo) -> 'Job':
        return cls(
            id=job_pb.id,
            kind=job_pb.kind,
            user=job_pb.user,
            human_readable_status=job_pb.human_readable_status,
            created_at=proto_datetime_to_py_datetime(job_pb.created_at),
            finished_at=proto_datetime_to_py_datetime(job_pb.finished_at),
            status=JobState(job_pb.status),
        )

    def __str__(self) -> str:
        """Return a string representation of the job."""

        time_annotation = ': '

        # If the job has finished, we can stringify that information
        run_time = self.duration
        if self.finished_at is not None and run_time is not None:
            simplified_finish_dt = self.finished_at.strftime('%m-%d %H:%M')
            simplified_duration = str(timedelta(days=run_time.days, seconds=run_time.seconds))
            time_annotation = f'[{simplified_finish_dt} ({simplified_duration})]: '

        return f'{self.kind} ({self.user}: {self.id_prefix}) {time_annotation}{self.human_readable_status}'

    @property
    def id_prefix(self) -> str:
        """Return the first 8 characters of the job ID."""
        return self.id[:8] if self.id else ''

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate the duration between created_at and finished_at."""
        if self.created_at is not None and self.finished_at is not None:
            return self.finished_at - self.created_at
        if self.created_at is not None:
            return datetime.now() - self.created_at
        return None

    @property
    def is_running(self) -> bool:
        """Check if the job is currently running."""
        return self.status == JobState.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if the job has completed (successfully)."""
        return self.status == JobState.COMPLETE

    @property
    def is_failed(self) -> bool:
        """Check if the job has failed."""
        return self.status == JobState.FAIL

    @property
    def is_aborted(self) -> bool:
        """Check if the job has been aborted."""
        return self.status == JobState.ABORT

    def has_id(self, check_id: str) -> bool:
        """Check if the job has the specified ID or ID prefix."""
        if len(check_id) == len(self.id) or len(check_id) == 8:
            return self.id.startswith(check_id)
        return False

    def has_status(self, check_status: Union[str, JobState] = JobState.COMPLETE) -> bool:
        """Check if the job has specified status."""
        if isinstance(check_status, str):
            return str(self.status) == check_status
        return self.status == check_status

    def finished_before(self, end: datetime) -> bool:
        """Check if the job finished before the given timedelta from now."""
        return self.finished_at is not None and self.finished_at <= end

    def finished_after(self, start: datetime) -> bool:
        """Check if the job finished within the given timedelta from now."""
        return self.finished_at is not None and self.finished_at >= start

    def finished_between(self, start: datetime, end: datetime) -> bool:
        """Check if the job finished between two datetimes."""
        return self.finished_after(start) and self.finished_before(end)

    def has_finished_range(
        self,
        *,  # From here only keyword arguments are allowed
        after_time: Optional[datetime] = None,
        before_time: Optional[datetime] = None,
    ) -> bool:
        if after_time is not None and before_time is not None:
            return self.finished_between(after_time, before_time)

        if after_time is not None:
            return self.finished_after(after_time)

        if before_time is not None:
            return self.finished_before(before_time)

        # Should be same as if filter was not provided
        return True


class JobLogStream(Enum):
    STDOUT = runner_events_pb.RuntimeLogEvent.OutputStream.OUTPUT_STREAM_STDOUT
    STDERR = runner_events_pb.RuntimeLogEvent.OutputStream.OUTPUT_STREAM_STDERR

    @classmethod
    def from_pb(cls, log_pb: runner_events_pb.RuntimeLogEvent) -> Optional[JobLogStream]:
        match log_pb.output_stream:
            case runner_events_pb.RuntimeLogEvent.OUTPUT_STREAM_STDOUT:
                return JobLogStream.STDOUT

            case runner_events_pb.RuntimeLogEvent.OUTPUT_STREAM_STDERR:
                return JobLogStream.STDERR

            case _:
                return None


class JobLogLevel(Enum):
    ERROR = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_ERROR
    WARN = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_WARNING
    DEBUG = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_DEBUG
    INFO = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_INFO
    TRACE = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_TRACE

    @classmethod
    def from_pb(cls, log_pb: runner_events_pb.RuntimeLogEvent) -> Optional[JobLogLevel]:
        match log_pb.level:
            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_ERROR:
                return JobLogLevel.ERROR

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_WARNING:
                return JobLogLevel.WARN

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_DEBUG:
                return JobLogLevel.DEBUG

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_INFO:
                return JobLogLevel.INFO

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_TRACE:
                return JobLogLevel.TRACE

            case _:
                return None


# TODO: I really want to change this to `JobLog`
class JobLogEvent(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobLogEvent is a model for a particular log message from a particular job.

    When you output logs within a Python model, they are persisted as JobLogEvents.

    """

    stream: Optional[JobLogStream]
    level: Optional[JobLogLevel]
    message: str

    @classmethod
    def from_proto(
        cls,
        event_pb: runner_events_pb.RunnerEvent,
        filter_by_type: Optional[runner_events_pb.RuntimeLogEvent.LogType],
    ) -> Optional[JobLogEvent]:
        if event_pb.HasField('runtime_user_log'):
            log_pb = event_pb.runtime_user_log

            if filter_by_type is None or log_pb.type == filter_by_type:
                return cls(
                    stream=JobLogStream.from_pb(log_pb),
                    level=JobLogLevel.from_pb(log_pb),
                    message=log_pb.msg,
                )

        return None

    @property
    def stream_name(self) -> str:
        return self.stream.name if self.stream is not None else ''

    @property
    def level_name(self) -> str:
        return self.level.name if self.level is not None else ''


# TODO: I think this should be the JobLog, because it's the actual log.
#       When we remove the JobLog alias (breaking change) maybe we can rename this
class JobLogList(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobLogList is a model for all of the logs from a particular job. This model is primarily
    provided as a convenience for "common" interactions with a job's log messages.

    """

    events: List[JobLogEvent]

    @classmethod
    def from_pb(
        cls,
        getlog_pb: get_logs_pb.GetLogsResponse,
        filter_by_type: runner_events_pb.RuntimeLogEvent.LogType = runner_events_pb.RuntimeLogEvent.LOG_TYPE_USER,
    ) -> JobLogList:
        log_events = []

        for runner_event in getlog_pb.events:
            job_log_event = JobLogEvent.from_proto(runner_event, filter_by_type=filter_by_type)

            if job_log_event is not None:
                log_events.append(job_log_event)

        return cls(events=log_events)

    @property
    def log_events(self) -> List[JobLogEvent]:
        return self.events

    def error_messages(self) -> list[str]:
        error_log_events = list(filter(lambda log: log.level == JobLogLevel.ERROR, self.events))
        if len(error_log_events) == 0:
            error_log_events = ['No error messages']

        return list(map(str, error_log_events))


class JobContext(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobContext is a model for immediate working context of a particular job. This currently
    includes: (1) Ref, (2) Code Snapshot, (3) Logs. A JobContext should enable a variety of
    workflows for iterating on an existing Job.

    """

    id: str
    project_id: Optional[str]
    project_name: Optional[str]

    ref: Optional[Ref]
    snapshot_dirpath: Optional[Path]
    logs: List[JobLogEvent]

    @classmethod
    def from_pb(cls, get_context_pb: job_context_pb.GetJobContextResponse) -> List[JobContext]:
        job_contexts = []
        for job_ctx in get_context_pb.job_contexts:
            id_prefix = job_ctx.job_id[:8]

            job_ref = Ref(name=job_ctx.ref)

            # Handle code snapshot decompression if present
            job_snapshot_dir = None
            if job_ctx.code_snapshot:
                try:
                    # Create a temporary directory for this job's snapshot
                    temp_dir = tempfile.mkdtemp(prefix=f'.bauplan_job_{id_prefix}')
                    snapshot_path = Path(temp_dir)

                    # The code_snapshot is a zip archive
                    with zipfile.ZipFile(file=io.BytesIO(job_ctx.code_snapshot)) as zip_handle:
                        for archive_member in zip_handle.namelist():
                            zip_handle.extract(archive_member, path=snapshot_path)

                    job_snapshot_dir = snapshot_path
                except Exception as e:
                    warnings.warn(
                        f'Failed to extract code snapshot for job {job_ctx.job_id}: {e}',
                        stacklevel=1,
                    )

            job_logs = []
            for runner_event in job_ctx.job_events:
                log_event = JobLogEvent.from_proto(
                    runner_event, filter_by_type=runner_events_pb.RuntimeLogEvent.LOG_TYPE_USER
                )

                if log_event is not None:
                    job_logs.append(log_event)

            job_contexts.append(
                JobContext(
                    id=job_ctx.job_id,
                    project_id=job_ctx.project_id,
                    project_name=job_ctx.project_name,
                    ref=job_ref,
                    snapshot_dirpath=job_snapshot_dir,
                    logs=job_logs,
                )
            )

        return job_contexts
