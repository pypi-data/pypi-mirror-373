from dataclasses import dataclass
from typing import List

from ...utils.dataclass_validations import BaseDataClassValidator
from .metrics import MetricsCalculation
from .mos_config import SimulationSettings, Strategy, SolutionSettings, CalculationContext, OptimizerMetrics
from .enums import CalculationTypeEnum
from ...utils.validations import TypeValidation

BDAY_METRICS = [
                ("LEVEL", "ABSOLUTE"),
                ("LEVEL", "ABSOLUTE_BMK"),
                ("PERFORMANCE", "ABSOLUTE"),
                ("PERFORMANCE", "ABSOLUTE_BMK"),
                ("PERFORMANCE", "RELATIVE"),
                ("SIMPLE", "NUM_CONS"),
                ("SIMPLE", "NUM_CONS_BMK"),
                ("TURNOVER", "STANDARD")
                ]

REBAL_METRICS = [("OPTIMIZER_RESULT", "TAX_BY_GROUP_FULL_PORTFOLIO"),
                 ("OPTIMIZER_RESULT", "PORTFOLIO_SUMMARY"),
                 ("OPTIMIZER_RESULT", "OPTIMIZATION_STATUS"),
                 ("OPTIMIZER_RESULT", "TRADE_LIST"),
                 ("OPTIMIZER_RESULT", "ASSET_DETAILS"),
                 ("OPTIMIZER_RESULT", "PROFILE_DIAGNOSTICS"),
                 ("OPTIMIZER_RESULT", "INPUT_DATA_ERRORS"),
                 ("OPTIMIZER_RESULT", "ASSET_REALIZED_GAIN"),
                 ("OPTIMIZER_RESULT", "POST_OPT_ROUNDLOTTING_ERRORS"),
                 ("INITIAL_PORTFOLIO", "ALL"),
                 ("INITIAL_PORTFOLIO", "UNREALIZED_GAIN_LOSS"),
                 ("INITIAL_PORTFOLIO", "RISK")
                 ]


@dataclass()
class SolutionSettingsPerAccount(BaseDataClassValidator):
    account_id: str
    sol_settings: SolutionSettings


class Profile:
    """
    A profile request definition (also referred to as profile) contains all information required to construct a portfolio using the defined strategy on a specific date or to run a backtest over a period of time.

    Args:
        strategy (Strategy): Strategy definition containing universe, optimization settings, etc.
        simulation_settings (SimulationSettings): Settings containing type of calculation and date range.
        metrics_calculation (MetricsCalculation): (optional) Metrics as per calculation type.
        save_tax_lots(bool): (optional) For rebalancing the taxlots are automatically saved but in case of backtesting if you want to save the taxlots you will need to set the parameter save_tax_lots as True. Default value is False.
        
        Default for REBALANCE:
            ``[("OPTIMIZER_RESULT", "TAX_BY_GROUP_FULL_PORTFOLIO"),
            ("OPTIMIZER_RESULT", "PORTFOLIO_SUMMARY"),
            ("OPTIMIZER_RESULT", "OPTIMIZATION_STATUS"),
            ("OPTIMIZER_RESULT", "TRADE_LIST"),
            ("OPTIMIZER_RESULT", "ASSET_DETAILS"),
            ("OPTIMIZER_RESULT", "PROFILE_DIAGNOSTICS"),
            ("OPTIMIZER_RESULT", "INPUT_DATA_ERRORS"),
            ("OPTIMIZER_RESULT", "ASSET_REALIZED_GAIN"),
            ("OPTIMIZER_RESULT", "POST_OPT_ROUNDLOTTING_ERRORS")]``
        
        Default for BACKCALCULATION :
            ``[("OPTIMIZER_RESULT", "TAX_BY_GROUP_FULL_PORTFOLIO"),
            ("OPTIMIZER_RESULT", "PORTFOLIO_SUMMARY"),
            ("OPTIMIZER_RESULT", "OPTIMIZATION_STATUS"),
            ("OPTIMIZER_RESULT", "TRADE_LIST"),
            ("OPTIMIZER_RESULT", "ASSET_DETAILS"),
            ("OPTIMIZER_RESULT", "PROFILE_DIAGNOSTICS"),
            ("OPTIMIZER_RESULT", "INPUT_DATA_ERRORS"),
            ("OPTIMIZER_RESULT", "ASSET_REALIZED_GAIN"),
            ("OPTIMIZER_RESULT", "POST_OPT_ROUNDLOTTING_ERRORS"),
            ("LEVEL", "ABSOLUTE"),
            ("LEVEL", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "ABSOLUTE"),
            ("PERFORMANCE", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "RELATIVE"),
            ("SIMPLE", "NUM_CONS"),
            ("SIMPLE", "NUM_CONS_BMK"),
            ("TURNOVER", "STANDARD")]``
        
        Default for Other calc types :
            ``[("LEVEL", "ABSOLUTE"),
            ("LEVEL", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "ABSOLUTE"),
            ("PERFORMANCE", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "RELATIVE"),
            ("SIMPLE", "NUM_CONS"),
            ("SIMPLE", "NUM_CONS_BMK"),
            ("TURNOVER", "STANDARD")]``

    Returns:
            body (dict): Dictionary representation of Profile.
    """

    strategy = TypeValidation('strategy', Strategy, mandatory=True)
    simulation_settings = TypeValidation('simulation_settings', SimulationSettings, mandatory=True)
    metrics_calculation = TypeValidation('metrics_calculation', MetricsCalculation)
    solution_settings = TypeValidation('solution_settings', SolutionSettings)
    calculation_context = TypeValidation('calculation_context', CalculationContext)

    def __init__(
            self,
            strategy,
            simulation_settings,
            metrics_calculation=None,
            solution_settings=None,
            solution_settings_multi_account: List[SolutionSettingsPerAccount] = None,
            profile_id=None,
            profile_name=None,
            calculation_context=None,
            save_tax_lots=False,

    ):
        self.strategy = strategy
        self.simulation_settings = simulation_settings
        self.solution_settings = solution_settings
        self.solution_settings_multi_account = solution_settings_multi_account
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.calculation_context = calculation_context
        self.save_tax_lots = save_tax_lots

        if metrics_calculation is None:
            metrics_calculation = MetricsCalculation()

        self.metrics_calculation = metrics_calculation

        # change metric list based on calc type
        if metrics_calculation is not None and isinstance(metrics_calculation, MetricsCalculation):
            if simulation_settings is not None and isinstance(simulation_settings, SimulationSettings):
                if metrics_calculation.metric_list is None:
                    if simulation_settings.calculation_type == CalculationTypeEnum.REBALANCE:
                        metrics_calculation.metric_list = REBAL_METRICS
                    elif simulation_settings.calculation_type in (
                            CalculationTypeEnum.BACKCALCULATION, CalculationTypeEnum.SIMULATION):
                        metrics_calculation.metric_list = REBAL_METRICS + BDAY_METRICS
                    else:
                        metrics_calculation.metric_list = BDAY_METRICS

    @property
    def body(self):
        """
         Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the profile.
        """
        strategy_input = {
            "values": [self.strategy.body],
            "objType": "StrategyDefinitions",
        }

        debug_options = None
        if self.save_tax_lots:
            debug_options = {
                "flags": [
                    "save-tax-lots"
                ]
            }

        profile = {
            # "id": self.profile_id,
            # "rebasingEnabled": None,
            "debugOptions": debug_options,
            "requestInfo": None,
            "calculationContext": self.calculation_context.body if self.calculation_context is not None else None,
            "strategyInput": strategy_input,
            "simulationSettings": self.simulation_settings.body,
            "solutionSettings": self.solution_settings.body if self.solution_settings is not None else None,
            "solutionSettingsPerAccount": {a.account_id: a.sol_settings.body for a in
                self.solution_settings_multi_account} if self.solution_settings_multi_account is not None else None,

            "metricsCalculation": self.metrics_calculation.body if self.metrics_calculation is not None else None,
        }

        if self.profile_name:
            profile["requestInfo"] = {"name": self.profile_name}

        return profile

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"
