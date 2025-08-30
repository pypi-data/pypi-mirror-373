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

class CodeSnapshotRunRequest(_message.Message):
    __slots__ = (
        'job_request_common',
        'zip_file',
        'ref',
        'namespace',
        'dry_run',
        'transaction',
        'strict',
        'cache',
        'preview',
        'project_id',
        'project_name',
        'parameters',
        'public_key',
    )
    JOB_REQUEST_COMMON_FIELD_NUMBER: _ClassVar[int]
    ZIP_FILE_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    STRICT_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    job_request_common: _common_pb2.JobRequestCommon
    zip_file: bytes
    ref: str
    namespace: str
    dry_run: _common_pb2.JobRequestOptionalBool
    transaction: str
    strict: str
    cache: str
    preview: str
    project_id: str
    project_name: str
    parameters: _containers.RepeatedCompositeFieldContainer[_common_pb2.Parameter]
    public_key: str
    def __init__(
        self,
        job_request_common: _Optional[_Union[_common_pb2.JobRequestCommon, _Mapping]] = ...,
        zip_file: _Optional[bytes] = ...,
        ref: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        dry_run: _Optional[_Union[_common_pb2.JobRequestOptionalBool, str]] = ...,
        transaction: _Optional[str] = ...,
        strict: _Optional[str] = ...,
        cache: _Optional[str] = ...,
        preview: _Optional[str] = ...,
        project_id: _Optional[str] = ...,
        project_name: _Optional[str] = ...,
        parameters: _Optional[_Iterable[_Union[_common_pb2.Parameter, _Mapping]]] = ...,
        public_key: _Optional[str] = ...,
    ) -> None: ...

class CodeSnapshotRunResponse(_message.Message):
    __slots__ = (
        'job_response_common',
        'snapshot_id',
        'snapshot_uri',
        'ref',
        'namespace',
        'dry_run',
        'transaction',
        'strict',
        'cache',
        'preview',
        'user_branch_prefix',
        'project_id',
        'project_name',
        'parameters',
        'public_key',
        'dag_ascii',
    )
    JOB_RESPONSE_COMMON_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_URI_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    STRICT_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    USER_BRANCH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    DAG_ASCII_FIELD_NUMBER: _ClassVar[int]
    job_response_common: _common_pb2.JobResponseCommon
    snapshot_id: str
    snapshot_uri: str
    ref: str
    namespace: str
    dry_run: bool
    transaction: str
    strict: str
    cache: str
    preview: str
    user_branch_prefix: str
    project_id: str
    project_name: str
    parameters: _containers.RepeatedCompositeFieldContainer[_common_pb2.Parameter]
    public_key: str
    dag_ascii: str
    def __init__(
        self,
        job_response_common: _Optional[_Union[_common_pb2.JobResponseCommon, _Mapping]] = ...,
        snapshot_id: _Optional[str] = ...,
        snapshot_uri: _Optional[str] = ...,
        ref: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        dry_run: bool = ...,
        transaction: _Optional[str] = ...,
        strict: _Optional[str] = ...,
        cache: _Optional[str] = ...,
        preview: _Optional[str] = ...,
        user_branch_prefix: _Optional[str] = ...,
        project_id: _Optional[str] = ...,
        project_name: _Optional[str] = ...,
        parameters: _Optional[_Iterable[_Union[_common_pb2.Parameter, _Mapping]]] = ...,
        public_key: _Optional[str] = ...,
        dag_ascii: _Optional[str] = ...,
    ) -> None: ...
