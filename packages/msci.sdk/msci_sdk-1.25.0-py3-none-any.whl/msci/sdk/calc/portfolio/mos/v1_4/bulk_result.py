import pandas as pd
import json
import logging
from .optimizer_result import OptimizerResult
from .metrics import Metrics
from ...utils.job_utility import portfolios_to_df


class BulkResult:
    """
    Class for parsing bulk results corresponding to list of job IDs submitted as a batch of profiles.
    """

    def __init__(self, bulk_response):
        self.logger = logging.getLogger(__name__)
        self.bulk_response = bulk_response

    @staticmethod
    def _append_profile_name(target_df, job):
        """
        Append profile name to the dataframe.
        """
        if not target_df.empty:
            target_df['jobId'] = job['jobId']
            if 'requestJson' in job:
                request_obj = json.loads(job['requestJson'])
                if 'requestInfo' in request_obj:
                    target_df['profileName'] = request_obj['requestInfo']['name']

    def trade_suggestions(self) -> pd.DataFrame:
        """
        Retrieve the suggested trades for a list of jobs.
        Returns:
            pandas dataframe
        """
        trade = []
        trade_suggestions = pd.DataFrame()
        for job in self.bulk_response:
            if job["tradeSuggestions"]:
                trade_sug = pd.json_normalize(job["tradeSuggestions"])
                if not trade_sug.empty:
                    self._append_profile_name(trade_sug, job)
                    trade.append(trade_sug)
        if trade:
            trade_suggestions = pd.concat(trade, ignore_index=True)
        return trade_suggestions

    def transfer_suggestions(self) -> pd.DataFrame:
        """
        Retrieve the suggested trades for a list of jobs.
        Returns:
            pandas dataframe
        """
        transfer = []
        transfer_suggestions = pd.DataFrame()
        for job in self.bulk_response:
            if job["transferSuggestions"]:
                trans_sug = pd.json_normalize(job["transferSuggestions"])
                if not trans_sug.empty:
                    self._append_profile_name(trans_sug, job)
                    transfer.append(trans_sug)
        if transfer:
            transfer_suggestions = pd.concat(transfer, ignore_index=True)
        return transfer_suggestions

    def sleeve_assignments(self) -> pd.DataFrame:
        """
        Retrieve the suggested trades for a list of jobs.
        Returns:
            pandas dataframe
        """
        sleeve = []
        sleeve_assignments = pd.DataFrame()
        for job in self.bulk_response:
            if job["sleeveAssignments"]:
                sleeve_assign = pd.json_normalize(job["sleeveAssignments"])
                if not sleeve_assign.empty:
                    self._append_profile_name(sleeve_assign, job)
                    sleeve.append(sleeve_assign)
        if sleeve:
            sleeve_assignments = pd.concat(sleeve, ignore_index=True)
        return sleeve_assignments

    def sleeve_value_flow(self) -> pd.DataFrame:
        """
        Retrieve the suggested sleeve value changes for a list of jobs.
        Returns:
            pandas dataframe
        """
        sleeve_value = []
        sleeve_value_flow = pd.DataFrame()
        for job in self.bulk_response:
            sleeve_value_flow_data = job.get("sleeveValueFlow")
            if sleeve_value_flow_data:
                sleeve_assign = pd.json_normalize(sleeve_value_flow_data)
                if not sleeve_assign.empty:
                    self._append_profile_name(sleeve_assign, job)
                    sleeve_value.append(sleeve_assign)
        if sleeve_value:
            sleeve_value_flow = pd.concat(sleeve_value, ignore_index=True)
        return sleeve_value_flow

    def get_valuations(self) -> pd.DataFrame:
        """
        Retrieve the valuations of optimized portfolio corresponding to job IDs executed in batch.
        Returns:
            pandas dataframe
        """
        val = []
        valuation = pd.DataFrame()
        for job in self.bulk_response:
            if job["valuations"]:
                if 'values' in job["valuations"]:
                    value = pd.json_normalize(job["valuations"]['values'])
                    if not value.empty:
                        self._append_profile_name(value, job)
                        val.append(value)
        if val:
            valuation = pd.concat(val, ignore_index=True)
        return valuation

    def get_benchmarks(self) -> pd.DataFrame:
        """
        Retrieve benchmarks corresponding to the benchmarks configured in the profiles defined for the submitted jobs.
        Returns:
            pandas dataframe
        """
        bench = []
        benchmarks = pd.DataFrame()
        for job in self.bulk_response:
            if job["benchmarkIds"]:
                bm = pd.DataFrame(job["benchmarkIds"], columns=['BenchmarkId'])
                if not bm.empty:
                    self._append_profile_name(bm, job)
                    bench.append(bm)
        if bench:
            benchmarks = pd.concat(bench, ignore_index=True)
        return benchmarks

    def get_trigger_dates(self) -> pd.DataFrame:
        """
        Retrieve Trigger dates corresponding to each Job IDs.
        Returns:
            pandas dataframe
        """
        trigger = []
        trigger_dates = pd.DataFrame()
        for job in self.bulk_response:
            if job["triggerDates"]:
                trig = pd.json_normalize(job["triggerDates"])
                if not trig.empty:
                    self._append_profile_name(trig, job)
                    trigger.append(trig)
        if trigger:
            trigger_dates = pd.concat(trigger, ignore_index=True)
        return trigger_dates

    def get_job_warnings(self) -> pd.DataFrame:
        warnings = []
        job_warnings = pd.DataFrame()
        for job in self.bulk_response:
            if job["jobWarnings"]:
                warn = pd.json_normalize(job["jobWarnings"])
                if not warn.empty:
                    self._append_profile_name(warn, job)
                    warnings.append(warn)
        if warnings:
            job_warnings = pd.concat(warnings, ignore_index=True)
        return job_warnings

    def _parse_bulk_portfolios(self, resp, snap_type):
        port_list = []
        for job in resp:
            if job['portfolios']:
                if snap_type in job['portfolios']:
                    port = portfolios_to_df(portfolio=job['portfolios'][snap_type])
                    if not port.empty:
                        self._append_profile_name(port, job)
                        port_list.append(port)
                else:
                    self.logger.info(f"No '{snap_type}' portfolio available for job id: {job['jobId']}")
        return port_list

    def _parse_bulk_taxlots(self, resp, snap_type):
        port_list = []
        for job in resp:
            if job['taxLots']:
                if snap_type in job['taxLots']:
                    port = pd.json_normalize(job['taxLots'][snap_type]['valuesOnDay'])
                    if not port.empty:
                        self._append_profile_name(port, job)
                        port_list.append(port)
                else:
                    self.logger.info(f"No '{snap_type}' taxlot available for job id: {job['jobId']}")
        return port_list

    def close_portfolio(self) -> pd.DataFrame:
        """
        Retrieve close portfolios for a corresponding job IDs executed in batch, snapshot type and as of date.
        Returns:
            pandas dataframe
        """
        close_portfolio = pd.DataFrame()
        open_port = self._parse_bulk_portfolios(self.bulk_response, snap_type='CLOSE')
        if open_port:
            close_portfolio = pd.concat(open_port, ignore_index=True)
        return close_portfolio

    def open_portfolio(self) -> pd.DataFrame:
        """
        Retrieve open portfolios for a corresponding job IDs executed in batch, snapshot type and as of date.
        Returns:
            pandas dataframe
        """
        open_portfolio = pd.DataFrame()
        open_port = self._parse_bulk_portfolios(self.bulk_response, snap_type='OPEN')
        if open_port:
            open_portfolio = pd.concat(open_port, ignore_index=True)
        return open_portfolio

    def rebalanced_portfolio(self) -> pd.DataFrame:
        """
        Retrieve rebalanced portfolios for a corresponding job IDs executed in batch, snapshot type and as of date.
        Returns:
            pandas dataframe
        """
        rebalance_portfolio = pd.DataFrame()
        rebal_port = self._parse_bulk_portfolios(self.bulk_response, snap_type='REBALANCED')
        if rebal_port:
            rebalance_portfolio = pd.concat(rebal_port, ignore_index=True)
        return rebalance_portfolio

    def _extract_bulk_metrics(self, method):
        job_metrics = []
        metric_results = pd.DataFrame()
        for job in self.bulk_response:
            if job["metrics"]:
                all_metrics = job["metrics"]
                metrics = Metrics(all_metrics)
                data = eval(f'metrics.{method}()')
                if not data.empty:
                    self._append_profile_name(data, job)
                    job_metrics.append(data)
        if job_metrics:
            metric_results = pd.concat(job_metrics, ignore_index=True)
        return metric_results

    def get_metrics_rebal(self) -> pd.DataFrame:
        """
        Retrieve metrics calculations corresponding to submitted batch jobs
        Returns:
            pandas dataframe
        """
        return self._extract_bulk_metrics('to_rebal_dataframe')

    def get_metrics_to_dataframe(self) -> pd.DataFrame:
        """
        Converts to dataframe for all the metrics fields on business day.

        Note: This works for calculation types BACKCALCULATION and SIMULATION.
        Returns:
            pandas dataframe
        """
        return self._extract_bulk_metrics('to_dataframe')

    def open_taxlots(self) -> pd.DataFrame:
        """
        Retrieve open tax lots for given date corresponding to list of Job IDs submitted as batch.
        Returns:
            pandas dataframe
        """
        open_taxlots = pd.DataFrame()
        open_tax = self._parse_bulk_taxlots(self.bulk_response, snap_type='OPEN')
        if open_tax:
            open_taxlots = pd.concat(open_tax, ignore_index=True)
        return open_taxlots

    def close_taxlots(self) -> pd.DataFrame:
        """
        Retrieve close tax lots for given date corresponding to list of Job IDs submitted as batch.
        Returns:
            pandas dataframe
        """
        close_taxlots = pd.DataFrame()
        close_tax = self._parse_bulk_taxlots(self.bulk_response, snap_type='CLOSE')
        if close_tax:
            close_taxlots = pd.concat(close_tax, ignore_index=True)
        return close_taxlots

    def rebalanced_taxlots(self) -> pd.DataFrame:
        """
        Retrieve rebalanced tax lots for given date corresponding to list of Job IDs submitted as batch.
        Returns:
            pandas dataframe
        """
        rebalance_taxlots = pd.DataFrame()
        rebalance_tax = self._parse_bulk_taxlots(self.bulk_response, snap_type='REBALANCED')
        if rebalance_tax:
            rebalance_taxlots = pd.concat(rebalance_tax, ignore_index=True)
        return rebalance_taxlots

    def _extract_bulk_optimizer_result(self, method, date):
        port_tax_summ = []
        portfolio_tax_summary = pd.DataFrame()
        for job in self.bulk_response:
            if job['metrics']:
                bulk_opt = OptimizerResult(job['metrics'])
                if date:
                    resp = eval(f"bulk_opt.{method}(date='{date}')")
                else:
                    resp = eval(f"bulk_opt.{method}(date={date})")
                if resp is not None and not resp.empty:
                    self._append_profile_name(resp, job)
                    port_tax_summ.append(resp)
        if port_tax_summ:
            portfolio_tax_summary = pd.concat(port_tax_summ, ignore_index=True)
        return portfolio_tax_summary

    def get_portfolio_summary_detail(self, date=None) -> pd.DataFrame:
        """
        Get portfolio summary details from optimal portfolio like beta, risk, return etc.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PORTFOLIO_SUMMARY

        Args:
            date(str): (optional)String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for all the available dates.

        Returns:
            pandas dataframe with columns:
                ``['dataDate', 'beta', 'constraintSlack', 'impliedAversion', 'penalty', 'totalRisk',
                'commonFactorRisk', 'specificRisk', 'turnover', 'transactionCost',
                'utility', 'period', 'shortRebate', 'overlap', 'portfolioConcentration',
                'accountId', 'jointMarketImpactBuyCost', 'jointMarketImpactSellCost',
                'upperBoundOnUtility', 'expectedShortfall', 'return']``
        """
        return self._extract_bulk_optimizer_result('get_portfolio_summary_detail', date)

    def get_portfolio_holdings(self, date) -> pd.DataFrame:
        """
        Get portfolio holdings for optimal portfolio
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PORTFOLIO_SUMMARY

        Args:
            date(str): String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for latest date.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_portfolio_holdings', date)

    def get_portfolio_tax_summary(self, date=None) -> pd.DataFrame:
        """
        Get portfolio tax summary for optimal portfolio.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PORTFOLIO_SUMMARY

        Args:
            date(str): (optional) String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for all the available dates.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_portfolio_tax_summary', date)

    def get_tax_by_group_category(self, date=None) -> pd.DataFrame:
        """
        Get tax details by group category for optimal portfolio.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PORTFOLIO_SUMMARY

        Args:
            date(str): (optional) String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for all the available dates.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_tax_by_group_category', date)

    def get_tax_by_group_full_portfolio(self, date=None) -> pd.DataFrame:
        """
        Get tax by group for full portfolio.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : TAX_BY_GROUP_FULL_PORTFOLIO

        Args:
            date(str): (optional) String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for all the available dates.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_tax_by_group_full_portfolio', date)

    def get_trade_list(self, date) -> pd.DataFrame:
        """
        Get trade list for all transactions.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : TRADE_LIST

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_trade_list', date)

    def get_asset_details(self, date) -> pd.DataFrame:
        """
        Get asset details with initial weight and optimal weight.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : ASSET_DETAILS

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_asset_details', date)

    def get_asset_tax_detail(self, date) -> pd.DataFrame:
        """
        Get asset level tax details for optimal portfolio.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PORTFOLIO_SUMMARY

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_asset_tax_detail', date)

    def get_asset_realized_gain(self, date) -> pd.DataFrame:
        """
        Get asset realized gain details.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : ASSET_REALIZED_GAIN

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_asset_realized_gain', date)

    def get_constraint_diagnostics(self, date) -> pd.DataFrame:
        """
        Get constraint diagnostics details.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PROFILE_DIAGNOSTICS

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_constraint_diagnostics', date)

    def get_asset_cardinality_info(self, date=None) -> pd.DataFrame:
        """
        Get asset cardinality information.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : PROFILE_DIAGNOSTICS

        Args:
            date(str): (optional) String date in the YYYY-MM-DD format. Default value is None, so it will fetch data for all the available dates.

        Returns:
            pandas dataframe
        """
        return self._extract_bulk_optimizer_result('get_asset_cardinality_info', date)
