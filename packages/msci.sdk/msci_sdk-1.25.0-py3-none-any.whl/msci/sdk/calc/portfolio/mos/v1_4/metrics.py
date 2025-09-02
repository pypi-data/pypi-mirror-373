import pandas as pd
import datetime


class MetricsCalculation:
    """
    Describes the metrics to compute as part of the request.

    Args:
        metric_list (list) : Based on calculation type, list of matrices can be configured to compute portfolio or asset level information. Available metrics are:
            ``[("LEVEL", "ABSOLUTE"),
            ("LEVEL", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "ABSOLUTE"),
            ("PERFORMANCE", "ABSOLUTE_BMK"),
            ("PERFORMANCE", "RELATIVE"),
            ("SIMPLE", "NUM_CONS"),
            ("SIMPLE", "NUM_CONS_BMK"),
            ("TURNOVER", "STANDARD"),
            ("OPTIMIZER_RESULT", "TAX_BY_GROUP_FULL_PORTFOLIO"),
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
            ("INITIAL_PORTFOLIO", "RISK")]``
    """

    def __init__(
            self,
            metric_list=None,
    ):
        self.metric_list = metric_list

    @property
    def body(self):
        return {
            "metrics": [
                {
                    "objType": "MetricDefinition",
                    "metricType": mtype,
                    "subType": msubtype,
                }
                for (mtype, msubtype) in self.metric_list
            ]
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"


ON_REBAL_FIELDS = [
    "OPTIMIZER_RESULT-OPTIMIZATION_STATUS",
    "OPTIMIZER_RESULT-INPUT_DATA_ERRORS",
    "OPTIMIZER_RESULT-PORTFOLIO_SUMMARY",
    "OPTIMIZER_RESULT-TRADE_LIST",
    "OPTIMIZER_RESULT-ASSET_DETAILS",
    "OPTIMIZER_RESULT-PROFILE_DIAGNOSTICS",
    "OPTIMIZER_RESULT-TAX_BY_GROUP_FULL_PORTFOLIO",
    "OPTIMIZER_RESULT-ASSET_REALIZED_GAIN",
    "OPTIMIZER_RESULT-POST_OPT_ROUNDLOTTING_ERRORS",
    "INITIAL_PORTFOLIO-ALL",
    "INITIAL_PORTFOLIO-UNREALIZED_GAIN_LOSS",
    "INITIAL_PORTFOLIO-RISK"
]

ON_BDAY_FIELDS = [
    "PERFORMANCE-ABSOLUTE",
    "PERFORMANCE-ABSOLUTE_BMK",
    "PERFORMANCE-RELATIVE",
    "SIMPLE-NUM_CONS",
    "SIMPLE-NUM_CONS_BMK",
    "TURNOVER-STANDARD",
    "INFORMATION_RATIO-STANDARD",
    "LEVEL-ABSOLUTE",
    "LEVEL-ABSOLUTE_BMK",
    "TRACKING_ERROR-STANDARD",
    "ACTIVE_RETURN-STANDARD",
]


def to_dataframe(metric_values, which_fields):
    """
    Converts to dataframe for metric results and provided fields.
    """
    flat = {
        vv['metricType']
        + "-"
        + vv['subType']: [list(aa.values())[0] if aa else 0.0 for aa in vv['values']]
        for vv in metric_values
    }
    dates = {
        vv['metricType'] + "-" + vv['subType']: vv['dataDates'] for vv in metric_values
    }
    on_fields = [f for f in which_fields if f in flat.keys()]
    on_dict = {k: flat[k] for k in on_fields}
    if len(on_fields) > 0:
        on_dict["data_dates"] = [
            datetime.datetime.strptime(dd, "%Y-%m-%d") for dd in dates[on_fields[0]]
        ]

    df = pd.DataFrame(on_dict)

    return df


class Metrics:
    """
    Retrieve all the metrics computed by a job.

    Args:
        all_metrics : Metrics results stored in raw JSON format.
    """
    def __init__(self, all_metrics):
        self.metric_results = all_metrics

    def to_dict(self):
        """
        Converts to dictionary.
        """
        metrics_dict = {
            vv["metricType"] + "-" + vv["subType"]: dict(vv)
            for vv in self.metric_results["values"]
        }
        return metrics_dict

    def to_dataframe(self):
        """
        Converts to dataframe for all the metrics fields on business day.

        Note: This works for calculation types BACKCALCULATION and SIMULATION.
        """
        return to_dataframe(self.metric_results["values"], ON_BDAY_FIELDS)

    def to_rebal_dataframe(self):
        """
        Converts to dataframe for all the metrics fields on rebalanced day.
        """
        return to_dataframe(self.metric_results["values"], ON_REBAL_FIELDS)

