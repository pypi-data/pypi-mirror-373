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

class GetBauplanInfoRequest(_message.Message):
    __slots__ = ('api_key',)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    def __init__(self, api_key: _Optional[str] = ...) -> None: ...

class RunnerNodeInfo(_message.Message):
    __slots__ = ('public_key', 'hostname')
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    public_key: str
    hostname: str
    def __init__(self, public_key: _Optional[str] = ..., hostname: _Optional[str] = ...) -> None: ...

class OrganizationInfo(_message.Message):
    __slots__ = ('id', 'name', 'slug', 'default_parameter_secret_key', 'default_parameter_secret_public_key')
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PARAMETER_SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PARAMETER_SECRET_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    slug: str
    default_parameter_secret_key: str
    default_parameter_secret_public_key: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        slug: _Optional[str] = ...,
        default_parameter_secret_key: _Optional[str] = ...,
        default_parameter_secret_public_key: _Optional[str] = ...,
    ) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ('id', 'username', 'first_name', 'last_name')
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    username: str
    first_name: str
    last_name: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        username: _Optional[str] = ...,
        first_name: _Optional[str] = ...,
        last_name: _Optional[str] = ...,
    ) -> None: ...

class GetBauplanInfoResponse(_message.Message):
    __slots__ = ('runners', 'user', 'client_version', 'server_version', 'organization_info', 'user_info')
    RUNNERS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_INFO_FIELD_NUMBER: _ClassVar[int]
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    runners: _containers.RepeatedCompositeFieldContainer[RunnerNodeInfo]
    user: str
    client_version: str
    server_version: str
    organization_info: OrganizationInfo
    user_info: UserInfo
    def __init__(
        self,
        runners: _Optional[_Iterable[_Union[RunnerNodeInfo, _Mapping]]] = ...,
        user: _Optional[str] = ...,
        client_version: _Optional[str] = ...,
        server_version: _Optional[str] = ...,
        organization_info: _Optional[_Union[OrganizationInfo, _Mapping]] = ...,
        user_info: _Optional[_Union[UserInfo, _Mapping]] = ...,
    ) -> None: ...
