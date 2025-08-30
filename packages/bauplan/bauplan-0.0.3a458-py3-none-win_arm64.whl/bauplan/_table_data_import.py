from typing import Dict, Iterable, Optional, Union

from google.protobuf.json_format import MessageToJson

from bauplan._bpln_proto.commander.service.v2.subscribe_logs_pb2 import (
    SubscribeLogsRequest,
    SubscribeLogsResponse,
)

from ._bpln_proto.commander.service.v2.common_pb2 import JobRequestCommon
from ._bpln_proto.commander.service.v2.table_data_import_pb2 import (
    TableDataImportRequest,
    TableDataImportResponse,
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
from .state import TableDataImportContext, TableDataImportState


def _handle_log(
    log: SubscribeLogsResponse,
    run_state: TableDataImportState,
    debug: Optional[bool],
    verbose: Optional[bool],
) -> bool:
    runner_event = log.runner_event
    event_type = runner_event.WhichOneof('event')
    if event_type == 'job_completion':
        match runner_event.job_completion.WhichOneof('outcome'):
            case 'success':
                run_state.job_status = JobStatus.success
            case 'failure':
                run_state.job_status = JobStatus.failed
                run_state.error = runner_event.job_completion.failure.error_message
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
    return False


class _TableImport(_OperationContainer):
    @_lifecycle
    def data_import(
        self,
        table_name: str,
        search_uri: str,
        branch_name: Optional[str] = None,
        namespace: Optional[str] = None,
        continue_on_error: bool = False,
        import_duplicate_files: bool = False,
        best_effort: bool = False,
        transformation_query: Optional[str] = None,
        preview: Optional[str] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        # internal
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
        detach: bool = False,
    ) -> TableDataImportState:
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
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        continue_on_error = _Validate.boolean('continue_on_error', continue_on_error)
        import_duplicate_files = _Validate.boolean('import_duplicate_files', import_duplicate_files)
        best_effort = _Validate.boolean('best_effort', best_effort)
        transformation_query = _Validate.optional_string('transformation_query', transformation_query)
        preview = _Validate.optional_string('preview', preview)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        args = _Validate.args('args', args, self.profile.args)
        verbose = _Validate.optional_boolean('verbose', verbose, self.profile.verbose)
        detach = _Validate.boolean('detach', detach)
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

        plan_request = TableDataImportRequest(
            job_request_common=job_request_common,
            branch_name=branch_name,
            table_name=table_name,
            search_string=search_uri,
            import_duplicate_files=import_duplicate_files,
            best_effort=best_effort,
            continue_on_error=continue_on_error,
            transformation_query=transformation_query,
            namespace=namespace,
            preview=preview,
        )
        if debug or verbose:
            print(
                'TableDataImportRequest',
                'request',
                MessageToJson(plan_request),
            )

        plan_response: TableDataImportResponse = client_v2.TableDataImport(plan_request, metadata=metadata)
        if debug or verbose:
            print(
                'TableDataImportResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(plan_response.job_response_common.logs, debug or verbose)

        state = TableDataImportState(
            job_id=plan_response.job_response_common.job_id,
            ctx=TableDataImportContext(
                branch_name=plan_response.branch_name,
                table_name=plan_response.table_name,
                namespace=plan_response.namespace,
                search_string=search_uri,
                import_duplicate_files=import_duplicate_files,
                best_effort=best_effort,
                continue_on_error=continue_on_error,
                transformation_query=transformation_query,
                preview=plan_response.preview,
                debug=plan_response.job_response_common.debug,
                detach=detach,
            ),
        )

        if detach:
            return state

        job_id = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)
        # ATM there is no termination event so runner only sends a "JobComplete"
        for log in log_stream:
            if verbose:
                print('log_stream:', log)
            _handle_log(log, state, debug, verbose)
        return state
