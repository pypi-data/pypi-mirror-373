from typing import List, Optional, Union

from google.protobuf.json_format import MessageToJson

from ._bpln_proto.commander.service.v2.bauplan_info_pb2 import (
    GetBauplanInfoRequest,
    GetBauplanInfoResponse,
)
from ._common_operation import (
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
)
from ._validators import _Validate
from .schema import _BauplanData


class RunnerNodeInfo(_BauplanData):
    hostname: Optional[str] = None


class OrganizationInfo(_BauplanData):
    id: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    default_parameter_secret_key: Optional[str] = None
    default_parameter_secret_public_key: Optional[str] = None


class UserInfo(_BauplanData):
    id: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @property
    def full_name(self) -> Optional[str]:
        return f'{self.first_name or ""} {self.last_name or ""}'.strip() or None


class InfoState(_BauplanData):
    client_version: Optional[str] = None
    organization: Optional[OrganizationInfo] = None
    user: Optional[UserInfo] = None
    runners: Optional[List[RunnerNodeInfo]] = None


class _Info(_OperationContainer):
    @_lifecycle
    def info(
        self,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> InfoState:
        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        debug, _ = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        verbose = _Validate.optional_boolean('verbose', verbose)

        # We can now submit the request
        client_v2, metadata = self._common.get_commander_v2_and_metadata({})

        info_request = GetBauplanInfoRequest(
            api_key=self.profile.api_key,
        )
        if debug or verbose:
            print(
                'GetBauplanInfoRequest',
                'request',
                MessageToJson(info_request),
            )

        info_response: GetBauplanInfoResponse = client_v2.GetBauplanInfo(info_request, metadata=metadata)
        if debug or verbose:
            print(
                'GetBauplanInfoResponse',
                'response',
                MessageToJson(info_response),
            )

        # We can now map the response to the InfoState
        organization: Optional[OrganizationInfo] = None
        if info_response.HasField('organization_info'):
            organization = OrganizationInfo(
                id=info_response.organization_info.id,
                name=info_response.organization_info.name,
                slug=info_response.organization_info.slug,
                default_parameter_secret_key=info_response.organization_info.default_parameter_secret_key,
                default_parameter_secret_public_key=info_response.organization_info.default_parameter_secret_public_key,
            )

        user: Optional[UserInfo] = None
        if info_response.HasField('user_info'):
            user = UserInfo(
                id=info_response.user_info.id,
                username=info_response.user_info.username,
                first_name=info_response.user_info.first_name,
                last_name=info_response.user_info.last_name,
            )

        runners: List[RunnerNodeInfo] = [
            RunnerNodeInfo(
                hostname=runner.hostname,
            )
            for runner in info_response.runners
        ]

        return InfoState(
            client_version=info_response.client_version,
            organization=organization,
            user=user,
            runners=runners,
        )
