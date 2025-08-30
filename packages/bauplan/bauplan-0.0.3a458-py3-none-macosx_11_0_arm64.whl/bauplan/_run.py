import time
from dataclasses import dataclass
from datetime import datetime
from itertools import starmap
from typing import Dict, Iterable, List, Optional, TypeVar, Union

from google.protobuf.json_format import MessageToJson

from ._bpln_proto.commander.service.v2.code_snapshot_re_run_pb2 import (
    CodeSnapshotReRunRequest,
    CodeSnapshotReRunResponse,
)
from ._bpln_proto.commander.service.v2.code_snapshot_run_pb2 import (
    CodeSnapshotRunRequest,
    CodeSnapshotRunResponse,
)
from ._bpln_proto.commander.service.v2.common_pb2 import (
    BoolParameterValue,
    FloatParameterValue,
    IntParameterValue,
    JobRequestCommon,
    Parameter,
    SecretParameterValue,
    StrParameterValue,
    VaultParameterValue,
)
from ._bpln_proto.commander.service.v2.subscribe_logs_pb2 import (
    SubscribeLogsRequest,
    SubscribeLogsResponse,
)
from ._common import (
    BAUPLAN_VERSION,
    CLIENT_HOSTNAME,
    Constants,
)
from ._common_operation import (
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
    _print_planner_logs,
)
from ._info import _Info
from ._project_manager import (
    BaseParameter,
    BoolParameter,
    FloatParameter,
    IntParameter,
    ProjectManager,
    SecretParameter,
    StrParameter,
    VaultParameter,
)
from ._validators import _Validate
from .errors import EncryptionNotSupportedError
from .state import CommonRunState, ReRunExecutionContext, ReRunState, RunExecutionContext, RunState

GenericState = TypeVar('GenericState', bound=CommonRunState)


@dataclass
class JobStatus:
    """The status of a submitted job."""

    canceled: str = Constants.JOB_STATUS_CANCELLED
    cancelled: str = Constants.JOB_STATUS_CANCELLED
    failed: str = Constants.JOB_STATUS_FAILED
    rejected: str = Constants.JOB_STATUS_REJECTED
    success: str = Constants.JOB_STATUS_SUCCESS
    timeout: str = Constants.JOB_STATUS_TIMEOUT
    heartbeat_failure: str = Constants.JOB_STATUS_HEARTBEAT_FAILURE
    unknown: str = Constants.JOB_STATUS_UNKNOWN


def _handle_log(
    log: SubscribeLogsResponse,
    run_state: CommonRunState,
    debug: Optional[bool],
    verbose: Optional[bool],
) -> bool:
    runner_event = log.runner_event
    event_type = runner_event.WhichOneof('event')
    run_state.runner_events.append(runner_event)
    if event_type == 'task_start':
        ev = runner_event.task_start
        run_state.tasks_started[ev.task_name] = datetime.now()
    elif event_type == 'task_completion':
        ev = runner_event.task_completion
        run_state.tasks_stopped[ev.task_name] = datetime.now()
    elif event_type == 'job_completion':
        match runner_event.job_completion.WhichOneof('outcome'):
            case 'success':
                run_state.job_status = JobStatus.success
            case 'failure':
                run_state.job_status = JobStatus.failed
            case 'rejected':
                run_state.job_status = JobStatus.rejected
            case 'cancellation':
                run_state.job_status = JobStatus.cancelled
            case 'timeout':
                run_state.job_status = JobStatus.timeout
            case 'heartbeat_failure':
                run_state.job_status = JobStatus.heartbeat_failure
            case _:
                run_state.job_status = JobStatus.unknown
        return True
    elif event_type == 'runtime_user_log':
        ev = runner_event.runtime_user_log
        run_state.user_logs.append(ev)
    elif debug or verbose:
        print(debug, 'Unknown event type', event_type)
    return False


def _handle_log_stream(
    state: GenericState,
    log_stream: Iterable[SubscribeLogsResponse],
    debug: Optional[bool],
    verbose: Optional[bool],
) -> GenericState:
    for log in log_stream:
        if verbose:
            print('log_stream:', log)
        if _handle_log(log, state, debug, verbose):
            break

    state.ended_at_ns = time.time_ns()

    return state


class _Run(_OperationContainer):
    @_lifecycle
    def run(
        self,
        project_dir: Optional[str] = None,
        ref: Optional[str] = None,
        namespace: Optional[str] = None,
        parameters: Optional[Dict[str, Optional[Union[str, int, float, bool]]]] = None,
        cache: Optional[str] = None,
        transaction: Optional[str] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[str] = None,
        preview: Optional[str] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # internal
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
        detach: bool = False,
    ) -> RunState:
        """
        Run a Bauplan project and return the state of the run. This is the equivalent of
        running through the CLI the `bauplan run` command.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        started_at_ns = time.time_ns()

        secret_key: Optional[str] = None
        secret_public_key: Optional[str] = None

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        parameters = _Validate.parameters('parameters', parameters)
        project_dir = _Validate.optional_string('project_dir', project_dir) or str(
            self.profile.project_dir or '.'
        )
        ref = _Validate.optional_ref('ref', ref, self.profile.branch)
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        cache_flag = _Validate.optional_on_off_flag('cache', cache, self.profile.cache)
        transaction_flag = _Validate.optional_on_off_flag('transaction', transaction)
        dry_run, dry_run_flag = _Validate.pb2_optional_boolean('dry_run', dry_run)
        strict_flag = _Validate.optional_on_off_flag('strict', strict)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        preview = _Validate.optional_string('preview', preview)
        args = _Validate.args('args', args, self.profile.args)
        verbose = _Validate.optional_boolean('verbose', verbose)
        detach = _Validate.boolean('detach', detach)
        priority = _Validate.optional_int('priority', priority)

        # We can now parse the user's project
        project_manager = ProjectManager.parse_project_dir(project_dir)
        assert project_manager.file_path is not None
        if project_manager.overwrite_secret_parameters(parameters):
            # When the user wants to overwrite some secret parameters, we need to fetch the public key
            info_res = _Info(self._common.profile).info(
                debug=debug,
                verbose=verbose,
                client_timeout=client_timeout,
            )
            if info_res.organization is None:
                raise EncryptionNotSupportedError
            if info_res.organization.default_parameter_secret_key is None:
                raise EncryptionNotSupportedError
            if info_res.organization.default_parameter_secret_public_key is None:
                raise EncryptionNotSupportedError
            secret_key = info_res.organization.default_parameter_secret_key
            secret_public_key = info_res.organization.default_parameter_secret_public_key

        zip_file, final_parameters, _ = project_manager.package(
            overwrite_values=parameters,
            secret_key=secret_key,
            secret_public_key=secret_public_key,
        )

        # We can now submit the request
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args)

        project_name = project_manager.project.name
        if not project_name or not project_name.strip():
            project_name = project_manager.project.id

        job_request_common = JobRequestCommon(
            module_version=BAUPLAN_VERSION,
            hostname=CLIENT_HOSTNAME,
            args=args,
            debug=debug_flag,
        )
        if priority is not None:
            job_request_common.priority = priority

        plan_request = CodeSnapshotRunRequest(
            job_request_common=job_request_common,
            zip_file=zip_file,
            ref=ref,
            namespace=namespace,
            dry_run=dry_run_flag,
            transaction=transaction_flag,
            strict=strict_flag,
            cache=cache_flag,
            preview=preview,
            project_id=project_manager.project.id,
            project_name=project_name,
            parameters=_get_proto_parameters(final_parameters),
        )
        if debug or verbose:
            print(
                'CodeSnapshotRunRequest',
                'project_dir',
                project_manager.dir_path,
                'project_file',
                project_manager.file_path,
                'project_id',
                project_manager.project.id,
                'project_name',
                project_name,
                'request',
                MessageToJson(plan_request),
            )

        plan_response: CodeSnapshotRunResponse = client_v2.CodeSnapshotRun(plan_request, metadata=metadata)
        if debug or verbose:
            print(
                'CodeSnapshotRunResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(
            plan_response.job_response_common.logs,
            debug or verbose,
            project_dir=project_dir,
        )

        if detach:
            return RunState(
                job_id=plan_response.job_response_common.job_id,
                ctx=RunExecutionContext(
                    snapshot_id=plan_response.snapshot_id,
                    snapshot_uri=plan_response.snapshot_uri,
                    project_dir=project_dir,
                    ref=plan_response.ref,
                    namespace=plan_response.namespace,
                    dry_run=plan_response.dry_run,
                    transaction=plan_response.transaction,
                    strict=plan_response.strict,
                    cache=plan_response.cache,
                    preview=plan_response.preview,
                    debug=plan_response.job_response_common.debug,
                    detach=detach,
                ),
                started_at_ns=started_at_ns,
            )

        job_id = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)

        return _handle_log_stream(
            state=RunState(
                job_id=plan_response.job_response_common.job_id,
                ctx=RunExecutionContext(
                    snapshot_id=plan_response.snapshot_id,
                    snapshot_uri=plan_response.snapshot_uri,
                    project_dir=project_dir,
                    ref=plan_response.ref,
                    namespace=plan_response.namespace,
                    dry_run=plan_response.dry_run,
                    transaction=plan_response.transaction,
                    strict=plan_response.strict,
                    cache=plan_response.cache,
                    preview=plan_response.preview,
                    debug=plan_response.job_response_common.debug,
                    detach=detach,
                ),
                started_at_ns=started_at_ns,
            ),
            log_stream=log_stream,
            debug=debug,
            verbose=verbose,
        )

    @_lifecycle
    def rerun(
        self,
        job_id: str,
        ref: Optional[str] = None,
        namespace: Optional[str] = None,
        cache: Optional[str] = None,
        transaction: Optional[str] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[str] = None,
        preview: Optional[str] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        # internal
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> ReRunState:
        """
        Run a Bauplan project and return the state of the run. This is the equivalent of
        running through the CLI the `bauplan run` command.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        started_at_ns = time.time_ns()

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        re_run_job_id = _Validate.string('job_id', job_id)
        ref = _Validate.optional_ref('ref', ref, self.profile.branch)
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        cache_flag = _Validate.optional_on_off_flag('cache', cache, self.profile.cache)
        transaction_flag = _Validate.optional_on_off_flag('transaction', transaction)
        dry_run, dry_run_flag = _Validate.pb2_optional_boolean('dry_run', dry_run)
        strict_flag = _Validate.optional_on_off_flag('strict', strict)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        preview = _Validate.optional_string('preview', preview)
        args = _Validate.args('args', args, self.profile.args)
        verbose = _Validate.optional_boolean('verbose', verbose)
        priority = _Validate.optional_int('priority', priority)

        # We can now submit the request
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args)

        job_request_common = JobRequestCommon(
            module_version=BAUPLAN_VERSION,
            hostname=CLIENT_HOSTNAME,
            args=args,
            debug=debug_flag,
        )
        if priority is not None:
            job_request_common.priority = priority

        plan_request = CodeSnapshotReRunRequest(
            job_request_common=job_request_common,
            re_run_job_id=re_run_job_id,
            ref=ref,
            namespace=namespace,
            dry_run=dry_run_flag,
            transaction=transaction_flag,
            strict=strict_flag,
            preview=preview,
            cache=cache_flag,
        )
        if debug or verbose:
            print(
                'CodeSnapshotReRunRequest',
                'request',
                MessageToJson(plan_request),
            )

        plan_response: CodeSnapshotReRunResponse = client_v2.CodeSnapshotReRun(
            plan_request, metadata=metadata
        )
        if debug or verbose:
            print(
                'CodeSnapshotReRunResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(plan_response.job_response_common.logs, debug or verbose)

        job = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)

        return _handle_log_stream(
            state=ReRunState(
                job_id=plan_response.job_response_common.job_id,
                ctx=ReRunExecutionContext(
                    re_run_job_id=re_run_job_id,
                    ref=plan_response.ref,
                    namespace=plan_response.namespace,
                    dry_run=plan_response.dry_run,
                    transaction=plan_response.transaction,
                    strict=plan_response.strict,
                    cache=plan_response.cache,
                    preview=plan_response.preview,
                    debug=plan_response.job_response_common.debug,
                ),
                started_at_ns=started_at_ns,
            ),
            log_stream=log_stream,
            debug=debug,
            verbose=verbose,
        )


def _get_proto_parameters(parameters: Dict[str, BaseParameter]) -> List[Parameter]:
    return list(starmap(_get_proto_parameter, parameters.items()))


def _get_proto_parameter(name: str, parameter: BaseParameter) -> Parameter:
    match parameter:
        case IntParameter():
            return Parameter(name=name, int_value=IntParameterValue(value=parameter.default))
        case FloatParameter():
            return Parameter(name=name, float_value=FloatParameterValue(value=parameter.default))
        case BoolParameter():
            return Parameter(name=name, bool_value=BoolParameterValue(value=parameter.default))
        case StrParameter():
            return Parameter(name=name, str_value=StrParameterValue(value=parameter.default))
        case SecretParameter():
            return Parameter(
                name=name,
                secret_value=SecretParameterValue(
                    value=parameter.default,
                    key=parameter.key,
                ),
            )
        case VaultParameter():
            return Parameter(name=name, vault_value=VaultParameterValue(value=parameter.default))
        case _:
            raise ValueError(f'Unknown parameter type: {type(parameter)}')
