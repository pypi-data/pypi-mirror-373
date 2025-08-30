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

class Component(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPONENT_UNSPECIFIED: _ClassVar[Component]
    COMPONENT_RUNNER: _ClassVar[Component]
    COMPONENT_RUNTIME: _ClassVar[Component]

class JobErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_ERROR_CODE_UNSPECIFIED: _ClassVar[JobErrorCode]
    JOB_ERROR_CODE_RUNTIME_TASK_OUT_OF_MEMORY: _ClassVar[JobErrorCode]
    JOB_ERROR_CODE_RUNTIME_TASK_USER_CODE_ERROR: _ClassVar[JobErrorCode]

COMPONENT_UNSPECIFIED: Component
COMPONENT_RUNNER: Component
COMPONENT_RUNTIME: Component
JOB_ERROR_CODE_UNSPECIFIED: JobErrorCode
JOB_ERROR_CODE_RUNTIME_TASK_OUT_OF_MEMORY: JobErrorCode
JOB_ERROR_CODE_RUNTIME_TASK_USER_CODE_ERROR: JobErrorCode

class TaskMetadata(_message.Message):
    __slots__ = (
        'level',
        'human_readable_task_type',
        'task_type',
        'function_name',
        'line_number',
        'file_name',
        'model_name',
    )
    class TaskLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TASK_LEVEL_UNSPECIFIED: _ClassVar[TaskMetadata.TaskLevel]
        TASK_LEVEL_DAG: _ClassVar[TaskMetadata.TaskLevel]
        TASK_LEVEL_SYSTEM: _ClassVar[TaskMetadata.TaskLevel]

    TASK_LEVEL_UNSPECIFIED: TaskMetadata.TaskLevel
    TASK_LEVEL_DAG: TaskMetadata.TaskLevel
    TASK_LEVEL_SYSTEM: TaskMetadata.TaskLevel
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    HUMAN_READABLE_TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    level: TaskMetadata.TaskLevel
    human_readable_task_type: str
    task_type: str
    function_name: str
    line_number: int
    file_name: str
    model_name: str
    def __init__(
        self,
        level: _Optional[_Union[TaskMetadata.TaskLevel, str]] = ...,
        human_readable_task_type: _Optional[str] = ...,
        task_type: _Optional[str] = ...,
        function_name: _Optional[str] = ...,
        line_number: _Optional[int] = ...,
        file_name: _Optional[str] = ...,
        model_name: _Optional[str] = ...,
    ) -> None: ...

class JobCompleteEvent(_message.Message):
    __slots__ = ('success', 'failure', 'cancellation', 'timeout', 'rejected', 'heartbeat_failure', 'job_id')
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FAILURE_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    success: JobSuccess
    failure: JobFailure
    cancellation: JobCancellation
    timeout: JobTimeout
    rejected: JobRejected
    heartbeat_failure: JobHeartbeatFailure
    job_id: str
    def __init__(
        self,
        success: _Optional[_Union[JobSuccess, _Mapping]] = ...,
        failure: _Optional[_Union[JobFailure, _Mapping]] = ...,
        cancellation: _Optional[_Union[JobCancellation, _Mapping]] = ...,
        timeout: _Optional[_Union[JobTimeout, _Mapping]] = ...,
        rejected: _Optional[_Union[JobRejected, _Mapping]] = ...,
        heartbeat_failure: _Optional[_Union[JobHeartbeatFailure, _Mapping]] = ...,
        job_id: _Optional[str] = ...,
    ) -> None: ...

class JobSuccess(_message.Message):
    __slots__ = ('msg',)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class JobRejected(_message.Message):
    __slots__ = ('reason',)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class JobHeartbeatFailure(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class JobFailure(_message.Message):
    __slots__ = ('component', 'error_message', 'error_code', 'stack_trace')
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    component: Component
    error_message: str
    error_code: int
    stack_trace: str
    def __init__(
        self,
        component: _Optional[_Union[Component, str]] = ...,
        error_message: _Optional[str] = ...,
        error_code: _Optional[int] = ...,
        stack_trace: _Optional[str] = ...,
    ) -> None: ...

class JobCancellation(_message.Message):
    __slots__ = ('reason',)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class JobTimeout(_message.Message):
    __slots__ = ('msg',)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class TaskStartEvent(_message.Message):
    __slots__ = ('task_metadata', 'timestamp', 'task_id', 'task_name')
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    def __init__(
        self,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
    ) -> None: ...

class TaskCompleteEvent(_message.Message):
    __slots__ = (
        'success',
        'failure',
        'cancel',
        'timeout',
        'skipped',
        'task_metadata',
        'timestamp',
        'task_id',
        'task_name',
    )
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    success: TaskSuccess
    failure: TaskFailure
    cancel: TaskCancelled
    timeout: TaskTimeout
    skipped: TaskSkipped
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    def __init__(
        self,
        success: _Optional[_Union[TaskSuccess, _Mapping]] = ...,
        failure: _Optional[_Union[TaskFailure, _Mapping]] = ...,
        cancel: _Optional[_Union[TaskCancelled, _Mapping]] = ...,
        timeout: _Optional[_Union[TaskTimeout, _Mapping]] = ...,
        skipped: _Optional[_Union[TaskSkipped, _Mapping]] = ...,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
    ) -> None: ...

class TaskSuccess(_message.Message):
    __slots__ = ('message', 'runtime_table_preview')
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_TABLE_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    message: str
    runtime_table_preview: _containers.RepeatedCompositeFieldContainer[RuntimeTablePreview]
    def __init__(
        self,
        message: _Optional[str] = ...,
        runtime_table_preview: _Optional[_Iterable[_Union[RuntimeTablePreview, _Mapping]]] = ...,
    ) -> None: ...

class RuntimeTablePreview(_message.Message):
    __slots__ = ('columns', 'table_name')
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[RuntimeTableColumnInfo]
    table_name: str
    def __init__(
        self,
        columns: _Optional[_Iterable[_Union[RuntimeTableColumnInfo, _Mapping]]] = ...,
        table_name: _Optional[str] = ...,
    ) -> None: ...

class RuntimeTableColumnInfo(_message.Message):
    __slots__ = ('column_name', 'column_type', 'values')
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    column_type: str
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        column_name: _Optional[str] = ...,
        column_type: _Optional[str] = ...,
        values: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class TaskSkipped(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskFailure(_message.Message):
    __slots__ = ('component', 'error_message', 'error_code', 'stack_trace', 'is_fatal')
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    IS_FATAL_FIELD_NUMBER: _ClassVar[int]
    component: Component
    error_message: str
    error_code: int
    stack_trace: str
    is_fatal: bool
    def __init__(
        self,
        component: _Optional[_Union[Component, str]] = ...,
        error_message: _Optional[str] = ...,
        error_code: _Optional[int] = ...,
        stack_trace: _Optional[str] = ...,
        is_fatal: bool = ...,
    ) -> None: ...

class TaskCancelled(_message.Message):
    __slots__ = ('reason',)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class TaskTimeout(_message.Message):
    __slots__ = ('message',)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class FlightServerStartEvent(_message.Message):
    __slots__ = ('endpoint', 'job_id', 'task_id', 'num_rows', 'use_tls', 'connection_method', 'magic_token')
    class ServerAccessMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVER_ACCESS_METHOD_UNSPECIFIED: _ClassVar[FlightServerStartEvent.ServerAccessMethod]
        SERVER_ACCESS_METHOD_PRIVATE_LINK: _ClassVar[FlightServerStartEvent.ServerAccessMethod]
        SERVER_ACCESS_METHOD_PUBLIC_INTERNET: _ClassVar[FlightServerStartEvent.ServerAccessMethod]

    SERVER_ACCESS_METHOD_UNSPECIFIED: FlightServerStartEvent.ServerAccessMethod
    SERVER_ACCESS_METHOD_PRIVATE_LINK: FlightServerStartEvent.ServerAccessMethod
    SERVER_ACCESS_METHOD_PUBLIC_INTERNET: FlightServerStartEvent.ServerAccessMethod
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_ROWS_FIELD_NUMBER: _ClassVar[int]
    USE_TLS_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    MAGIC_TOKEN_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    job_id: str
    task_id: str
    num_rows: int
    use_tls: bool
    connection_method: FlightServerStartEvent.ServerAccessMethod
    magic_token: str
    def __init__(
        self,
        endpoint: _Optional[str] = ...,
        job_id: _Optional[str] = ...,
        task_id: _Optional[str] = ...,
        num_rows: _Optional[int] = ...,
        use_tls: bool = ...,
        connection_method: _Optional[_Union[FlightServerStartEvent.ServerAccessMethod, str]] = ...,
        magic_token: _Optional[str] = ...,
    ) -> None: ...

class RuntimeLogEvent(_message.Message):
    __slots__ = ('level', 'output_stream', 'type', 'emit_timestamp_ns', 'msg', 'task_metadata', 'job_id')
    class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOG_LEVEL_UNSPECIFIED: _ClassVar[RuntimeLogEvent.LogLevel]
        LOG_LEVEL_ERROR: _ClassVar[RuntimeLogEvent.LogLevel]
        LOG_LEVEL_WARNING: _ClassVar[RuntimeLogEvent.LogLevel]
        LOG_LEVEL_DEBUG: _ClassVar[RuntimeLogEvent.LogLevel]
        LOG_LEVEL_INFO: _ClassVar[RuntimeLogEvent.LogLevel]
        LOG_LEVEL_TRACE: _ClassVar[RuntimeLogEvent.LogLevel]

    LOG_LEVEL_UNSPECIFIED: RuntimeLogEvent.LogLevel
    LOG_LEVEL_ERROR: RuntimeLogEvent.LogLevel
    LOG_LEVEL_WARNING: RuntimeLogEvent.LogLevel
    LOG_LEVEL_DEBUG: RuntimeLogEvent.LogLevel
    LOG_LEVEL_INFO: RuntimeLogEvent.LogLevel
    LOG_LEVEL_TRACE: RuntimeLogEvent.LogLevel
    class OutputStream(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OUTPUT_STREAM_UNSPECIFIED: _ClassVar[RuntimeLogEvent.OutputStream]
        OUTPUT_STREAM_STDOUT: _ClassVar[RuntimeLogEvent.OutputStream]
        OUTPUT_STREAM_STDERR: _ClassVar[RuntimeLogEvent.OutputStream]

    OUTPUT_STREAM_UNSPECIFIED: RuntimeLogEvent.OutputStream
    OUTPUT_STREAM_STDOUT: RuntimeLogEvent.OutputStream
    OUTPUT_STREAM_STDERR: RuntimeLogEvent.OutputStream
    class LogType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOG_TYPE_UNSPECIFIED: _ClassVar[RuntimeLogEvent.LogType]
        LOG_TYPE_SYSTEM: _ClassVar[RuntimeLogEvent.LogType]
        LOG_TYPE_USER: _ClassVar[RuntimeLogEvent.LogType]

    LOG_TYPE_UNSPECIFIED: RuntimeLogEvent.LogType
    LOG_TYPE_SYSTEM: RuntimeLogEvent.LogType
    LOG_TYPE_USER: RuntimeLogEvent.LogType
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EMIT_TIMESTAMP_NS_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    level: RuntimeLogEvent.LogLevel
    output_stream: RuntimeLogEvent.OutputStream
    type: RuntimeLogEvent.LogType
    emit_timestamp_ns: int
    msg: str
    task_metadata: TaskMetadata
    job_id: str
    def __init__(
        self,
        level: _Optional[_Union[RuntimeLogEvent.LogLevel, str]] = ...,
        output_stream: _Optional[_Union[RuntimeLogEvent.OutputStream, str]] = ...,
        type: _Optional[_Union[RuntimeLogEvent.LogType, str]] = ...,
        emit_timestamp_ns: _Optional[int] = ...,
        msg: _Optional[str] = ...,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        job_id: _Optional[str] = ...,
    ) -> None: ...

class RuntimeLogMsg(_message.Message):
    __slots__ = ('level', 'message')
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: str
    message: str
    def __init__(self, level: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class TableCreatePlanDoneEvent(_message.Message):
    __slots__ = (
        'task_metadata',
        'timestamp',
        'task_id',
        'task_name',
        'plan_as_yaml',
        'success',
        'error_message',
        'files_to_be_imported',
        'can_auto_apply',
    )
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAN_AS_YAML_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILES_TO_BE_IMPORTED_FIELD_NUMBER: _ClassVar[int]
    CAN_AUTO_APPLY_FIELD_NUMBER: _ClassVar[int]
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    plan_as_yaml: str
    success: bool
    error_message: str
    files_to_be_imported: _containers.RepeatedScalarFieldContainer[str]
    can_auto_apply: bool
    def __init__(
        self,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
        plan_as_yaml: _Optional[str] = ...,
        success: bool = ...,
        error_message: _Optional[str] = ...,
        files_to_be_imported: _Optional[_Iterable[str]] = ...,
        can_auto_apply: bool = ...,
    ) -> None: ...

class TableCreatePlanApplyDoneEvent(_message.Message):
    __slots__ = ('task_metadata', 'timestamp', 'task_id', 'task_name', 'success', 'error_message')
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    success: bool
    error_message: str
    def __init__(
        self,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
        success: bool = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...

class ImportPlanCreatedEvent(_message.Message):
    __slots__ = (
        'task_metadata',
        'timestamp',
        'task_id',
        'task_name',
        'plan_as_yaml',
        'success',
        'error_message',
    )
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAN_AS_YAML_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    plan_as_yaml: str
    success: bool
    error_message: str
    def __init__(
        self,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
        plan_as_yaml: _Optional[str] = ...,
        success: bool = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...

class ApplyPlanDoneEvent(_message.Message):
    __slots__ = ('task_metadata', 'timestamp', 'task_id', 'task_name', 'success', 'error_message')
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_metadata: TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    success: bool
    error_message: str
    def __init__(
        self,
        task_metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        task_id: _Optional[str] = ...,
        task_name: _Optional[str] = ...,
        success: bool = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...

class GlobalLivelinessHeartbeat(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RunnerEvent(_message.Message):
    __slots__ = (
        'task_start',
        'task_completion',
        'job_completion',
        'runtime_user_log',
        'flight_server_start',
        'import_plan_created',
        'apply_plan_done',
        'table_create_plan_done_event',
        'table_create_plan_apply_done_event',
        'global_liveliness_heartbeat',
    )
    TASK_START_FIELD_NUMBER: _ClassVar[int]
    TASK_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    JOB_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_USER_LOG_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_SERVER_START_FIELD_NUMBER: _ClassVar[int]
    IMPORT_PLAN_CREATED_FIELD_NUMBER: _ClassVar[int]
    APPLY_PLAN_DONE_FIELD_NUMBER: _ClassVar[int]
    TABLE_CREATE_PLAN_DONE_EVENT_FIELD_NUMBER: _ClassVar[int]
    TABLE_CREATE_PLAN_APPLY_DONE_EVENT_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_LIVELINESS_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    task_start: TaskStartEvent
    task_completion: TaskCompleteEvent
    job_completion: JobCompleteEvent
    runtime_user_log: RuntimeLogEvent
    flight_server_start: FlightServerStartEvent
    import_plan_created: ImportPlanCreatedEvent
    apply_plan_done: ApplyPlanDoneEvent
    table_create_plan_done_event: TableCreatePlanDoneEvent
    table_create_plan_apply_done_event: TableCreatePlanApplyDoneEvent
    global_liveliness_heartbeat: GlobalLivelinessHeartbeat
    def __init__(
        self,
        task_start: _Optional[_Union[TaskStartEvent, _Mapping]] = ...,
        task_completion: _Optional[_Union[TaskCompleteEvent, _Mapping]] = ...,
        job_completion: _Optional[_Union[JobCompleteEvent, _Mapping]] = ...,
        runtime_user_log: _Optional[_Union[RuntimeLogEvent, _Mapping]] = ...,
        flight_server_start: _Optional[_Union[FlightServerStartEvent, _Mapping]] = ...,
        import_plan_created: _Optional[_Union[ImportPlanCreatedEvent, _Mapping]] = ...,
        apply_plan_done: _Optional[_Union[ApplyPlanDoneEvent, _Mapping]] = ...,
        table_create_plan_done_event: _Optional[_Union[TableCreatePlanDoneEvent, _Mapping]] = ...,
        table_create_plan_apply_done_event: _Optional[_Union[TableCreatePlanApplyDoneEvent, _Mapping]] = ...,
        global_liveliness_heartbeat: _Optional[_Union[GlobalLivelinessHeartbeat, _Mapping]] = ...,
    ) -> None: ...
