from typing import Any, Dict, Iterable, Optional, Union

from google.protobuf.json_format import MessageToJson

from bauplan._bpln_proto.commander.service.v2.subscribe_logs_pb2 import (
    SubscribeLogsRequest,
    SubscribeLogsResponse,
)

from ._bpln_proto.commander.service.v2.common_pb2 import JobRequestCommon
from ._bpln_proto.commander.service.v2.table_create_plan_apply_pb2 import (
    TableCreatePlanApplyRequest,
    TableCreatePlanApplyResponse,
)
from ._bpln_proto.commander.service.v2.table_create_plan_pb2 import (
    TableCreatePlanRequest,
    TableCreatePlanResponse,
)
from ._common import BAUPLAN_VERSION, CLIENT_HOSTNAME
from ._common_operation import (
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
    _print_planner_logs,
)
from ._run import JobStatus
from ._validators import _Validate
from .exceptions import TableCreatePlanApplyStatusError, TableCreatePlanStatusError
from .state import (
    TableCreatePlanApplyContext,
    TableCreatePlanApplyState,
    TableCreatePlanContext,
    TableCreatePlanState,
)


def _dump_plan_to_yaml(name: str, plan: Dict[str, Any]) -> str:
    if plan is None or not isinstance(plan, Dict):
        raise ValueError(f'{name} dict is required')

    import yaml

    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.safe_dump(plan)


def _load_plan_from_yaml(plan: str) -> Dict:
    import yaml

    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.safe_load(plan)


def _handle_table_create_plan_apply_log(
    log: SubscribeLogsResponse,
    state: TableCreatePlanApplyState,
    debug: Optional[bool],
    verbose: Optional[bool],
) -> bool:
    if verbose:
        print('log_stream:', log)

    runner_event = log.runner_event
    event_type = runner_event.WhichOneof('event')
    if event_type == 'job_completion':
        match runner_event.job_completion.WhichOneof('outcome'):
            case 'success':
                state.job_status = JobStatus.success
            case 'failure':
                state.job_status = JobStatus.failed
            case 'rejected':
                state.job_status = JobStatus.rejected
            case 'cancellation':
                state.job_status = JobStatus.cancelled
            case 'timeout':
                state.job_status = JobStatus.timeout
            case 'heartbeat_failure':
                state.job_status = JobStatus.heartbeat_failure
            case _:
                state.job_status = JobStatus.unknown
        return True

    if log.runner_event.apply_plan_done.error_message:
        state.error = log.runner_event.apply_plan_done.error_message
        state.job_status = JobStatus.failed
        if debug or verbose:
            print(f'log_stream: table create plan apply error - {state.error}')
        return True
    if log.runner_event.apply_plan_done.success:
        state.job_status = JobStatus.success
        if debug or verbose:
            print('log_stream: table create plan apply success')
        return True
    return False


def _handle_table_create_plan_log(
    log: SubscribeLogsResponse,
    state: TableCreatePlanState,
    debug: Optional[bool],
    verbose: Optional[bool],
) -> bool:
    if verbose:
        print('log_stream:', log)

    runner_event = log.runner_event
    event_type = runner_event.WhichOneof('event')
    if event_type == 'job_completion':
        match runner_event.job_completion.WhichOneof('outcome'):
            case 'success':
                state.job_status = JobStatus.success
            case 'failure':
                state.job_status = JobStatus.failed
            case 'rejected':
                state.job_status = JobStatus.rejected
            case 'cancellation':
                state.job_status = JobStatus.cancelled
            case 'timeout':
                state.job_status = JobStatus.timeout
            case 'heartbeat_failure':
                state.job_status = JobStatus.heartbeat_failure
            case _:
                state.job_status = JobStatus.unknown
        return True

    if log.runner_event.table_create_plan_done_event.error_message:
        state.error = log.runner_event.import_plan_created.error_message
        state.job_status = JobStatus.failed
        if debug or verbose:
            print(f'log_stream: table create plan error - {state.error}')
        return True
    if log.runner_event.table_create_plan_done_event.success:
        table_create_plan_done_event = log.runner_event.table_create_plan_done_event

        state.job_status = JobStatus.success
        plan_yaml = table_create_plan_done_event.plan_as_yaml
        if plan_yaml is not None:
            state.plan = _load_plan_from_yaml(plan_yaml)

        state.can_auto_apply = table_create_plan_done_event.can_auto_apply
        state.files_to_be_imported = list(table_create_plan_done_event.files_to_be_imported)
        if debug or verbose:
            print('log_stream: table create plan success')
        return True
    return False


class _TableCreate(_OperationContainer):
    @_lifecycle
    def plan(
        self,
        table_name: str,
        search_uri: str,
        branch_name: Optional[str] = None,
        partitioned_by: Optional[str] = None,
        namespace: Optional[str] = None,
        replace: Optional[bool] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        # internal
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> TableCreatePlanState:
        """
        Create a table import plan from an S3 location.
        This is the equivalent of running through the CLI the `bauplan import plan` command.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        table_name = _Validate.string('table_name', table_name)
        search_uri = _Validate.string('search_uri', search_uri).strip()
        if not search_uri.startswith('s3://'):
            raise ValueError('search_uri must be an S3 path, e.g., s3://bucket-name/*.parquet')
        branch_name = _Validate.optional_ref('ref', branch_name, self.profile.branch)
        partitioned_by = _Validate.optional_string('partitioned_by', partitioned_by)
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        replace = _Validate.optional_boolean('replace', replace) or False
        args = _Validate.args('args', args, self.profile.args)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        verbose = _Validate.optional_boolean('verbose', verbose, self.profile.verbose)
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

        plan_request = TableCreatePlanRequest(
            job_request_common=job_request_common,
            table_name=table_name,
            table_replace=replace,
            table_partitioned_by=partitioned_by,
            search_string=search_uri,
            branch_name=branch_name,
            namespace=namespace,
        )
        if debug or verbose:
            print(
                'TableCreatePlanRequest',
                'request',
                MessageToJson(plan_request),
            )

        plan_response: TableCreatePlanResponse = client_v2.TableCreatePlan(plan_request, metadata=metadata)
        if debug or verbose:
            print(
                'TableCreatePlanResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(plan_response.job_response_common.logs, debug)

        state = TableCreatePlanState(
            job_id=plan_response.job_response_common.job_id,
            ctx=TableCreatePlanContext(
                table_name=plan_response.table_name,
                table_partitioned_by=plan_response.table_partitioned_by,
                table_replace=plan_response.table_replace,
                search_string=plan_response.search_string,
                branch_name=plan_response.branch_name,
                namespace=plan_response.namespace,
                debug=plan_response.job_response_common.debug,
            ),
        )

        job_id = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)
        for log in log_stream:
            if _handle_table_create_plan_log(log, state, debug, verbose):
                break

        if state.job_status != JobStatus.success:
            raise TableCreatePlanStatusError(
                message=state.error or 'table create plan failed',
                state=state,
            )

        # can_auto_apply can have 3 states:
        # - Null: the service is not able to determine if the plan can be auto-applied
        #  - we should never be in this state, because we're in a success state
        # - True: the plan can be auto-applied
        # - False: the plan has conflicts and cannot be auto-applied
        if state.can_auto_apply is False:
            # There's a conflict in the plan, and we can't auto-apply it
            state.error = 'table plan created but has conflicts'

        return state

    @_lifecycle
    def apply(
        self,
        plan: Union[Dict, TableCreatePlanState],
        debug: Optional[bool] = None,
        args: Optional[Dict] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        # internal
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> TableCreatePlanApplyState:
        """
        Apply a Bauplan table import plan for a given branch.
        This is the equivalent of running through the CLI the `bauplan import apply` command.

        The user needs to pass a dict of the plan, as generated by the `plan` function defined in this module.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        if isinstance(plan, TableCreatePlanState):
            if plan.job_status != JobStatus.success or not plan.plan:
                raise TableCreatePlanStatusError(
                    message=plan.error or 'table create plan failed',
                    state=plan,
                )
            plan = plan.plan
        plan_yaml = _dump_plan_to_yaml('plan', plan)
        args = _Validate.args('args', args, self.profile.args)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        verbose = _Validate.optional_boolean('verbose', verbose, self.profile.verbose)
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

        plan_request = TableCreatePlanApplyRequest(
            job_request_common=job_request_common,
            plan_yaml=plan_yaml,
        )
        if debug or verbose:
            print(
                'TableCreatePlanApplyRequest',
                'request',
                MessageToJson(plan_request),
            )

        plan_response: TableCreatePlanApplyResponse = client_v2.TableCreatePlanApply(
            plan_request, metadata=metadata
        )
        if debug or verbose:
            print(
                'TableCreatePlanApplyResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(plan_response.job_response_common.logs, debug)

        state = TableCreatePlanApplyState(
            job_id=plan_response.job_response_common.job_id,
            ctx=TableCreatePlanApplyContext(
                debug=plan_response.job_response_common.debug,
            ),
        )

        job_id = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)
        for log in log_stream:
            if _handle_table_create_plan_apply_log(log, state, debug, verbose):
                break

        if state.job_status != JobStatus.success:
            raise TableCreatePlanApplyStatusError(
                message=state.error or 'table create plan apply failed',
                state=state,
            )
        return state
