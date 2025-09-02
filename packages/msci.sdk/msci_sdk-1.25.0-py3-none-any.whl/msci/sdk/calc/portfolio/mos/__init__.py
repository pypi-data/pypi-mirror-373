from ..utils.utility import get_version
from ..utils.constants import MOS_VERSIONS_SUPPORTED

version = get_version()

if version == "1.4":
    from .v1_4.rule_based_nodes import RuleBasedNode, BenchmarkWeightMappings, GroupScheme, GroupByCustomRange
    from .v1_4.partial_optimiser import PartialOptimizationNode, ExposureGroupBy
    from .v1_4.mos_session import MOSSession
    from .v1_4.mos_config import SimulationSettings, Strategy, ReferenceUniverse, SolutionSettings, \
        CalculationContext, UniversePerAccount, BenchmarkPerAccount, CurrentPortfolioPerAccount, NodeListPerAccount, \
        RebalanceContext, FieldQueryDate, FieldQuerySetting, FieldDataDefault, ProxySetting, OptimizerMetrics, RiskModelSource, RiskModelDetails, DefaultFieldQuerySettings, \
        SpecificCovariance, FactorCovariance, FactorExposure, IdMappings, TriggerCalendar, TriggerDates, ShiftedTriggerCalendar, CompositeTrigger
    from .v1_4.profile import Profile, SolutionSettingsPerAccount
    from .v1_4.enums import IndexUniverseEnum, CalculationTypeEnum, TriggerCalendarEnum, \
        ScreenerTypeEnum, \
        CountryEnum, ComparisonSignEnum, ScopeEnum, ConstraintScopeEnum, ExclusionTypeEnum, RestrictiveLevelEnum, \
        WeightingEnum, ESGRatingEnum, TaxArbitrageGainEnum, \
        PortfolioTypeEnum, ValuationTypeEnum, MultiAccountStyleEnum
    from .v1_4.metrics import MetricsCalculation
    from .v1_4.client_portfolio import TaxLotPortfolio, ClientPortfolio, CashPortfolio, SimplePortfolio
    from .v1_4.constraints import ConstraintFactory, Bounds, OverallBound, GroupBound, SpecificBound, Aggregation, \
        CategoryOrder, AssetWeight, ConditionalAssetWeight, AssetTradeSize, NetTaxImpact, SpecificFactorBound, \
        GroupedFactorBound, LeverageConstraintBySide, CrossAccountAssetBoundTotalPosition, \
        CrossAccountMaxAssetTotalTradeType, LinearPenalty, FreeRangeLinearPenalty, \
        CrossAccountGroupedLinearBounds, CrossAccountGeneralLinearBounds, CrossAccountGeneralRatioBounds, \
        CrossAccountTradeThresholdOverallBounds, CrossAccountTradeThresholdAssetBounds, \
        CrossAccountTradeThresholdGroupBounds, TradeThresholdOverallBounds,TradeThresholdAssetBounds, TradeThresholdGroupBounds, \
        SimplePortfolioCondition, SimpleTaxLotCondition, ConditionalTaxLotTradingRule
    from .v1_4.full_optimizer_node import GenericObjectiveFunction, OptimizationSettings, \
        TaxOptimizationSetting, CashFlowOptSetting, FullSpecOptimizationNode, TaxArbitrage, DoNotTradeList, \
        DoNotTradeExpression, DoNotTradeListsAndExpressions, SimpleIdentification, CustomAttribute, PostRoundLotSettings, RiskTargetOptimization, RatioUtilityObjectiveFunction
    from .v1_4.templates import TaxAdvantagedModelTrackingTemplate, TaxNeutralTemplate, GainBudgetingTemplate, \
        MaxLossHarvestingTemplate, GainRealizationTemplate, GenericTaxTemplate, PureOptimizationTemplate, \
        InitialTETemplate, UnrealizedGainsTemplate, InitialPortfolioMetricsTemplate
    from .v1_4.user_datapoints import UserDataPoint
    from .v1_4.mso_templates import GenericTaxTemplateMSO, SleeveConfig, TaxAdvantagedModelTrackingTemplateMSO, \
        TaxNeutralTemplateMSO, GainBudgetingTemplateMSO, MaxLossHarvestingTemplateMSO, GainRealizationTemplateMSO
else:
    raise ValueError(f"MOS version {version} not supported. Supported versions are {MOS_VERSIONS_SUPPORTED}")
