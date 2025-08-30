from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple, Union

import yaml

from ._common import Constants
from ._validators import _Validate


@dataclass
class Profile:
    """
    A configuration profile.
    """

    name: Optional[str]
    api_key: Optional[str]
    user_session_token: Optional[str]
    project_dir: Optional[Union[str, Path]]
    branch: Optional[str]
    namespace: Optional[str]
    args: Optional[Dict[str, str]]
    cache: Optional[str]
    debug: Optional[bool]
    verbose: Optional[bool]
    api_endpoint: str
    catalog_endpoint: str
    catalog_max_records: int
    client_timeout: Optional[int]
    env: Optional[str]
    config_file_path: Optional[Union[str, Path]]
    feature_flags: Dict[str, str]

    def __init__(
        self,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        user_session_token: Optional[str] = None,
        project_dir: Optional[Union[str, Path]] = None,
        branch: Optional[str] = None,
        namespace: Optional[str] = None,
        cache: Optional[Literal['on', 'off']] = None,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        api_endpoint: Optional[str] = None,
        catalog_endpoint: Optional[str] = None,
        catalog_max_records: Optional[int] = None,
        client_timeout: Optional[int] = None,
        env: Optional[str] = None,
        config_file_path: Optional[Union[str, Path]] = None,
        feature_flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = _get_fallback_env_string('name', name, Constants.ENV_PROFILE)
        self.user_session_token = _Validate.optional_string('user_session_token', user_session_token)
        self.api_key = _get_fallback_env_string('api_key', api_key, Constants.ENV_API_KEY)
        if self.user_session_token is not None:
            self.api_key = None
        elif self.api_key is None:
            raise ValueError('api_key must be a non-empty string or None')
        self.env = _get_fallback_env_string('env', env, Constants.ENV_ENVIRONMENT) or 'prod'
        self.project_dir = Path(project_dir) if project_dir else None
        if self.project_dir:
            self.project_dir = self.project_dir.expanduser().resolve()
            if not self.project_dir.is_dir():
                raise ValueError(f'project_dir must be a directory: {self.project_dir}')
            if not self.project_dir.exists():
                raise ValueError(f'project_dir folder does not exist: {self.project_dir}')
        self.cache = _Validate.optional_string('cache', cache)
        self.branch = _Validate.optional_string('branch', branch)
        self.namespace = _Validate.optional_string('namespace', namespace)
        self.debug = _get_fallback_env_bool('debug', debug, Constants.ENV_DEBUG)
        self.verbose = _get_fallback_env_bool('verbose', verbose, Constants.ENV_VERBOSE)
        self.args = _Validate.args('args', args, {})
        self.api_endpoint = _get_api_env_endpoint('api_endpoint', self.env, api_endpoint)
        self.catalog_endpoint = _get_catalog_env_endpoint('catalog_endpoint', self.env, catalog_endpoint)
        self.catalog_max_records = (
            _Validate.optional_int('catalog_max_records', catalog_max_records)
            or Constants.CATALOG_MAX_RECORDS
        )
        self.client_timeout = _get_fallback_env_int(
            'client_timeout', client_timeout, Constants.ENV_CLIENT_TIMEOUT
        )
        self.config_file_path = Path(config_file_path) if config_file_path else None

        self.feature_flags = _Validate.feature_flags('feature_flags', feature_flags)

    @classmethod
    def load_profile(
        cls,
        profile: Optional[str] = None,
        api_key: Optional[str] = None,
        user_session_token: Optional[str] = None,
        project_dir: Optional[Union[str, Path]] = None,
        branch: Optional[str] = None,
        namespace: Optional[str] = None,
        cache: Optional[Literal['on', 'off']] = None,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        api_endpoint: Optional[str] = None,
        catalog_endpoint: Optional[str] = None,
        catalog_max_records: Optional[int] = None,
        client_timeout: Optional[int] = None,
        env: Optional[str] = None,
        config_file_path: Optional[Union[str, Path]] = None,
        feature_flags: Optional[Dict[str, Any]] = None,
    ) -> Profile:
        """
        Load a profile from a profile file.
        """
        profile = _get_fallback_env_string('profile', profile, Constants.ENV_PROFILE)
        config_file_path, raw_profile_config = _load_config_profile(profile, config_file_path)
        # TODO: how can I get the path to the config file?
        if profile is not None and not raw_profile_config:
            raise ValueError(f'profile {profile} not found in {config_file_path}')

        # Envs can override the profile file
        env = (
            _get_fallback_env_string('env', env, Constants.ENV_ENVIRONMENT)
            or raw_profile_config.get('env')
            or 'prod'
        )
        # These are the original inputs
        input_config = {
            'name': profile or 'default',
            'config_file_path': config_file_path,
            'api_key': _get_fallback_env_string('api_key', api_key, Constants.ENV_API_KEY),
            'user_session_token': user_session_token,
            'project_dir': project_dir,
            'branch': branch or raw_profile_config.get('active_branch'),
            'namespace': namespace,
            'cache': cache,
            'debug': _get_fallback_env_bool('debug', debug, Constants.ENV_DEBUG),
            'verbose': _get_fallback_env_bool('verbose', verbose, Constants.ENV_VERBOSE),
            'args': {
                # Profile args are overridden by input args
                **(raw_profile_config.get('args') or {}),
                **(args or {}),
            },
            'api_endpoint': _get_api_env_endpoint('api_endpoint', env, api_endpoint),
            'catalog_endpoint': _get_catalog_env_endpoint('api_endpoint', env, catalog_endpoint),
            'catalog_max_records': catalog_max_records,
            'client_timeout': _get_fallback_env_int(
                'client_timeout', client_timeout, Constants.ENV_CLIENT_TIMEOUT
            ),
            'env': env,
            'feature_flags': feature_flags,
        }

        # We can now map the user's config, and print a warn when a unknow key is found
        profile_config = {}
        for k, v in raw_profile_config.items():
            if k in input_config:
                profile_config[k] = v
            elif k == 'active_branch':
                profile_config['branch'] = v
            elif input_config['debug']:
                print(f'DBG: unknown profile key {k} in {config_file_path}')

        return cls(**{
            **profile_config,
            **{k: v for k, v in input_config.items() if v is not None},
        })

    @property
    def _api_grpc_base_uri(self) -> str:
        match = re.match(r'^([^:]+)://(.*)$', self.api_endpoint)
        if not match:
            raise ValueError(f'invalid api_endpoint: {self.api_endpoint}')
        return match.group(2)

    @property
    def _api_grpc_ssl(self) -> bool:
        match = re.match(r'^([^:]+)://(.*)$', self.api_endpoint)
        if not match:
            raise ValueError(f'invalid api_endpoint: {self.api_endpoint}')
        return match.group(1) == 'https'

    @property
    def _api_http_base_uri(self) -> str:
        return f'{self.api_endpoint}/api'


def _get_config_path(file_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    path = Path(file_path) if file_path else Path(os.getenv(Constants.ENV_CONFIG_PATH, Constants.CONFIG_PATH))
    if not path.is_file():
        return None
    return path


def _load_config_profile(
    name: Optional[str] = None,
    file_path: Optional[Union[str, Path]] = None,
) -> Tuple[Optional[Path], Dict[str, Any]]:
    name = _Validate.optional_string('profile', name)
    path = _get_config_path(file_path)
    if path is None or not path.exists():
        # When profile_name is set, the file must exist
        if name is not None:
            raise ValueError(f'config file {path} not found')
        # Fallback to an empty dict
        return (None, {})
    # The file exists, let's load the profile
    with open(path, 'r') as fp:
        try:
            config_data: dict[str, Any] = yaml.safe_load(fp)
        except yaml.YAMLError as e:
            raise ValueError(f'Error parsing config file {path}: {e}') from e
    # We can now load all the available profiles
    all_profiles: Dict[str, Any] = config_data.get('profiles', {})
    # Now we can fallback to the default profile
    name = name or 'default'
    profile = all_profiles.get(name)
    if name != 'default' and profile is None:
        raise ValueError(f'profile "{name}" not found in {path}')
    return (path, profile or {})


def _get_api_env_endpoint(name: str, env: Optional[str], api_endpoint: Optional[str]) -> str:
    api_endpoint = _Validate.optional_endpoint(
        name,
        endpoint=_get_fallback_env_string(
            name,
            api_endpoint,
            Constants.ENV_API_ENDPOINT,
        ),
    )
    if api_endpoint is not None:
        return api_endpoint

    if env == 'local':
        return 'http://localhost:2758'
    if env == 'dev':
        return 'https://api.use1.adev.bauplanlabs.com'
    if env == 'qa':
        return 'https://api.use1.aqa.bauplanlabs.com'
    return Constants.API_ENDPOINT


def _get_catalog_env_endpoint(name: str, env: Optional[str], catalog_endpoint: Optional[str]) -> str:
    catalog_endpoint = _Validate.optional_endpoint(
        name,
        endpoint=_get_fallback_env_string(name, catalog_endpoint, Constants.ENV_CATALOG_ENDPOINT),
    )
    if catalog_endpoint is not None:
        return catalog_endpoint

    if env == 'local':
        return 'http://localhost:35432'
    if env == 'dev':
        return 'https://api.use1.adev.bauplanlabs.com/catalog'
    if env == 'qa':
        return 'https://api.use1.aqa.bauplanlabs.com/catalog'
    return Constants.CATALOG_ENDPOINT


def _get_fallback_env_string(name: str, value: Optional[str], fallback_env_name: str) -> Optional[str]:
    safe_value = _Validate.optional_string(name, value)
    if safe_value is not None:
        return safe_value
    return os.getenv(fallback_env_name)


def _get_fallback_env_bool(name: str, value: Optional[bool], fallback_env_name: str) -> Optional[bool]:
    safe_value = _Validate.optional_boolean(name, value)
    if safe_value is not None:
        return safe_value
    env_value = os.getenv(fallback_env_name)
    if env_value is None:
        return None
    return env_value in ['1', 'on', 'true', 'yes']


def _get_fallback_env_int(name: str, value: Optional[int], fallback_env_name: str) -> Optional[int]:
    if value is not None:
        if not isinstance(value, int):
            raise ValueError(f'{name} must be a int or None')
        return value
    env_value = os.getenv(fallback_env_name)
    if env_value is None:
        return None
    try:
        return int(env_value)
    except (TypeError, ValueError) as e:
        raise ValueError(f'{fallback_env_name} must be a int or None') from e
