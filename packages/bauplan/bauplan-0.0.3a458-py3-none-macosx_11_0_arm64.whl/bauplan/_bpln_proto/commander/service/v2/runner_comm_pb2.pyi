from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RunnerJobRequest(_message.Message):
    __slots__ = ('physical_plan_v2', 'priority')
    PHYSICAL_PLAN_V2_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    physical_plan_v2: bytes
    priority: int
    def __init__(self, physical_plan_v2: _Optional[bytes] = ..., priority: _Optional[int] = ...) -> None: ...

class RunnerAction(_message.Message):
    __slots__ = ('job_id', 'action', 'runner_job_request', 'trace_id', 'parent_span_id', 'job_args')
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ACTION_UNSPECIFIED: _ClassVar[RunnerAction.Action]
        ACTION_START: _ClassVar[RunnerAction.Action]
        ACTION_CANCEL: _ClassVar[RunnerAction.Action]
        ACTION_UPLOAD: _ClassVar[RunnerAction.Action]
        ACTION_QUERY: _ClassVar[RunnerAction.Action]
        ACTION_GLOBAL_LIVELINESS_HEARTBEAT: _ClassVar[RunnerAction.Action]

    ACTION_UNSPECIFIED: RunnerAction.Action
    ACTION_START: RunnerAction.Action
    ACTION_CANCEL: RunnerAction.Action
    ACTION_UPLOAD: RunnerAction.Action
    ACTION_QUERY: RunnerAction.Action
    ACTION_GLOBAL_LIVELINESS_HEARTBEAT: RunnerAction.Action
    class JobArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    RUNNER_JOB_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ARGS_FIELD_NUMBER: _ClassVar[int]
    job_id: _common_pb2.JobId
    action: RunnerAction.Action
    runner_job_request: RunnerJobRequest
    trace_id: str
    parent_span_id: str
    job_args: _containers.ScalarMap[str, str]
    def __init__(
        self,
        job_id: _Optional[_Union[_common_pb2.JobId, _Mapping]] = ...,
        action: _Optional[_Union[RunnerAction.Action, str]] = ...,
        runner_job_request: _Optional[_Union[RunnerJobRequest, _Mapping]] = ...,
        trace_id: _Optional[str] = ...,
        parent_span_id: _Optional[str] = ...,
        job_args: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...
