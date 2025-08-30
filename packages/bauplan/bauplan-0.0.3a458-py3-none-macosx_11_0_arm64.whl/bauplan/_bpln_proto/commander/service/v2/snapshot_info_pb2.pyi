from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSnapshotInfoRequest(_message.Message):
    __slots__ = ('snapshot_sha',)
    SNAPSHOT_SHA_FIELD_NUMBER: _ClassVar[int]
    snapshot_sha: str
    def __init__(self, snapshot_sha: _Optional[str] = ...) -> None: ...

class GetSnapshotInfoResponse(_message.Message):
    __slots__ = ('snapshot_info',)
    SNAPSHOT_INFO_FIELD_NUMBER: _ClassVar[int]
    snapshot_info: SnapshotInfo
    def __init__(self, snapshot_info: _Optional[_Union[SnapshotInfo, _Mapping]] = ...) -> None: ...

class SnapshotInfo(_message.Message):
    __slots__ = ('snapshot_zip', 'created_at')
    SNAPSHOT_ZIP_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    snapshot_zip: bytes
    created_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        snapshot_zip: _Optional[bytes] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...
