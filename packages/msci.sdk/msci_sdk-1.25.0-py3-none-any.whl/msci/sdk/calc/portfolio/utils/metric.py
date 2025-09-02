import functools
import json

import pandas as pd

from msci.sdk.calc.portfolio.utils.request_utility import logger


def get_metric_subtype_data(metrics_list, metric_sub_type, date):
    dict = get_metric_values(metrics_list, metric_sub_type, date)
    data = dict[metric_sub_type]
    sub_type_data_dict = json.loads(data)
    return sub_type_data_dict


def get_metric_values(metrics_list, metric_sub_type, date):
    dict_n = search_subtype(metrics_list, metric_sub_type)
    list_n = dict_n['values']
    list_dates = dict_n['dataDates']
    if date not in list_dates:
        raise ValueError("Date parameter is incorrect")
    index = list_dates.index(date)
    dict = list_n[index]
    return dict


def search_subtype(metrics_list, name):
    for metric in metrics_list:
        if metric['subType'] == name:
            return metric


def check_null(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'metrics_list') and self.metrics_list:
            return func(self, *args, **kwargs)
        else:
            logger.info('No optimizer result')
            return pd.DataFrame()

    return wrapper
