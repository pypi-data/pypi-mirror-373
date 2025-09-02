import pandas as pd
import logging

from ...utils.metric import check_null, get_metric_values, search_subtype


class InitialPortfolioMetrics:
    """
    Displays initial portfolio metric for all sub metric types. It fetches and stores metrics output to different methods as per usage. Includes data for below SUB_TYPES:
    ``["UNREALIZED_GAIN_LOSS",
    "RISK",
    "ALL"]``
    """

    def __init__(self, metrics_response, account_id=None):
        self.logger = logging.getLogger(__name__)
        self.metrics_list = metrics_response['values']
        self.account_id = account_id
        if not self.metrics_list:
            self.logger.info('No optimizer result')

    @check_null
    def get_unrealized_gain_loss(self, date=None) -> pd.DataFrame:
        """
        Get unrealized gain/loss metrics from initial portfolio for the sub type UNREALIZED_GAIN_LOSS.
        """

        metric_sub_type = "UNREALIZED_GAIN_LOSS"
        columns = ['dataDate', 'gain', 'loss', 'net', 'longTermGain', 'shortTermGain',
                   'taxFreeGain', 'longTermLoss', 'shortTermLoss', 'taxFreeLoss',
                   'longTermNet', 'shortTermNet', 'taxFreeNet']

        if date:
            unrealized_gain_loss_dict = get_metric_values(metric_sub_type=metric_sub_type, date=date,
                                                          metrics_list=self.metrics_list)

            if self.account_id:
                key = f"compute_unrealized_gain_{self.account_id}"
                data = [item[key] for item in unrealized_gain_loss_dict[metric_sub_type] if key in item]
            else:
                key = "compute_unrealized_gain_default"
                data = [item[key] for item in unrealized_gain_loss_dict[metric_sub_type] if key in item]

            if not data:
                self.logger.info(f"No data found for account_id: {self.account_id}")
                return pd.DataFrame()

            data = data[0] if data else {}

            unrealized_gain_loss_df = pd.json_normalize(data)
            unrealized_gain_loss_df['dataDate'] = date
            unrealized_gain_loss_df.insert(0, 'dataDate', unrealized_gain_loss_df.pop('dataDate'))
            return unrealized_gain_loss_df[columns]

        else:
            combined_data = []
            _dict_n = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n['dataDates']

            for d in _list_dates:
                unrealized_gain_loss_dict = get_metric_values(metric_sub_type=metric_sub_type, date=d,
                                                              metrics_list=self.metrics_list)

                if self.account_id:
                    key = f"compute_unrealized_gain_{self.account_id}"
                    data = [item[key] for item in unrealized_gain_loss_dict[metric_sub_type] if key in item]
                else:
                    key = "compute_unrealized_gain_default"
                    data = [item[key] for item in unrealized_gain_loss_dict[metric_sub_type] if key in item]

                if data:
                    data = data[0] if data else {}
                    data['dataDate'] = d
                    combined_data.append(data)

            if not combined_data:
                self.logger.info("No data found for any date.")
                return pd.DataFrame()

            port_df = pd.json_normalize(combined_data)
            return port_df[columns]

    @check_null
    def get_risk(self, date=None) -> pd.DataFrame:
        """
        Get risk metrics from initial portfolio for the sub type RISK.
        """

        metric_sub_type = "RISK"

        if date:
            risk_dict = get_metric_values(metric_sub_type=metric_sub_type, date=date, metrics_list=self.metrics_list)

            if self.account_id:
                key = f"risk_{self.account_id}"
                data = [item[key] for item in risk_dict[metric_sub_type] if key in item]
            else:
                key = "risk_default"
                data = [item[key] for item in risk_dict[metric_sub_type] if key in item]

            if not data:
                self.logger.info(f"No data found for account_id: {self.account_id}")
                return pd.DataFrame()

            data = data[0] if data else {}

            if isinstance(data, str):
                data = {key: data}

            risk_df = pd.json_normalize(data)
            risk_df['dataDate'] = date
            risk_df.insert(0, 'dataDate', risk_df.pop('dataDate'))
            return risk_df

        else:
            combined_data = []
            _dict_n = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n['dataDates']

            for d in _list_dates:
                risk_dict = get_metric_values(metric_sub_type=metric_sub_type, date=d, metrics_list=self.metrics_list)

                if self.account_id:
                    key = f"risk_{self.account_id}"
                    data = [item[key] for item in risk_dict[metric_sub_type] if key in item]
                else:
                    key = "risk_default"
                    data = [item[key] for item in risk_dict[metric_sub_type] if key in item]

                if data:
                    data = data[0] if data else {}
                    if isinstance(data, str):
                        data = {key: data}
                    data['dataDate'] = d
                    data[key] = data.pop(key, None)

                    combined_data.append(data)

            if not combined_data:
                self.logger.info("No data found for any date.")
                return pd.DataFrame()

            risk_df = pd.json_normalize(combined_data)
            return risk_df

    @check_null
    def get_all(self, date=None) -> pd.DataFrame:
        """
        Get unrealized gain/loss and risk metrics from initial portfolio for the sub type ALL.
        """

        metric_sub_type = "ALL"

        if date:
            all_dict = get_metric_values(metric_sub_type=metric_sub_type, date=date, metrics_list=self.metrics_list)

            if self.account_id:
                risk_key = f"risk_{self.account_id}"
                gain_loss_key = f"compute_unrealized_gain_{self.account_id}"
            else:
                risk_key = "risk_default"
                gain_loss_key = "compute_unrealized_gain_default"

            data_risk = [item[risk_key] for item in all_dict.get("RISK", []) if risk_key in item]
            data_unrealized_gain_loss = [item[gain_loss_key] for item in all_dict.get("UNREALIZED_GAIN_LOSS", []) if
                                         gain_loss_key in item]

            if not data_risk:
                self.logger.info(f"No risk data found for account_id: {self.account_id}")
                return pd.DataFrame()

            data_risk = data_risk[0] if data_risk else {}
            if isinstance(data_risk, str):
                data_risk = {risk_key: data_risk}

            risk_df = pd.json_normalize(data_risk)
            risk_df['dataDate'] = date
            risk_df.insert(0, 'dataDate', risk_df.pop('dataDate'))

            if data_unrealized_gain_loss:
                data_unrealized_gain_loss = data_unrealized_gain_loss[0] if data_unrealized_gain_loss else {}
                un_gain_loss_df = pd.json_normalize(data_unrealized_gain_loss)
                combined_df = pd.concat([risk_df, un_gain_loss_df], axis=1)
            else:
                combined_df = risk_df

            return combined_df

        else:
            risk_data_list = []
            gain_loss_data_list = []
            _dict_n = search_subtype(name=metric_sub_type, metrics_list=self.metrics_list)
            _list_dates = _dict_n['dataDates']

            for d in _list_dates:
                risk_dict = get_metric_values(metric_sub_type="RISK", date=d, metrics_list=self.metrics_list)
                if self.account_id:
                    risk_key = f"risk_{self.account_id}"
                    risk_data = [item[risk_key] for item in risk_dict.get("RISK", []) if risk_key in item]
                else:
                    risk_key = "risk_default"
                    risk_data = [item[risk_key] for item in risk_dict.get("RISK", []) if risk_key in item]

                if risk_data:
                    risk_data = risk_data[0] if risk_data else {}
                    if isinstance(risk_data, str):
                        risk_data = {risk_key: risk_data}
                    risk_data['dataDate'] = d
                    risk_data[risk_key] = risk_data.pop(risk_key, None)
                    risk_data_list.append(risk_data)

                gain_loss_dict = get_metric_values(metric_sub_type="UNREALIZED_GAIN_LOSS", date=d,
                                                   metrics_list=self.metrics_list)
                if self.account_id:
                    gain_loss_key = f"compute_unrealized_gain_{self.account_id}"
                    gain_loss_data = [item[gain_loss_key] for item in
                                      gain_loss_dict.get("UNREALIZED_GAIN_LOSS", []) if gain_loss_key in item]
                else:
                    gain_loss_key = "compute_unrealized_gain_default"
                    gain_loss_data = [item[gain_loss_key] for item in
                                      gain_loss_dict.get("UNREALIZED_GAIN_LOSS", []) if gain_loss_key in item]

                if gain_loss_data:
                    gain_loss_data = gain_loss_data[0] if gain_loss_data else {}
                    gain_loss_data['dataDate'] = d
                    gain_loss_data_list.append(gain_loss_data)

            if not risk_data_list and not gain_loss_data_list:
                self.logger.info("No data found for any date.")
                return pd.DataFrame()

            risk_df = pd.DataFrame(risk_data_list)
            gain_loss_df = pd.DataFrame(gain_loss_data_list)

            combined_df = pd.merge(risk_df, gain_loss_df, on="dataDate", how="outer")
            return combined_df





