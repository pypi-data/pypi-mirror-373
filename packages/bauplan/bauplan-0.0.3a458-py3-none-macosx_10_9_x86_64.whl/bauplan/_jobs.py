import time
from typing import List, Optional, Union

from ._bpln_proto.commander.service.v2 import (
    CancelJobRequest,
    GetJobContextRequest,
    GetJobsRequest,
    GetLogsRequest,
    JobId,
)
from ._common_operation import (
    _OperationContainer,
)
from .errors import (
    JobCancelError,
    JobContextError,
    JobGetError,
    JobLogsError,
    JobNotFoundError,
    JobsListError,
)
from .schema import (
    DateRange,
    Job,
    JobContext,
    JobLogList,
    JobState,
)


class _Jobs(_OperationContainer):
    """Implements operations for retrieving jobs and logs."""

    def get_job(self, job_ids: Union[str, list[str]]) -> List[Job]:
        """
        Retrieve jobs for the user matching the specified ID, ID prefix, list of IDs, or list of ID
        prefixes. The jobs are filtered on the server-side.
        """

        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        query_jobids = job_ids if isinstance(job_ids, list) else [job_ids]
        req = GetJobsRequest(job_ids=query_jobids)

        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobGetError(query_jobids) from e

        if len(resp.jobs) < 1:
            raise JobNotFoundError(query_jobids)

        return list(map(Job.from_proto, resp.jobs))

    def list_jobs(
        self,
        all_users: Optional[bool] = None,
        *,  # From here only keyword arguments are allowed
        filter_by_id: Optional[str] = None,
        filter_by_status: Optional[Union[str, JobState]] = None,
        filter_by_finish_time: Optional[DateRange] = None,
    ) -> List[Job]:
        """
        List (retrieve) all jobs for the user or (optionally) for the organization.

        The filtering parameters apply client-side filtering for convenience, which can also be
        done by the caller if no filters are provided and they apply filtering themselves.

        Filters:
        filter_by_id: Filters received jobs by their ID or ID prefix.
        filter_by_status: Filters received jobs by their JobState status ('Complete', etc.)
        filter_by_finish_time: Filters received jobs by their completion time.
        """

        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = GetJobsRequest()

        if all_users is not None:
            req.all_users = all_users

        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobsListError(f'Failed to list jobs: {e}') from e

        all_jobs = [Job.from_proto(j) for j in resp.jobs]

        # Filter `all_jobs` by specified Job ID
        if filter_by_id is not None:
            all_jobs = filter(lambda j: j.has_id(filter_by_id), all_jobs)

        # Filter `all_jobs` by specified status
        if filter_by_status is not None:
            all_jobs = filter(lambda j: j.has_status(filter_by_status), all_jobs)

        # Filter `all_jobs` by a pair of start and stop times
        if filter_by_finish_time is not None:
            all_jobs = filter(
                lambda j: j.has_finished_range(
                    after_time=filter_by_finish_time[0], before_time=filter_by_finish_time[1]
                ),
                all_jobs,
            )

        # Return the materialized list (apply accumulated filters)
        return list(all_jobs)

    def get_logs(self, job: Union[str, Job]) -> JobLogList:
        """
        Retrieve *only user logs* for one job by matching a prefix of its ID.

        Steps:
        1) Call GetLogs on each provided job ID.
        2) Gather user logs from RunnerEvents in response.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        # Use the provided ID or extract from provided job
        query_jobid = job if isinstance(job, str) else job.id_prefix

        logs_req = GetLogsRequest(job_id=query_jobid)
        try:
            logs_resp = client_v2.GetLogs(logs_req, metadata=metadata)
        except Exception as e:
            raise JobLogsError(query_jobid) from e

        # TODO: optionally add server-side filters
        return JobLogList.from_pb(logs_resp)

    def get_context(self, jobs: List[Union[str, Job]]) -> List[JobContext]:
        """
        Retrieve a JobContext for each entry in jobs, which is a list of job IDs or a list of Job
        instances.

        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        # Use the provided ID or extract from provided job
        query_jobids = [job if isinstance(job, str) else job.id for job in jobs]

        jobctx_req = GetJobContextRequest(job_ids=query_jobids)
        try:
            jobctx_resp = client_v2.GetJobContext(jobctx_req, metadata=metadata)
        except Exception as e:
            raise JobContextError(query_jobids) from e

        return JobContext.from_pb(jobctx_resp)

    def cancel_job(self, id: str) -> None:
        """
        Cancels a running job and polls its status to verify it has been
        cancelled.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = CancelJobRequest(job_id=JobId(id=id))

        try:
            client_v2.CancelJob(req, metadata=metadata)
        except Exception as e:
            raise JobCancelError(id, f'Failed to cancel job {id}: {e}') from e

        retry_count = 0
        encountered_states = []

        while retry_count < 10:
            job = self.get_job(id)[0]
            encountered_states.append(job.status)

            if job.status == JobState.ABORT:
                return

            retry_count += 1
            time.sleep(1)

        raise JobCancelError(
            id, f'Could not verify job was cancelled. Encountered states: {encountered_states}'
        )
