import functools
import json
import pandas as pd
import logging

from ...utils import constants
from ...utils.metric import check_null, get_metric_subtype_data, get_metric_values, search_subtype


class OptimizerResult:
    """
    Displays optimizer results metric for all sub metric types. It fetches and stores metrics output to different methods as per usage. Includes data for below SUB_TYPES:
    ``["OPTIMIZATION_STATUS",
    "INPUT_DATA_ERRORS",
    "PORTFOLIO_SUMMARY",
    "TRADE_LIST",
    "ASSET_DETAILS",
    "PROFILE_DIAGNOSTICS",
    "TAX_BY_GROUP_FULL_PORTFOLIO",
    "ASSET_REALIZED_GAIN"]``
    """

    def __init__(self, metrics_response, account_id=None):
        self.logger = logging.getLogger(__name__)
        self.metrics_list = metrics_response['values']
        self.account_id = account_id
        if not self.metrics_list:
            self.logger.info('No optimizer result')

    def _prep_portfolio_summary(self, metric_sub_type, date):
        port_summary_dict = get_metric_subtype_data(metric_sub_type=metric_sub_type, date=date, metrics_list=self.metrics_list)
        return port_summary_dict['optimalPortfolio'][0]

    @check_null
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

        metric_sub_type = "PORTFOLIO_SUMMARY"
        combined_data = []
        columns = ['dataDate',
                   'beta', 'constraintSlack', 'impliedAversion', 'penalty', 'totalRisk',
                   'commonFactorRisk', 'specificRisk', 'turnover', 'transactionCost',
                   'utility', 'period', 'shortRebate', 'overlap', 'portfolioConcentration',
                   'accountId', 'jointMarketImpactBuyCost', 'jointMarketImpactSellCost',
                   'upperBoundOnUtility', 'expectedShortfall', 'return']
        if date:
            optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, date)
            optimal_port_dict['dataDate'] = date
            port_df = pd.json_normalize(optimal_port_dict)
        else:
            _dict_n = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n['dataDates']
            for d in _list_dates:
                optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, d)
                optimal_port_dict['dataDate'] = d
                combined_data.append(optimal_port_dict)
            port_df = pd.json_normalize(combined_data)
        return port_df[columns]

    @check_null
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

        optimal_port_dict = self._prep_portfolio_summary("PORTFOLIO_SUMMARY", date)
        port_df = pd.json_normalize(optimal_port_dict['portfolioHoldings'], 'holding')
        port_df.insert(0, 'dataDate', date)
        return port_df

    @check_null
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
        metric_sub_type = "PORTFOLIO_SUMMARY"
        combined_data = []
        columns = ['dataDate', 'totalTax', 'disallowedLossByPurchases',
                   'totalLossBenefit', 'netTaxImpact']

        if date:
            optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, date)
            if optimal_port_dict['portfolioTax']:
                port_df = pd.json_normalize(optimal_port_dict['portfolioTax'])
                port_df['dataDate'] = date
            else:
                self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                return
        else:
            _dict_n_sum = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n_sum['dataDates']
            for d in _list_dates:
                optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, d)
                if optimal_port_dict['portfolioTax']:
                    port_tax = optimal_port_dict['portfolioTax']
                    port_tax['dataDate'] = d
                    combined_data.append(port_tax)
                else:
                    self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                    return
            port_df = pd.json_normalize(combined_data)
        return port_df[columns]

    @check_null
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
        metric_sub_type = "PORTFOLIO_SUMMARY"
        combined_data = []
        if date:
            optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, date)
            if optimal_port_dict['portfolioTax']:
                port_df = pd.json_normalize(optimal_port_dict['portfolioTax'],
                                            ['taxByGroup', 'taxByCategory'])
                port_df['dataDate'] = date
            else:
                self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                return
        else:
            _dict_n_group = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n_group['dataDates']
            for d in _list_dates:
                optimal_port_dict = self._prep_portfolio_summary(metric_sub_type, d)
                if optimal_port_dict['portfolioTax']:
                    tax_cat_list = optimal_port_dict['portfolioTax']['taxByGroup'][0]['taxByCategory']
                    for dict_item in tax_cat_list:
                        dict_item['dataDate'] = d
                    combined_data.extend(tax_cat_list)
                else:
                    self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                    return
            port_df = pd.json_normalize(combined_data)
        return port_df

    @check_null
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
        columns = ['dataDate', 'assetId', 'newShares', 'disqualifiedShares', 'gain', 'loss']
        optimal_port_dict = self._prep_portfolio_summary("PORTFOLIO_SUMMARY", date)
        if optimal_port_dict['portfolioTax']:
            asset_tax_df = pd.json_normalize(optimal_port_dict['portfolioTax'], ['assetTaxDetail'])
            asset_tax_df['dataDate'] = date
            return asset_tax_df[columns]
        else:
            self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)

    @check_null
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
        columns = ['dataDate', 'tradeType', 'assetId', 'initialShares', 'tradedShares',
                   'finalShares', 'price', 'tradedValue', 'tradedValuePcnt',
                   'fixedTransactionCost', 'nonlinearTransactionCost',
                   'piecewiseLinearTransactionCost', 'totalTransactionCost']
        trade_list = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type="TRADE_LIST")
        transaction_list = trade_list[0]['transaction']
        trade_list_df = pd.json_normalize(transaction_list)
        trade_list_df['dataDate'] = date
        return trade_list_df[columns]

    @check_null
    def get_asset_details(self, date) -> pd.DataFrame:
        """
        Get asset details with initial weight and optimal weight.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : ASSET_DETAILS

        Note: Metric subtype ASSET_DETAILS not supported for Multi-account optimization.

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        columns = ['dataDate', 'assetId', 'initialWeight', 'optimalWeight',
                   'roundlottedWeight', 'residualAlpha']
        if self.account_id is not None:
            raise ValueError(constants.ASSET_DETAILS_MULTI_ACCOUNT_ERROR)
        asset_details_dict = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type="ASSET_DETAILS")
        asset_detail_list = asset_details_dict['assetDetail']
        asset_detail_df = pd.json_normalize(asset_detail_list)
        asset_detail_df['dataDate'] = date
        return asset_detail_df[columns]

    @check_null
    def get_asset_realized_gain(self, date) -> pd.DataFrame:
        """
        Get asset realized gain.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : ASSET_REALIZED_GAIN

        Args:
            date: String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        metric_sub_type = "ASSET_REALIZED_GAIN"
        asset_realized_gain_dict = get_metric_values(metric_sub_type=metric_sub_type, date=date, metrics_list=self.metrics_list)
        data = asset_realized_gain_dict[metric_sub_type]
        asset_realized_gain_list = data['entries']
        asset_realized_gain_df = pd.json_normalize(asset_realized_gain_list)
        asset_realized_gain_df['dataDate'] = date
        return asset_realized_gain_df

    @check_null
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
        metric_sub_type = "TAX_BY_GROUP_FULL_PORTFOLIO"
        combined_data = []
        if date:
            tax_by_group_full_portfolio = get_metric_values(metric_sub_type=metric_sub_type, date=date, metrics_list=self.metrics_list)
            if tax_by_group_full_portfolio:
                tax_by_group_df = pd.json_normalize(tax_by_group_full_portfolio)
                tax_by_group_df.insert(0, 'dataDate', date)
            else:
                self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                return
        else:
            _dict_n_tax = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n_tax['dataDates']
            for d in _list_dates:
                tax_by_group_full_portfolio = get_metric_values(metric_sub_type=metric_sub_type, date=d, metrics_list=self.metrics_list)
                if tax_by_group_full_portfolio:
                    tax_by_group_full_portfolio['dataDate'] = d
                    combined_data.append(tax_by_group_full_portfolio)
                else:
                    self.logger.info(constants.NO_TAX_OUTPUT_MESSAGE)
                    return
            tax_by_group_df = pd.json_normalize(combined_data)
        return tax_by_group_df

    @check_null
    def _get_optimization_status(self, date) -> str:
        """
        Get status of optimisation run.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : OPTIMIZATION_STATUS

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        # TODO: need to check if this is really needed
        optimization_status = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type="OPTIMIZATION_STATUS")
        return optimization_status['message']

    @check_null
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
        # TODO: check why asset id is not part of output.
        #  Should we join it with other asset details to show assetId as column?
        profile_diagnostics = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type="PROFILE_DIAGNOSTICS")[0]
        return pd.json_normalize(profile_diagnostics['constraintDiagnostics'])

    @check_null
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
        metric_sub_type = "PROFILE_DIAGNOSTICS"
        combined_data = []
        if date:
            profile_diagnostics = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type=metric_sub_type)[0]
            profile_diagnostics_df = pd.json_normalize(profile_diagnostics['assetCardinalityInfo'])
            profile_diagnostics_df.insert(0, 'dataDate', date)
        else:
            _dict_n = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n['dataDates']
            for d in _list_dates:
                profile_diagnostics = get_metric_subtype_data(metrics_list=self.metrics_list,date=d, metric_sub_type=metric_sub_type)[0]
                asset_cardinality_list = profile_diagnostics['assetCardinalityInfo']
                for dict_item in asset_cardinality_list:
                    dict_item['dataDate'] = d
                combined_data.extend(asset_cardinality_list)
            profile_diagnostics_df = pd.json_normalize(combined_data)
        return profile_diagnostics_df

    @check_null
    def get_input_data_errors(self, date) -> str:
        """
        Get input data errors for the run.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : INPUT_DATA_ERRORS

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        # TODO: need to check the format, returning string for now
        input_data_errors = get_metric_subtype_data(metrics_list=self.metrics_list,date=date, metric_sub_type="INPUT_DATA_ERRORS")
        return input_data_errors

    @check_null
    def get_post_op_roundlotting_errors(self, date) -> str:
        """
        Get status of roundlotting.
        Source metric : OPTIMIZER_RESULT
        Source metric subtype : POST_OPT_ROUNDLOTTING_ERRORS

        Args:
            date(str): String date in the YYYY-MM-DD format.

        Returns:
            pandas dataframe
        """
        optimization_status = get_metric_subtype_data(metrics_list=self.metrics_list, date=date, metric_sub_type="POST_OPT_ROUNDLOTTING_ERRORS")
        if optimization_status:
            optimization_status = json.loads(optimization_status)

        if 'message' in optimization_status and optimization_status['message']:
            return optimization_status['message']
