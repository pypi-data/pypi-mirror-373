from enum import Enum
import warnings

class CalculationTypeEnum(Enum):
    REBALANCE = "REBALANCE"
    SIMULATION = "SIMULATION"
    EOD = "EOD"
    BACKCALCULATION = "BACKCALCULATION"

class TriggerCalendarEnum(Enum):
    FIRST_DAY_OF_MONTH = "FirstDayOfMonth"
    END_OF_MONTH = "LastDayOfMonth"
    DAILY = "Daily"
    QUARTERLY = "Quarterly"
    SEMI_ANNUALLY = "Semiannually"
    NEVER = "Never"
    LAST_DAY_OF_QUARTER = "LastDayOfQuarter"
    LAST_DAY_OF_HALF_YEAR = "LastDayOfHalfYear"


class RestrictiveLevelEnum(Enum):
    MOST_RESTRICTIVE = "MOST_RESTRICTIVE"
    HIGHLY_RESTRICTIVE = "HIGHLY_RESTRICTIVE"
    MODERATELY_RESTRICTIVE = "MODERATELY_RESTRICTIVE"
    LEAST_RESTRICTIVE = "LEAST_RESTRICTIVE"


class IndexUniverseEnum(Enum):
    MSCI_USA = "UNX000000034908161"
    MSCI_JAPAN = "UNX000000034908141"
    MSCI_CANADA = "UNX000000034908111"
    MSCI_EUROPE_AND_MIDDLE_EAST = "UNX000000046916733"


class ExclusionTypeEnum(Enum):
    CIVILIAN_FIRE_ARM_EXCLUSION = "CivilianFirearmsExclusion"
    TOBACCO_EXCLUSION = "TobaccoExclusion"
    CONTROVERSIAL_WEAPONS_EXCLUSION = 'ControversialWeaponsExclusion'
    NUCLEAR_WEAPONS_EXCLUSIONS = "NuclearWeaponsExclusion"
    ABORTION_EXCLUSION = "AbortionExclusion"
    ADULT_ENTERTAINMENT_EXCLUSION = "AdultEntertainmentExclusion"
    GAMBLING_EXCLUSION = "GamblingExclusion"
    STEM_CELL_RESEARCH_EXCLUSION = "StemCellResearchExclusion"
    ALCOHOL_EXCLUSION = "AlcoholExclusion"
    GENETICALLY_MODIFIED_ORGANISMS_EXCLUSION = "GeneticallyModifiedOrganismsExclusion"


class ESGRatingEnum(Enum):
    CCC = "CCC"
    B = "B"
    BB = "BB"
    BBB = "BBB"
    A = "A"
    AA = "AA"
    AAA = "AAA"


class ScreenerTypeEnum(Enum):
    ScreenCountry = "ScreenCountry"
    ScreenEsgScore = "ScreenEsgScore"
    ScreenIndustry = "ScreenIndustry"
    ScreenIndustryGroup = "ScreenIndustryGroup"
    ScreenSubIndustry = "ScreenSubIndustry"
    ScreenCarbonTransitionCategory = "ScreenCarbonTransitionCategory"
    ScreenSector = "ScreenSector"


class ScopeEnum(Enum):
    UNIVERSE = "universe"
    PORTFOLIO = "portfolio"


class CountryEnum(Enum):
    FRANCE = "FR"
    USA = "US"
    JAPAN = "JP"
    INDIA = "IN"


class ComparisonSignEnum(Enum):
    EQUAL = "EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"


class RiskModelEnum(Enum):
    GEMLTL = "GEMLTL"


class ConstraintScopeEnum(Enum):
    """
    net, long, short
    """
    NET = "net"
    LONG = "long"
    SHORT = "short"


class WeightingEnum(Enum):
    BENCHMARK = 'BENCHMARK'
    CAP = 'CAP'
    EQUAL = 'EQUAL'
    REPLICATE = 'REPLICATE'


class ExposureGroupBy(Enum):
    """
    Exposure Group Enum
    """
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    COUNTRY = "COUNTRY"


class TaxArbitrageGainEnum(Enum):
    CAPITAL_NET = "capitalNet"
    CAPITAL_GAIN = "capitalGain"
    CAPITAL_LOSS = "capitalLoss"


class PortfolioTypeEnum(Enum):
    LONG_ONLY = "LONG_ONLY"
    LONG_SHORT = "LONG_SHORT"
    # DOLLAR_NEUTRAL = "DOLLAR_NEUTRAL"


class ValuationTypeEnum(Enum):
    NET = "NET"
    LONG_SIDE = "LONG_SIDE"
    USER_DEFINED = "USER_DEFINED"


class MultiAccountStyleEnum(Enum):
    MULTI_SLEEVE = "MULTI_SLEEVE"
    MULTI_ACCOUNT = "MULTI_ACCOUNT"

