from dataclasses import dataclass
from typing import List

from .client_portfolio import TaxLotPortfolio, ClientPortfolio, SimplePortfolio, CashPortfolio
from .constraints import ConstraintFactory
from .enums import MultiAccountStyleEnum
from .full_optimizer_node import FullSpecOptimizationNode, GenericObjectiveFunction, OptimizationSettings, \
    TaxOptimizationSetting, TaxArbitrage
from .mos_config import Strategy, ReferenceUniverse, BenchmarkPerAccount, UniversePerAccount, \
    CurrentPortfolioPerAccount, NodeListPerAccount, SimulationSettings
from .profile import Profile


@dataclass
class SleeveConfig:
    """
    A sleeve configuration for the MSO template.

    Args:
        id (str): The id or name of the sleeve.
        target (float): The target weight of the sleeve.
        drift (float): (optional) The drift of the sleeve. Default value is 0.05.
        risk_aversion (float): (optional) Risk aversion to use in the optimization problem. Default value is None.
            Default value is 0.0001 for template TaxAdvantagedModelTrackingTemplateMSO.
            Default value is 1 for template TaxNeutralTemplateMSO.
            Default value is 100 for template GainBudgetingTemplateMSO.
            Default value is 0.0001 for template MaxLossHarvestingTemplateMSO.
            Default value is 0.0001 for template GainRealizationTemplateMSO.
        te_limit (float): (optional) The tracking error limit of the sleeve. Default value is None.
            Default value is 0.05 for template TaxAdvantagedModelTrackingTemplateMSO.
            For TaxAdvantagedModelTrackingTemplateMSO, the aggregate risk constraint's reference portfolio we set the first benchmark from the global benchmark list.
        benchmark_list (List): A list of benchmarks. Default value is Empty list.
        universe_list (List): A list of universes. Default value is Empty list.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        constraints (List): (optional) A list of constraints. Default value is None.
        prefix_nodes (List): (optional) A list of prefix nodes. Default value is None.
    """

    def __init__(
            self,
            id: str,
            target: float,
            portfolio,
            benchmark_list=[],
            universe_list=[],
            drift: float = 0.05,
            risk_aversion=None,
            te_limit: float = None,
            cash_lower_bound: float = 0.03,
            cash_upper_bound: float = 0.05,
            constraints: List = None,
            prefix_nodes: List = None
    ):
        self.id = id
        self.target = target
        self.drift = drift
        self.te_limit = te_limit
        self.benchmark_list = benchmark_list
        self.universe_list = universe_list
        self.portfolio = portfolio
        self.risk_aversion = risk_aversion
        self.cash_upper_bound = cash_upper_bound
        self.cash_lower_bound = cash_lower_bound
        self.constraints = constraints
        self.prefix_nodes = prefix_nodes


class GenericTaxTemplateMSO(Profile):
    """
    A template for a Multi-Sleeve Optimization (MSO) profile.

    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        benchmark_list (List): (optional) A list of benchmarks. Default is Empty list.
        universe_list (List): (optional) A list of universes. Default is Empty list.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is 0.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.

    """

    def __init__(
            self,
            sleeves_config: List[SleeveConfig],
            analysis_date,
            portfolio,
            universe_list=[],
            benchmark_list=[],
            te_limit: float = None,
            tax_multiplier=1,
            loss_benefit_multiplier=0,
            tax_unit: str = "dollar",
            cash_lower_bound: float = 0.03,
            cash_upper_bound: float = 0.05,
            tax_arbitrage: List[TaxArbitrage] = None,
            constraints: List = None,
            prefix_nodes: List = None,
            profile_name: str = None
    ):

        sleeve_ids = []
        bmk_sleeves = []
        univ_sleeves = []
        portfolio_sleeves = []

        for sleeve in sleeves_config:
            sleeve_ids.append(sleeve.id)
            bmk_sleeves += [BenchmarkPerAccount(account_id=sleeve.id, benchmark=sleeve.benchmark_list)]
            univ_sleeves += [UniversePerAccount(account_id=sleeve.id, universe=sleeve.universe_list)]
            portfolio_sleeves += [CurrentPortfolioPerAccount(account_id=sleeve.id, portfolio=sleeve.portfolio)]

        ref_univ = ReferenceUniverse(benchmark_multi_account=bmk_sleeves,
                                     universe_multi_account=univ_sleeves,
                                     current_portfolio_multi_account=portfolio_sleeves,
                                     universe=universe_list,
                                     benchmark=benchmark_list,
                                     portfolio=portfolio
                                     )

        bmk_ref_names = ref_univ.get_benchmark_ref_name()

        sleeve_optimization_nodes = []

        for sleeve in sleeves_config:
            sleeve_target = ConstraintFactory.SleeveBalanceConstraint(lower_bound=f'{sleeve.target - sleeve.drift}',
                                                                      upper_bound=f'{sleeve.target + sleeve.drift}')

            if sleeve.constraints:
                sleeve_constraints = sleeve.constraints + [sleeve_target]
            else:
                sleeve_constraints = [sleeve_target]

            if sleeve.te_limit:
                sleeve_te = ConstraintFactory.RiskConstraint(reference_portfolio=bmk_ref_names[
                    bmk_ref_names['account_id'] == sleeve.id]['benchmark_ref_name'].reset_index(drop=True)[0],
                                                             upper_bound=sleeve.te_limit)
                sleeve_constraints += [sleeve_te]

            sleeve_opt_settings = OptimizationSettings(
                cash_in_portfolio_upper_bound=sleeve.cash_upper_bound,
                cash_in_portfolio_lower_bound=sleeve.cash_lower_bound
            )
            minimize_active_risk = bool(sleeve.benchmark_list) if sleeve.benchmark_list is not None else False
            obj_function = GenericObjectiveFunction(
                sp_risk_aversion=sleeve.risk_aversion,
                cf_risk_aversion=sleeve.risk_aversion,
                minimize_active_risk=minimize_active_risk
            )
            optimization_node = FullSpecOptimizationNode(constraints=sleeve_constraints,
                                                         opt_settings=sleeve_opt_settings,
                                                         objective_function=obj_function)

            if sleeve.prefix_nodes:
                sleeve_node_list = sleeve.prefix_nodes + [optimization_node]
            else:
                sleeve_node_list = [optimization_node]
            sleeve_optimization_nodes += [
                NodeListPerAccount(account_id=sleeve.id, node_list=sleeve_node_list)]

        opt_settings = OptimizationSettings(
            transaction_type='allowAll',
            cash_in_portfolio_upper_bound=cash_upper_bound,
            cash_in_portfolio_lower_bound=cash_lower_bound,
            tax_optimization_setting=TaxOptimizationSetting(tax_unit=tax_unit, selling_order_rule="auto",
                                                            long_term_tax_rate=0.238, short_term_tax_rate=0.408,
                                                            wash_sale_rule="disallowed")
        )
        minimize_active_risk = bool(benchmark_list) if benchmark_list is not None else False
        obj_function = GenericObjectiveFunction(
            tax_term=tax_multiplier,
            loss_benefit_term=loss_benefit_multiplier,
            # sp_risk_aversion=risk_aversion,
            # cf_risk_aversion=risk_aversion,
            minimize_active_risk=minimize_active_risk
        )

        if constraints:
            shared_constraints = constraints
        else:
            shared_constraints = []

        if te_limit:
            shared_constraints = self._set_agg_risk_constraint(bmk_ref_names, shared_constraints, te_limit)

        shared_optimization_node = FullSpecOptimizationNode(opt_settings=opt_settings,
                                                            tax_arbitrages=tax_arbitrage,
                                                            objective_function=obj_function,
                                                            constraints=shared_constraints)

        if prefix_nodes:
            node_list = prefix_nodes + [shared_optimization_node]
        else:
            node_list = [shared_optimization_node]

        # if benchmark_list is None or len(benchmark_list) == 0:
        #     node_list = self._set_composite_benchmark_ref(bmk_ref_names, node_list, sleeves_config)

        shared_strategy = Strategy(
            ref_universe=ref_univ,
            node_list=node_list,
            node_list_multi_account=sleeve_optimization_nodes
        )

        sim_settings = SimulationSettings(analysis_date=analysis_date,
                                          account_ids=sleeve_ids,
                                          multi_account_style=MultiAccountStyleEnum.MULTI_SLEEVE)

        super().__init__(
            strategy=shared_strategy,
            simulation_settings=sim_settings,
            profile_name=profile_name
        )

    # def _set_composite_benchmark_ref(self, bmk_ref_names, node_list, sleeves_config):
    #     """
    #     Set the composite benchmark reference when benchmark_list is not provided.
    #     Construct the CompositeBenchmarkReference using BenchmarkWeightMappings for each sleeve.
    #
    #     """
    #     bmk_weigh_maps = []
    #     total_target = sum(sleeve.target for sleeve in sleeves_config)
    #     for sleeve in sleeves_config:
    #         bmk_name = bmk_ref_names[
    #             bmk_ref_names['account_id'] == sleeve.id]['benchmark_ref_name'].reset_index(drop=True)[0]
    #         bmk_weigh_map = BenchmarkWeightMappings(benchmark_ref=bmk_name, weight=sleeve.target / total_target)
    #         bmk_weigh_maps.append(bmk_weigh_map)
    #     composite_bmk_ref = RuleBasedNode.PromoteBenchmarkLayer.CompositeBenchmarkReference(
    #         composite_benchmark_ref=bmk_weigh_maps)
    #     node_list = [composite_bmk_ref] + node_list
    #     return node_list

    def _set_agg_risk_constraint(self, bmk_ref_names, shared_constraints, te_limit):
        """
        Set the aggregate risk constraint for all templates when te_limit is provided. Also, set the reference_portfolio as the first benchmark from the global benchmark list.
        """
        if not bmk_ref_names[bmk_ref_names['account_id'].isna()].empty:
            default_bmk = \
                bmk_ref_names[bmk_ref_names['account_id'].isna()]['benchmark_ref_name'].reset_index(drop=True)[
                    0]
            agg_constraint = ConstraintFactory.AggregateRiskConstraint(upper_bound=te_limit,
                                                                       reference_portfolio=default_bmk)
        else:
            agg_constraint = ConstraintFactory.AggregateRiskConstraint(upper_bound=te_limit)
        shared_constraints += [agg_constraint]
        return shared_constraints


class TaxAdvantagedModelTrackingTemplateMSO(GenericTaxTemplateMSO):
    """
    Template to maximize losses while managing risk relative to a benchmark with risk aversion and tracking error limit.


    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.05.
        benchmark_list (List): (optional) A list of benchmarks. Default value is None.
        universe_list (List): A list of universes.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is 1.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.
        **kwargs: Options to pass to GenericTaxTemplateMSO.

    Note: Default value of risk_aversion for each sleeve is 0.0001.
          Default value of te_limit for each sleeve if not set is 0.05.
          For TaxAdvantagedModelTrackingTemplateMSO, the aggregate risk constraint's reference portfolio we set the first benchmark from the global benchmark list.
    """

    def __init__(self, sleeves_config: List[SleeveConfig], tax_multiplier=1,
                 loss_benefit_multiplier=1, te_limit=0.05, **kwargs):
        # The default limit for the sleeves should be 5%.
        for sleeve in sleeves_config:
            if sleeve.te_limit is None:
                sleeve.te_limit = 0.05
            if sleeve.risk_aversion is None:
                sleeve.risk_aversion = 0.0001
        super().__init__(sleeves_config=sleeves_config, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, te_limit=te_limit, **kwargs)


class TaxNeutralTemplateMSO(GenericTaxTemplateMSO):
    """
    Template to stay tax neutral (gains similar to losses) while managing risk relative to a benchmark with risk aversion and tracking error limit.

    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        benchmark_list (List): (optional) A list of benchmarks. Default value is None.
        universe_list (List): A list of universes.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is 100.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is 0.0001.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.
        use_tax_constraint (bool): (optional) If True, tax arbitrage will be set to [TaxArbitrage(upper_bound=0, lower_bound=None)]. Default value is False.
        **kwargs: Options to pass to GenericTaxTemplateMSO.

    Note: Default value of risk_aversion for each sleeve is 1.

    """

    def __init__(self, sleeves_config: List[SleeveConfig], tax_multiplier=100,
                 loss_benefit_multiplier=0.0001, use_tax_constraint=False,
                 **kwargs):
        for sleeve in sleeves_config:
            if sleeve.risk_aversion is None:
                sleeve.risk_aversion = 1
        tax_arbitrage = [TaxArbitrage(upper_bound=0, lower_bound=None)] if use_tax_constraint else []
        super().__init__(sleeves_config=sleeves_config, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier,
                         tax_arbitrage=tax_arbitrage, **kwargs)


class GainBudgetingTemplateMSO(GenericTaxTemplateMSO):
    """
    Template to stay as close as possible to a benchmark while staying within a user-specified gain budget.

    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        gain_budget (float): maximum allowed gains in dollar value.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        benchmark_list (List): (optional) A list of benchmarks. Default value is None.
        universe_list (List): A list of universes.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is 1.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.
        **kwargs: Options to pass to GenericTaxTemplateMSO.

    Note: Default value of risk_aversion for each sleeve is 100.

    """

    def __init__(self, sleeves_config: List[SleeveConfig], gain_budget: float,
                 tax_multiplier: float = 1,
                 loss_benefit_multiplier: float = 1, tax_unit="dollar", **kwargs):
        for sleeve in sleeves_config:
            if sleeve.risk_aversion is None:
                sleeve.risk_aversion = 100
        tax_arbitrage = [TaxArbitrage(upper_bound=gain_budget)]
        super().__init__(sleeves_config=sleeves_config, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier,
                         tax_unit=tax_unit, tax_arbitrage=tax_arbitrage, **kwargs)


class MaxLossHarvestingTemplateMSO(GenericTaxTemplateMSO):
    """
    Template to maximize losses without aversion to risk beyond a user specified optional bound.

    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        benchmark_list (List): (optional) A list of benchmarks. Default value is None.
        universe_list (List): A list of universes.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is 1.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is 1.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.
        **kwargs: Options to pass to GenericTaxTemplateMSO.

    Note: Default value of risk_aversion for each sleeve is 0.0001.

    """

    def __init__(self, sleeves_config: List[SleeveConfig], tax_multiplier=1, loss_benefit_multiplier=1, **kwargs):
        for sleeve in sleeves_config:
            if sleeve.risk_aversion is None:
                sleeve.risk_aversion = 0.0001
        super().__init__(sleeves_config=sleeves_config, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, **kwargs)


class GainRealizationTemplateMSO(GenericTaxTemplateMSO):
    """
    Template to maximize gains while managing risk relative to a benchmark with risk aversion and tracking error limit.


    Args:
        sleeves_config (List[SleeveConfig]): A list of sleeve configurations.
        analysis_date (str): The date in YYYY-MM-DD format.
        te_limit (float): (optional) The global tracking error limit. Tracking error limit (predicted active risk) set in decimal terms. Default value is 0.005.
        benchmark_list (List): (optional) A list of benchmarks. Default value is None.
        universe_list (List): A list of universes.
        portfolio (CashPortfolio|TaxLotPortfolio|SimplePortfolio|ClientPortfolio): The portfolio.
        tax_multiplier (float): (optional) Tax penalty rate from gains in the objective function. Default value is -1.
        loss_benefit_multiplier (float): (optional) Tax benefit rate from losses in the objective function. Default value is -1.
        tax_unit (str): (optional) Tax unit, "dollar" or "decimal". Default value is "dollar".
        cash_upper_bound (float): (optional) The upper bound of cash. Default value is 0.05.
        cash_lower_bound (float): (optional) The lower bound of cash. Default value is 0.03.
        tax_arbitrage (List[TaxArbitrage]): (optional) Tax arbitrage ranges. Default value is None.
        constraints (List): (optional) A list of global constraints. Default value is None.
        prefix_nodes (List): (optional) A list of global prefix nodes. Default value is None.
        profile_name (str): (optional) The name of the profile request. Default value is None.
        **kwargs: Options to pass to GenericTaxTemplateMSO.

    Note: Default value of risk_aversion for each sleeve is 0.0001.

    """

    def __init__(self, sleeves_config: List[SleeveConfig], tax_multiplier=-1, loss_benefit_multiplier=-1, **kwargs):
        for sleeve in sleeves_config:
            if sleeve.risk_aversion is None:
                sleeve.risk_aversion = 0.0001
        super().__init__(sleeves_config=sleeves_config, tax_multiplier=tax_multiplier,
                         loss_benefit_multiplier=loss_benefit_multiplier, **kwargs)
