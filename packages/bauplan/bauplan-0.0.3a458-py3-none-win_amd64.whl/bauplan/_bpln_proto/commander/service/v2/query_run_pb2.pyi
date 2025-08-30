from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryRunRequest(_message.Message):
    __slots__ = ('job_request_common', 'ref', 'sql_query', 'cache', 'namespace')
    JOB_REQUEST_COMMON_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    SQL_QUERY_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    job_request_common: _common_pb2.JobRequestCommon
    ref: str
    sql_query: str
    cache: str
    namespace: str
    def __init__(
        self,
        job_request_common: _Optional[_Union[_common_pb2.JobRequestCommon, _Mapping]] = ...,
        ref: _Optional[str] = ...,
        sql_query: _Optional[str] = ...,
        cache: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
    ) -> None: ...

class QueryRunResponse(_message.Message):
    __slots__ = ('job_response_common', 'sql_query', 'ref', 'namespace', 'cache')
    JOB_RESPONSE_COMMON_FIELD_NUMBER: _ClassVar[int]
    SQL_QUERY_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    job_response_common: _common_pb2.JobResponseCommon
    sql_query: str
    ref: str
    namespace: str
    cache: str
    def __init__(
        self,
        job_response_common: _Optional[_Union[_common_pb2.JobResponseCommon, _Mapping]] = ...,
        sql_query: _Optional[str] = ...,
        ref: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        cache: _Optional[str] = ...,
    ) -> None: ...
