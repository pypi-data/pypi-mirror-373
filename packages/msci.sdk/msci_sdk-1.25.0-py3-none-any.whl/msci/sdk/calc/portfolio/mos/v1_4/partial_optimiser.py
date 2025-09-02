from dataclasses import dataclass
from typing import Optional, Union

from .full_optimizer_node import DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions
from .enums import ExposureGroupBy
from ...utils.dataclass_validations import BaseDataClassValidator


@dataclass
class RiskAversion(BaseDataClassValidator):
    """
    Set the risk aversion for common factor risk and specific risk.

    Args:
        riskaversion_specific (int, float): Optional. Risk aversion for specific risk. Default value is 0.0075.
        riskaversion_commonfactor (int, float): Optional. Risk aversion for common factor risk. Default value is 0.0075.

    Returns:
            body (dict): Dictionary representation of RiskAversion.

    """

    riskaversion_specific: Optional[Union[float, int]] = 0.0075
    riskaversion_commonfactor: Optional[Union[float, int]] = 0.0075


@dataclass
class BenchmarkWeightMappings(BaseDataClassValidator):
    """
    Benchmark reference and its weight.

    Args:
        benchmark_ref (string): Reference benchmark.
        weight (int, float): Benchmark weight.

    Returns:
            body (dict): Dictionary representation of BenchmarkWeightMappings.
    """

    benchmark_ref: str
    weight: Union[float, int]

    @property
    def body(self):
        """
        Dictionary representation of BenchmarkWeightMappings node.
        
        Returns:
            dict: Dictionary representation of the node.
        """
        return {
            "benchmarkRef": self.benchmark_ref,
            "weight": self.weight
        }


class PartialOptimizationNode:
    """
    Represents all partial optimization nodes.
    """

    @dataclass
    class MaximizeTaxAlpha(BaseDataClassValidator):
        """Represents maximize tax alpha objective node.


        Args:
            tax_term (int, float): Tax term or alpha.
            short_term_tax_rate (int, float): Short term tax rate.
            long_term_tax_rate (int, float): Long tern tax rate.
            loss_benefit_term (int, float) : (optional) Loss benefit term. Default value is None.
            active (bool): (optional) If active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of MaximizeTaxAlpha objective.
        """

        tax_term: Union[float, int]
        short_term_tax_rate: Union[float, int]
        long_term_tax_rate: Union[float, int]
        active: Optional[bool] = True
        loss_benefit_term: Optional[Union[float, int]] = None

        @property
        def body(self):
            """
            Dictionary representation of MaximizeTaxAlpha objective node.

            Returns:
                dict: Dictionary representation of the node.
            """
            return {
                    "taxTerm": self.tax_term,
                    "objType": "MaximizeTaxAlpha",
                    "shortTermTaxRate": self.short_term_tax_rate,
                    "longTermTaxRate": self.long_term_tax_rate,
                    "active": self.active,
                    "lossBenefitTerm": self.loss_benefit_term,
            }

    @dataclass
    class MinimizeTrackingError(BaseDataClassValidator):
        """Represents minimize tracking error objective node.

        Args:
            riskaversion_specific (float, int): (optional) Risk aversion for specific risk. Default value is 0.0075.
            riskaversion_commonfactor (float, int): (optional). Risk aversion for common factor risk. Default value is 0.0075.
            risk model (str): Risk model to be used for optimization. Default is GEMLTL supported for equity assets.
            minimize_active_risk (bool):  If set “True” the objective would be to minimize Portfolio risk
                                and if set to “False” the objective would be to minimize ActiveRisk of the optimized Portfolio. Default value is True.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of MinimizeTrackingError objective node.
        """

        riskaversion_specific: Optional[Union[float, int]] = 0.0075
        riskaversion_commonfactor: Optional[Union[float, int]] = 0.0075
        risk_model: Optional[str] = "GEMLTL"
        minimize_active_risk: Optional[bool] = True
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of MinimizeTrackingError objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "MinimizeTrackingError",
                    "riskAversion": {
                        "specific": self.riskaversion_specific,
                        "commonFactor": self.riskaversion_commonfactor
                    },
                    "minimizeActiveRisk": self.minimize_active_risk,
                    "riskModel": self.risk_model,
                    "active": self.active
            }

    @dataclass
    class ConstrainAssetsHeld(BaseDataClassValidator):
        """Add a constraint on how many assets should be held in the resulting optimized portfolio.

        Args:
            min_assets (float, int): Minimum number of assets to be held in the portfolio.
            max_assets (float, int): Maximum number of assets to be held in the portfolio.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of ConstrainAssetsHeld objective node.
        """

        min_assets: Union[float, int]
        max_assets: Union[float, int]
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of ConstrainAssetsHeld objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "ConstrainAssetsHeld",
                    "minNumberAssets": self.min_assets,
                    "maxNumberAssets": self.max_assets,
                    "active": self.active
            }


    @dataclass
    class LimitActiveWeight(BaseDataClassValidator):
        """Determine the weights range as a percentage of benchmark in the optimization.

        Args:
            active_weight (int, float): Active weight target.
            benchmark (str): Benchmark used in the strategy.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitActiveWeight objective node.
        """

        active_weight: Union[float, int]
        benchmark: str
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitActiveWeight objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitActiveWeight",
                    "activeWeight": self.active_weight,
                    "benchmark": self.benchmark,
                    "active": self.active
            }


    @dataclass
    class LimitCarbonEmission(BaseDataClassValidator):
        """Limit the carbon emission intensity.

        Args:
            carbon_intensity_target (str): Target carbon emission intensity value.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitCarbonEmission objective node.
        """

        carbon_intensity_target: str
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitCarbonEmission objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitCarbonEmission",
                    "carbonIntensityTarget": self.carbon_intensity_target,
                    "active": self.active
            }


    @dataclass
    class LimitActiveExposure(BaseDataClassValidator):
        """Limit the active exposure after grouping by sector or industry or country, relative to the given benchmark.

        Args:
            exposure_groupby (ExposureGroupBy): Grouping definition; allowed values are SECTOR, INDUSTRY or COUNTRY.
            active_weight (float): Active weight target.
            benchmark (str): (optional) Benchmark used in the strategy. Default value is None.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitActiveExposure objective node.
        """

        exposure_groupby: ExposureGroupBy
        active_weight: Union[float, int]
        benchmark: Optional[str] = None
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitActiveExposure objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitActiveExposure",
                    "groupBy": self.exposure_groupby.value,
                    "activeWeight": self.active_weight,
                    "benchmark": self.benchmark,
                    "active": self.active
                }


    @dataclass
    class LimitClimateValueAtRisk(BaseDataClassValidator):
        """Limit the climate-value-at-risk to the given target value in the composed optimization.

        Args:
            target_climate_at_risk (str): Target climate-value-at-risk value.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitClimateValueAtRisk objective node.
        """

        target_climate_at_risk: str
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitClimateValueAtRisk objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitClimateValueAtRisk",
                    "targetClimateAtRisk": self.target_climate_at_risk,
                    "active": self.active
            }

    @dataclass
    class LimitTurnover(BaseDataClassValidator):
        """Limit the amount of turnover that the composed optimization will suggest to the given amount.

        Args:
            turnover (int, float): Specify the upper bound of turnover you want the optimizer to observe in generating portfolios.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitTurnover objective node.
        """

        turnover: Union[float, int]
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitTurnover objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitTurnover",
                    "turnover": self.turnover,
                    "active": self.active
            }

    @dataclass
    class LimitTransactionCost(BaseDataClassValidator):
        """Specify the maximum cost of achieving the optimal portfolio.

        Args:
            max_transaction_cost (int, float): Specify the maximum cost of achieving the optimal portfolio.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): Dictionary representation of LimitTransactionCost objective node.
        """

        max_transaction_cost: Union[float, int]
        active: Optional[bool] = True

        @property
        def body(self):
            """
            Dictionary representation of LimitTransactionCost objective node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "LimitTransactionCost",
                    "maxTransactionCost": self.max_transaction_cost,
                    "active": self.active
            }

    @dataclass
    class DoNotTrade(BaseDataClassValidator):
        """Restricts the optimizer’s possible action for the assets/portfolios specified to buy only.

        Args:
            do_not_trade_criteria (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): Do not trade criteria.

        Returns:
            body (dict): Dictionary representation of DoNotTrade objective node.
        """

        do_not_trade_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]

        @property
        def body(self):
            """
            Dictionary representation of DoNotTrade node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "DoNotTrade",
                    "doNotTradeCriteria": self.do_not_trade_criteria.body,
            }

    @dataclass
    class DoNotHold(BaseDataClassValidator):
        """Restricts the optimizer’s possible action for the assets/portfolios specified to buy only.

        Args:
            do_not_hold_criteria (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): Do not hold criteria.

        Returns:
            body (dict): Dictionary representation of DoNotHold objective node.
        """

        do_not_hold_criteria: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]

        @property
        def body(self):
            """
            Dictionary representation of DoNotHold node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "DoNotHold",
                    "doNotHoldCriteria": self.do_not_hold_criteria.body,
            }

    @dataclass
    class NoSell(BaseDataClassValidator):
        """Composable optimizer node. Restricts the optimizers possible action for the assets specified to buy only.

        Args:
            no_sell (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): Do sell.

        Returns:
            body (dict): Dictionary representation of NoSell objective node.
        """

        no_sell: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]

        @property
        def body(self):
            """
            Dictionary representation of NoSell node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "NoSell",
                    "noSell": self.no_sell.body,
            }

    @dataclass
    class NoBuy(BaseDataClassValidator):
        """Composable optimizer node. Restricts the optimizers possible action for the assets specified to sell only.

        Args:
            no_buy (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): Do buy.

        Returns:
            body (dict): Dictionary representation of NoBuy objective node.
        """

        no_buy: Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]

        @property
        def body(self):
            """
            Dictionary representation of NoBuy node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "objType": "NoBuy",
                    "noBuy": self.no_buy.body,
            }
