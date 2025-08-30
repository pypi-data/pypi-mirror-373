from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class PushRunnerStatusRequest(_message.Message):
    __slots__ = ('runner_status',)
    RUNNER_STATUS_FIELD_NUMBER: _ClassVar[int]
    runner_status: RunnerStatus
    def __init__(self, runner_status: _Optional[_Union[RunnerStatus, _Mapping]] = ...) -> None: ...

class PushRunnerStatusResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RunnerStatus(_message.Message):
    __slots__ = ('job_statuses',)
    JOB_STATUSES_FIELD_NUMBER: _ClassVar[int]
    job_statuses: _containers.RepeatedCompositeFieldContainer[JobStatusV2]
    def __init__(self, job_statuses: _Optional[_Iterable[_Union[JobStatusV2, _Mapping]]] = ...) -> None: ...

class JobStatusV2(_message.Message):
    __slots__ = ('job_id', 'started_at', 'last_state_update', 'job_state', 'task_infos', 'ended_at')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_STATE_UPDATE_FIELD_NUMBER: _ClassVar[int]
    JOB_STATE_FIELD_NUMBER: _ClassVar[int]
    TASK_INFOS_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    started_at: _timestamp_pb2.Timestamp
    last_state_update: _timestamp_pb2.Timestamp
    job_state: JobState
    task_infos: _containers.RepeatedCompositeFieldContainer[TaskStatus]
    ended_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        last_state_update: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        job_state: _Optional[_Union[JobState, _Mapping]] = ...,
        task_infos: _Optional[_Iterable[_Union[TaskStatus, _Mapping]]] = ...,
        ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class JobState(_message.Message):
    __slots__ = ('state', 'since', 'not_started', 'running', 'complete', 'abort', 'fail', 'other')
    STATE_FIELD_NUMBER: _ClassVar[int]
    SINCE_FIELD_NUMBER: _ClassVar[int]
    NOT_STARTED_FIELD_NUMBER: _ClassVar[int]
    RUNNING_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    ABORT_FIELD_NUMBER: _ClassVar[int]
    FAIL_FIELD_NUMBER: _ClassVar[int]
    OTHER_FIELD_NUMBER: _ClassVar[int]
    state: _common_pb2.JobStateType
    since: _timestamp_pb2.Timestamp
    not_started: JobNotStartedDetails
    running: JobRunningDetails
    complete: JobCompleteDetails
    abort: JobAbortDetails
    fail: JobFailDetails
    other: JobOtherDetails
    def __init__(
        self,
        state: _Optional[_Union[_common_pb2.JobStateType, str]] = ...,
        since: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        not_started: _Optional[_Union[JobNotStartedDetails, _Mapping]] = ...,
        running: _Optional[_Union[JobRunningDetails, _Mapping]] = ...,
        complete: _Optional[_Union[JobCompleteDetails, _Mapping]] = ...,
        abort: _Optional[_Union[JobAbortDetails, _Mapping]] = ...,
        fail: _Optional[_Union[JobFailDetails, _Mapping]] = ...,
        other: _Optional[_Union[JobOtherDetails, _Mapping]] = ...,
    ) -> None: ...

class JobNotStartedDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class JobRunningDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class JobCompleteDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class JobAbortDetails(_message.Message):
    __slots__ = ('reason',)
    class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REASON_UNSPECIFIED: _ClassVar[JobAbortDetails.Reason]
        REASON_USER_CANCELLED: _ClassVar[JobAbortDetails.Reason]
        REASON_RUNNER_SHUTDOWN: _ClassVar[JobAbortDetails.Reason]
        REASON_TIMEOUT: _ClassVar[JobAbortDetails.Reason]

    REASON_UNSPECIFIED: JobAbortDetails.Reason
    REASON_USER_CANCELLED: JobAbortDetails.Reason
    REASON_RUNNER_SHUTDOWN: JobAbortDetails.Reason
    REASON_TIMEOUT: JobAbortDetails.Reason
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: JobAbortDetails.Reason
    def __init__(self, reason: _Optional[_Union[JobAbortDetails.Reason, str]] = ...) -> None: ...

class JobFailDetails(_message.Message):
    __slots__ = ('error_message',)
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    def __init__(self, error_message: _Optional[str] = ...) -> None: ...

class JobOtherDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskStatus(_message.Message):
    __slots__ = ('task_id', 'task_state', 'task_details', 'started_at', 'ended_at')
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_STATE_FIELD_NUMBER: _ClassVar[int]
    TASK_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    task_state: TaskState
    task_details: TaskDetailed
    started_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        task_id: _Optional[str] = ...,
        task_state: _Optional[_Union[TaskState, _Mapping]] = ...,
        task_details: _Optional[_Union[TaskDetailed, _Mapping]] = ...,
        started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class TaskState(_message.Message):
    __slots__ = ('state', 'since', 'not_started', 'running', 'complete', 'abort', 'fail', 'other')
    STATE_FIELD_NUMBER: _ClassVar[int]
    SINCE_FIELD_NUMBER: _ClassVar[int]
    NOT_STARTED_FIELD_NUMBER: _ClassVar[int]
    RUNNING_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    ABORT_FIELD_NUMBER: _ClassVar[int]
    FAIL_FIELD_NUMBER: _ClassVar[int]
    OTHER_FIELD_NUMBER: _ClassVar[int]
    state: _common_pb2.TaskStateType
    since: _timestamp_pb2.Timestamp
    not_started: TaskNotStartedDetails
    running: TaskRunningDetails
    complete: TaskCompleteDetails
    abort: TaskAbortDetails
    fail: TaskFailDetails
    other: TaskOtherDetails
    def __init__(
        self,
        state: _Optional[_Union[_common_pb2.TaskStateType, str]] = ...,
        since: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        not_started: _Optional[_Union[TaskNotStartedDetails, _Mapping]] = ...,
        running: _Optional[_Union[TaskRunningDetails, _Mapping]] = ...,
        complete: _Optional[_Union[TaskCompleteDetails, _Mapping]] = ...,
        abort: _Optional[_Union[TaskAbortDetails, _Mapping]] = ...,
        fail: _Optional[_Union[TaskFailDetails, _Mapping]] = ...,
        other: _Optional[_Union[TaskOtherDetails, _Mapping]] = ...,
    ) -> None: ...

class TaskNotStartedDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskRunningDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskCompleteDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskAbortDetails(_message.Message):
    __slots__ = ('reason',)
    class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REASON_UNSPECIFIED: _ClassVar[TaskAbortDetails.Reason]
        REASON_CANCELLED: _ClassVar[TaskAbortDetails.Reason]
        REASON_RUNNER_SHUTDOWN: _ClassVar[TaskAbortDetails.Reason]
        REASON_TIMEOUT: _ClassVar[TaskAbortDetails.Reason]

    REASON_UNSPECIFIED: TaskAbortDetails.Reason
    REASON_CANCELLED: TaskAbortDetails.Reason
    REASON_RUNNER_SHUTDOWN: TaskAbortDetails.Reason
    REASON_TIMEOUT: TaskAbortDetails.Reason
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: TaskAbortDetails.Reason
    def __init__(self, reason: _Optional[_Union[TaskAbortDetails.Reason, str]] = ...) -> None: ...

class TaskFailDetails(_message.Message):
    __slots__ = ('error_message',)
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    def __init__(self, error_message: _Optional[str] = ...) -> None: ...

class TaskOtherDetails(_message.Message):
    __slots__ = ('message',)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TaskDetailed(_message.Message):
    __slots__ = (
        'model_flight_serve',
        'model_read',
        'model_write',
        'data_lake_checkout',
        'table_create_plan',
        'table_create_plan_apply',
        'branch_merge',
        'user_sql_model_run',
        'user_python_model_run',
        'table_data_import',
    )
    MODEL_FLIGHT_SERVE_FIELD_NUMBER: _ClassVar[int]
    MODEL_READ_FIELD_NUMBER: _ClassVar[int]
    MODEL_WRITE_FIELD_NUMBER: _ClassVar[int]
    DATA_LAKE_CHECKOUT_FIELD_NUMBER: _ClassVar[int]
    TABLE_CREATE_PLAN_FIELD_NUMBER: _ClassVar[int]
    TABLE_CREATE_PLAN_APPLY_FIELD_NUMBER: _ClassVar[int]
    BRANCH_MERGE_FIELD_NUMBER: _ClassVar[int]
    USER_SQL_MODEL_RUN_FIELD_NUMBER: _ClassVar[int]
    USER_PYTHON_MODEL_RUN_FIELD_NUMBER: _ClassVar[int]
    TABLE_DATA_IMPORT_FIELD_NUMBER: _ClassVar[int]
    model_flight_serve: ModelFlightServe
    model_read: ModelRead
    model_write: ModelWrite
    data_lake_checkout: DataLakeCheckout
    table_create_plan: TableCreatePlan
    table_create_plan_apply: TableCreatePlanApply
    branch_merge: BranchMerge
    user_sql_model_run: UserSQLModelRun
    user_python_model_run: UserPythonModelRun
    table_data_import: TableDataImport
    def __init__(
        self,
        model_flight_serve: _Optional[_Union[ModelFlightServe, _Mapping]] = ...,
        model_read: _Optional[_Union[ModelRead, _Mapping]] = ...,
        model_write: _Optional[_Union[ModelWrite, _Mapping]] = ...,
        data_lake_checkout: _Optional[_Union[DataLakeCheckout, _Mapping]] = ...,
        table_create_plan: _Optional[_Union[TableCreatePlan, _Mapping]] = ...,
        table_create_plan_apply: _Optional[_Union[TableCreatePlanApply, _Mapping]] = ...,
        branch_merge: _Optional[_Union[BranchMerge, _Mapping]] = ...,
        user_sql_model_run: _Optional[_Union[UserSQLModelRun, _Mapping]] = ...,
        user_python_model_run: _Optional[_Union[UserPythonModelRun, _Mapping]] = ...,
        table_data_import: _Optional[_Union[TableDataImport, _Mapping]] = ...,
    ) -> None: ...

class ModelFlightServe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ModelRead(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ModelWrite(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DataLakeCheckout(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TableCreatePlan(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TableCreatePlanApply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BranchMerge(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserSQLModelRun(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserPythonModelRun(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TableDataImport(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
