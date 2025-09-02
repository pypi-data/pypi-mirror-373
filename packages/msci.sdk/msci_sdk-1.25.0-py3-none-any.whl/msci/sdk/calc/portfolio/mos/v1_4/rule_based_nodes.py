from dataclasses import dataclass
from typing import List, Optional, Union
from .enums import ScreenerTypeEnum, ExclusionTypeEnum, \
    RestrictiveLevelEnum, ComparisonSignEnum, ESGRatingEnum, WeightingEnum
from ...utils.dataclass_validations import BaseDataClassValidator


@dataclass
class GroupByCustomRange(BaseDataClassValidator):
    """
    min_value (int) : min_value of range
    max_value (int) : max_value of the range
    """
    min_value: int
    max_value: int

    @property
    def body(self):
        """
        Dictionary representation of GroupByCustomRange node

        Returns:
            dict: dictionary representation of the node
        """
        return {
            "minValue": self.min_value,
            "maxValue": self.max_value
        }


@dataclass
class GroupScheme(BaseDataClassValidator):
    """
    field_name (str) :
    group_by_custom_range (List[GroupByCustomRange]) :

    """
    field_name: str
    group_by_custom_range: List[GroupByCustomRange]

    @property
    def body(self):
        """
        Dictionary representation of GroupByCustomRange node

        Returns:
            dict: dictionary representation of the node
        """
        return {
            "fieldName": self.field_name,
            "groupByCustomRange": [v.body for v in self.group_by_custom_range]
        }


@dataclass
class BenchmarkWeightMappings(BaseDataClassValidator):
    """
    benchmark reference and its weight

    Args:
        benchmark_ref (string): reference benchmark
        weight (int, float): weight

    Returns:
            body (dict): dictionary representation of BenchmarkWeightMappings
    """

    benchmark_ref: str
    weight: Union[float, int]

    @property
    def body(self):
        """
        Dictionary representation of BenchmarkWeightMappings node

        Returns:
            dict: dictionary representation of the node
        """
        return {
            "benchmarkRef": self.benchmark_ref,
            "weight": self.weight
        }


class RuleBasedNode:
    """
        Represents all rule based nodes.
    """

    @dataclass
    class Filter(BaseDataClassValidator):
        """Represents all filter nodes.

        Args:
            condition (str): Generic expression based filtering condition, e.g. “equity.security.industry_code == 30203010”.
            scope (str): (optional) Scope of the filter. Default value is portfolio.
            keep (bool): (optional) Indicates whether to keep or drop results of the filter. Default value is False.

        Returns:
            body (dict): Dictionary representation of Filter node.
        """

        condition: str
        scope: Optional[str] = "portfolio"
        keep: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of Filter node.

            Returns:
                dict: Dictionary representation of the node.
            """

            return {
                    "scope": self.scope,
                    "filterConditional": self.condition,
                    "keep": self.keep,
                    "objType": "Filter"
            }

    @dataclass
    class Screen(BaseDataClassValidator):
        """Represents all screen nodes.

        Args:
            screener_type (ScreenerTypeEnum): Filter companies based on different criteria, e.g. carbon transition category or ESG score.
            screener_value ([str, int]): Value based on which companies are filtered, e.g. user specified ESG score. Type depends on screener_type.
            comparator (ComparisonSignEnum): Comparator values allowed ["EQUAL", "GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL", "NOT_EQUAL"].
            scope (str): (optional) Scope of the filter. Default value is portfolio.
            keep (bool): (optional) Indicates whether to keep or drop results of the screening. Default value is False.

        Returns:
            body (dict): Dictionary representation of Screen node.
        """

        screener_type: ScreenerTypeEnum
        screener_value: Union[str, int]
        comparator: ComparisonSignEnum
        scope: Optional[str] = "portfolio"
        keep: Optional[bool] = False

        @property
        def body(self):
            """
            Dictionary representation of Screen node.

            Returns:
                dict: Dictionary representation of the node.
            """
            self.screener_name = self.screener_type.value

            screen_body = {
                    "objType": self.screener_name,
                    "keep": self.keep,
                    "comparator": self.comparator.value,
                    "scope": self.scope,
                    "nodeId": self.screener_name
            }

            if self.screener_name == 'ScreenCarbonTransitionCategory':
                screen_body["esgTransitionCategory"] = self.screener_value

            if self.screener_name == 'ScreenCountry':
                if isinstance(self.screener_value, str):
                    screen_body["countrySymbol"] = self.screener_value
                if isinstance(self.screener_value, int):
                    screen_body["countryId"] = self.screener_value

            if self.screener_name == 'ScreenEsgScore':
                screen_body["value"] = self.screener_value

            if self.screener_name == 'ScreenIndustry':
                screen_body["industryCode"] = self.screener_value

            if self.screener_name == 'ScreenSector':
                screen_body["sectorCode"] = self.screener_value

            if self.screener_name == 'ScreenIndustryGroup':
                screen_body["industryGroupCode"] = self.screener_value

            if self.screener_name == 'ScreenSubIndustry':
                screen_body["subIndustryCode"] = self.screener_value

            return screen_body

    @dataclass
    class BISRExclusionNode(BaseDataClassValidator):
        """
        A node representing a BISR exclusion, applied ahead of other portfolio construction operations.

        Args:
            category (ExclusionTypeEnum): Must be one of ``[
                        'CivilianFirearmsExclusion',
                        'ControversialWeaponsExclusion',
                        'NuclearWeaponsExclusion',
                        'AbortionExclusion',
                        'AdultEntertainmentExclusion',
                        'GamblingExclusion',
                        'StemCellResearchExclusion',
                        'TobaccoExclusion',
                        'AlcoholExclusion',
                        'GeneticallyModifiedOrganismsExclusion'
                        ]``
            level (RestrictiveLevelEnum): Must be one of ``[
                        'MOST_RESTRICTIVE',
                        'HIGHLY_RESTRICTIVE',
                        'MODERATELY_RESTRICTIVE',
                        'LEAST_RESTRICTIVE']``
            scope (str): (optional) Scope of the filter. Default value is universe.
            active (bool): (optional) Indicates if active or inactive. Default value is True.
            coal (bool) : (optional) Default value is False.
            fossil_fuel (bool) : (optional) Default value is False.

        Returns:
            body (dict): dictionary representation of Exclusion node.
        """

        exclusion_type: ExclusionTypeEnum
        level: RestrictiveLevelEnum
        scope: Optional[str] = 'universe'
        active: Optional[bool] = True

        @property
        def body(self):
            """MOS form of Exclusion node.

            Returns:
                body (dict): Dictionary representation of the node.
            """

            _body = {
                    "objType": self.exclusion_type.value,
                    "scope": self.scope,
                    "level": self.level.value,
                    "active": self.active
            }

            return _body

    @dataclass
    class ClimateExclusions(BaseDataClassValidator):
        """
        Exclusion node for climate.

        Args:
            scope (str): (optional) Scope of the filter. Default value is universe.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): dictionary representation of ClimateExclusions node.

        """

        scope: Optional[str] = 'universe'
        active: Optional[bool] = True
        coal: Optional[bool] = False
        fossil_fuels: Optional[bool] = False

        @property
        def body(self):
            """MOS form of ClimateExclusions node.

            Returns:
                body (dict): Dictionary representation of the node.
            """

            _body = {
                    "objType": "ClimateExclusions",
                    "scope": self.scope,
                    "active": self.active,
                    "coal": self.coal,
                    "fossilFuels": self.fossil_fuels
            }

            return _body

    @dataclass
    class SevereESGControversiesExclusion(BaseDataClassValidator):
        """
        Exclusion node for severe ESG controversies.

        Args:
            scope (str): (optional) Scope of the filter. Default value is universe.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): dictionary representation of SevereESGControversiesExclusion node.

        """

        scope: Optional[str] = 'universe'
        active: Optional[bool] = True

        @property
        def body(self):
            """MOS form of SevereESGControversiesExclusion node.

            Returns:
                body (dict): Dictionary representation of the node.
            """

            _body = {
                    "objType": "SevereESGControversiesExclusion",
                    "scope": self.scope,
                    "active": self.active
            }

            return _body

    @dataclass
    class MinimumEligibleESGRatingExclusion(BaseDataClassValidator):
        """
        Exclude ESG ratings below certain level

        Args:
            level (ESGRatingEnum): Must be one of ``[
                        'AAA',
                        'AA',
                        'A',
                        'BBB',
                        'BB',
                        'B',
                        'CCC']``
            scope (str): (optional) Scope of the filter. Default value is universe.
            active (bool): (optional) Indicates if active or inactive. Default value is True.

        Returns:
            body (dict): dictionary representation of MinimumEligibleESGRatingExclusion node.

        """

        level: ESGRatingEnum
        scope: Optional[str] = 'universe'
        active: Optional[bool] = True

        @property
        def body(self):
            """MOS form of MinimumEligibleESGRatingExclusion node.

            Returns:
                body (dict): Dictionary representation of the node.
            """

            _body = {
                    "objType": "MinimumEligibleESGRatingExclusion",
                    "scope": self.scope,
                    "level": self.level.value,
                    "active": self.active
            }

            return _body

    @dataclass
    class UniverseReplicationLayer(BaseDataClassValidator):
        """Replicate the universe as the current result portfolio using specified weighting method

        Args:
            weighting (WeightingEnum): Weighting enum.
            benchmark_ref (str): Optional. Reference benchmark.

        Returns:
            body (dict): Dictionary representation of UniverseReplicationLayer.
        """

        weighting: WeightingEnum
        benchmark_ref: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of UniverseReplicationLayer objective node

            Returns:
            dict : dictionary representation of the node
            """

            body = {
                    "objType": "UniverseReplicationLayer",
                    "weighting": self.weighting.value,
                    "benchmarkRef": self.benchmark_ref,
            }

            return body

    @dataclass
    class RankDrop(BaseDataClassValidator):
        """	Rank and sort assets in "universe"|benchmarkRef|"portfolio" by a field
            and then drop (or keep) a certain number of assets

        Args:
            scope (str): scope
            rank_by (str): Rank By
            ascending (bool): True if Ascending else False for Descending
            drop (bool): Keep or Drop.
            top_quantity (int): Top Quantity
            bottom_quantity (int):  Bottom Quantity
            group_by (str): Group by

        Returns:
            body (dict): dictionary representation of RankDrop
        """
        scope: str
        rank_by: str
        ascending: Optional[bool] = None
        keep: Optional[bool] = False
        top_quantity: Optional[int] = None
        bottom_quantity: Optional[int] = None
        group_by: Optional[str] = None

        @property
        def body(self):
            """
            Dictionary representation of UniverseReplicationLayer objective node

            Returns:
            dict : dictionary representation of the node
            """

            body = {
                    "objType": "RankDrop",
                    "scope": self.scope,
                    "rankBy": self.rank_by,
                    "ascending": self.ascending,
                    "keep": self.keep,
                    "topQuantity": self.top_quantity,
                    "bottomQuantity": self.bottom_quantity,
                    "groupBy": self.group_by
            }

            return body

    @dataclass
    class Quantiles(BaseDataClassValidator):
        """

        Args:
            quantile (int): Quantile
            quantile_index (int): quantile Index
            attribute (str): attribute
            scope (str): scope


        Returns:
            body (dict): dictionary representation of Quantiles
        """
        quantile: int
        quantile_index: int
        attribute: str
        scope: str

        @property
        def body(self):
            """
            Dictionary representation of Quantiles objective node

            Returns:
            dict : dictionary representation of the node
            """

            body = {
                    "objType": "Quantiles",
                    "quantile": self.quantile,
                    "quantileIndex": self.quantile_index,
                    "attribute": self.attribute,
                    "scope": self.scope,
            }

            return body

    class PromoteBenchmarkLayer:
        """Promote or mix the given benchmark(s) a chosen benchmark to be the result portfolio (which can then be
           further filtered etc)

        """

        @dataclass
        class CompositeBenchmarkReference(BaseDataClassValidator):
            """
            Args:
                composite_benchmark_ref (str): Array of benchmarks to promote with weightings of each.

            Returns:
                body (dict): dictionary representation of Composite node
            """
            composite_benchmark_ref: List[BenchmarkWeightMappings]

            @property
            def body(self):
                """
                Dictionary representation of Composite node

                Returns:
                dict : dictionary representation of the node
                """

                body = {
                        "objType": "CompositeBenchmarkReference",
                        "compositeBenchmarkRef": [a.body for a in self.composite_benchmark_ref]
                }

                return body

        @dataclass
        class SingleBenchmarkReference(BaseDataClassValidator):
            """
            Args:
                benchmark_ref (str): Reference benchmark.

            Returns:
                body (dict): dictionary representation of Single node
            """
            benchmark_ref: str

            @property
            def body(self):
                """
                Dictionary representation of Single node

                Returns:
                dict : dictionary representation of the node
                """

                body = {
                        "objType": "SingleBenchmarkReference",
                        "benchmarkRef": self.benchmark_ref,
                }

                return body
