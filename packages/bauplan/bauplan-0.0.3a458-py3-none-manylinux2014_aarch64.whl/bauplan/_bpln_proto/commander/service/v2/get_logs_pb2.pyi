from bauplan._bpln_proto.commander.service.v2 import runner_events_pb2 as _runner_events_pb2
from google.protobuf.internal import containers as _containers
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

class GetLogsRequest(_message.Message):
    __slots__ = ('job_id', 'start', 'end', 'limit')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    start: int
    end: int
    limit: int
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class GetLogsResponse(_message.Message):
    __slots__ = ('events',)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[_runner_events_pb2.RunnerEvent]
    def __init__(
        self, events: _Optional[_Iterable[_Union[_runner_events_pb2.RunnerEvent, _Mapping]]] = ...
    ) -> None: ...
