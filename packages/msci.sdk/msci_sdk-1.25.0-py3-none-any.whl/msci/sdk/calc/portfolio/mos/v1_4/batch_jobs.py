import datetime
import json
import logging
import time
import uuid
import pandas as pd
import warnings

from .bulk_result import BulkResult
from ...utils.request_utility import get, post, delete
from ...utils.utility import bulk_request_body


class BatchJob:

    def __init__(self, base_url, headers, ssl_verify):

        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.headers = headers
        self.ssl_verify = ssl_verify

    def execute_jobs(self, profile_list: list, batch_id: str = None) -> pd.DataFrame:
        """
        Executes list of profiles in batched mechanism with each batch allowing maximum 1000 profiles.

        Args:
            profile_list (list): List of profiles to be included in the bulk execution request.
            batch_id (str): (optional) Unique ID of the batch. By default, a random UUID is generated. Please provide a new batch id for each run, as using an old batch ID will overwrite the existing batch.


        Returns:
            Dataframe consisting of jobId, statusCode, errorText, batchId and profileName.
        """
        batch_size = 1000
        resp_list = []
        batch_res = pd.DataFrame()

        if not batch_id:
            batch_id = str(uuid.uuid4())

        self.logger.info(f"Creating bulk job upload request with batch_id: {batch_id}")

        for i in range(0, len(profile_list), batch_size):
            pf_lst = profile_list[i:i + batch_size]
            payload = [prof.body for prof in pf_lst]
            for prof in payload:
                if prof['requestInfo'] is None:
                    raise ValueError('Please provide a name for the profile using profile_name')
            profile_names = [prof['requestInfo']['name'] for prof in payload]
            resp = post(url=self.base_url + f"bulkJobs?batchId={batch_id}", headers=self.headers,
                        data=payload, ssl_verify=self.ssl_verify)
            response_json = json.loads(resp.text)
            self.logger.debug(response_json)
            response_df = pd.json_normalize(response_json)
            response_df['batchId'] = batch_id
            response_df['profileName'] = profile_names
            resp_list.append(response_df)

        if resp_list:
            batch_res = pd.concat(resp_list, ignore_index=True)
        return batch_res

    def get_batch_status(self, batch_id: str):
        """
        Use to check if all jobs in a batch are completed (failed counts as complete).
        You will need the batch ID to call this endpoint.

        Args:
            batch_id (str): Batch ID of the batch for which the job statuses are to be retrieved.

        Returns:
            Response dict
        """
        resp = get(url=self.base_url + f"batchJobs/{batch_id}/complete", headers=self.headers,
                   ssl_verify=self.ssl_verify)
        return json.loads(resp.text)

    def get_jobs_status(self, batch_id: str = None, job_ids: list = None, return_failed_only: bool = False):
        """
        Use to retrieve status on a specified list of jobs along with their status and IDs.

        Args:
            batch_id(str): (optional) Batch ID of the batch for which the job statuses are to be retrieved.

                .. deprecated:: 1.8.0
                    ``batch_id`` is deprecated. To get batch status, use :func:`get_batch_status`

            job_ids(list): (optional) List of job IDs for which job statuses are to be fetched.
            return_failed_only(boolean): (optional) True if status of only failed jobs is to be returned. Default value is False.

        Returns:
            DataFrame of jobs status.
        """
        if batch_id is None and job_ids is None:
            raise ValueError('Please provide either batch_id or job_ids list.')
        if batch_id:
            warnings.warn(
                "batch_id param is deprecated and will be removed in the next version. Kindly use get_batch_status instead for getting batch status.",
                DeprecationWarning)
            return self.get_batch_status(batch_id)

        resp = post(url=self.base_url + "/jobs/status", headers=self.headers, data=job_ids,
                    ssl_verify=self.ssl_verify)

        jobs_status = json.loads(resp.text)
        if return_failed_only:
            jobs_status = [j for j in jobs_status if j['status'] == 'failed']

        return pd.DataFrame(jobs_status)

    def get_batch_info(self, batch_id: str):
        """
        Read info about batch. Contains a list of all associated jobIds and profileNames. This does not include profiles that were rejected from the batch.

        Args:
            batch_id (str): Batch ID of the batch for which the job IDs are to be retrieved.

        Returns:
            Response dict
        """
        resp = get(url=self.base_url + f"batch/info/{batch_id}", headers=self.headers, ssl_verify=self.ssl_verify)
        return json.loads(resp.text)

    def _get_batch_response(self, job_id_list: list, as_of_date: str = None, snapshot_types: list = None,
                            account_id: str = None):
        """
        Get compound results for many jobs in a single call for a specified list of jobs and a specified result types.

        Args:
            job_id_list (list): List of job IDs for which results are to be fetched.
            as_of_date (str): (optional) As of date for the results. Default value is None.
            snapshot_types (list): (optional) List of snapshot_types for the portfolios.
                            Required if portfolios or tax lots need to be included in the results.
            account_id (str): (optional) Account for multi account optimization profile. Default value is None.

        Returns:
            Response dict
        """
        keys = bulk_request_body(job_id_list, as_of_date, snapshot_types, account_id)
        body = {
            "keys": keys,
            "includePortfolios": False,
            "includeTaxLots": False,
            "includeTradeSuggestions": True if as_of_date else False,
            "includeTransferSuggestions": True if as_of_date else False,
            "includeSleeveAssignments": True if as_of_date else False,
            "includeValuations": True,
            "includeMetrics": True,
            "includeTriggerDates": True,
            "includeBenchmarkIds": True,
            "includeJobWarnings": True,
            "includeProfile": True,
            "includeSleeveValueFlows": True if as_of_date else False
        }
        if as_of_date and snapshot_types:
            body['includePortfolios'] = True
            body['includeTaxLots'] = True

        resp = post(url=self.base_url + f"jobs/bulkResults", headers=self.headers, data=body,
                    ssl_verify=self.ssl_verify)
        return resp.json()

    def cancel_jobs(self, job_ids: list):
        """
        Use to cancel/delete a set of jobs. You will need the IDs of the jobs to use this endpoint.

        Args:
            job_ids (list): List of job IDs.

        Returns:
            Response dict
        """
        self.logger.debug(f"Canceling bulk job upload request with job ids: {job_ids}")
        resp = post(url=self.base_url + f"bulkJobs/cancel", headers=self.headers, data=job_ids,
                    ssl_verify=self.ssl_verify)
        return json.loads(resp.text)

    def delete_job(self, job_id: str):
        """
        Use to delete/cancel a job. You will need the ID of the job to use this endpoint.

        Args:
            job_id (str): Job ID of the active job that has to be cancelled.

        Returns:
            None
        """
        self.logger.debug(f"Deleting job with job id: {job_id}")
        resp = delete(url=self.base_url + f"jobs/{job_id}", headers=self.headers, ssl_verify=self.ssl_verify)
        if resp.status_code == 200:
            self.logger.info(f"Job deleted with job id: {job_id}.")
        else:
            self.logger.info(f"Job delete failed for job id: {job_id}.")

    def wait(self, batch_id: str, wait_time: int = 5):
        """
        Wait for the batch to get completed. It will check the status every 5 secs.

        Args:
            batch_id (str): ID of the batch
            wait_time (int): Wait time(in secs) between each check of job status. Default value is 5 secs.

        Returns:
            Dict of status for the batch where

                - complete (bool): represents the overall status of the batch.

                - batchSize (int): number of jobs in the batch.

                - finishedJobs (int): number of jobs in the batch which have status = complete.

                - failedJobs (int): number of jobs in the batch which have status = complete and subStatus = failed.

        """
        start_time = datetime.datetime.now()
        batch_status = self.get_batch_status(batch_id)
        while not batch_status["complete"]:
            self.logger.info(f"Batch status is not yet completed. Retrying after {wait_time} secs.")
            self.logger.info(f"{batch_status}")
            time.sleep(wait_time)
            batch_status = self.get_batch_status(batch_id)
        td = (datetime.datetime.now() - start_time).total_seconds()
        self.logger.info(f"Batch status completed in {td} seconds.")
        return batch_status

    def bulk_results(self, job_id_list: list, as_of_date: str = None,
                     snapshot_types: list = ['REBALANCED'], account_id: str = None):
        """
        Get compound results for many jobs in a single call for a specified list of jobs and a specified result type. To get the results for all dates specified and in the case of backtesting use get_tax_by_group_full_portfolio(), get_portfolio_summary_detail(), get_portfolio_tax_summary(), get_tax_by_group_category().

        Args:
            job_id_list (list): List of job IDs for which results need to be fetched.
            as_of_date (str): (optional) As of date for the results. Default value is None.
            snapshot_types (list): (optional) List of snapshot_types for the portfolios. Required if portfolios or tax lots need to be included in the results.
            account_id (str): (optional) Account for multi account optimization profile. Default value is None.

        Returns:
            Response dict
        """

        job_id_list = [job for job in job_id_list if job]
        if not job_id_list:
            self.logger.info("No successful jobs found to retrieve the bulk results")
            return
        bulk_response = self._get_batch_response(job_id_list, as_of_date=as_of_date, snapshot_types=snapshot_types,
                                                 account_id=account_id)
        for job in bulk_response:
            if job["errorMessage"] is not None:
                self.logger.error(job["errorMessage"])

        return BulkResult(bulk_response)
