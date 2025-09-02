from dataclasses import dataclass
from typing import List, Optional, Union
from msci.sdk.calc.portfolio import mos as mos
from .client_portfolio import CashPortfolio
from .constraints import ConstraintFactory
from .full_optimizer_node import FullSpecOptimizationNode, GenericObjectiveFunction, TaxOptimizationSetting, \
    OptimizationSettings, TaxArbitrage, CashFlowOptSetting, DoNotTradeList, DoNotTradeExpression, \
    DoNotTradeListsAndExpressions
from .mos_config import Strategy, SimulationSettings, ReferenceUniverse
from .profile import Profile
from .enums import CalculationTypeEnum, PortfolioTypeEnum
from ...utils.utility import get_default_universe_and_benchmark
import warnings


@dataclass
class OptimizationOptions:
    """
    Dataclass for providing options for creating generic optimization node.

    Args:
        solver (int): to be tested, should be the same as values used in
            opstool. {
                BARRAOPT::eNO_SOLVER = 0,
                BARRAOPT::eQUADRATIC_SOLVER = 1,
                BARRAOPT::eSECOND_ORDER_CONE_SOLVER = 2,
                BARRAOPT::eNONLINEAR_SOLVER = 3
            }
        paring_approach (int): to be tested. Should be the same as options that
            can be entered in open optimizer.
        transaction_type (str): valid values are [allowAll, buyNone, sellNone,
            shortNone, buyFromUniv, sellNoneBuyFromUniv, buyShortFromUniv,
            disallowBuyShort, disallowSellCover,
            buyShortUnivNoSellCover, buyNoneSellFromUniv, univOnly]
        alpha_attribute (str): attribute field name that will be used as alpha
            values for investable
        return_multiplier (float,int): multiplier for return term.

    """

    solver: Optional[int] = None
    paring_approach: Optional[int] = None
    transaction_type: str = "allowAll"
    alpha_attribute: Optional[str] = None
    return_multiplier: Optional[Union[float, int]] = None


class GenericTaxTemplate(Profile):
    """
    Generic template to use for all tax optimization strategies.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
        
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 0.0075.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is 1.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        allow_short_positions (boolean): If True, portfolio type is set to LONG_SHORT. Default value is False in which case portfolio type is set to LONG_ONLY.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.

    Returns:
            None

    """

    def __init__(
            self,
            benchmark_list: List = None,
            universe_list: List = None,
            calculation_type=CalculationTypeEnum.REBALANCE,
            te_limit=None,
            te_limit_soft=True,
            max_assets=None,
            analysis_date=None,
            from_date=None,
            to_date=None,
            portfolio=CashPortfolio(),
            to_limit=None,
            risk_aversion=0.01,
            tax_multiplier=1,
            loss_benefit_multiplier=0,
            prefix_nodes=None,
            tax_arbitrage: List[TaxArbitrage] = None,
            tax_unit: str = "dollar",
            cash_upper_bound: float = 0.010,
            cash_lower_bound: float = 0.009,
            constraints: List = None,
            opt_options: OptimizationOptions = OptimizationOptions(),
            no_trade_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions] = None,
            no_hold_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions] = None,
            no_sell_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions] = None,
            no_buy_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions] = None,
            profile_name: str = None,
            allow_short_positions: Optional[bool] = False,
            risk_model: str = "GEMLTL",
            save_tax_lots: bool = False,
    ):

        usa_daily_bench = get_default_universe_and_benchmark()

        if universe_list is None:
            universe_list = [usa_daily_bench]

        if benchmark_list is None:
            benchmark_list = [usa_daily_bench]

        if analysis_date is None:
            if from_date is not None and to_date is not None:
                calculation_type = CalculationTypeEnum.SIMULATION

        # if isinstance(portfolio, CashPortfolio):
        cashflow_usd = 0  # cash already inline
        # else:
        #     cashflow_usd = portfolio.initial_cash # for now, apply it to the optimization, in the future this should be added to omps

        if constraints is None:
            constraints = []

        if te_limit:
            constraints += [ConstraintFactory.RiskConstraint(upper_bound=te_limit,
                                                             is_soft=te_limit_soft,
                                                             reference_portfolio="BaseBenchmark")]
        if max_assets:
            constraints += [ConstraintFactory.NumberOfAssets(max=max_assets)]
        if to_limit:
            constraints += [ConstraintFactory.TurnoverConstraint(upper_bound=to_limit)]

        objective_function = GenericObjectiveFunction(
            tax_term=tax_multiplier,
            loss_benefit_term=loss_benefit_multiplier,
            cf_risk_aversion=risk_aversion,
            sp_risk_aversion=risk_aversion,
            alpha_attribute=opt_options.alpha_attribute,
            alpha_term=opt_options.return_multiplier
        )
        tax_opt_setting = TaxOptimizationSetting(tax_unit=tax_unit, selling_order_rule="auto",
                                                 long_term_tax_rate=0.238, short_term_tax_rate=0.408,
                                                 wash_sale_rule="disallowed")
        # if cashflow_usd:
        #     cash_flow_settings = CashFlowOptSetting(amount=cashflow_usd,cash_type='AMOUNT')
        # else:
        cash_flow_settings = None
        opt_settings = OptimizationSettings(
            risk_model=risk_model,
            tax_optimization_setting=tax_opt_setting,
            cash_flow_settings=cash_flow_settings,
            cash_in_portfolio_upper_bound=cash_upper_bound,
            cash_in_portfolio_lower_bound=cash_lower_bound,
            paring_approach=opt_options.paring_approach,
            solver=opt_options.solver,
            transaction_type=opt_options.transaction_type
        )

        tax_opt_node = FullSpecOptimizationNode(
            constraints=constraints,
            objective_function=objective_function,
            tax_arbitrages=tax_arbitrage,
            opt_settings=opt_settings,
            do_not_trade_criteria=no_trade_criteria,
            do_not_hold_criteria=no_hold_criteria,
            no_sell=no_sell_criteria,
            no_buy=no_buy_criteria,
        )
        ref_universe = ReferenceUniverse(
            benchmark=benchmark_list,
            universe=universe_list,
            portfolio=portfolio,
        )
        if prefix_nodes:
            node_list = prefix_nodes + [tax_opt_node]
        else:
            node_list = [tax_opt_node]
        strat = Strategy(node_list=node_list, ref_universe=ref_universe)

        if allow_short_positions:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date,
                                              portfolio_type=PortfolioTypeEnum.LONG_SHORT)
        else:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date)

        super().__init__(
            strategy=strat,
            simulation_settings=sim_settings,
            profile_name=profile_name,
            save_tax_lots=save_tax_lots
        )


class TaxAdvantagedModelTrackingTemplate(GenericTaxTemplate):
    """
    Template to maximize losses while managing risk relative to a benchmark with risk aversion and tracking error limit.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 0.0001.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is 1.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self, risk_aversion=0.0001, tax_multiplier=1, loss_benefit_multiplier=1, te_limit=0.005,
                 te_limit_soft=True, **kwargs):
        super().__init__(risk_aversion=risk_aversion, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, te_limit=te_limit,
                         te_limit_soft=te_limit_soft, **kwargs)


class TaxNeutralTemplate(GenericTaxTemplate):
    """
    Template to stay tax neutral (gains similar to losses) while managing risk relative to a benchmark with risk aversion and tracking error limit.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 1.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is 100.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is 0.0001.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self, risk_aversion=1, tax_multiplier=100, loss_benefit_multiplier=0.0001, use_tax_constraint=False,
                 **kwargs):
        tax_arbitrage = [TaxArbitrage(upper_bound=0, lower_bound=None)] if use_tax_constraint else []
        super().__init__(risk_aversion=risk_aversion, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier,
                         tax_arbitrage=tax_arbitrage, **kwargs)


class GainBudgetingTemplate(GenericTaxTemplate):
    """
    Template to stay as close as possible to a benchmark while staying within a user-specified gain budget.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 100.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is 1.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        gain_budget (float): maximum allowed gains in dollar value. Default value is None.
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self, gain_budget: float, risk_aversion: float = 100, tax_multiplier: float = 1,
                 loss_benefit_multiplier: float = 1, tax_unit="dollar", **kwargs):
        tax_arbitrage = [TaxArbitrage(upper_bound=gain_budget)]
        super().__init__(risk_aversion=risk_aversion, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier,
                         tax_unit=tax_unit, tax_arbitrage=tax_arbitrage, **kwargs)


class MaxLossHarvestingTemplate(GenericTaxTemplate):
    """
    Template to maximize losses without aversion to risk beyond a user specified optional bound.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 0.0001.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is 1.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self, risk_aversion: float = 0.0001, tax_multiplier=1, loss_benefit_multiplier=1, **kwargs):
        super().__init__(risk_aversion=risk_aversion, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, **kwargs)


class GainRealizationTemplate(GenericTaxTemplate):
    """
    Template to maximize gains while managing risk relative to a benchmark with risk aversion and tracking error limit.

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
                    
        te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
        te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
        max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
        risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 0.0001.
        tax_multiplier (float): Tax penalty rate from gains in the objective function. Default value is -1.
        loss_benefit_multiplier (float): Tax benefit rate from losses in the objective function. Default value is -1.
        prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
        tax_arbitrage (List[TaxArbitrage]): Tax arbitrage ranges. Default value is None.
        tax_unit (str): Tax unit, "dollar" or "decimal". Default value is "dollar".
        no_trade_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Trade criteria from a previously uploaded portfolio. Default value is None.
        no_hold_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): Do Not Hold criteria from a previously uploaded portfolio. Default value is None.
        no_sell_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Sell criteria from a previously uploaded portfolio. Default value is None.
        no_buy_criteria (DoNotTradeList, DoNotTradeExpression, DoNotTradeListsAndExpressions): No Buy criteria from a previously uploaded portfolio. Default value is None.
        profile_name (str): Name of the profile request. Useful in case of bulk jobs.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self, risk_aversion: float = 0.0001, tax_multiplier=-1, loss_benefit_multiplier=-1, **kwargs):
        super().__init__(risk_aversion=risk_aversion, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, **kwargs)


class PureOptimizationTemplate(Profile):
    """
    Generic template to use for all tax optimization strategies
    Args:
    calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:

                •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.

    te_limit (float): Tracking error limit (predicted active risk) set in decimal terms. Default value is None.
    te_limit_soft (bool): If True, Tracking Error limit is a soft constraint. If False, Tracking Error limit is a hard constraint. Default value is True.
    max_assets (int): Maximum number of assets in optimal portfolio, soft bound. Default value is None.
    analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
    from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
    to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
    benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
    universe_list (list): List of MSCI index to use as a universe. Default value is None.
    portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
    to_limit (int) : Maximum turnover the optimizer must observe in producing an optimal portfolio.
    risk_aversion (float): Risk aversion to use in the optimization problem. Default value is 0.0075.
    prefix_nodes (list): Nodes to screen the  ahead of the optimization, such as BISR screens of Node. Default value is None.
    cash_upper_bound (float): Upper bound for cash buffer. Default value is 1 bps.
    cash_lower_bound (float): Lower bound for cash buffer. Default value is .9 bps.
    constraints (List): Additional constraints to include in the optimization. Default value is None.
    profile_name (str): Name of the profile request. Useful in case of bulk jobs.
    allow_short_positions(boolean): If True, portfolio type is set to LONG_SHORT. Default value is False in which case portfolio type is set to LONG_ONLY.
    risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
    save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
    """

    def __init__(
            self,
            benchmark_list: List = None,
            universe_list: List = None,
            calculation_type=CalculationTypeEnum.REBALANCE,
            te_limit=None,
            te_limit_soft=True,
            max_assets=None,
            analysis_date=None,
            from_date=None,
            to_date=None,
            portfolio=CashPortfolio(),
            to_limit=None,
            risk_aversion=0.01,
            prefix_nodes=None,
            cash_upper_bound: Optional[float] = 0.010,
            cash_lower_bound: Optional[float] = 0.009,
            disable_cash_bound: Optional[bool] = False,
            constraints: List = None,
            opt_options: OptimizationOptions = OptimizationOptions(),
            profile_name: str = None,
            allow_short_positions: Optional[bool] = False,
            risk_model: str = "GEMLTL",
            save_tax_lots: bool = False
    ):

        usa_daily_bench = get_default_universe_and_benchmark()

        if universe_list is None:
            universe_list = [usa_daily_bench]

        if benchmark_list is None:
            benchmark_list = [usa_daily_bench]

        # if isinstance(portfolio, CashPortfolio):
        cashflow_usd = 0  # cash already inline
        # else:
        #     cashflow_usd = portfolio.initial_cash  # for now, apply it to the optimization, in the future this should be added to omps

        if constraints is None:
            constraints = []
        if te_limit:
            constraints += [ConstraintFactory.RiskConstraint(upper_bound=te_limit,
                                                             is_soft=te_limit_soft,
                                                             reference_portfolio="BaseBenchmark")]
        if max_assets:
            constraints += [ConstraintFactory.NumberOfAssets(max=max_assets)]
        if to_limit:
            constraints += [ConstraintFactory.TurnoverConstraint(to_limit)]

        objective_function = GenericObjectiveFunction(
            cf_risk_aversion=risk_aversion,
            sp_risk_aversion=risk_aversion,
            alpha_attribute=opt_options.alpha_attribute,
            alpha_term=opt_options.return_multiplier
        )
        tax_opt_setting = None
        cash_flow_settings = CashFlowOptSetting(amount=cashflow_usd, cash_type='AMOUNT')
        opt_settings = OptimizationSettings(
            risk_model=risk_model,
            tax_optimization_setting=tax_opt_setting,
            cash_flow_settings=cash_flow_settings,
            cash_in_portfolio_upper_bound=cash_upper_bound,
            cash_in_portfolio_lower_bound=cash_lower_bound,
            disable_cash_bound=disable_cash_bound,
            paring_approach=opt_options.paring_approach,
            solver=opt_options.solver,
            transaction_type=opt_options.transaction_type
        )
        tax_opt_node = FullSpecOptimizationNode(
            constraints=constraints,
            objective_function=objective_function,
            opt_settings=opt_settings
        )
        ref_universe = ReferenceUniverse(
            benchmark=benchmark_list,
            universe=universe_list,
            portfolio=portfolio,
        )
        if prefix_nodes:
            node_list = prefix_nodes + [tax_opt_node]
        else:
            node_list = [tax_opt_node]

        strat = Strategy(node_list=node_list, ref_universe=ref_universe)

        if allow_short_positions:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date,
                                              portfolio_type=PortfolioTypeEnum.LONG_SHORT)
        else:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date)
        super().__init__(
            strategy=strat,
            simulation_settings=sim_settings,
            profile_name=profile_name,
            save_tax_lots=save_tax_lots
        )


class InitialTETemplate(PureOptimizationTemplate):
    """
    Template to calculate tracking error of the initial portfolio

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:
            
                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.                    
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
    """

    def __init__(self,
                 **kwargs):
        warnings.warn(
            "InitialTETemplate is deprecated and may be removed in future releases. "
            "Please use InitialPortfolioMetricsTemplate as the recommended alternative.",
            DeprecationWarning,
            stacklevel=2
        )
        to_constraint = ConstraintFactory.TurnoverConstraint(0.0)
        super().__init__(
            risk_aversion=0,
            cash_lower_bound=None,
            cash_upper_bound=None,
            disable_cash_bound=True,
            constraints=[to_constraint],
            **kwargs)


class UnrealizedGainsTemplate(GenericTaxTemplate):
    """
    Template to calculate unrealized gains of the initial portfolio

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:

                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.                    
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self,
                 **kwargs):
        warnings.warn(
            "UnrealizedGainsTemplate is deprecated and may be removed in future releases. "
            "Please use InitialPortfolioMetricsTemplate as the recommended alternative.",
            DeprecationWarning,
            stacklevel=2
        )

        super().__init__(
            risk_aversion=0,
            tax_multiplier=1,
            loss_benefit_multiplier=0,
            cash_lower_bound=1,
            cash_upper_bound=1,
            **kwargs)

        metric_list = self.metrics_calculation.metric_list
        required_metric = ('INITIAL_PORTFOLIO', 'UNREALIZED_GAIN_LOSS')
        if required_metric not in metric_list:
            metric_list.append(required_metric)


class InitialPortfolioMetricsTemplate(Profile):
    """
    Template to calculate unrealized gains of the initial portfolio

    Args:
        calculation_type (CalculationTypeEnum): (optional) Use to specify behavior of the calculation. The following options are available:

                    •REBALANCE - (default)rebalance a portfolio for one day only. Use the latest available portfolio given the date of calculation.
                    •SIMULATION - compute a time series of portfolio using the latest available portfolio given the first day of calculation. Skip last rebalancing.
                    •EOD/BACKCALCULATION - compute a time series of portfolio using the portfolio at the day of the calculation. Fail if not present. Perform last rebalancing.
        analysis_date (str): The date in YYYY-MM-DD format for which the account is being REBALANCED. Do not set with from_date.
        from_date (str): The starting date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        to_date (str): The ending date in YYYY-MM-DD format for a SIMULATION/ BACKCALCULATION. Do not set with analysis_date.
        benchmark_list (list): List of MSCI index to use as a benchmark. Default value is None.
        universe_list (list): List of MSCI index to use as a universe. Default value is None.
        portfolio (Portfolio):  A portfolio object to use as the initial portfolio of a rebalance or simulation. Default value is CashPortfolio with 10,000,000 USD.
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplate.
    """

    def __init__(self,
            benchmark_list: List = None,
            universe_list: List = None,
            calculation_type=CalculationTypeEnum.REBALANCE,
            analysis_date=None,
            from_date=None,
            to_date=None,
            portfolio=CashPortfolio(),
            risk_model: str = "GEMLTL",
            save_tax_lots: bool = False,
            allow_short_positions: Optional[bool] = False):

        usa_daily_bench = get_default_universe_and_benchmark()

        if universe_list is None:
            universe_list = [usa_daily_bench]

        if benchmark_list is None:
            benchmark_list = [usa_daily_bench]
        ref_universe = ReferenceUniverse(
            benchmark=benchmark_list,
            universe=universe_list,
            portfolio=portfolio,
        )

        if allow_short_positions:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date,
                                              portfolio_type=PortfolioTypeEnum.LONG_SHORT)
        else:
            sim_settings = SimulationSettings(analysis_date=analysis_date, calculation_type=calculation_type,
                                              from_date=from_date, to_date=to_date)

        optimizer_metrics = mos.OptimizerMetrics(metrics_risk_model=risk_model)
        strat = Strategy(node_list=[optimizer_metrics], ref_universe=ref_universe)

        super().__init__(
            strategy=strat,
            simulation_settings=sim_settings,
            save_tax_lots=save_tax_lots
        )


