"""
The module contains functions to launch SQL queries on Bauplan and retrieve
the result sets in a variety of formats (arrow Table, generator, file).
"""

import concurrent.futures
import json
import multiprocessing
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Literal, Optional, Tuple, Union

import grpc
import grpc._channel
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.flight as flight
import pyarrow.parquet as pq
from google.protobuf.json_format import MessageToJson

from bauplan._bpln_proto.commander.service.v2.subscribe_logs_pb2 import (
    SubscribeLogsRequest,
    SubscribeLogsResponse,
)
from bauplan.errors import InternalError

from . import exceptions
from ._bpln_proto.commander.service.v2.common_pb2 import JobRequestCommon
from ._bpln_proto.commander.service.v2.query_run_pb2 import QueryRunRequest, QueryRunResponse
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
from ._validators import _Validate


def _get_system_cpu_count() -> int:
    return multiprocessing.cpu_count()


def _create_call_options(token: str, timeout: int) -> flight.FlightCallOptions:
    flight_auth_headers: tuple[bytes, bytes] = (
        b'authorization',
        f'Bearer {token}'.encode(),
    )
    return flight.FlightCallOptions(
        headers=[flight_auth_headers],
        timeout=timeout,
    )


def _read_flight_stream(
    reader: flight.FlightStreamReader,
) -> pa.Table:
    if reader is None:
        raise exceptions.NoResultsFoundError('No results found')

    return reader.read_all()


def _read_flight_stream_batches(
    reader: flight.FlightStreamReader,
) -> Generator[pa.RecordBatch, None, None]:
    if reader is None:
        raise exceptions.NoResultsFoundError('No results found')

    while True:
        try:
            chunk = reader.read_chunk()
            if chunk is None or chunk.data is None:
                break

            yield chunk.data
        except StopIteration:
            break


def _add_connector_strings_to_query(
    query: str,
    connector: Optional[str] = None,
    connector_config_key: Optional[str] = None,
    connector_config_uri: Optional[str] = None,
) -> str:
    """
    Add the connector strings to the query to allow the backend to direct the query to the correct engine.
    We assume that if the connector is not specified we use Bauplan as is; the other properties default to
    sensible values (check the docs for the details!).

    Parameters:
        query: str:
        connector: Optional[str]:  (Default value = None)
        connector_config_key: Optional[str]:  (Default value = None)
        connector_config_uri: Optional[str]:  (Default value = None)

    """
    if not isinstance(query, str) or query.strip() == '':
        raise ValueError('query must be a non-empty string')

    # If no connector is specified, we return the query as is
    if connector is None and connector_config_key is None and connector_config_uri is None:
        return query

    # Otherwise we make sure the settings are valid
    connector = _Validate.string('connector', connector)

    lines: list[str] = []
    lines.append(f'-- bauplan: connector={connector}')

    connector_config_key = _Validate.optional_string('connector_config_key', connector_config_key)
    connector_config_uri = _Validate.optional_string('connector_config_uri', connector_config_uri)

    if connector_config_key is not None:
        lines.append(f'-- bauplan: connector.config_key={connector_config_key.strip()}')

    if connector_config_uri is not None:
        lines.append(f'-- bauplan: connector.config_uri={connector_config_uri.strip()}')

    lines.append(query)

    return '\n'.join(lines)


def _build_query_from_scan(
    table_name: str,
    columns: Optional[list[str]] = None,
    filters: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Take as input the arguments of the scan function and build a SQL query
    using SQLGlot.
    """
    from sqlglot import select

    cols = columns or ['*']
    q = select(*cols).from_(table_name).where(filters)
    if limit:
        q = q.limit(limit)

    return q.sql()


def _row_to_dict(
    batch: pa.RecordBatch,
    row_index: int,
    schema: pa.Schema,
    as_json: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Convert a row of a `pyarrow.RecordBatch` to a dictionary.

    Parameters:
        batch: The `pyarrow.RecordBatch` containing the row.
        row_index: The index of the row to convert.
        schema: The schema of the `RecordBatch`.
        as_json: Whether or not to cast to JSON-compatible types (i.e. datetime -> ISO format string).

    Returns:
        A dictionary representing the row.

    """
    row: Dict[str, Any] = {}
    for j, name in enumerate(schema.names):
        column: pa.ChunkedArray = batch.column(j)
        value = column[row_index].as_py()
        if as_json is True:
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, date):
                value = value.isoformat()
        row[name] = value
    return row


class _Query(_OperationContainer):
    @_lifecycle
    def query(
        self,
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> pa.Table:
        """
        Execute a SQL query and return the results as a pyarrow.Table.

        If you prefer to return the raw FlightStreamReader, pass `return_flight_stream=True`.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        readers, shutdown_fn = self.query_to_flight_stream(
            query=query,
            ref=ref,
            max_rows=max_rows,
            cache=cache,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            namespace=namespace,
            args=args,
            priority=priority,
            debug=debug,
            verbose=verbose,
            client_timeout=client_timeout,
            # lifecycle_handler=lifecycle_handler,
        )

        num_threads = _get_system_cpu_count()
        if args:
            num_threads = int(args.get('query_concurrency', str(num_threads)))

        try:
            futures = []
            tables = []
            with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
                for reader in readers:
                    f = executor.submit(_read_flight_stream, reader)
                    futures.append(f)

                for f in futures:
                    table = f.result()
                    tables.append(table)

            return pa.concat_tables(tables)
        except Exception as e:
            raise e
        finally:
            shutdown_fn()

    @_lifecycle
    def query_to_flight_stream(
        self,
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> Tuple[List[flight.FlightStreamReader], Callable]:
        """
        Execute a SQL query and return the results as a raw FlightStreamReader.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        query = _add_connector_strings_to_query(query, connector, connector_config_key, connector_config_uri)
        ref = _Validate.optional_ref('ref', ref, self.profile.branch)
        if max_rows is not None:
            # max_rows limits
            if not isinstance(max_rows, int) or not (0 < max_rows < 100000000):
                raise ValueError('max_rows must be positive integer 1-100000000')
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        cache_flag = _Validate.optional_on_off_flag('cache', cache, self.profile.cache)
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

        plan_request = QueryRunRequest(
            job_request_common=job_request_common,
            ref=ref,
            sql_query=query,
            cache=cache_flag,
            namespace=namespace,
        )
        if debug or verbose:
            print(
                'QueryRunRequest',
                'request',
                MessageToJson(plan_request),
            )

        plan_response: QueryRunResponse = client_v2.QueryRun(plan_request, metadata=metadata)
        if debug or verbose:
            print(
                'QueryRunResponse',
                'job_id',
                plan_response.job_response_common.job_id,
                'response',
                MessageToJson(plan_response),
            )
        _print_planner_logs(plan_response.job_response_common.logs, debug or verbose)

        job_id = plan_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)

        flight_endpoint: Optional[str] = None
        auth_token: Optional[str] = None

        # default to true
        use_tls = True
        for log in log_stream:
            if verbose:
                print('log_stream:', log)
            ev = log.runner_event
            if not ev:
                continue

            event_type = ev.WhichOneof('event')
            if event_type == 'job_completion':
                outcome_type = ev.job_completion.WhichOneof('outcome')
                if outcome_type == 'failure':
                    raise exceptions.BauplanQueryError(ev.job_completion.failure.error_message)
                if outcome_type == 'rejected':
                    raise exceptions.BauplanQueryError(f'Query rejected: {ev.job_completion.rejected.reason}')
                if outcome_type == 'cancellation':
                    raise exceptions.BauplanQueryError(
                        f'Query cancelled: {ev.job_completion.cancellation.reason}'
                    )
                if outcome_type == 'timeout':
                    raise exceptions.BauplanQueryError(f'Query timed out: {ev.job_completion.timeout.msg}')
                if outcome_type == 'heartbeat_failure':
                    raise exceptions.BauplanQueryError(
                        'Query failed due to unresponsive runner: no heartbeat received, indicating a possible crash or connection loss'
                    )
                if outcome_type == 'success':
                    raise exceptions.NoResultsFoundError('Job completed before Flight server is started.')
                raise exceptions.InternalError(
                    f'Unexpected job completion outcome: {outcome_type}',
                )

            if event_type == 'flight_server_start':
                flight_endpoint = ev.flight_server_start.endpoint
                use_tls = ev.flight_server_start.use_tls
                auth_token = ev.flight_server_start.magic_token
                break

        if not flight_endpoint:
            raise InternalError(error_message='flight server was never started', job_id=job_id)

        flight_protocol = 'grpc+tls' if use_tls else 'grpc'
        location = f'{flight_protocol}://{flight_endpoint}'
        flight_client: flight.FlightClient = flight.FlightClient(location=location)
        lifecycle_handler.register_flight_client(flight_client)

        if auth_token is None or auth_token == '':
            raise ValueError('internal error: auth token missing')

        initial_options = _create_call_options(
            token=auth_token,
            timeout=Constants.FLIGHT_INTIAL_TIMEOUT_SECONDS,
        )
        query_options = _create_call_options(
            token=auth_token,
            timeout=Constants.FLIGHT_QUERY_TIMEOUT_SECONDS,
        )

        num_endpoints = _get_system_cpu_count()
        if args:
            num_endpoints = int(args.get('num_endpoints', str(num_endpoints)))

        criteria_dict = {
            'max_rows': max_rows,
            'num_endpoints': num_endpoints,
        }
        criteria = json.dumps(criteria_dict).encode('utf-8')
        endpoints = []
        try:
            flight_info = next(
                flight_client.list_flights(criteria=criteria, options=initial_options),
            )
            endpoints = flight_info.endpoints
        except grpc.RpcError as e:
            is_call_error = isinstance(e, grpc.CallError)
            is_deadline_exceeded = e.code() == grpc.StatusCode.DEADLINE_EXCEEDED
            if is_call_error and is_deadline_exceeded:
                raise TimeoutError(
                    f'Initial Flight connection timed out after {Constants.FLIGHT_INTIAL_TIMEOUT_SECONDS} seconds',
                ) from e
            raise e

        def shutdown_fn() -> None:
            # Shutdown the flight server
            try:
                shutdown_results = flight_client.do_action(
                    Constants.FLIGHT_ACTION_SHUTDOWN_QUERY_SERVER,
                    query_options,
                )
                for _ in shutdown_results:
                    pass
            except Exception:  # noqa: S110
                pass

        def _fetch_reader(ticket: flight.Ticket, location: str) -> flight.FlightStreamReader:
            standalone_client: flight.FlightClient = flight.FlightClient(location=location)
            return standalone_client.do_get(
                ticket,
                options=query_options,
            )

        futures = []
        readers = []
        with concurrent.futures.ThreadPoolExecutor(num_endpoints) as executor:
            for e in endpoints:
                f = executor.submit(_fetch_reader, e.ticket, location)
                futures.append(f)
            for f in futures:
                reader = f.result()
                readers.append(reader)

        return readers, shutdown_fn

    def query_to_generator(
        self,
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        as_json: Optional[bool] = False,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SQL query and return the results as a generator, where each row is
        a Python dictionary.
        """
        readers, shutdown_fn = self.query_to_flight_stream(
            query=query,
            ref=ref,
            max_rows=max_rows,
            cache=cache,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            namespace=namespace,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
        )
        if readers is None:
            raise exceptions.NoResultsFoundError('No results found')
        try:

            def read_batches_from_reader(reader: flight.FlightStreamReader) -> List[pa.RecordBatch]:
                return [f for f in _read_flight_stream_batches(reader)]

            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for reader in readers:
                    f = executor.submit(read_batches_from_reader, reader)
                    futures.append(f)

                for f in futures:
                    batch_list = f.result()
                    for batch in batch_list:
                        for i in range(batch.num_rows):
                            yield _row_to_dict(
                                batch=batch,
                                row_index=i,
                                schema=batch.schema,
                                as_json=as_json,
                            )
        except StopIteration:
            pass
        finally:
            shutdown_fn()

    def query_to_json_file(
        self,
        path: Union[str, Path],
        query: str,
        file_format: Optional[Literal['json', 'jsonl']] = 'json',
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Path:
        """
        Execute a SQL query and write the results to a json file.
        """

        path = _Validate.ensure_parent_dir_exists('path', path)
        if file_format == 'json':
            first_line = '[\n'
            last_line = '\n]'
            line_suffix = ',\n'
            line_prefix = '  '
        elif file_format == 'jsonl':
            first_line = None
            last_line = None
            line_suffix = '\n'
            line_prefix = ''
        else:
            raise ValueError('file_format must be "json" or "jsonl"')

        with open(path, 'w') as outfile:
            is_first_row = True

            for row in self.query_to_generator(
                query=query,
                ref=ref,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace,
                debug=debug,
                as_json=True,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            ):
                if is_first_row and first_line:
                    outfile.write(first_line)
                if not is_first_row and line_suffix:
                    outfile.write(line_suffix)
                outfile.write(line_prefix + json.dumps(row))
                is_first_row = False

            if last_line:
                outfile.write(last_line)
        return path

    def query_to_jsonl_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Path:
        """
        Execute a SQL query and write the results to a jsonl file.
        """
        path = _Validate.ensure_parent_dir_exists('path', path)

        with open(path, 'w') as outfile:
            outfile.writelines(
                json.dumps(row)
                for row in self.query_to_generator(
                    query=query,
                    ref=ref,
                    max_rows=max_rows,
                    cache=cache,
                    connector=connector,
                    connector_config_key=connector_config_key,
                    connector_config_uri=connector_config_uri,
                    namespace=namespace,
                    debug=debug,
                    as_json=True,
                    args=args,
                    priority=priority,
                    verbose=verbose,
                    client_timeout=client_timeout,
                )
            )
        return path

    def query_to_parquet_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs,
    ) -> Path:
        """
        Execute a SQL query and write the results to a parquet file.
        """
        path = _Validate.ensure_parent_dir_exists('path', path)
        if not path.suffix.lower() == '.parquet':
            raise ValueError('path should have a .parquet extension')

        table = self.query(
            query=query,
            ref=ref,
            max_rows=max_rows,
            cache=cache,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            namespace=namespace,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
        )
        pq.write_table(table, str(path), **kwargs)
        return path

    def query_to_csv_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[str] = None,
        max_rows: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs,
    ) -> Path:
        """
        Execute a SQL query and write the results to a parquet file.
        """
        path = _Validate.ensure_parent_dir_exists('path', path)

        if not path.suffix.lower() == '.csv':
            raise ValueError('path should have a .csv extension')

        table = self.query(
            query=query,
            ref=ref,
            max_rows=max_rows,
            cache=cache,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            namespace=namespace,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
        )
        pcsv.write_csv(table, str(path), **kwargs)
        return path

    def scan(
        self,
        table_name: str,
        ref: Optional[str] = None,
        columns: Optional[List[str]] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        cache: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        # shared
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> pa.Table:
        """
        Execute a table scan (with optional filters) and return the results as an arrow Table.
        Note that this function uses SQLGlot to compose a safe SQL query,
        and then internally defer to the query_to_arrow function for the actual scan.
        """
        table_name = _Validate.string('table_name', table_name)
        query = _build_query_from_scan(table_name, columns, filters, limit)
        return self.query(
            query=query,
            ref=ref,
            cache=cache,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            namespace=namespace,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
            **kwargs,
        )
