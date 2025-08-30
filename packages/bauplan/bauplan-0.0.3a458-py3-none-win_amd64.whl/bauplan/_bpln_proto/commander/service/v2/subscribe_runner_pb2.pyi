from bauplan._bpln_proto.commander.service.v2 import runner_comm_pb2 as _runner_comm_pb2
from bauplan._bpln_proto.commander.service.v2 import runner_events_pb2 as _runner_events_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscribeRunnerResponse(_message.Message):
    __slots__ = ('action',)
    ACTION_FIELD_NUMBER: _ClassVar[int]
    action: _runner_comm_pb2.RunnerAction
    def __init__(self, action: _Optional[_Union[_runner_comm_pb2.RunnerAction, _Mapping]] = ...) -> None: ...

class SubscribeRunnerRequest(_message.Message):
    __slots__ = ('job_id', 'runner_event')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_EVENT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    runner_event: _runner_events_pb2.RunnerEvent
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        runner_event: _Optional[_Union[_runner_events_pb2.RunnerEvent, _Mapping]] = ...,
    ) -> None: ...
