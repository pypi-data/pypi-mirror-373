from dataclasses import dataclass
from typing import List, Optional, Union
from .enums import ConstraintScopeEnum
from .full_optimizer_node import TaxArbitrage
from ...utils.dataclass_validations import BaseDataClassValidator

@dataclass()
class LinearPenalty(BaseDataClassValidator):
    """
    Allows to specify a penalty for the holdings of the optimized portfolio.

    Args:
        target (Union[int, float]): Desired value of constraint slack.
        upside_slope (Union[int, float]): Penalty rate when the variable exceeds the target value.
        downside_slope (Union[int, float]): Penalty rate when the variable falls short of the target value.

    Returns:
        body (dict): Dictionary representation of LinearPenalty constraint.
    """

    target: Union[int, float]
    upside_slope: Union[int, float]
    downside_slope: Union[int, float]

    @property
    def body(self):
        """
        Dictionary representation of LinearPenalty constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "target": self.target,
            "upsideSlope": self.upside_slope,
            "downsideSlope": self.downside_slope
        }
        return body

@dataclass()
class FreeRangeLinearPenalty(BaseDataClassValidator):
    """
    Allows to specify a penalty for the holdings of the optimized portfolio.

    Args:
        target_low (Union[int, float]): Lower bound of the free range.
        target_high (Union[int, float]): Upper bound of the free range.
        upside_slope (Union[int, float]): Penalty rate when the variable falls at the upside outside free range.
        downside_slope (Union[int, float]): Penalty rate when the variable falls at the downside outside free range.

    Returns:
        body (dict): Dictionary representation of FreeRangeLinearPenalty constraint.
    """

    target_low: Union[int, float]
    target_high: Union[int, float]
    upside_slope: Union[int, float]
    downside_slope: Union[int, float]

    @property
    def body(self):
        """
        Dictionary representation of FreeRangeLinearPenalty constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "targetLow": self.target_low,
            "targetHigh": self.target_high,
            "upsideSlope": self.upside_slope,
            "downsideSlope": self.downside_slope
        }
        return body

@dataclass()
class CategoryOrder(BaseDataClassValidator):
    """
    Allows users to specify a relaxation order for constraint categories to help build constraint hierarchy.

    Args:
        category (str) : Category of the constraint. Valid values are:
            ``["linear",
            "factor",
            ”transactionCost”,
            "turnover",
            "hedge",
            "cardinalityThreshold",
            "assetCardinality",
            "holdingLevelThreshold",
            "tranxsizeLevelThreshold",
            "tradeCardinality",
            "risk",
            "roundlotting"]``
        order (str) : Relaxation order; the lower the priority, the earlier the constraint category is relaxed.

    Returns:
            body (dict): Dictionary representation of CategoryOrder constraint.
    """

    category: str
    order: str

    @property
    def body(self):
        """
        Dictionary representation of CategoryOrder constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "category": self.category,
            "order": self.order
        }
        return body


@dataclass()
class GroupBound(BaseDataClassValidator):
    """
    Set lower and/or upper weight bounds for all groups created by groupField.

    Args:
        group_field (list) : Category/group of the constraint.
        scope (ConstraintScopeEnum) : (optional) Scope of the constraint. Default value is net.
        lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        is_soft (bool) : Specify if the constraint is mandatory or soft. Default value is False.
        linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
        free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

    Returns:
            body (dict): Dictionary representation of GroupBound constraint.
    """

    group_field: List[str]
    scope: ConstraintScopeEnum = ConstraintScopeEnum.NET
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False
    linear_penalty: Optional[LinearPenalty] = None
    free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

    @property
    def body(self):
        """
        Dictionary representation of GroupBound constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {'scope': self.scope.value,
                'groupField': [a for a in self.group_field],
                'upperBound': self.upper_bound,
                'lowerBound': self.lower_bound,
                'isSoft': self.is_soft,
                "linearPenalty": self.linear_penalty.body if self.linear_penalty is not None else None,
                "freeRangeLinearPenalty": self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
                }
        return body


@dataclass()
class SpecificBound(BaseDataClassValidator):
    """
    Set lower and/or upper weight bounds for the group satisfying the condition.

    Args:
        condition (str) : condition of the constraint. example: Instrument.Class=='Govt Debt'.
        scope (ConstraintScopeEnum) : (optional) Scope of the constraint. Default value is net.
        lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        is_soft (bool) : Specify if the constraint is mandatory or soft. Default value is False.
        linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
        free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

    Returns:
            body (dict): Dictionary representation of SpecificBound constraint.
    """

    condition: str
    scope: ConstraintScopeEnum = ConstraintScopeEnum.NET
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False
    linear_penalty: Optional[LinearPenalty] = None
    free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

    @property
    def body(self):
        """
        Dictionary representation of SpecificBound constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {'scope': self.scope.value,
                'condition': self.condition,
                'upperBound': self.upper_bound,
                'lowerBound': self.lower_bound,
                'isSoft': self.is_soft,
                "linearPenalty": self.linear_penalty.body if self.linear_penalty is not None else None,
                "freeRangeLinearPenalty": self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
                }

        return body


@dataclass()
class OverallBound(BaseDataClassValidator):
    """
    Set lower and/or upper weight bounds on the total holdings of a specific issuer in the optimized portfolio.

    Args:
        scope (ConstraintScopeEnum) : (optional) Scope of the constraint. Default value is net.
        lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account. Default value is None.
        is_soft (bool) : Specify if the constraint is mandatory or soft. Default value is False.
        linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
        free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

    Returns:
            body (dict): Dictionary representation of OverallBound constraint.
    """

    scope: ConstraintScopeEnum = ConstraintScopeEnum.NET
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False
    linear_penalty: Optional[LinearPenalty] = None
    free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

    @property
    def body(self):
        """
        Dictionary representation of OverallBound constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {'scope': self.scope.value,
                'lowerBound': self.lower_bound,
                'upperBound': self.upper_bound,
                'isSoft': self.is_soft,
                'linearPenalty': self.linear_penalty.body if self.linear_penalty is not None else None,
                'freeRangeLinearPenalty': self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
                }

        return body


@dataclass()
class Bounds(BaseDataClassValidator):
    """
    Bounds constraint

    Args:
       overall (List[OverallBound]) : (optional) List of overall bounds. Default value is None.
       groups (List[GroupBound]) : (optional) List of group bounds. Default value is None.
       specific (List[SpecificBound]) : (optional) List of specific bounds. Default value is None.

    Returns:
        body (dict): Dictionary representation of Bounds constraint.
   """

    overall: Optional[List[OverallBound]] = None
    groups: Optional[List[GroupBound]] = None
    specific: Optional[List[SpecificBound]] = None

    @property
    def body(self):
        """
        Dictionary representation of Bounds constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {}
        if self.overall:
            body['overall'] = [a.body for a in self.overall]
        if self.specific:
            body['specific'] = [a.body for a in self.specific]
        if self.groups:
            body['groups'] = [a.body for a in self.groups]

        return body


@dataclass()
class Aggregation(BaseDataClassValidator):
    """
    Aggregation constraint

    Args:
       agg_method (str) : Aggregation method
       weight (str) : Weight

    Returns:
        body (dict): Dictionary representation of Aggregation constraint.
    """

    agg_method: str
    weight: str

    @property
    def body(self):
        """
        Dictionary representation of Aggregation constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """

        body = {'aggMethod': self.agg_method,
                'weight': self.weight
                }

        return body


@dataclass()
class AssetWeight(BaseDataClassValidator):
    """
    Asset weight for AssetBoundConstraint.

    Args:
       id (str) : Id of Asset.
       id_type (str) : (optional) Id type of asset. Default value is MDSUID
       weight (int, float) : Weight of Asset. Do not set with lower_bound and upper_bound.
       lower_bound (int, float): (optional) Lower bound for the weight of an Asset. Do not set with weight.
       upper_bound (int, float): (optional) Upper bound for the weight of an Asset. Do not set with weight.
       is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

    Returns:
        body (dict): Dictionary representation of AssetWeight.
    """

    id: str
    id_type: Optional[str] = 'MDSUID'
    weight: Optional[Union[int, float]] = None
    upper_bound: Optional[Union[int, float]] = None
    lower_bound: Optional[Union[int, float]] = None
    is_soft: Optional[bool] = False

    def __post_init__(self):
        if self.weight is not None and (self.lower_bound is not None or self.upper_bound is not None):
            raise ValueError("Either weight can be set, or bounds, but not both")

    @property
    def body(self):
        """
        Dictionary representation of AssetWeight.

        Returns:
            dict: Dictionary representation of AssetWeight.
        """

        body = {
            'id': self.id,
            'idType': self.id_type,
            'weight': self.weight,
            'lowerBound': self.lower_bound,
            'upperBound': self.upper_bound,
            'isSoft': self.is_soft
        }

        return body


@dataclass()
class ConditionalAssetWeight(BaseDataClassValidator):
    """
    Conditional asset weight for AssetBoundConstraint.

    Args:
       condition (str) : Condition for Asset.
       weight (int, float) : (optional) Weight of Asset. Do not set with lower_bound and upper_bound.
       lower_bound (int, float): (optional) Lower bound for the weight of an Asset. Do not set with weight.
       upper_bound (int, float): (optional) Upper bound for the weight of an Asset. Do not set with weight.
       is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

    Returns:
        body (dict): Dictionary representation of ConditionalAssetWeight.
    """

    condition: str
    weight: Optional[Union[int, float]] = None
    lower_bound: Optional[Union[int, float]] = None
    upper_bound: Optional[Union[int, float]] = None
    is_soft: Optional[bool] = False

    def __post_init__(self):
        if self.weight is not None and (self.lower_bound is not None or self.upper_bound is not None):
            raise ValueError("Either weight can be set, or bounds, but not both")

    @property
    def body(self):
        """
        Dictionary representation of ConditionalAssetWeight.

        Returns:
            dict: Dictionary representation of ConditionalAssetWeight.
        """

        body = {
            "objType": 'ConditionalAssetsWeight',
            'condition': self.condition,
            'weight': self.weight,
            'lowerBound': self.lower_bound,
            'upperBound': self.upper_bound,
            'isSoft': self.is_soft
        }

        return body


@dataclass()
class AssetTradeSize(BaseDataClassValidator):
    """
    Asset trade size for AssetTradeSizeConstraint.

    Args:
        id (str) : Id of asset.
        trade_value (int, float) : trade size.
        id_type (str) : (optional) Id type of asset. Default value is MDSUID

    Returns:
        body (dict): Dictionary representation of AssetTradeSize.
    """

    id: str
    trade_value: Union[int, float]
    id_type: Optional[str] = 'MDSUID'

    @property
    def body(self):
        """
        Dictionary representation of AssetTradeSize.

        Returns:
            dict: Dictionary representation of AssetTradeSize.
        """

        body = {
            'assetId': self.id,
            'tradeValue': self.trade_value,
            'idType': self.id_type
        }

        return body


@dataclass
class NetTaxImpact(BaseDataClassValidator):
    """
    Net tax impact settings for TaxConstraint. Specify a lower bound and/or an upper bound on the net tax impact of the portfolio.

    Args:
        id (str) : Id.
        upper_bound (int, float) : If omitted then does not affect the bounds in the net tax impact of optimization.
        lower_bound (int, float) : If omitted then does not affect the bounds in the net tax impact of optimization.

    Returns:
        body (dict): Dictionary representation of NetTaxImpact.
    """

    id: str
    upper_bound: Union[int, float]
    lower_bound: Union[int, float]

    @property
    def body(self):
        """
        Dictionary representation of NetTaxImpact.

        Returns:
            dict: Dictionary representation of NetTaxImpact.
        """

        body = {
            'id': self.id,
            'upperBound': self.upper_bound,
            'lowerBound': self.lower_bound
        }

        return body


@dataclass
class SpecificFactorBound(BaseDataClassValidator):
    """
        Specific bound factor required for factor constraint.

        Args:
            factor (str) : Factor code for which bounds are created.
            upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
            by_side(str): (optional) This can accept following values net, long, short, total. Default value is net.
            relax_order(str): (optional) Relax order, for example first.
            linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
            free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

        Returns:
            body (dict): Dictionary representation of SpecificFactorBound.
        """
    factor: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False
    by_side: Optional[str] = 'net'
    relax_order: Optional[str] = None
    linear_penalty: Optional[LinearPenalty] = None
    free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

    @property
    def body(self):
        """
        Dictionary representation of SpecificFactorBound constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "factor": self.factor,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft,
            "bySide": self.by_side,
            "relaxOrder": self.relax_order,
            "linearPenalty": self.linear_penalty.body if self.linear_penalty is not None else None,
            "freeRangeLinearPenalty": self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
        }
        return body


@dataclass
class GroupedFactorBound(BaseDataClassValidator):
    """
         Grouped bound factor required for factor constraint.

        Args:
            group_field (List[str]) : Category/group of the constraint.
            upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
            linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
            free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

        Returns:
            body (dict): Dictionary representation of GroupedFactorBound.
        """
    group_field: List[str]
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False
    linear_penalty: Optional[LinearPenalty] = None
    free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

    @property
    def body(self):
        """
        Dictionary representation of GroupedFactorBound constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "groupField": self.group_field,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft,
            "linearPenalty": self.linear_penalty.body if self.linear_penalty is not None else None,
            "freeRangeLinearPenalty": self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
        }
        return body


@dataclass
class LeverageConstraintBySide(BaseDataClassValidator):
    """

    Args:
    by_side (str) : by_side
    is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
    upper_bound (str) : (optional) This accepts constants.
    lower_bound (str) : (optional) This accepts constants.

    Returns:
    LeverageConstraintBySide dictionary
    """
    by_side: str
    lower_bound: float
    upper_bound: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of LeverageConstraintBySide constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "bySide": self.by_side,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft,
        }
        return body


@dataclass()
class CrossAccountAssetBoundTotalPosition(BaseDataClassValidator):
    """
    Cross-account general linear (group) constraint for multi-account optimization

    Args:
    asset_id (List) : Asset Id for portfolio upload
    upper_bound (str) : (optional) This accepts constants.
    lower_bound (str) : (optional) This accepts constants.

    Returns:
    CrossAccountAssetBoundTotalPosition dictionary
    """
    asset_id: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountAssetBoundTotalPosition constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "assetId": self.asset_id,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound
        }
        return body


@dataclass()
class CrossAccountMaxAssetTotalTradeType(BaseDataClassValidator):
    """
    Asset bound on total tradesize/buys/sells across all accounts; units of bound is in dollar value

    Args:
    asset_id (str) : Asset Id for portfolio upload
    upper_bound (str) : This accepts constants.
    trade_type (str) : Allowed trade types are:
    ``["buy",
    "sell",
    "trade"]``

    Returns:
    CrossAccountMaxAssetTotalTradeType dictionary
    """
    asset_id: str
    upper_bound: str
    trade_type: str

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountMaxAssetTotalTradeType constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "assetId": self.asset_id,
            "upperBound": self.upper_bound,
            "tradeType": self.trade_type
        }
        return body


@dataclass()
class CrossAccountGeneralLinearBounds(BaseDataClassValidator):
    """
    Cross account general linear constraint.

    Args:
    group_field (List) : Category/group of the constraint.
    coefficient_attribute (str) : coefficient_attribute
    is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
    upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
    lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.

    Returns:
    CrossAccountGeneralLinearBounds dictionary
    """

    coefficient_attribute: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountGeneralLinearBounds constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "coefficientAttribute": self.coefficient_attribute,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft
        }
        return body


@dataclass()
class CrossAccountGroupedLinearBounds:
    """
    Cross account general linear group constraint.

    Args:
    group_field (List) : Category/group of the constraint.
    coefficient_attribute (str) : coefficient_attribute
    is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
    upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
    lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.

    Returns:
    CrossAccountGroupedLinearBounds dictionary
    """
    group_field: List[str]
    coefficient_attribute: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountGroupedLinearBounds constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "groupField": self.group_field,
            "coefficientAttribute": self.coefficient_attribute,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound,
            "isSoft": self.is_soft
        }
        return body


@dataclass()
class CrossAccountGeneralRatioBounds(BaseDataClassValidator):
    """
    Cross account general ratio constraint. Both the numerator and the denominator coefficients come from group attributes.

    Args:
    numerator_attribute (str) : numerator_attribute
    denominator_attribute (str) : denominator_attribute
    lower_bound (str) :(optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
    upper_bound (str) :(optional) This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.

    Returns:
    CrossAccountGeneralRatioBounds dictionary
    """
    numerator_attribute: str
    denominator_attribute: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountGeneralRatioBounds constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "numeratorAttribute": self.numerator_attribute,
            "denominatorAttribute": self.denominator_attribute,
            "upperBound": self.upper_bound,
            "lowerBound": self.lower_bound
        }
        return body


@dataclass()
class CrossAccountTradeThresholdOverallBounds(BaseDataClassValidator):
    """
    Cross-account threshold constraint.

    Args:
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        CrossAccountTradeThresholdOverallBounds dictionary.
    """
    trade_type: str
    minimum: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountTradeThresholdOverallBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "isSoft": self.is_soft
        }

        return body


@dataclass()
class CrossAccountTradeThresholdAssetBounds(BaseDataClassValidator):
    """
    Cross-account threshold constraint by asset.

    Args:
        asset_id (str): Asset Id for portfolio upload.
        id_type (str): Type of Id of the asset. Default value is MDSUID. Allowed Id types are:
            ``["ISIN",
            "CUSIP",
            "MDSUID",
            "BARRA",
            "SEDOL"]``
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        CrossAccountTradeThresholdAssetBounds dictionary.
    """
    asset_id: str
    id_type: str
    trade_type: str
    minimum: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountTradeThresholdAssetBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """

        body = {
            "assetId": self.asset_id,
            "idType": self.id_type,
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "isSoft": self.is_soft
        }

        return body


@dataclass()
class CrossAccountTradeThresholdGroupBounds(BaseDataClassValidator):
    """
    Cross-account threshold constraint by group

    Args:
        condition (str): condition of the constraint. example: userdata1 == 'A'
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        CrossAccountTradeThresholdGroupBounds dictionary.
    """
    condition: str
    trade_type: str
    minimum: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of CrossAccountTradeThresholdGroupBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "condition": self.condition,
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "isSoft": self.is_soft
        }

        return body


@dataclass()
class TradeThresholdOverallBounds(BaseDataClassValidator):
    """
    Trade threshold constraint.

    Args:
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        TradeThresholdOverallBounds dictionary.
    """

    trade_type: str
    minimum: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of TradeThresholdOverallBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "isSoft": self.is_soft
        }

        return body


@dataclass()
class TradeThresholdAssetBounds(BaseDataClassValidator):
    """
    Trade threshold constraint by asset.

    Args:
        asset_id (str): Asset Id for portfolio upload.
        id_type (str): Type of Id of the asset. Default value is MDSUID. Allowed Id types are:
            ``["ISIN",
            "CUSIP",
            "MDSUID",
            "BARRA",
            "SEDOL"]``
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        TradeThresholdAssetBounds dictionary.
    """

    trade_type: str
    minimum: float
    asset_id: str
    is_soft: Optional[bool] = False
    id_type: str = "MDSUID"

    @property
    def body(self):
        """
        Dictionary representation of TradeThresholdAssetBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """

        body = {
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "assetId": self.asset_id,
            "isSoft": self.is_soft,
            "idType": self.id_type
        }

        return body


@dataclass()
class TradeThresholdGroupBounds(BaseDataClassValidator):
    """
    Trade threshold constraint by group

    Args:
        condition (str): condition of the constraint. example: userdata1 == 'A'
        trade_type (str): Allowed trade types are:
            ``["long",
            "short",
            "buy",
            "sell"]``
        minimum (float): Minimum level.
        is_soft (bool): (Optional) Default value is False.

    Returns:
        TradeThresholdGroupBounds dictionary.
    """

    condition: str
    trade_type: str
    minimum: float
    is_soft: Optional[bool] = False

    @property
    def body(self):
        """
        Dictionary representation of TradeThresholdGroupBounds constraint

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {

            "condition": self.condition,
            "tradeType": self.trade_type,
            "minimum": self.minimum,
            "isSoft": self.is_soft
        }

        return body

@dataclass()
class SimpleTaxLotCondition(BaseDataClassValidator):
    """
    Simple logical expression for the initial tax lots where possible fields are: taxlot.age, taxlot.gainPerShare, taxlot.gainPerLot.

    Args:
        expression (str): Expression defining the condition.
    """
    expression: str

    @property
    def body(self):
        """
        Dictionary representation of SimpleTaxLotCondition constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "expression": self.expression
        }
        return body


@dataclass()
class SimplePortfolioCondition:
    """
    Simple logical expression for the initial portfolio, where possible fields are: portfolio.unrealizedGain, portfolio.unrealizedLoss, portfolio.unrealizedNet.

    Args:
        expression (str): Expression defining the condition.
    """
    expression: str

    @property
    def body(self):
        """
        Dictionary representation of SimplePortfolioCondition constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "expression": self.expression
        }
        return body

@dataclass()
class ConditionalTaxLotTradingRule:
    """
    	Allows to set trading rule for the tax lots that fulfils a selected condition. An optional portfolio level condition can be also selected to only apply the trading rules on selected occasions

    Args:
        trading_rule (str): Allowed values are keepLot, sellLot.
        condition (Union[SimpleTaxLotCondition]): Condition to define which tax lots set the trading rule for.
        trigger_condition (SimplePortfolioCondition): (Optional) Condition to define when to apply the trading rules.
    """
    trading_rule: str
    condition: Union[SimpleTaxLotCondition]
    trigger_condition: Optional[SimplePortfolioCondition] = None

    @property
    def body(self):
        """
        Dictionary representation of ConditionalTaxLotTradingRule constraint.

        Returns:
            dict: Dictionary representation of the constraint.
        """
        body = {
            "tradingRule": self.trading_rule,
            "condition": {}
        }
        if isinstance(self.condition, SimpleTaxLotCondition):
            body["condition"] = self.condition.body
            body["condition"]["objType"] = "SimpleTaxLotCondition"
        if isinstance(self.trigger_condition, SimplePortfolioCondition):
            body["triggerCondition"] = self.trigger_condition.body
            body["triggerCondition"]["objType"] = "SimplePortfolioCondition"

        return body

class ConstraintFactory:
    """
    Class to represent all constraint nodes.
    """

    @dataclass()
    class RoundLotConstraint(BaseDataClassValidator):
        """
        Allows you to specify a round lot constraint.

        Args:
            lot_size (str): User can provide either 1 for unit lot size for all assets or userdata point for asset level lot size. Default is 1 if userdata is not provided for an asset.
            enforce_closeout (bool): If set to true, lots smaller than the lot size are closed out. Default value is False.
            allow_closeout (bool): If set to true, optimizer may close out a position even if the lot size is below the lot_size. Default value is False.
            is_soft (bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

        Returns:
            RoundLotConstraint dictionary
        """

        lot_size: Optional[str] = None
        enforce_closeout: Optional[bool] = False
        allow_closeout: Optional[bool] = False
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of RoundLotConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "RoundLotConstraint",
                "lotSize": self.lot_size,
                "enforceOddLotCloseOut": self.enforce_closeout,
                "allowOddLotCloseOut": self.allow_closeout,
                "isSoft": self.is_soft
            }
            return body

    @dataclass()
    class NonCashAssetBound(BaseDataClassValidator):
        """
        Allows you to specify the upper and lower weight bounds for all non-cash assets.

        Args:
            upper_bound (str): Maximum weight that any non-cash asset must have in the optimal portfolio.
            lower_bound (str):  Minimum weight that any non-cash asset must have in the optimal portfolio. If you set a minimum, the optimizer must include these assets and weights, or it will not produce an optimal portfolio.

        Returns:
            NonCashAssetBound dictionary
        """

        upper_bound: str
        lower_bound: str

        @property
        def body(self):
            """
            Dictionary representation of NonCashAssetBound constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'NonCashAssetBound',
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound
            }
            return body

    @dataclass()
    class GeneralRatioConstraint(BaseDataClassValidator):
        """
        Add a ratio constraint with arbitrary coefficients.

        Args:
            upper_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            lower_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            numerator_field (str): Numerator field.
            denominator_field (str): (optional) Denominator field. Default value is None.
        Returns:
            GeneralRatioConstraint dictionary
        """

        upper_bound: str
        lower_bound: str
        numerator_field: str
        denominator_field: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of GeneralRatioConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'GeneralRatioConstraint',
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound,
                "numeratorField": self.numerator_field,
                "denominatorField": self.denominator_field,
            }
            return body

    @dataclass()
    class GroupRatio(BaseDataClassValidator):
        """
        Create group level ratio constraint.

        Args:
            field (str): Field
            group_field  (List[str]): List of group fields.
            group_key (str): Group key.

        Returns:
            GroupRatio dictionary
        """

        field: str
        group_field: List[str]
        group_key: str

        @property
        def body(self):
            """
            Dictionary representation of GroupRatio constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "field": self.field,
                "groupField": self.group_field,
                "groupKey": self.group_key,
            }
            return body

    @dataclass()
    class GroupRatioConstraint(BaseDataClassValidator):
        """
        Add a ratio constraint with arbitrary coefficients for group of assets. Both the numerator and the denominator coefficients come from group attributes.

        Args:
            upper_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            lower_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
            numerator_field (str): Numerator field.
            numerator_group_field (List[str]): Numerator group field.
            numerator_group_key (str): Numerator group key.
            denominator_field (str): (optional) Denominator field. Default value is None.
            denominator_group_field (List[str]): (optional) Denominator group field. Default value is None.
            denominator_group_key (str): (optional) Denominator group key. Default value is None.

        Returns:
            GroupRatioConstraint dictionary

        """

        upper_bound: str
        lower_bound: str
        numerator_field: str
        numerator_group_field: List[str]
        numerator_group_key: str
        denominator_field: Optional[str] = None
        denominator_group_field: Optional[List[str]] = None
        denominator_group_key: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of GroupRatioConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """

            numerator_group = ConstraintFactory.GroupRatio(field=self.numerator_field,
                                                           group_field=self.numerator_group_field,
                                                           group_key=self.numerator_group_key).body

            if self.denominator_field is None:
                denominator_group = None
            else:
                denominator_group = ConstraintFactory.GroupRatio(field=self.denominator_field,
                                                                 group_field=self.denominator_group_field,
                                                                 group_key=self.denominator_group_key).body

            body = {
                "objType": 'GroupRatioConstraint',
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound,
                "numeratorGroup": numerator_group,
                "denominatorGroup": denominator_group
            }
            return body

    @dataclass()
    class HoldingThresholdConstraint(BaseDataClassValidator):
        """
        Allows you to specify a minimum holding (long) asset weight threshold for all assets in the optimized portfolio.

        Args:
            minimum_holding_level (int, float): Minimum holding level for an asset if it takes on a long position.
            enable_grand_father_rule (bool): If set to true, then the grandfather rule is enabled for minimum holding level threshold constraint. Default value is False.
            is_soft (bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

        Returns:
            HoldingThresholdConstraint dictionary

        """

        minimum_holding_level: Union[int, float]
        enable_grand_father_rule: Optional[bool] = False
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of HoldingThresholdConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'HoldingThresholdConstraint',
                "enableGrandfatherRule": self.enable_grand_father_rule,
                "longSide": {'isSoft': self.is_soft, 'minimum': self.minimum_holding_level}
            }
            return body

    @dataclass()
    class AssetTradeSizeConstraint(BaseDataClassValidator):
        """
        Allows you to set upper trade size bound on the specific security.

        Args:
            trade_size_list (List(AssetTradeSize)) : List of assets and the trade size bound.
            is_soft (bool) : (optional) Specify if the constraint is mandatory or soft. Default value is False.

        Returns:
            AssetTradeSizeConstraint dictionary
        """

        trade_size_list: List[AssetTradeSize]
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of AssetTradeSizeConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "AssetTradeSizeConstraint",
                "tradeSize": [a.body for a in self.trade_size_list]
            }
            return body

    @dataclass()
    class NumberOfAssets(BaseDataClassValidator):
        """
        Allows you to specify the minimum and maximum number of assets that the optimized portfolio can have.

        Args:
            min (int): (optional) Minimum number of assets to be held in the portfolio. Default value is None.
            max (int): (optional) Maximum number of assets that can be held in the portfolio. Default value is None.
            is_soft (bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

        Returns:
            NumberOfAssets dictionary

        """

        min: Optional[int] = None
        max: Optional[int] = None
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of NumberOfAssets constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'NumberOfAssets',
                "min": self.min,
                "max": self.max,
                "isSoft": self.is_soft
            }
            return body

    @dataclass()
    class ConstraintPriority(BaseDataClassValidator):
        """
        Allows you to build a constraint hierarchy. If the problem becomes infeasible, the optimization algorithm will relax the constraints in the specified order until a solution can be found, or infeasibility will be reported.

        Args:
            category_orders (List[CategoryOrder]) : Relaxation order for the categories. If the problem becomes infeasible, the optimization algorithm will relax the constraints in the specified order until a solution is found, or infeasibility will be reported.

        Returns:
            ConstraintPriority dictionary

        """
        category_orders: List[CategoryOrder]

        @property
        def body(self):
            """
            Dictionary representation of ConstraintPriority constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'ConstraintPriority',
                "categoryOrders": [a.body for a in self.category_orders],

            }
            return body

    @dataclass()
    class RiskConstraint(BaseDataClassValidator):
        """
        Allows you to specify a target portfolio or active risk for the optimized portfolio.

        Args:
            upper_bound (int, float) : An upper bound on the level of total or active risk for the optimal portfolio.
            lower_bound (int, float) : An lower bound on the level of total or active risk for the optimal portfolio.
            use_relative_risk (bool) : If set to true, the upper bound limits the contribution of a particular risk source to the portfolio’s total risk. Should be set as false for tax aware optimization cases. Default value is False.
            risk_source_type (str): Limit total risk, factor risk, or specific risk. Default value is None.
            reference_portfolio (str): If this parameter is set, the risk constraint limits active risk of the optimal portfolio. Default value is None.
            is_soft (bool) : (optional) Specify if the constraint is mandatory or soft. Default value is False.


        Returns:
            RiskConstraint dictionary
        """

        upper_bound: Optional[Union[int, float]] = None
        lower_bound: Optional[Union[int, float]] = None
        use_relative_risk: bool = False
        risk_source_type: Optional[str] = None
        reference_portfolio: Optional[str] = None
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of RiskConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'RiskConstraint',
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound,
                "useRelativeRisk": self.use_relative_risk,
                "riskSourceType": self.risk_source_type,
                "referencePortfolio": self.reference_portfolio,
                "isSoft": self.is_soft
            }
            return body

    @dataclass()
    class TransactionCostConstraint(BaseDataClassValidator):
        """
        Allows you to specify an upper bound on the transaction costs(% of portfolio AUM) to be undertaken to arrive at the optimized portfolio.

        Args:
            upper_bound (int, float): Specify the maximum transaction cost the optimizer can incur in constructing an optimal portfolio.
            t_cost_attribute (str): Datapoint name that contains the transaction cost amount.
            is_soft (bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.


        Returns:
            TransactionCostConstraint dictionary
        """

        upper_bound: Union[int, float]
        t_cost_attribute: str
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of TransactionCostConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'TransactionCostConstraint',
                "upperBound": self.upper_bound,
                "tCostAttribute": self.t_cost_attribute,
                "isSoft": self.is_soft
            }
            return body

    @dataclass()
    class TradabilityConstraint(BaseDataClassValidator):
        """
        Allows you to specify upper and lower bound weight limits relative to the current weight of the asset in the initial portfolio based on the tradability score of the asset in MarketAxess.

        Args:
            required_score (int): Tradability score of the asset in MarketAxess.
            condition (str): (optional) Condition. Default value is None.

        Returns:
            TradabilityConstraint dictionary
        """

        required_score: int
        condition: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of TradabilityConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'TradabilityConstraint',
                "requiredScore": self.required_score,
                "condition": self.condition,
            }
            return body

    @dataclass()
    class TurnoverConstraint(BaseDataClassValidator):
        """
        Allows you to specify an upper bound on the turnover (% of portfolio AUM) to be undertaken to arrive at the optimized portfolio.

        Args:
            upper_bound (int, float): Specify the maximum turnover the optimizer must observe in producing an optimal portfolio.
            is_soft (bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.

        Returns:
            TurnoverConstraint dictionary
        """

        upper_bound: Union[int, float]
        is_soft: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of TurnoverConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'TurnoverConstraint',
                "upperBound": self.upper_bound,
                "isSoft": self.is_soft
            }
            return body

    @dataclass()
    class AssetBoundConstraint(BaseDataClassValidator):
        """
        Allows you to set asset-level bound for specific assets in the optimal portfolio.

        Args:
            asset_bound_type (ConditionalAssetWeight, List(AssetWeight)) : Asset bound constraint type.

        Returns:
            AssetBoundConstraint dictionary
        """

        asset_bound_type: Union[List[AssetWeight], ConditionalAssetWeight]

        @property
        def body(self):
            """
            Dictionary representation of AssetBoundConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'AssetBoundConstraint',
                "assetBoundConstraintType": {}
            }

            if isinstance(self.asset_bound_type, ConditionalAssetWeight):
                body["assetBoundConstraintType"] = self.asset_bound_type.body
            elif isinstance(self.asset_bound_type, List) and all(
                    isinstance(x, AssetWeight) for x in self.asset_bound_type):
                body["assetBoundConstraintType"]["objType"] = "AssetsWeight"
                body["assetBoundConstraintType"]["assets"] = [n.body for n in self.asset_bound_type]
            return body

    @dataclass()
    class LinearConstraint(BaseDataClassValidator):
        """
        Allows you to specify asset bounds, custom constraint and group constraint on the holdings of the optimized portfolio.

        Args:
            constraint_field  (str): Name of the constraint.
            bounds (Bounds): Minimum and maximum value for the constraint; 3 levels are available: overall, groups, specific.

        Returns:
            LinearConstraint dictionary
        """

        bounds: Bounds
        constraint_field: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of LinearConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'LinearConstraint',
                "constraintField": self.constraint_field,
                "bounds": self.bounds.body
            }
            return body

    @dataclass()
    class TaxConstraint(BaseDataClassValidator):
        """
        Allows you to specify tax limit and tax settings.

        Args:
            tax_limit  (int, float): (optional) Tax limit.
            min_holding_period (int): (optional) Minimum holding period.
            net_tax_impact (NetTaxImpact): (optional) Specify a lower bound and/or an upper bound on the net tax impact of the portfolio.
            tax_arbitrages (List(TaxArbitrage)): (optional) Net Realized Gain Cap that defines net realize capital gain constraint.
            conditional_taxLot_trading_rules (List(ConditionalTaxLotTradingRule)): (optional) Allows to set trading rule for the tax lots that fulfils a selected condition. An optional portfolio level condition can be also selected to only apply the trading rules on selected occasions.

        Returns:
            TaxConstraint dictionary
        """

        tax_limit: Optional[Union[int, float]] = None
        min_holding_period: Optional[int] = None
        net_tax_impact: Optional[NetTaxImpact] = None
        tax_arbitrages: Optional[List[TaxArbitrage]] = None
        conditional_taxLot_trading_rules: Optional[List[ConditionalTaxLotTradingRule]] = None

        @property
        def body(self):
            """
            Dictionary representation of TaxConstraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'TaxConstraint',
                "taxLimit": self.tax_limit,
                "minHoldingPeriod": self.min_holding_period,
                "netTaxImpact": self.net_tax_impact.body if self.net_tax_impact is not None else None,
                "taxArbitrage": [a.body for a in self.tax_arbitrages] if self.tax_arbitrages is not None else None,
                "conditionalTaxLotTradingRules": [a.body for a in self.conditional_taxLot_trading_rules] if self.conditional_taxLot_trading_rules is not None else None
            }
            return body

    @dataclass()
    class FactorConstraint(BaseDataClassValidator):
        """
        Linear constraints in the optimizer with which users can control the magnitude of a factor exposure by using
        an upper or lower bound or both.

        Args:
            specific_factor_bound (List[SpecificFactorBound]): Specific bound factor required for factor constraint.
            grouped_factor_bound (List[GroupedFactorBound]): Grouped bound factor required for factor constraint.

            Returns:
                body (dict): Dictionary representation of Factor Constraints.
            """
        specific_factor_bound: Optional[List[SpecificFactorBound]] = None
        grouped_factor_bound: Optional[List[GroupedFactorBound]] = None

        @property
        def body(self):
            """
            Dictionary representation of Factor constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "FactorConstraint",
                "specificBounds": [a.body for a in
                                   self.specific_factor_bound] if self.specific_factor_bound is not None else None,
                "groupedBounds": [a.body for a in
                                  self.grouped_factor_bound] if self.grouped_factor_bound is not None else None
            }
            return body

    @dataclass()
    class LeverageConstraint(BaseDataClassValidator):
        """
        Constraint for long short portfolio, allow you to limit the amount of debt used to acquire additional assets.

        Args:
        leverage (List[LeverageConstraintBySide]): LeverageConstraintBySide required for LeverageConstraint.
        Returns:
        LeverageConstraint dictionary
        """
        leverage: List[LeverageConstraintBySide]

        @property
        def body(self):
            """
            Dictionary representation of Leverage constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "LeverageConstraint",
                "leverage": [a.body for a in
                             self.leverage] if self.leverage is not None else None,
            }
            return body

    @dataclass()
    class CrossAccountNetTurnoverConstraint(BaseDataClassValidator):
        """
        Internal-use-only. Cross-account turnover constraint for multi-account optimization.

        Args:
        upper_bound (str): Upper bound; in units of dollar(currency) value.
        Returns:
        CrossAccountNetTurnoverConstraint dictionary
        """
        upper_bound: str

        @property
        def body(self):
            """
            Dictionary representation of Cross Account Net Turnover Constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountNetTurnoverConstraint",
                "upperBound": self.upper_bound
            }
            return body

    @dataclass()
    class CrossAccountAssetBoundTotalConstraint(BaseDataClassValidator):
        """
        Internal-use-only. Asset bound on total position across all accounts; units of bound is in dollar value

        Args:
        asset_bounds (List[CrossAccountAssetBoundTotalPosition]) : CrossAccountAssetBoundTotalPosition required for CrossAccountAssetBoundTotalConstraint.
        Returns:
        CrossAccountAssetBoundTotalConstraint dictionary
        """
        asset_bounds: List[CrossAccountAssetBoundTotalPosition]

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountAssetBoundTotalConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountAssetBoundTotalConstraint",
                "assetBounds": [a.body for a in
                                self.asset_bounds] if self.asset_bounds is not None else None
            }
            return body

    @dataclass
    class CrossAccountTradeThresholdConstraint(BaseDataClassValidator):
        """
        Cross-account constraint which applies a minimum transaction size constraint on the aggregated trade sizes from each sleeve.

        Args:
            allow_close_out (bool): (Optional) If True, completely trading out of the position is allowed regardless of transaction size. Default value is False
            overall_bounds (List[CrossAccountTradeThresholdOverallBounds]): Cross-account threshold constraint.
            asset_bounds (List[CrossAccountTradeThresholdAssetBounds]): Cross-account threshold constraint by asset.
            group_bounds (List[CrossAccountTradeThresholdGroupBounds]): Cross-account threshold constraint by group.
        """

        overall_bounds: List[CrossAccountTradeThresholdOverallBounds] = None
        asset_bounds: List[CrossAccountTradeThresholdAssetBounds] = None
        group_bounds: List[CrossAccountTradeThresholdGroupBounds] = None
        allow_close_out: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountTradeThresholdConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """

            body = {
                "objType": "CrossAccountTradeThresholdConstraint",
                "allowCloseOut": self.allow_close_out,
                "overall": [a.body for a in
                            self.overall_bounds] if self.overall_bounds is not None else None,
                "asset": [a.body for a in
                          self.asset_bounds] if self.asset_bounds is not None else None,
                "group": [a.body for a in
                          self.group_bounds] if self.group_bounds is not None else None
            }

            return body

    @dataclass()
    class CrossAccountAssetTotalTradeTypeConstraint(BaseDataClassValidator):
        """
        Internal-use-only. Trade Size on total tradesize/buys/sells across all accounts; units of bound is in dollar value.

        Args:
        trade_size (List[CrossAccountMaxAssetTotalTradeType]) : CrossAccountMaxAssetTotalTradeType required for CrossAccountAssetTotalTradeTypeConstraint.
        Returns:
        CrossAccountAssetTotalTradeTypeConstraint dictionary
        """
        trade_size: Optional[List[CrossAccountMaxAssetTotalTradeType]] = None

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountAssetTotalTradeTypeConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountAssetTotalTradeTypeConstraint",
                "tradeSize": [a.body for a in
                              self.trade_size] if self.trade_size is not None else None
            }
            return body

    @dataclass()
    class AggregateRiskConstraint(BaseDataClassValidator):
        """
        Allows to specify a target portfolio or active risk for the aggregated optimized portfolio of all accounts.

        Args:
        reference_portfolio (str) : (Optional) If this parameter is set, the risk constraint limits active risk of the optimal portfolio. If not specified, the constraint will be set to the absolute portfolio risk.
        upper_bound (float) : An upper bound on the level of total or active risk for the optimal portfolio.
        Returns:
        AggregateRiskConstraint dictionary
        """
        upper_bound: float
        reference_portfolio: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of AggregateRiskConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "AggregateRiskConstraint",
                "referencePortfolio": self.reference_portfolio,
                "upperBound": self.upper_bound
            }
            return body

    @dataclass()
    class CrossAccountTaxLimitConstraint(BaseDataClassValidator):
        """
        Cross-account tax limit constraint.

        Args:
        upper_bound (float) : The upper bound should be in the same unit as the selected taxUnit in TaxOptimizationSettings, where taxUnit was dollar(deprecated) or amount for absolute value, and decimal for amounts relative to the base value.

        Returns:
        CrossAccountTaxLimitConstraint dictionary
        """
        upper_bound: float

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountTaxLimitConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountTaxLimitConstraint",
                "upperBound": self.upper_bound
            }
            return body

    @dataclass()
    class CrossAccountLinearConstraint(BaseDataClassValidator):
        """
        Cross-account general linear (group) constraint for multi-account optimization

        Args:
        general_bound (List) : List of cross account general linear constraint.
        grouped_bound (List) : List of cross account general linear group constraint.

        Returns:
        CrossAccountLinearConstraint dictionary
        """

        general_bound: List[CrossAccountGeneralLinearBounds]
        grouped_bound: List[CrossAccountGroupedLinearBounds]

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountLinearConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountLinearConstraint",
                "generalBounds": [a.body for a in
                                  self.general_bound] if self.general_bound is not None else None,
                "groupedBounds": [a.body for a in
                                  self.grouped_bound] if self.grouped_bound is not None else None
            }
            return body

    @dataclass()
    class CrossAccountGroupedRatioBounds(BaseDataClassValidator):
        """
        Cross account general ratio constraint. Both the numerator and the denominator coefficients come from group attributes.

        Args:
        upper_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
        lower_bound (str): This accepts constants, or an expression relative to a benchmark reference name or init_pf. If init_pf is used in the expression, the bound will be relative to the currentPortfolio of the account.
        numerator_field (str): Numerator field.
        numerator_group_field (List[str]): Numerator group field.
        numerator_group_key (str): Numerator group key.
        denominator_field (str): (optional) Denominator field. Default value is None.
        denominator_group_field (List[str]): (optional) Denominator group field. Default value is None.
        denominator_group_key (str): (optional) Denominator group key. Default value is None.

        Returns:
        CrossAccountGroupedRatioBounds dictionary
        """
        upper_bound: str
        lower_bound: str
        numerator_field: str
        numerator_group_field: List[str]
        numerator_group_key: str
        denominator_field: Optional[str] = None
        denominator_group_field: Optional[List[str]] = None
        denominator_group_key: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountGroupedRatioBounds constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """

            numerator_group = ConstraintFactory.GroupRatio(field=self.numerator_field,
                                                           group_field=self.numerator_group_field,
                                                           group_key=self.numerator_group_key).body

            if self.denominator_field is None:
                denominator_group = None
            else:
                denominator_group = ConstraintFactory.GroupRatio(field=self.denominator_field,
                                                                 group_field=self.denominator_group_field,
                                                                 group_key=self.denominator_group_key).body

            body = {
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound,
                "numeratorGroup": numerator_group,
                "denominatorGroup": denominator_group
            }
            return body

    @dataclass()
    class CrossAccountRatioConstraint(BaseDataClassValidator):
        """
        Cross-account general ratio (group) constraint for multi-account optimization

        Args:
        general_bound :
        grouped_bound :

        Returns:
        CrossAccountRatioConstraint dictionary
        """

        general_bounds: CrossAccountGeneralRatioBounds
        grouped_bounds: "ConstraintFactory.CrossAccountGroupedRatioBounds"

        @property
        def body(self):
            """
            Dictionary representation of CrossAccountRatioConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "CrossAccountRatioConstraint",
                "generalBounds": self.general_bounds.body,
                "groupedBounds": self.grouped_bounds.body
            }
            return body

    @dataclass()
    class SleeveBalanceConstraint(BaseDataClassValidator):
        """
        Allows to constrain how much a sleeve's market value can change relatively to its current market value. The constraint is only available with Multi Sleeve Optimization

        Args:
        is_soft(bool): (optional) Specify if the constraint is mandatory or soft. Default value is False.
        upper_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name.
        lower_bound (str) : (optional) This accepts constants, or an expression relative to a benchmark reference name.

        Returns:
        SleeveBalanceConstraint dictionary
        """

        is_soft: Optional[bool] = False
        lower_bound: Optional[str] = "0"
        upper_bound: Optional[str] = "1"

        @property
        def body(self):
            """
            Dictionary representation of SleeveBalanceConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": "SleeveBalanceConstraint",
                "isSoft": self.is_soft,
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound
            }
            return body

    @dataclass()
    class TradeThresholdConstraint(BaseDataClassValidator):
        """
        Trade threshold constraint which applies a minimum transaction size constraint

        Args:
        allowCloseOut(bool): (optional)
        overall (List[TradeThresholdOverallBounds]) : (optional) Trade threshold constraint.
        asset (List[TradeThresholdAssetBounds]) : (optional) Trade threshold constraint by asset.
        group (List[TradeThresholdGroupBounds]) : (optional) Trade threshold constraint by group.

        Returns:
        TradeThresholdConstraint dictionary
        """

        allow_close_out: Optional[bool] = False
        overall: Optional[List[TradeThresholdOverallBounds]] = None
        asset: Optional[List[TradeThresholdAssetBounds]] = None
        group: Optional[List[TradeThresholdGroupBounds]] = None

        @property
        def body(self):
            """
            Dictionary representation of TradeThresholdConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """

            body = {
                "objType": "TradeThresholdConstraint",
                "allowCloseOut": self.allow_close_out,
                "overall": [a.body for a in
                            self.overall] if self.overall is not None else None,
                "asset": [a.body for a in
                          self.asset] if self.asset is not None else None,
                "group": [a.body for a in
                          self.group] if self.group is not None else None
            }

            return body

    @dataclass()
    class NumberOfTrades(BaseDataClassValidator):
        """
        Number of trades involved in transacting an initial portfolio into an optimal one cannot be greater or less
        than a certain number

        Args:
            trade_type (str) : Allowed trade types are: [ long, short, buy, sell, trade ]
            min (int): (optional) Minimum number of trades. Default value is None.
            max (int): (optional) Maximum number of trades. Default value is None.
            is_min_soft (bool): (optional) If omitted defaults to false. Specify if the min trade constraint is soft. Default value is False.
            is_max_soft (bool): (optional) If omitted defaults to false. Specify if the max trade constraint is soft. Default value is False.

        Returns:
            NumberOfTrades dictionary

        """

        trade_type: str
        min: Optional[int] = None
        max: Optional[int] = None
        is_min_soft: Optional[bool] = False
        is_max_soft: Optional[bool] = False

        def __post_init__(self):
            allowed_values = {"long", "short", "buy", "sell", "trade"}
            if self.trade_type is not None and self.trade_type not in allowed_values:
                raise ValueError(f"trade_type must be one of {allowed_values}")

        @property
        def body(self):
            """
            Dictionary representation of NumberOfTrades constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'NumberOfTrades',
                "tradeType": self.trade_type,
                "min": self.min,
                "max": self.max,
                "isMinSoft": self.is_min_soft,
                "isMaxSoft": self.is_max_soft
            }
            return body

    @dataclass()
    class BetaConstraint(BaseDataClassValidator):
        """
        A general linear constraint in the Optimizer which allows the user to set a constraint on their portfolio’s beta using the betas calculated within the optimization.

        Args:
            relax_order (str): (optional) Lower the priority of the constraint, the earlier the constraint category is relaxed. Default value is None.
            lower_bound (Union[int, float]): (optional) Default value is -10000000000.
            upper_bound (Union[int, float]): (optional) Default value is 10000000000.
            is_soft (bool): (optional) Default value is False.
            linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.
            free_range_linear_penalty(LinearPenalty): (optional) Allows to specify a penalty for the holdings of the optimized portfolio.

        Returns:
            BetaConstraint dictionary

        """

        relax_order: Optional[str] = None
        lower_bound: Optional[Union[int, float]] = -10000000000
        upper_bound: Optional[Union[int, float]] = 10000000000
        is_soft: Optional[bool] = False
        linear_penalty: Optional[LinearPenalty] = None
        free_range_linear_penalty: Optional[FreeRangeLinearPenalty] = None

        @property
        def body(self):
            """
            Dictionary representation of BetaConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'BetaConstraint',
                "relaxOrder": self.relax_order,
                "upperBound": self.upper_bound,
                "lowerBound": self.lower_bound,
                "isSoft": self.is_soft,
                "linearPenalty": self.linear_penalty.body if self.linear_penalty is not None else None,
                "freeRangeLinearPenalty": self.free_range_linear_penalty.body if self.free_range_linear_penalty is not None else None
            }
            return body

    @dataclass()
    class FiveTenFortyRule(BaseDataClassValidator):
        """
        The 5/10/40 rule sets a holding constraint that limits the total weight of all issuers that represent more than 5% of the optimal portfolio to 40%, and limit any single issuer weight to 10% of the optimal portfolio. The user will have to upload data for userdata.issuer_id and specify the fieldQuerySettings

        Args:
            five (int, float): (optional) Default value is 5.
            ten (int, float): (optional) Default value is 10.
            forty (int, float): (optional) Default value is 40.

        Returns:
            FiveTenFortyRule dictionary

        """

        five: Optional[Union[int, float]] = 5
        ten: Optional[Union[int, float]] = 10
        forty: Optional[Union[int, float]] = 40

        @property
        def body(self):
            """
            Dictionary representation of FiveTenFortyRule constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'FiveTenFortyRule',
                "five": self.five,
                "ten": self.ten,
                "forty": self.forty
            }
            return body

    @dataclass()
    class RiskParityConstraint(BaseDataClassValidator):
        """
        Allows to set risk parity constraint and hence equalize the additive risk contribution of specified assets/factors.

        Args:
            risk_parity_type (str): (optional) Type of risk parity constraint. Default value is assetRiskParity. Allowed values are assetRiskParity, factorRiskParity, assetXsrRiskParity.
            can_use_excluded (bool): (optional) Determines whether assets/factors outside specified group can contribute to risk. Default value is True.
            reference_portfolio (str): (optional) If set, active risk contribution is calculated relative to specified portfolio. If not specified, portfolio risk contribution is used. Should be set if asset XSR risk parity is used.
            condition(str): (optional) Condition for group of constrained assets/factors.

        Returns:
            RiskParityConstraint dictionary

        """

        risk_parity_type: Optional[str] = "assetRiskParity"
        can_use_excluded: Optional[bool] = True
        reference_portfolio: Optional[str] = None
        condition: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of RiskParityConstraint constraint.

            Returns:
                dict: Dictionary representation of the constraint.
            """
            body = {
                "objType": 'RiskParityConstraint',
                "riskParityType": self.risk_parity_type,
                "canUseExcluded": self.can_use_excluded,
                "referencePortfolio": self.reference_portfolio,
                "condition": self.condition
            }
            return body
