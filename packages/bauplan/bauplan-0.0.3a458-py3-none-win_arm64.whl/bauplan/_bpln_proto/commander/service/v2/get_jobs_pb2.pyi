from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
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

class GetJobsRequest(_message.Message):
    __slots__ = ('job_ids', 'all_users')
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    ALL_USERS_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    all_users: bool
    def __init__(self, job_ids: _Optional[_Iterable[str]] = ..., all_users: bool = ...) -> None: ...

class GetJobsResponse(_message.Message):
    __slots__ = ('jobs',)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_common_pb2.JobInfo]
    def __init__(self, jobs: _Optional[_Iterable[_Union[_common_pb2.JobInfo, _Mapping]]] = ...) -> None: ...
