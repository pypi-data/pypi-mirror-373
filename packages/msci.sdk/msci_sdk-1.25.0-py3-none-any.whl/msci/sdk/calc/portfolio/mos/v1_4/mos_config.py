import copy
import warnings
from dataclasses import dataclass
from typing import Optional, List, Union

import pandas as pd
import json

from .full_optimizer_node import CustomAttribute
from .enums import CalculationTypeEnum, TriggerCalendarEnum, PortfolioTypeEnum, ValuationTypeEnum, MultiAccountStyleEnum
from ...utils.validations import TypeValidation, StringDateFormat
from .client_portfolio import CashPortfolio, ClientPortfolio
from ...utils.dataclass_validations import BaseDataClassValidator


class SimulationSettings:
    """
    Service to define the job type and date range for running the optimization.

    Args:
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being rebalanced; do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a simulation; do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a simulation; do not set with analysis_date.
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
                    •REBALANCE - (default) rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
        portfolio_type (PortfolioTypeEnum): (optional) What kind of portfolio is required after optimization. The following options are available:
                    •LONG_ONLY - (default) long portfolio only.
                    •LONG_SHORT - long/short portfolio with net weight = 1.
        valuation_type (ValuationTypeEnum): (optional) What kind of valuation will be applied to long/short portfolio. The following optiions are available:
                    •NET - sum of all positions irrespective of sign.
                    •LONG_SIDE - sum of long positions only.
                    •USER_DEFINED - user defined fix value of portfolio as provided in param userDefinedPortfolioValue.
                     These options are only applicable for long/short portfolio with following defaults.
                    •portfolioType - LONG_ONLY ==> This option not supported (as the valuation is always sum of all positions).
                    •portfolioType - LONG_SHORT ==> NET.
                    •portfolioType - DOLLAR_NEUTRAL ==> LONG_SIDE.
        user_defined_portfolio_value (float, int): (optional) Fix portfolio value used for long/short portfolio when valuationType is USER_DEFINED.
        calculation_currency (str): Currency to be used as numeraire in the profile. Defaults to USD.
        account_ids (list): List of account Ids(int) for multi account optimization profile, if not provided, the profile will be treated as a single account problem.
        multi_account_style(MultiAccountStyleEnum): (optional) Defines what kind of multi-account handling to be used if accountIds are provided.
                    •MULTI_ACCOUNT - (default)
                    •MULTI_SLEEVE - all "accounts" share the tax lots from the default portfolio.
        allow_user_defined_assets (boolean): (Optional) If true, then the user can provide assets in the portfolio that are not identifiable by QIS, the user upload the corresponding data for such assets. Default value is False.

    Returns:
            None

    """

    analysis_date = StringDateFormat('analysis_date')
    calculation_type = TypeValidation('calculation_type', CalculationTypeEnum)
    from_date = StringDateFormat('from_date')
    to_date = StringDateFormat('to_date')
    portfolio_type = TypeValidation('portfolio_type', PortfolioTypeEnum)
    valuation_type = TypeValidation('valuation_type', ValuationTypeEnum)
    account_ids = TypeValidation('account_ids', list)
    multi_account_style = TypeValidation('multi_account_style', MultiAccountStyleEnum)

    def __init__(self, analysis_date=None, calculation_type=CalculationTypeEnum.REBALANCE, from_date=None,
                 to_date=None, calculation_currency: str = "USD",
                 allow_user_defined_assets: Optional[bool] = False,
                 portfolio_type: PortfolioTypeEnum = PortfolioTypeEnum.LONG_ONLY,
                 valuation_type: Optional[ValuationTypeEnum] = None,
                 user_defined_portfolio_value: Optional[Union[int, float]] = None,
                 account_ids: Optional[List[str]] = None,
                 multi_account_style: Optional[MultiAccountStyleEnum] = None):

        self._validate_calc_dates(analysis_date, calculation_type, from_date, to_date)

        self.calculation_type = calculation_type
        self.analysis_date = analysis_date
        self.from_date = from_date
        self.to_date = to_date
        self.calculation_currency = calculation_currency
        self.portfolio_type = portfolio_type
        self.valuation_type = valuation_type
        self.user_defined_portfolio_value = user_defined_portfolio_value
        self.account_ids = account_ids
        self.multi_account_style = multi_account_style
        self.allow_user_defined_assets = allow_user_defined_assets

        self.calendar_name = None

    def _validate_calc_dates(self, analysis_date, calculation_type, from_date, to_date):
        if from_date and analysis_date:
            raise ValueError('Both analysis_date and from_date specified, please pass one or the other')
        if calculation_type == CalculationTypeEnum.REBALANCE:
            if analysis_date is None:
                raise ValueError("analysis_date should be provided in calculationType REBALANCE")
        if calculation_type in (
                CalculationTypeEnum.EOD, CalculationTypeEnum.BACKCALCULATION, CalculationTypeEnum.SIMULATION):
            if from_date is None or to_date is None:
                raise ValueError(
                    "From date and To date should be provided in calculationType EOD/BACKCALCULATION/SIMULATION")

    @property
    def body(self):
        """
        Dictionary representation of Simulation settings.

        Returns:
            dict: Dictionary representation of the node.
        """
        if self.calculation_type == CalculationTypeEnum.REBALANCE:
            date_settings = {
                "objType": "AnalysisDate",
                "value": self.analysis_date,
            }
        else:
            date_settings = {
                "fromDate": self.from_date,
                "toDate": self.to_date,
                "objType": "DateRange",
            }

        return {
            "calculationCurrency": self.calculation_currency,
            "dateSettings": date_settings,
            "asAtDate": None,
            "calendarName": self.calendar_name,
            "region": None,
            "maxGap": None,
            "calculationType": self.calculation_type.value,
            "portfolioType": self.portfolio_type.value,
            "valuationType": None if self.valuation_type is None else self.valuation_type.value,
            "userDefinedPortfolioValue": self.user_defined_portfolio_value,
            "accountIds": [n for n in self.account_ids] if self.account_ids is not None else None,
            "multiAccountStyle": None if self.multi_account_style is None else self.multi_account_style.value,
            "allowUserDefinedAssets": self.allow_user_defined_assets
        }


@dataclass()
class UniversePerAccount(BaseDataClassValidator):
    """
        Defines universe as above, for each multi-account.

        Args:
            account_id (str): Account for multi account optimization profile.
            universe (List[Portfolio,pd.Dataframe]) : An interface allowing definition of a universe (a set of all assets that can be in the resulting portfolio).

        Returns:
                None
    """
    account_id: str
    universe: list


@dataclass()
class BenchmarkPerAccount(BaseDataClassValidator):
    """
        Defines the referenceBenchmark as above, for each multi-account.

        Args:
            account_id (str): Account for multi account optimization profile.
            benchmark (List[pd.Dataframe]) : A named benchmark entry, the benchmarkRefName can be used within various parts of the strategy.
        Returns:
                None
    """
    account_id: str
    benchmark: list


@dataclass()
class CurrentPortfolioPerAccount(BaseDataClassValidator):
    """
        Defines the currentPortfolio as above, for each multi-account.

        Args:
            account_id (str): Account for multi account optimization profile.
            portfolio (Portfolio): Interface allowing various ways to define the contents of a portfolio.


        Returns:
                None
    """
    account_id: str
    portfolio: ClientPortfolio


class ReferenceUniverse:
    """
    ReferenceUniverse holds the universe, benchmark and portfolio for a strategy.

    Args:
        universe (List[Portfolio,pd.Dataframe]) : Universe portfolio, which is the list of all assets eligible for consideration for inclusion in a portfolio. You can use an existing saved portfolio or benchmark to define the universe.
        universe_multi_account : (optional) Defines universe as above, for each multi-account.
        benchmark (List[pd.Dataframe]) : Benchmark for the optimization.
        benchmark_multi_account : (optional) Defines the referenceBenchmark as above, for each multi-account.
        portfolio (Portfolio): (optional) Client portfolio object or cash portfolio. Default value is CashPortfolio.
        current_portfolio_multi_account : (optional) Defines the currentPortfolio as above, for each multi-account.

    Returns:
            None
    """

    universe = TypeValidation('universe', list)
    benchmark = TypeValidation('benchmark', list)

    def __init__(
            self,
            universe: list,
            benchmark: list,
            universe_multi_account: List[UniversePerAccount] = None,
            benchmark_multi_account: List[BenchmarkPerAccount] = None,
            portfolio=CashPortfolio(),
            current_portfolio_multi_account: List[CurrentPortfolioPerAccount] = None

    ):
        """"""
        # universe can take a list of universes, and be constructed from a benchmark or
        # user portfolio

        self.universe = universe
        self.benchmark = benchmark
        self.universe_multi_account = universe_multi_account
        self.benchmark_multi_account = benchmark_multi_account
        self.current_portfolio_multi_account = current_portfolio_multi_account

        if universe and not isinstance(universe, list):
            raise TypeError("Universe must be list of Dataframes or client portfolios.")

        if benchmark and not isinstance(benchmark, list):
            raise TypeError("Benchmark  must be list of Dataframes or client portfolios.")

        self.portfolio = portfolio
        self.benchmark_ref_name = "BaseBenchmark"
        self.universe_ref_name = "BaseUniverse"

    def get_benchmark_ref_name(self):
        """
        Retrieve benchmark reference names for either single-account optimization or for each account in a multi-account optimization.

        Returns:
            pd.DataFrame: Benchmark reference names.
        """
        bench_ref_name_data = []
        if self.benchmark_multi_account:
            for benchmark_account in self.benchmark_multi_account:
                bench_list = self.get_univ(benchmark_account.benchmark)
                bench_ref_name_data.extend(
                    self._get_each_account_benchmark_ref_name(bench_list, benchmark_account.account_id))
        if self.benchmark:
            bench_list = self.get_univ(self.benchmark)
            bench_ref_name_data.extend(self._get_each_account_benchmark_ref_name(bench_list))
        return pd.DataFrame(bench_ref_name_data, columns=["account_id", "portfolio_id", "benchmark_ref_name"])

    def _get_each_account_benchmark_ref_name(self, benchmark, account_id=None):
        data = []
        benchmark_name = f"{self.benchmark_ref_name}"
        for index, bench in enumerate(benchmark, start=1):
            if len(benchmark) > 1:
                benchmark_name = f"{self.benchmark_ref_name}_{index}"
            if account_id:
                if len(benchmark) > 1:
                    benchmark_name = f"{self.benchmark_ref_name}_Acc{account_id}_{index}"
                else:
                    benchmark_name = f"{self.benchmark_ref_name}_Acc{account_id}"
            data.append((account_id, bench, benchmark_name))
        return data

    def get_universe_body(self, universe):
        """
        Form universe body depending on if universe is a client portfolio or MDSUID dataframe.
        """

        univ_body = []
        for univ in universe:
            if self.is_client_port_univ(univ):
                univ_dict = {
                    "objType": "UniverseFromPortfolio",
                    "portfolioSearchInput": {}
                }
                univ_body.append(self.__update_univ_as_client_port(ref_dict=univ_dict, univ=univ))

            else:
                univ_dict = {
                    "objType": "UniverseFromPortfolio",
                    "portfolioSearchInput": {
                        "objType": "PortfolioSearchInput",
                        "identification": {
                            "objType": "SimpleIdentification",
                            "source": "PAT",
                        },
                    },
                }

                univ_body.append(self.__update_univ_dict(ref_dict=univ_dict, univ=univ))

        return univ_body

    def is_client_port_univ(self, field):
        """
        Check if the universe is a list of client portfolios. If yes set univ_as_client_port = True.
        """
        univ_as_client_port = False
        if isinstance(field, ClientPortfolio):
            univ_as_client_port = True
        return univ_as_client_port

    def is_df_univ(self, field):
        """
        Check if the universe is a list of dataframes. If yes set is_df_univ = True.
        """
        is_univ_df = False
        if isinstance(field, pd.DataFrame):
            is_univ_df = True
        return is_univ_df

    def get_univ(self, universe):
        """
        Get a list of MDSUID from dataframe.
        """
        univ_list = []
        for univ in universe:
            if self.is_df_univ(univ):
                univ_list.extend(univ['mdsId'].to_list())
            elif self.is_client_port_univ(univ):
                univ_list.append(univ)
            else:
                raise TypeError("Benchmark/Universe must be list of Dataframes or client portfolios.")

        return univ_list

    def __update_univ_dict(self, ref_dict, univ):
        """
        Update universe body if universe is MDSUID.
        """

        __dict_copy = copy.deepcopy(ref_dict)
        __dict_copy.get("portfolioSearchInput").get("identification").update(
            {"portfolioId": univ, "name": univ})
        return __dict_copy

    def __update_univ_as_client_port(self, ref_dict, univ):
        """
        Update universe body if universe is client portfolio.
        """
        __dict_copy = copy.deepcopy(ref_dict)
        __dict_copy.get("portfolioSearchInput").update(univ.body)
        return __dict_copy

    def get_benchmark_univ_body(self, benchmark, account_id=None):
        """
        Form benchmark body.
        """
        bench_body = []
        benchmark_name = f"{self.benchmark_ref_name}"

        for index, bench in enumerate(benchmark, start=1):

            if len(benchmark) > 1:
                benchmark_name = f"{self.benchmark_ref_name}_{index}"

            if account_id:
                if len(benchmark) > 1:
                    benchmark_name = f"{self.benchmark_ref_name}_Acc{account_id}_{index}"
                else:
                    benchmark_name = f"{self.benchmark_ref_name}_Acc{account_id}"

            if self.is_client_port_univ(bench):
                benchmark_dict = {
                    "benchmarkRefName": benchmark_name,
                    "portfolioSearchInput": {}
                }
                bench_body.append(self.__update_univ_as_client_port(ref_dict=benchmark_dict, univ=bench))

            else:
                benchmark_dict = {
                    "benchmarkRefName": benchmark_name,
                    "portfolioSearchInput": {
                        "objType": "PortfolioSearchInput",
                        "identification": {
                            "objType": "SimpleIdentification",
                            "source": "PAT",
                        },
                    },
                }

                bench_body.append(self.__update_univ_dict(ref_dict=benchmark_dict, univ=bench))

        return bench_body

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"


@dataclass()
class NodeListPerAccount(BaseDataClassValidator):
    account_id: str
    node_list: list


@dataclass
class TriggerCalendar(BaseDataClassValidator):
    """
    Trigger rebalances based on a regular calendar.

    Args:
        calendar (str): Calendar type. Available values are: Never, Daily, LastDayOfMonth, FirstDayOfMonth, Quarterly, LastDayOfQuarter, SemiAnnually, LastDayOfHalfYear.
    """
    calendar: str = "FirstDayOfMonth"

    def __post_init__(self):
        allowed_values = {"Never", "Daily", "LastDayOfMonth", "FirstDayOfMonth", "Quarterly", "LastDayOfQuarter",
                          "SemiAnnually", "LastDayOfHalfYear"}
        if self.calendar not in allowed_values:
            raise ValueError(
                f"Invalid calendar type '{self.calendar}'. Allowed values are: {', '.join(allowed_values)}")


    @property
    def body(self):
        return {
            "calendar": self.calendar
        }

@dataclass
class ShiftedTriggerCalendar(BaseDataClassValidator):
    """
    Trigger rebalances based on a regular calendar, but starting from the given month.

    Args:
        calendar (str): Calendar type. Available values are: Quarterly, LastDayOfQuarter, SemiAnnually, LastDayOfHalfYear.
        month (str): Month to start rebalancing. Must be written in uppercase letters (e.g., JANUARY, FEBRUARY, MARCH, etc.).
    """
    calendar: str
    month: str

    def __post_init__(self):
        allowed_values = {"Quarterly", "LastDayOfQuarter", "SemiAnnually", "LastDayOfHalfYear"}
        if self.calendar not in allowed_values:
            raise ValueError(
                f"Invalid calendar type '{self.calendar}'. Allowed values are: {', '.join(allowed_values)}")

    @property
    def body(self):
        return {
            "calendar": self.calendar,
            "month": self.month
        }

@dataclass
class TriggerDates(BaseDataClassValidator):
    """
    A list of dates of when to trigger rebalances.

    Args:
        dates (List[str]): List of ISO formatted dates.
    """
    dates: List[str]

    @property
    def body(self):
        return {
            "dates": self.dates
        }

@dataclass
class CompositeTrigger(BaseDataClassValidator):
    """
    Logically compose triggers together.

    Args:
        logical_method (str): Logical method to combine triggers. Example values: AND, OR.
        triggers (List[BaseDataClassValidator]): List of triggers (TriggerCalendar, ShiftedTriggerCalendar, TriggerDates, or CompositeTrigger).
    """
    logical_method: Optional[str]
    triggers: Optional[List[Union[TriggerCalendar, ShiftedTriggerCalendar, TriggerDates, 'CompositeTrigger']]]

    @property
    def body(self):
        body = {
            "logicalMethod": self.logical_method,
            "triggers": []
        }

        for trigger in self.triggers:
            trigger_body = trigger.body
            if isinstance(trigger, TriggerCalendar):
                trigger_body["objType"] = "TriggerCalendar"
            elif isinstance(trigger, ShiftedTriggerCalendar):
                trigger_body["objType"] = "ShiftedTriggerCalendar"
            elif isinstance(trigger, TriggerDates):
                trigger_body["objType"] = "TriggerDates"
            elif isinstance(trigger, CompositeTrigger):
                trigger_body["objType"] = "CompositeTrigger"
            body["triggers"].append(trigger_body)

        return body


class Strategy:
    """
    Service to create a strategy definition where you can further add the optimization settings, reference universe, optimization methodology and so on.

    Args:
        ref_universe (ReferenceUniverse): Defines the universe and set of benchmarks for the strategy to work with.
        node_list (List): List of nodes to add.
        trigger_calendar (TriggerCalendarEnum): (optional) TriggerCalendar to trigger rebalances based on a regular calendar. **Deprecated**. Use the `trigger` parameter instead. trigger_calendar parameter may be removed in future versions.
        trigger (Union[TriggerCalendar, ShiftedTriggerCalendar, TriggerDates, CompositeTrigger]): (optional) trigger_calender parameter is deprecated and the new preferred parameter is trigger.
        node_list_multi_account (List[NodeListPerAccount]): (optional) List of nodelist for each account in a multi account optimization profile.
    Returns:
            None

    """

    ref_universe = TypeValidation('ref_universe', ReferenceUniverse, mandatory=True)
    node_list = TypeValidation('node_list', list, mandatory=True)
    trigger_calendar = TypeValidation('trigger_calendar', TriggerCalendarEnum)

    def __init__(self, ref_universe, node_list, trigger_calendar = None, node_list_multi_account: List[NodeListPerAccount] = None
                 , trigger: Optional[Union[TriggerCalendar, ShiftedTriggerCalendar, TriggerDates, CompositeTrigger]] = TriggerCalendar()):

        if trigger_calendar is not None:
            warnings.warn(
                "The 'trigger_calendar' parameter and 'TriggerCalendarEnum' is deprecated and may be removed in future versions.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.ref_universe = ref_universe
        self.trigger_calendar = trigger_calendar
        self.trigger = trigger
        self.node_list = node_list
        self.node_list_multi_account = node_list_multi_account

        self.universe = self.ref_universe.get_univ(self.ref_universe.universe)

        self.universe_multi_account = [UniversePerAccount(account_id=universe_account.account_id,
                                                          universe=self.ref_universe.get_univ(
                                                              universe_account.universe)) for
                                       universe_account in
                                       self.ref_universe.universe_multi_account] if self.ref_universe.universe_multi_account else None

        self.benchmark = self.ref_universe.get_univ(self.ref_universe.benchmark)

        self.benchmark_multi_account = [BenchmarkPerAccount(account_id=benchmark_account.account_id,
                                                            benchmark=self.ref_universe.get_univ(
                                                                benchmark_account.benchmark)) for
                                        benchmark_account in
                                        self.ref_universe.benchmark_multi_account] if self.ref_universe.benchmark_multi_account else None

    @property
    def body(self):
        """
        Dictionary representation of Strategy settings.

        Returns:
            dict: Dictionary representation of the node.
        """
        problem_formulation = [n.body for n in self.node_list]

        if self.trigger_calendar is not None:
            trigger_body = {"objType": "TriggerCalendar", "calendar": self.trigger_calendar.value}
        elif self.trigger is not None:
            trigger_body = self.trigger.body
            if isinstance(self.trigger, TriggerCalendar):
                trigger_body["objType"] = "TriggerCalendar"
            elif isinstance(self.trigger, ShiftedTriggerCalendar):
                trigger_body["objType"] = "ShiftedTriggerCalendar"
            elif isinstance(self.trigger, TriggerDates):
                trigger_body["objType"] = "TriggerDates"
            elif isinstance(self.trigger, CompositeTrigger):
                trigger_body["objType"] = "CompositeTrigger"

        strategy = {
            "trigger": trigger_body,
            "problemFormulation": problem_formulation,
            "problemFormulationPerAccount": {
                node_list_account.account_id: [n.body for n in node_list_account.node_list]
                for node_list_account in
                self.node_list_multi_account} if self.node_list_multi_account is not None else None,
            "universe": self.ref_universe.get_universe_body(self.universe),
            "universePerAccount": {
                universe_account.account_id: self.ref_universe.get_universe_body(universe_account.universe)
                for universe_account in
                self.universe_multi_account} if self.universe_multi_account is not None else None,
            "referenceBenchmark": self.ref_universe.get_benchmark_univ_body(self.benchmark),
            "referenceBenchmarkPerAccount": {
                benchmark_account.account_id: self.ref_universe.get_benchmark_univ_body(benchmark_account.benchmark,
                                                                                        account_id=benchmark_account.account_id)
                for benchmark_account in
                self.benchmark_multi_account} if self.benchmark_multi_account is not None else None,
            "currentPortfolio": self.ref_universe.portfolio.body,
            "currentPortfolioPerAccount": {
                port.account_id: port.portfolio.body
                for port in
                self.ref_universe.current_portfolio_multi_account} if self.ref_universe.current_portfolio_multi_account is not None else None,

        }
        return strategy


@dataclass
class SolutionSettings(BaseDataClassValidator):
    """
    Where to save the resulting portfolios. If blank then the results will only be available from the MOS api using the jobs endpoints.

    Args:
        portfolio_id (str): Identifier assigned to the portfolio..
        source (str): (optional) Which portfolio store to resolve the portfolioId from. Default value is 'OMPS'.
        name (str): (optional) Name. Default value is None.
        description (str): (optional) Description. Default value is None.
        snapshot_type (str): (optional) Allowed snapshots; can be OPEN or CLOSE. Default is 'CLOSE'.
        owner (str): (optional) Owner. Default value is None.
        additional_attributes (List[CustomAttribute]): (optional) Additional attributes definition. Default value is None.

    Returns:
            None

    """

    portfolio_id: str
    source: Optional[str] = 'OMPS'
    name: Optional[str] = None
    description: Optional[str] = None
    snapshot_type: Optional[str] = 'CLOSE'
    owner: Optional[str] = None
    additional_attributes: Optional[List[CustomAttribute]] = None

    @property
    def body(self):
        """
        Dictionary representation of SolutionSettings settings.

        Returns:
            dict: Dictionary representation of the node.
        """
        return {
            "solutionPortfolio": {
                "identification": {
                    "objType": "SimpleIdentification",
                    "portfolioId": self.portfolio_id,
                    "source": self.source,
                    "name": self.name,
                    "description": self.description,
                    "snapshotType": self.snapshot_type,
                    "owner": self.owner,
                    "additionalAttributes": [a.body for a in
                                             self.additional_attributes] if self.additional_attributes is not None else None
                }
            },
        }


@dataclass
class ProxySetting(BaseDataClassValidator):
    """
    Proxy Settings for missing risk model data by group/logical expression. If a particular asset falls into more than one group, the settings are applied in order of priority ie favor the first one under this list.

    Args:
        expression (str): Logical expression to define the group.
        proxy_id (str): Identifier of the proxy.
        proxy_id_type (str): Type of the proxy from [MDSUID, ISIN, CUSIP, BARRA, SEDOL, TICKER]. Default value is 'MDSUID'.
        proxy_id_exchange (str): (optional) Exchange of the proxy identifier.

    """

    expression: Optional[str] = None
    proxy_id: Optional[str] = None
    proxy_id_type: Optional[str] = 'MDSUID'
    proxy_id_exchange: Optional[str] = None

    def __post_init__(self):
        allowed_values = {"MDSUID", "ISIN", "CUSIP", "BARRA", "SEDOL", "TICKER"}
        if self.proxy_id_type is not None and self.proxy_id_type not in allowed_values:
            raise ValueError(f"proxy_id_type must be one of {allowed_values}")

    @property
    def body(self):
        return {
            "expression": self.expression,
            "proxyId": self.proxy_id,
            "proxyIdType": self.proxy_id_type,
            "proxyIdExchange": self.proxy_id_exchange
        }


@dataclass
class FieldQueryDate(BaseDataClassValidator):
    """
    Interface of rebalance data query date override type.

    Args:
        field_query_date_type (str): Type of date to query. Allowed values are: [EffectiveDate, RebalanceDate, LastEOM, CustomDate].
        custom_date (str): (optional) Custom date in YYYY-MM-DD format and should be set if field_query_date_type is CustomDate. Default value is None.

    """
    field_query_date_type: str
    custom_date: Optional[str] = None

    def __post_init__(self):
        allowed_field_query_date_type = {"EffectiveDate", "RebalanceDate", "LastEOM", "CustomDate"}
        if self.field_query_date_type not in allowed_field_query_date_type:
            raise ValueError(f"field_query_date_type must be one of {allowed_field_query_date_type}")

        if self.field_query_date_type == "CustomDate" and self.custom_date is None:
            raise ValueError("custom_date must be set when field_query_date_type is 'CustomDate'")

        if self.field_query_date_type != "CustomDate" and self.custom_date is not None:
            raise ValueError("custom_date should only be set when field_query_date_type is 'CustomDate'")

    @property
    def body(self):
        _body = {
            "objType": self.field_query_date_type,
        }

        if self.custom_date is not None:
            _body.update({"customDate": self.custom_date})

        return _body


@dataclass
class FieldDataDefault(BaseDataClassValidator):
    """
    Interface of rebalance data defaulting type

    Args:
        field_data_default_type (str): Type of default value to use. Allowed values are: [DefaultValue, AverageValue].
        default_value (str): (optional) Default value to use when field_data_default_type is DefaultValue. Default value is None.
    """
    field_data_default_type: str
    default_value: Optional[str] = None

    def __post_init__(self):
        allowed_values = {"DefaultValue", "AverageValue"}
        if self.field_data_default_type not in allowed_values:
            raise ValueError(f"field_data_default_type must be one of {allowed_values}")

        if self.field_data_default_type == "DefaultValue" and self.default_value is None:
            raise ValueError("default_value must be set when field_data_default_type is 'DefaultValue'")

        if self.field_data_default_type != "DefaultValue" and self.default_value is not None:
            raise ValueError("default_value should only be set when field_data_default_type is 'DefaultValue'")

    @property
    def body(self):
        _body = {
            "objType": self.field_data_default_type,
        }

        if self.default_value is not None:
            _body.update({"value": self.default_value})

        return _body


@dataclass
class FieldQuerySetting(BaseDataClassValidator):
    """
    Rebalance field query settings for how to handle missing data

    Args:
        field_query_name (str): Name of the field query.
        query_date (FieldQueryDate): (optional) Interface of rebalance data query date override type. Default value is None.
        data_source_fallback (str): (optional) Choose the priority of data source (only for system assets), default is SYSTEM_ONLY. Accepted values for data_source_fallback are SYSTEM_ONLY, SYSTEM_THEN_USERDATA, USERDATA_THEN_SYSTEM.
        lookback_days (Union[float, int]): (optional) Number of days to lookback, if omitted then no fallback to previous values will occur.
        default (FieldDataDefault): (optional) Interface of rebalance data defaulting type. Default value is None.
        field_missing_data_handling (str): (optional) Action to take during optimization if data is missing. If omitted, defaults to MissingDataIgnore. The outcome of data being missing is context dependent. Allowed values are: [MissingDataIgnore, MissingDataDoNotTrade, MissingDataDoNotHold]
        proxies (List[ProxySetting]): (optional) Proxy settings for missing risk model data by group/logical expression. Default value is None.

    """

    field_query_name: str
    query_date: Optional[FieldQueryDate] = None
    data_source_fallback: Optional[str] = 'SYSTEM_ONLY'
    lookback_days: Optional[Union[float, int]] = None
    default: Optional[FieldDataDefault] = None
    field_missing_data_handling: Optional[str] = 'MissingDataIgnore'
    proxies: Optional[List[ProxySetting]] = None

    def __post_init__(self):
        allowed_values = {"MissingDataIgnore", "MissingDataDoNotTrade", "MissingDataDoNotHold"}
        if self.field_missing_data_handling not in allowed_values:
            raise ValueError(f"field_missing_data_handling must be one of {allowed_values}")

    @property
    def body(self):
        _body = {
            "fieldMissingDataHandling": self.field_missing_data_handling,
            "dataSourceFallback": self.data_source_fallback,
        }
        if self.query_date is not None:
            _body.update({"queryDate": self.query_date.body})
        if self.lookback_days is not None:
            _body.update({"lookbackDays": self.lookback_days})
        if self.default is not None:
            _body.update({"default": self.default.body})
        if self.proxies is not None:
            _body.update({"proxies": [p.body for p in self.proxies]})

        return _body

@dataclass
class DefaultFieldQuerySettings(BaseDataClassValidator):
    """
    Default settings for source fallback and days lookback.

    Args:
        data_source_fallback (str): (optional) Choose the priority of data source (only for system assets), default is SYSTEM_ONLY. Accepted values for data_source_fallback are SYSTEM_ONLY, SYSTEM_THEN_USERDATA, USERDATA_THEN_SYSTEM.

    """
    data_source_fallback: Optional[str] = 'SYSTEM_ONLY'

    @property
    def body(self):
        body = {
            "dataSourceFallback": self.data_source_fallback,
        }
        return body

@dataclass
class RebalanceContext(BaseDataClassValidator):
    """
    Settings for rebalance

    Args:
        user_price_field (str): (Optional) User datapoint for price in the form "ISO3Code 00.00", eg "USD 15.00"
        field_query_settings (List[FieldQuerySetting]): List of field query settings. Default value is None.
        default_field_query_settings (DefaultFieldQuerySettings): (Optional) Default settings for source fallback and days lookback. Default value is None.
    """
    user_price_field: Optional[str] = None
    field_query_settings: Optional[List[FieldQuerySetting]] = None
    default_field_query_settings: Optional[DefaultFieldQuerySettings] = None

    @property
    def body(self):
        return {
            "userPriceField": self.user_price_field,
            "fieldQuerySettings": {
                f.field_query_name: f.body for f in self.field_query_settings
            } if self.field_query_settings is not None else None,
            "defaultFieldQuerySettings": self.default_field_query_settings.body if self.default_field_query_settings is not None else None
        }

@dataclass
class RiskModelDetails(BaseDataClassValidator):
    """
    Add custom risk model and priority order.

    Args:
        custom_model (str): (Optional) custom risk model name
        order (str): (Optional) Default is SystemFirst. Allowed values are SystemFirst, CustomFirst, SystemOnly, CustomOnly.
    """

    risk_model: str
    custom_model: Optional[str] = None
    order: Optional[str] = 'SystemFirst'

    @property
    def body(self):
        return {
            "customModel": self.custom_model,
            "order": self.order
        }

@dataclass
class RiskModelSource(BaseDataClassValidator):
    """
    Optionally add RiskModelDetails.

    Args:
        risk_model_details (List[RiskModelDetails]): (Optional) Add custom risk model and priority order.
    """
    risk_model_details: Optional[List[RiskModelDetails]] = None

    @property
    def body(self):
        if self.risk_model_details is not None:
            return {
                detail.risk_model: detail.body
                for detail in self.risk_model_details
            }


@dataclass
class CalculationContext(BaseDataClassValidator):
    """
    For future expansion. A description of the market context under which the strategy is running. This context would
    typically perturb the market (prices) to demonstrate how a strategy would run in a different market scenario.

    Args:
        modular_derived_datapoints (dict): (Optional) Map of derived-data-point-name to formula. Default value is None.
        rebalance_context (RebalanceContext): (Optional) Settings for rebalance. Default value is None.
        risk_model_source (RiskModelSource): (Optional) Optionally add RiskModelDetails. Default value is None.

    """
    modular_derived_datapoints: Optional[dict] = None
    rebalance_context: Optional[RebalanceContext] = None
    risk_model_source: Optional[RiskModelSource] = None

    @property                                                                                                                                       
    def body(self):
        """
        Dictionary representation of CalculationContext settings.

        Returns:
            dict: Dictionary representation.
        """
        return {
            'modularDerivedDatapoints': self.modular_derived_datapoints,
            'rebalanceContext': self.rebalance_context.body if self.rebalance_context is not None else None,
            'riskModelSource': self.risk_model_source.body if self.risk_model_source is not None else None
        }


@dataclass
class OptimizerMetrics(BaseDataClassValidator):
    """
    Node that calls optimizer to calculate metrics on initial portfolio. This node can't be used with any other node in any account. It is a standalone node
    Args:
    metrics_risk_model (str): For metrics(INITIAL_PORTFOLIO) only, non optimization request, this is the risk model to use for metrics calculation by optimizer.

    """
    metrics_risk_model: str

    @property
    def body(self):
        """
        Dictionary representation of OptimizerMetrics.

        Returns:
            dict: Dictionary representation.
        """
        return {
            "objType": "OptimizerMetrics",
            "metricsRiskModel": self.metrics_risk_model
        }


@dataclass
class IdMappings(BaseDataClassValidator):
    """
    IdMappings is used to map a reference identifier to a specific asset identifier of a given type.

    Args:
    asset_id_type (str): Type of asset id. Allowed values are: MDSUID, ISIN, CUSIP, SEDOL, TICKER, USER_DEFINED
    reference_id (str): The identifier used as a reference for an asset.
    asset_id (str): The unique identifier assigned to a particular asset.

    """
    asset_id_type: str
    reference_id: str
    asset_id: str

    def __init__(self, asset_id_type: str, reference_id: str, asset_id: str):
        allowed_id_types = {"MDSUID", "ISIN", "CUSIP", "SEDOL", "TICKER", "USER_DEFINED"}
        if asset_id_type not in allowed_id_types:
            raise ValueError(f"id_type must be one of {allowed_id_types}")
        self.asset_id_type = asset_id_type
        self.reference_id = reference_id
        self.asset_id = asset_id

    @property
    def body(self):
        """
           Dictionary representation of IdMappings
        Returns:
            dict: Dictionary representation.
        """
        return {
            self.asset_id_type: {
                self.reference_id: self.asset_id
            }
        }
@dataclass
class FactorCovariance(BaseDataClassValidator):
    """
    FactorCovariance is used to store and manage the factor covariance values between different factors, which are identified by their respective factor IDs.

    Args:
    factor_id1 (List[str]): List of factor id to be passed.
    factor_id2 (List[str]): List of factor id to be passed.
    values (List[float, int]): List of factor covariance value between the given factor ids.
    """
    factor_id1: List[str]
    factor_id2: List[str]
    values: List[Union[float, int]]

    @property
    def body(self):
        """
        Dictionary representation of FactorCovariance.

        Returns:
            dict: Dictionary representation.
        """
        return {
            "factorId1": self.factor_id1,
            "factorId2": self.factor_id2,
            "values": self.values
        }

@dataclass
class FactorExposure(BaseDataClassValidator):
    """
    FactorExposure is used to store and manage the factor exposure values between respective factor id and security id.

    Args:
    factor_id (List[str]): List of factor ids to be passed.
    security_id (List[str]): List of security ids to be passed.
    values (List[float, int]): List of factor exposure values between the given factor ids and security ids.

    """
    factor_id: List[str]
    security_id: List[str]
    values: List[Union[float, int]]

    @property
    def body(self):
        """
        Dictionary representation of FactorExposure.

        Returns:
            dict: Dictionary representation.
        """
        return {
            "factorId": self.factor_id,
            "securityId": self.security_id,
            "values": self.values
        }

@dataclass
class SpecificCovariance(BaseDataClassValidator):
    """
    SpecificCovariance is used to store and manage the specific covariance values between different securities, which are identified by their respective security IDs.
    Args:
    security_id1 (List[str]): List of security ids to be passed.
    security_id2 (List[str]): List of security ids to be passed.
    values (List[float, int]): List of specific covariance values between the given security ids.

    """
    security_id1: List[str]
    security_id2: List[str]
    values: List[Union[float, int]]

    @property
    def body(self):
        """
        Dictionary representation of SpecificCovariance.

        Returns:
            dict: Dictionary representation.
        """
        return {
            "securityId1": self.security_id1,
            "securityId2": self.security_id2,
            "values": self.values
        }