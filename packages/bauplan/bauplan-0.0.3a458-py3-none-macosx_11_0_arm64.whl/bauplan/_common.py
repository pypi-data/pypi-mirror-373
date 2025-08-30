from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from typing import Optional


class Constants:
    HTTP_METHOD_GET = 'GET'
    HTTP_METHOD_POST = 'POST'
    HTTP_METHOD_PUT = 'PUT'
    HTTP_METHOD_DELETE = 'DELETE'
    HTTP_METHOD_PATCH = 'PATCH'

    HTTP_HEADER_API_KEY = 'x-bauplan-api-key'
    HTTP_HEADER_USER_SESSION_TOKEN = 'x-bauplan-user-session-token'  # noqa: S105
    HTTP_HEADER_FEATURE_FLAGS = 'x-bauplan-feature-flags'
    HTTP_HEADER_PYPI_VERSION_KEY = 'x-bauplan-pypi-version'

    FEATURE_FLAG_CHECK_PYPI_VERSION = 'check-pypi-version'

    FLIGHT_INTIAL_TIMEOUT_SECONDS = 30
    FLIGHT_QUERY_TIMEOUT_SECONDS = 600
    FLIGHT_ACTION_SHUTDOWN_QUERY_SERVER = b'shutdown'

    DEFAULT_JOB_TIMEOUT = 60 * 60 * 24
    DEFAULT_API_CALL_TIMEOUT_SECONDS = 30

    # TODO(nathanleclaire): These need to be reconciled with the new protobuf
    # definitions introduced for detach mode.
    JOB_STATUS_FAILED = 'FAILED'
    JOB_STATUS_SUCCESS = 'SUCCESS'
    JOB_STATUS_CANCELLED = 'CANCELLED'
    JOB_STATUS_TIMEOUT = 'TIMEOUT'
    JOB_STATUS_HEARTBEAT_FAILURE = 'HEARTBEAT_FAILURE'
    JOB_STATUS_REJECTED = 'REJECTED'
    JOB_STATUS_UNKNOWN = 'UNKNOWN'

    PROJECT_FILE_NAME = 'bauplan_project'
    CONFIG_PATH = Path.home() / '.bauplan' / 'config.yml'

    API_ENDPOINT = 'https://api.use1.aprod.bauplanlabs.com'
    CATALOG_ENDPOINT = 'https://api.use1.aprod.bauplanlabs.com/catalog'
    CATALOG_MAX_RECORDS = 500

    # Enviroment variables:
    # - when prefixed with BPLN_ are private, for internal use only
    ENV_VERSION = 'BPLN_VERSION'
    ENV_ENVIRONMENT = 'BPLN_ENV'
    ENV_DEBUG = 'BPLN_DEBUG'
    ENV_VERBOSE = 'BPLN_VERBOSE'
    # - when prefixed with BAUPLAN_ are public
    ENV_API_KEY = 'BAUPLAN_API_KEY'
    ENV_PROFILE = 'BAUPLAN_PROFILE'
    ENV_CLIENT_TIMEOUT = 'BAUPLAN_CLIENT_TIMEOUT'
    ENV_CONFIG_PATH = 'BAUPLAN_CONFIG_PATH'
    ENV_API_ENDPOINT = 'BAUPLAN_API_ENDPOINT'
    ENV_CATALOG_ENDPOINT = 'BAUPLAN_CATALOG_ENDPOINT'


if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib.metadata as metadata  # type: ignore


def get_metadata_version() -> str:
    return metadata.version(__package__ or 'bauplan')


BAUPLAN_VERSION: Optional[str] = None
try:
    BAUPLAN_VERSION = os.getenv(Constants.ENV_VERSION, get_metadata_version())
except Exception:
    print('`bauplan` package not found')

CLIENT_HOSTNAME = socket.gethostname()
