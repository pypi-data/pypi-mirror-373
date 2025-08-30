import datetime
import time
from typing import Dict, List, Optional

from bauplan._bpln_proto.commander.service.v2.runner_events_pb2 import RunnerEvent, RuntimeLogEvent

# from ._protobufs.commander_pb2 import (
#     RunnerEvent,
#     RuntimeLogEvent,
# )
from .schema import _BauplanData


class CommonRunState:
    user_logs: List[str]
    runner_events: List[RunnerEvent]
    runtime_logs: List[RuntimeLogEvent]
    tasks_started: Dict[str, datetime.datetime]
    tasks_stopped: Dict[str, datetime.datetime]
    job_status: Optional[str]
    started_at_ns: int
    ended_at_ns: Optional[int]

    @property
    def duration(self) -> Optional[float]:
        if self.ended_at_ns is not None:
            return (self.ended_at_ns - self.started_at_ns) / 1_000_000_000
        return None

    @property
    def duration_ns(self) -> Optional[int]:
        if self.ended_at_ns is not None:
            return self.ended_at_ns - self.started_at_ns
        return None


class RunExecutionContext(_BauplanData):
    snapshot_id: str
    snapshot_uri: str
    project_dir: str
    ref: str
    namespace: str
    dry_run: bool
    transaction: str
    strict: str
    cache: str
    preview: str
    debug: bool
    detach: bool


class RunState(CommonRunState):
    """
    RunState tracks information about what happened during the course of a Bauplan
    job run (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions, project directory,
    job status, and failed fatal task description.

    """

    job_id: Optional[str]
    ctx: RunExecutionContext

    def __init__(
        self,
        job_id: str,
        ctx: RunExecutionContext,
        started_at_ns: Optional[int] = None,
    ) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.started_at_ns = started_at_ns or time.time_ns()
        self.user_logs = []
        self.runner_events = []
        self.runtime_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.job_status = None


class ReRunExecutionContext(_BauplanData):
    re_run_job_id: str
    ref: str
    namespace: str
    dry_run: bool
    transaction: str
    strict: str
    cache: str
    preview: str
    debug: bool


class ReRunState(CommonRunState):
    """
    ReRunState tracks information about what happened during the course of a Bauplan
    job rerun (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions,
    job status, and failed fatal task description.

    """

    job_id: str
    run_id: str
    ctx: ReRunExecutionContext

    def __init__(
        self,
        job_id: str,
        ctx: ReRunExecutionContext,
        started_at_ns: Optional[int] = None,
    ) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.started_at_ns = started_at_ns or time.time_ns()
        self.user_logs = []
        self.runner_events = []
        self.runtime_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.job_status = None


class PlanImportState:
    """
    PlanImportState tracks information about what happened during the course of an "plan import" job
    that plans a job to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    plan: Optional[Dict] = None
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []


class ApplyPlanState:
    """
    ApplyPlanState tracks information about what happened during the course of an "apply import plan" job
    that executes the plan to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    """

    job_id: str
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []


class TableCreatePlanContext(_BauplanData):
    branch_name: str
    table_name: str
    table_replace: bool
    table_partitioned_by: Optional[str]
    namespace: str
    search_string: str
    debug: bool


class TableCreatePlanState:
    """
    TableCreatePlanState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    ctx: TableCreatePlanContext
    plan: Optional[Dict]
    error: Optional[str] = None
    can_auto_apply: Optional[bool] = None
    files_to_be_imported: List[str]
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableCreatePlanContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []
        self.files_to_be_imported = []


class TableCreatePlanApplyContext(_BauplanData):
    debug: bool


class TableCreatePlanApplyState:
    """
    TableCreatePlanApplyState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    ctx: TableCreatePlanApplyContext
    plan: Optional[str] = None
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableCreatePlanApplyContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []


class TableDataImportContext(_BauplanData):
    branch_name: str
    table_name: str
    namespace: str
    search_string: str
    import_duplicate_files: bool
    best_effort: bool
    continue_on_error: bool
    transformation_query: Optional[str]
    preview: str
    debug: bool
    detach: bool


class TableDataImportState:
    """
    TableDataImportState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    ctx: TableDataImportContext
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableDataImportContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []
        self.files_to_be_imported = []
