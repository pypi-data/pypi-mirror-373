from dataclasses import dataclass, field
from typing import Optional, Union, List
from .enums import TaxArbitrageGainEnum
from ...utils.dataclass_validations import BaseDataClassValidator


@dataclass
class CashFlowOptSetting:
    """
    Optimizer setting for cashflows.

    Args:
        amount (int): (optional) Amount of cashflow. Default value is None.
        cash_type (str): (optional) Cashflow type; accepted values are PERCENT or AMOUNT. Default value is PERCENT.

    Returns:
            body (dict): Dictionary representation of CashFlowOptSetting.
    """

    amount: Optional[int] = None
    cash_type: Optional[str] = "PERCENT"

    @property
    def body(self):
        """
        Dictionary representation of CashFlowOptSetting.

        Returns:
            dict: Dictionary representation of the node.
        """
        cash_opt_body = {
            "amount": self.amount,
            "type": self.cash_type
        }
        return cash_opt_body


@dataclass
class TaxOptimizationSetting(BaseDataClassValidator):
    """
    Settings for tax aware optimization.

    Args:
        tax_unit (str): (optional) Unit of tax-related parameters. Allowed values are 'dollar'(for absolute amounts) and 'decimal' (for amounts relative to the base). Default value is 'dollar'
        enable_two_rate (bool): (optional) When set to “true”, taxable tax lots are classified into either long-term or short-term and are taxed accordingly at the same two rates. Default value is True. In case of Canada the value would be False, any other value would be ignored.
        short_term_period (int): (optional) Number of days for a period to be termed short term. Default value is 365. This parameter would be ignored when tax_code is Canada and would not be set.
        long_term_tax_rate (int, float): (optional) Long term tax rate applied to assets.
        short_term_tax_rate (int, float): (optional) Short term tax rate applied to assets.
        wash_sale_rule (str):  (optional) Actions to take for washlots. Allowed values are:
        
                            • ignored – no action taken even if a wash sale occurred
                            • disallowed - (default) wash sales are prevented from happening
                            
        wash_sale_period (int): (optional) Number of days of wash sale period. Default value is 30.
        selling_order_rule (str): (optional) The order in which to sell from tax lots. Default value is auto. Allowed values are:
        
                            • auto - order in which tax lots are traded for each asset is automatically determined based on the marginal contribution of each tax lot to the objective
                            • hifo - tax lots with fewer gains or more losses are traded before those with more gains and fewer losses
                            • lifo - tax lots bought later are traded before those bought earlier
                            • fifo -tax lots bought earlier are traded before those bought later

        wash_sale_group_attribute (str): (optional) Attribute used to identified substantially identical assets for wash sale purposes. Not supported in multiple account optimization.
        enable_cross_netting_gain_loss (bool): (optional) If omitted defaults to false.
        tax_code: (str): (optional) Tax code for a particular country. Default value is 'US'.
        inclusion_rate (float): (optional) Inclusion rate for tax code Canada. Only effective, if taxCode = Canada. Default value is 0.5.
        short_inclusion_rate (int, float): (optional) Short inclusion rate for tax code Canada. Only effective, if taxCode = Canada. Default value is 0.5.
                            

    Returns:
            body (dict): Dictionary representation of TaxOptimizationSetting.

    """

    tax_unit: str = "dollar"
    enable_two_rate: bool = True
    short_term_period: int = 365
    long_term_tax_rate: Optional[Union[float, int]] = None
    short_term_tax_rate: Optional[Union[float, int]] = None
    wash_sale_rule: str = "disallowed"
    wash_sale_period: int = 30
    selling_order_rule: str = "auto"
    wash_sale_group_attribute: Optional[str] = None
    enable_cross_netting_gain_loss: Optional[bool] = False
    tax_code: Optional[str] = 'US'
    inclusion_rate: Optional[Union[float, int]] = 0.5
    short_inclusion_rate: Optional[Union[float, int]] = 0.5

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.
        Returns:
            dict: Dictionary representation of the node.
        """
        tax_opt_setting_body = {
            "taxUnit": self.tax_unit,
            "enableTwoRate": self.enable_two_rate,
            "longTermTaxRate": self.long_term_tax_rate,
            "shortTermTaxRate": self.short_term_tax_rate,
            "washSaleRule": self.wash_sale_rule,
            "washSalePeriod": self.wash_sale_period,
            "sellingOrderRule": self.selling_order_rule,
            "washSaleGroupAttribute": self.wash_sale_group_attribute,
            "enableCrossNettingGainLoss": self.enable_cross_netting_gain_loss,
            "taxCode": self.tax_code
        }
        if self.tax_code != 'Canada':
            tax_opt_setting_body["shortTermPeriod"] = self.short_term_period

        if self.tax_code == 'Canada':
            tax_opt_setting_body["enableTwoRate"] = False
            tax_opt_setting_body["inclusionRate"] = self.inclusion_rate
            tax_opt_setting_body['shortInclusionRate'] = self.short_inclusion_rate
        return tax_opt_setting_body


@dataclass
class PostRoundLotSettings(BaseDataClassValidator):
    """
    Setting for post-optimization round lotting

    Args:
        mode (str): POST_OPT_ROUNDLOTTING_MODE - Sets the constraint handling mode of post-optimization roundlotting. If not set or set to 0 (default mode), it allows violating the cash bounds if it is required to keep the cash flow unchanged. Set to 1, all asset bounds must be satisfied in the roundlotted portfolio, but the cash flow might change. If set to 2, then all asset bounds must be satisfied and the cash flow is not allowed to change.
        lot_size (str): User can provide either 1 for unit lot size for all assets or a userdata point for asset level lot size (default is 1, if userdata is not provided for an asset).
        allow_close_out (str): (Optional) POST_OPT_ROUNDLOTTING_ALLOW_CLOSEOUT - This can have 3 values: 0: Trades can only be made as whole roundlots. 1: Closing out is allowed, which means a trade might not be a whole roundlot as long as the asset weight is 0 in the optimal portfolio i.e. closed out 2: Enforces close out. Whenever a trade with a whole roundlot would make the remaining weight of the asset be less than a roundlot (in absolute value), closing out would be forced instead if not given, post optimization roundlotting closeouts are not allowed.
        sleeve_level_roundlotting (bool): (Optional) This option is only effective in Multi Sleeve Optimization - allows to decide if the sleeve level or the aggregated account level trades should be roundlotted.

    Returns:
            body (dict): Dictionary representation of PostRoundLotSettings.
    """
    mode: str = "0"
    lot_size: str = "1"
    allow_close_out: Optional[str] = None
    sleeve_level_roundlotting: Optional[bool] = False

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.
        Returns:
            dict: Dictionary representation of the node.
        """
        return {
            "mode": self.mode,
            "lotSize": self.lot_size,
            "allowCloseOut": self.allow_close_out,
            "sleeveLevelRoundlotting": self.sleeve_level_roundlotting
        }

@dataclass
class OptimizationSettings(BaseDataClassValidator):
    """
    General settings for optimization.

    Args:
        risk_model (str): (optional) Risk model to be used for optimization. Default value is GEMLTL.
        solver (int): (optional) Default value is None
        tax_approach (int): Tax approach
        paring_approach (int): (optional) Asset/trade paring information of the optimal portfolio. Default value is None.
        transaction_type (str): (optional) Transaction type. Default value is None. Allowed Id types are:
            ``["allowAll",
            "buyNone",
            "sellNone",
            "shortNone",
            "buyFromUniv",
            "sellNoneBuyFromUniv",
            "buyShortFromUniv",
            "disallowBuyShort",
            "disallowSellCover",
            "buyShortUnivNoSellCover",
            "buyNoneSellFromUniv",
            "univOnly"]``
        cash_in_portfolio_lower_bound (int, float): (optional) Lower bound to set up cashflow in relation to the portfolio base value.
        cash_in_portfolio_upper_bound (int, float): (optional) Upper bound to set up cashflow in relation to the portfolio base value.
        cash_flow_settings (CashFlowOptSetting): (optional) Settings for the cashflow.
        tax_optimization_setting (TaxOptimizationSetting): (optional) Settings for tax aware optimization – this is optional but required if tax aware optimization.
        post_round_lot_settings (PostRoundLotSettings): (optional) Setting for post-optimization round lotting.
        time_out (int): (optional) Controls optimization process timeout (in seconds). Default value is 570.
        cash_bound_unit (str): (optional) Allows users to set the unit of cash asset bound constraint. The default value is unitDecimal which sets bounds relative to initial portfolio base value. For MSO cases unitScaled is also available, allowing users to set a bound relative to optimal sleeve market value. Allowed values are unitDecimal, unitScaled.


    Returns:
            body (dict): Dictionary representation of OptimizationSettings.
    """

    risk_model: str = "GEMLTL"
    solver: Optional[int] = None
    tax_approach: Optional[int] = None
    paring_approach: Optional[int] = None
    transaction_type: Optional[str] = None
    cash_in_portfolio_lower_bound: Optional[Union[int, float]] = None
    cash_in_portfolio_upper_bound: Optional[Union[int, float]] = None
    disable_cash_bound: Optional[bool] = False
    cash_flow_settings: Optional[CashFlowOptSetting] = None
    tax_optimization_setting: Optional[TaxOptimizationSetting] = None
    post_round_lot_settings: Optional[PostRoundLotSettings] = None
    time_out: Optional[int] = 570
    cash_bound_unit: Optional[str] = None

    def __post_init__(self):
        allowed_values = {"allowAll", "buyNone", "sellNone", "shortNone", "buyFromUniv",
                          "sellNoneBuyFromUniv", "buyShortFromUniv", "disallowBuyShort",
                          "disallowSellCover", "buyShortUnivNoSellCover", "buyNoneSellFromUniv", "univOnly"}
        if self.transaction_type is not None and self.transaction_type not in allowed_values:
            raise ValueError(f"trade_type must be one of {allowed_values}")

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the node.
        """
        opt_setting_body = {
            "riskModel": self.risk_model,
            "solver": self.solver,
            "taxApproach": self.tax_approach,
            "paringApproach": self.paring_approach,
            "transactionType": self.transaction_type,
            "cashInPortfolioLowerBound": self.cash_in_portfolio_lower_bound,
            "cashInPortfolioUpperBound": self.cash_in_portfolio_upper_bound,
            "disableCashBound": self.disable_cash_bound,
            "timeOut": self.time_out,
            "cashBoundUnit": self.cash_bound_unit
        }
        if self.cash_flow_settings is not None:
            opt_setting_body.update({"cashFlowSettings": self.cash_flow_settings.body})
        if self.tax_optimization_setting is not None:
            opt_setting_body.update({"taxOptimizationSettings": self.tax_optimization_setting.body})
        if self.post_round_lot_settings is not None:
            opt_setting_body.update({"postRoundLotSettings": self.post_round_lot_settings.body})

        return opt_setting_body


@dataclass
class RiskTargetOptimization(BaseDataClassValidator):
    """
        The function for the optimization.

        Args:
            risk_target (int): Value of risk target in Risk Target Optimization
            check_efficiency (boolean):(optional) If True, the optimization returns only portfolios on the efficient frontier; otherwise, it returns the maximum-return portfolio with the targeted risk, if feasible. Default value is True.


        Returns:
                body (dict): Dictionary representation of GenericObjectiveFunction.
        """
    risk_target: Union[int, float]
    check_efficiency: Optional[bool] = True

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the node.
        """
        body = {
            "riskTarget": self.risk_target,
            "checkEfficiency": self.check_efficiency
        }
        return body

@dataclass
class RatioUtilityObjectiveFunction(BaseDataClassValidator):
    """
        The ratio based objective function for the optimization.

        Args:
            ratio_type (str): it determines the type of the ratio utility during Sharpe- or Information ratio utility optimization. Allowed values are sharpeRatio, informationRatio
            risk_free_rate (Union[int, float]): (optional) the value of risk-free rate that is used for calculating the Sharpe-ratio utility


        Returns:
                body (dict): Dictionary representation of RatioUtilityObjectiveFunction.
        """
    ratio_type: str
    risk_free_rate: Optional[Union[int, float]] = None

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the node.
        """
        body = {
            "ratioType": self.ratio_type,
            "riskFreeRate": self.risk_free_rate
        }
        return body

@dataclass
class GenericObjectiveFunction(BaseDataClassValidator):
    """
    Generic objective function for the optimization.

    Args:
        tax_term (int, float):(optional) Multiplier for tax based optimization. Default value is None.
        loss_benefit_term (int, float):(optional) Default value is None.
        sp_risk_aversion (int, float):(optional) Risk aversion for specific risk. Default value is 0.0075.
        cf_risk_aversion (int, float):(optional) Risk aversion for common factor risk. Default value is 0.0075.
        agg_sp_risk_aversion (int, float): (optional) Aggregate risk aversion for specific risk. Default value is None. Only supported for default account in multiaccount profile.
        agg_cf_risk_aversion (int, float): (optional) Aggregate risk aversion for common factor risk. Default value is None. Only supported for default account in multiaccount profile
        alpha_attribute (str): (optional) Default value is None.
        alpha_term (int, float): (optional) Default value is None.
        transaction_cost_term (str):(optional) Default value is None.
        minimize_active_risk (bool):(optional) Flag to minimize active risk . Default value is True.
        t_cost_attribute (str): (optional) Datapoint name that contains the transaction cost amount.Default value is None.
        risk_target_optimization (RiskTargetOptimization): (optional) The objective function for the optimization.
        ratio_utility_objective_function (RatioUtilityObjectiveFunction): (optional) The ratio based objective function for the optimization.
        short_rebate_term (int, float): (Optional) Optional multiplier of short rebate term. Will be defaulted to 1, if shortRebateAttribute is added to the profile but the shortRebateTerm is not added.
        short_rebate_attribute (str): (optional) Optional specification of short rebates/costs. This usually refers to userdata.

    Returns:
            body (dict): Dictionary representation of GenericObjectiveFunction.
    """
    tax_term: Optional[Union[float, int]] = None
    loss_benefit_term: Optional[Union[float, int]] = None
    sp_risk_aversion: Optional[Union[float, int]] = None
    cf_risk_aversion: Optional[Union[float, int]] = None
    agg_sp_risk_aversion: Optional[Union[float, int]] = None
    agg_cf_risk_aversion: Optional[Union[float, int]] = None
    alpha_attribute: Optional[str] = None
    alpha_term: Optional[Union[int, float]] = None
    transaction_cost_term: Optional[str] = None
    minimize_active_risk: Optional[bool] = None
    t_cost_attribute: Optional[str] = None
    risk_target_optimization: Optional[RiskTargetOptimization] = None
    ratio_utility_objective_function: Optional[RatioUtilityObjectiveFunction] = None
    short_rebate_term: Optional[Union[float, int]] = None
    short_rebate_attribute: Optional[str] = None

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the node.
        """

        # sp_risk_aversion_condtn = self.sp_risk_aversion if self.sp_risk_aversion is not None else (0.0075 if self.risk_target_optimization is None else None)
        # cf_risk_aversion_condtn = self.cf_risk_aversion if self.cf_risk_aversion is not None else (0.0075 if self.risk_target_optimization is None else None)

        gen_obj_body = {
            "info": "GenericObjectiveFunction",
            "taxTerm": self.tax_term,
            "lossBenefitTerm": self.loss_benefit_term,
            "alphaAttribute": self.alpha_attribute,
            # "riskAversion": {"specific": self.sp_risk_aversion, "commonFactor": self.cf_risk_aversion},
            "alphaTerm": self.alpha_term,
            "transactionCostTerm": self.transaction_cost_term,
            "minimizeActiveRisk": self.minimize_active_risk,
            "tCostAttribute": self.t_cost_attribute,
            "riskTargetOptimization": self.risk_target_optimization.body if self.risk_target_optimization else None,
            "ratioUtilityOptimization": self.ratio_utility_objective_function.body if self.ratio_utility_objective_function else None,
            "shortRebateTerm": self.short_rebate_term,
            "shortRebateAttribute": self.short_rebate_attribute
        }
        if self.agg_sp_risk_aversion is None and self.agg_cf_risk_aversion is None:
            sp_risk_aversion_condtn = self.sp_risk_aversion if self.sp_risk_aversion is not None else (
                0.0075 if self.risk_target_optimization is None else None)
            cf_risk_aversion_condtn = self.cf_risk_aversion if self.cf_risk_aversion is not None else (
                0.0075 if self.risk_target_optimization is None else None)

            if sp_risk_aversion_condtn is not None or cf_risk_aversion_condtn is not None:
                gen_obj_body.update({"riskAversion": {"specific": sp_risk_aversion_condtn, "commonFactor": cf_risk_aversion_condtn}})

        if self.agg_sp_risk_aversion is not None or self.agg_cf_risk_aversion is not None:
            gen_obj_body.update({"aggregateRiskAversion": {"specific": self.agg_sp_risk_aversion, "commonFactor": self.agg_cf_risk_aversion}})

        return gen_obj_body


@dataclass
class TaxArbitrage(BaseDataClassValidator):
    """
    Place bounds on the net realized capital gain or loss at the portfolio level.

    Args:
        tax_category (str): (optional) Allowed values are longTerm, shortTerm, taxFree, total. Default value is 'total'.
        gain_type (str): (optional) Allowed values are capitalGain, capitalLoss, capitalNet. Default value 'capitalNet'
        upper_bound (float): (optional) Maximum allowed value for the selected gain/loss. Default value is None.
        lower_bound (float): (optional) Minimum allowed value for the selected gain/loss. Default value is None.
        is_soft (bool): (optional) Specify if the constraint is soft. Soft constraints can be relaxed if the problem is otherwise infeasible. Default value is False.

    Returns:
            body (dict): Dictionary representation of TaxArbitrage.
    """

    tax_category: Optional[str] = "total"
    gain_type: TaxArbitrageGainEnum = TaxArbitrageGainEnum.CAPITAL_NET
    upper_bound: Optional[Union[float, int]] = None
    lower_bound: Optional[Union[float, int]] = None
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Method to generate request body as dictionary based on the parameters configured.

        Returns:
            dict: Dictionary representation of the node.
        """
        __body = {
            "taxCategory": self.tax_category,
            "gainType": self.gain_type.value,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft
        }
        return __body


@dataclass
class CustomAttribute(BaseDataClassValidator):
    """
    A custom attribute definition for simple identification used in DoNotTradeList

    Args:
        name (str): The unique name of the attribute, duplicates will be dropped with a warning.
        value (str): The value of the attribute.
        description (str): (optional) Description of attribute. Default value is None.
        type (str): (optional) The type for the attribute value. Defaults to a type of attribute's value. Default value is None.

    Returns:
            body (dict): Dictionary representation of CustomAttribute.
    """

    name: str
    value: str
    description: Optional[str] = None
    type: Optional[str] = None

    @property
    def body(self):
        """The dictionary structure for CustomAttribute.

        Returns:
            dict: Dictionary representation of CustomAttribute.
        """

        _body = {
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "type": self.type
        }
        return _body


@dataclass
class DoNotTradeExpression(BaseDataClassValidator):
    """
    Restricts the optimizer’s possible action for the assets/portfolios specified to buy only.

    Args:
        expression (str): expression.

    Returns:
            body (dict): Dictionary representation of DoNotTradeExpression.
    """

    expression: str

    @property
    def body(self):
        """The dictionary structure for DoNotTradeExpression.

        Returns:
            dict: Dictionary representation of the node.
        """

        _body = {
            "objType": "DoNotTradeExpression",
            "expression": self.expression
        }
        return _body


@dataclass
class DoNotTradeList(BaseDataClassValidator):
    """
    References a portfolio to define the assets not to trade over time.

    Args:
        portfolio_id (str): Identifier assigned to the portfolio..
        source (str): (optional) Which portfolio store to resolve the portfolioId from. Default value is 'OMPS'.
        name (str): (optional) Name. Default value is None.
        description (str): (optional) Description. Default value is None.
        snapshot_type (str): (optional) Allowed snapshots; can be OPEN or CLOSE. Default is 'CLOSE'.
        owner (str): (optional) Owner. Default value is None.
        additional_attributes (List[CustomAttribute]): (optional) Additional attributes definition. Default value is None.

    Returns:
            body (dict): Dictionary representation of DoNotTradeList.
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
        """The dictionary structure for DoNotTradeList.

        Returns:
            dict: Dictionary representation of the node.
        """

        _body = {
            "objType": "DoNotTradeList",
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
        }
        return _body


@dataclass
class SimpleIdentification(BaseDataClassValidator):
    """
    References a portfolio to define the assets not to trade over time.

    Args:
        portfolio_id (str): Identifier assigned to the portfolio.
        source (str): (optional) Which portfolio store to resolve the portfolioId from. Default value is 'OMPS'.
        name (str): (optional) Name. Default value is None.
        description (str): (optional) Description. Default value is None.
        snapshot_type (str): (optional) Allowed snapshots; can be OPEN or CLOSE. Default is 'CLOSE'.
        owner (str): (optional) Owner. Default value is None.
        additional_attributes (List[CustomAttribute]): (optional) Additional attributes definition. Default value is None.

    Returns:
            body (dict): Dictionary representation of SimpleIdentification.
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
        """The dictionary structure for SimpleIdentification.

        Returns:
            dict: Dictionary representation of the node.
        """

        _body = {
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
        return _body


@dataclass
class DoNotTradeListsAndExpressions(BaseDataClassValidator):
    """
    Specifies a list of expressions and portfolio

    Args:
        identifications (list): (optional) List of SimpleIdentification objects. Default value is None.
        expressions (list): (optional) List of str objects. Default value is None.

    Returns:
        body (dict): Dictionary representation of DoNotTradeListsAndExpressions.
    """

    identifications: Optional[List[SimpleIdentification]] = None
    expressions: Optional[List[str]] = None

    @property
    def body(self):
        """The dictionary structure for DoNotTradeListsAndExpressions.

        Returns:
            dict: Dictionary representation of the node.
        """

        _body = {
            "objType": "DoNotTradeListsAndExpressions",
            "identifications": [a.body for a in
                                self.identifications] if self.identifications is not None else None,
            "expressions": [a for a in
                            self.expressions] if self.expressions is not None else None
        }
        return _body


@dataclass
class FullSpecOptimizationNode(BaseDataClassValidator):
    """
    Used for tax optimization and other optimization problems where you are not composing the optimization problem by layers, but rather defining all at once.

    Args:
        opt_settings (OptimizationSettings): (optional) Optimizer setting parameter of type OptimizationSettings.
        objective_function (GenericObjectiveFunction): (optional) Optimizer objectives.
        constraints (list): (optional) List of constraints. Default value is None.
        tax_arbitrages (list): (optional) List of tax arbitrage of type TaxArbitrage. Default value is None.
        do_not_trade_criteria (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): (optional) Do not trade criteria. Default value is None.
        do_not_hold_criteria (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): (optional) Do not hold criteria. Default value is None.
        no_sell (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): (optional) No sell. Default value is None.
        no_buy (DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions): (optional) No buy. Default value is None.

    Returns:
            body (dict): Dictionary representation of FullSpecOptimizationNode.
    """

    opt_settings: Optional[OptimizationSettings] = field(default_factory=OptimizationSettings)
    objective_function: Optional[GenericObjectiveFunction] = field(default_factory=GenericObjectiveFunction)
    constraints: Optional[list] = None
    tax_arbitrages: Optional[list] = None

    do_not_trade_criteria: Optional[Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]] = None
    do_not_hold_criteria: Optional[Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]] = None
    no_sell: Optional[Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]] = None
    no_buy: Optional[Union[DoNotTradeExpression, DoNotTradeList, DoNotTradeListsAndExpressions]] = None

    @property
    def body(self):
        """The dictionary structure for MOS Full Optimization node.

        Returns:
            dict: Dictionary representation of the node.
        """

        _body = {

                "active": None,
                "doNotHoldCriteria": self.do_not_hold_criteria.body if self.do_not_hold_criteria is not None else None,
                "doNotTradeCriteria": self.do_not_trade_criteria.body if self.do_not_trade_criteria is not None else None,
                "hocDate": None,
                "noBuy": self.no_buy.body if self.no_buy is not None else None,
                "noSell": self.no_sell.body if self.no_sell is not None else None,
                "objType": "Optimization",
                "objectiveFunction": self.objective_function.body,
                "optSettings": self.opt_settings.body,
                "overrideTrigger": None

        }

        if self.constraints is not None and len(self.constraints) > 0:
            _body.update({"constraint": [c.body for c in self.constraints]})

        if self.tax_arbitrages is not None and len(self.tax_arbitrages) > 0:
            _body.update({"taxArbitrage": [a.body for a in self.tax_arbitrages]})

        return _body
