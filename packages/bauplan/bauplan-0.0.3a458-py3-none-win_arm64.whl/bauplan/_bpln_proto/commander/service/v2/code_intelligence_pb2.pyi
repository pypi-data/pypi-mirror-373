from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CodeIntelligenceError(_message.Message):
    __slots__ = ('type', 'message', 'traceback')
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRACEBACK_FIELD_NUMBER: _ClassVar[int]
    type: str
    message: str
    traceback: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        type: _Optional[str] = ...,
        message: _Optional[str] = ...,
        traceback: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class CodeIntelligenceResponseMetadata(_message.Message):
    __slots__ = ('status_code', 'response_id', 'response_ts')
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response_id: str
    response_ts: int
    def __init__(
        self,
        status_code: _Optional[int] = ...,
        response_id: _Optional[str] = ...,
        response_ts: _Optional[int] = ...,
    ) -> None: ...
