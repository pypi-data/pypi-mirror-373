from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableCreatePlanApplyRequest(_message.Message):
    __slots__ = ('job_request_common', 'plan_yaml')
    JOB_REQUEST_COMMON_FIELD_NUMBER: _ClassVar[int]
    PLAN_YAML_FIELD_NUMBER: _ClassVar[int]
    job_request_common: _common_pb2.JobRequestCommon
    plan_yaml: str
    def __init__(
        self,
        job_request_common: _Optional[_Union[_common_pb2.JobRequestCommon, _Mapping]] = ...,
        plan_yaml: _Optional[str] = ...,
    ) -> None: ...

class TableCreatePlanApplyResponse(_message.Message):
    __slots__ = ('job_response_common',)
    JOB_RESPONSE_COMMON_FIELD_NUMBER: _ClassVar[int]
    job_response_common: _common_pb2.JobResponseCommon
    def __init__(
        self, job_response_common: _Optional[_Union[_common_pb2.JobResponseCommon, _Mapping]] = ...
    ) -> None: ...
