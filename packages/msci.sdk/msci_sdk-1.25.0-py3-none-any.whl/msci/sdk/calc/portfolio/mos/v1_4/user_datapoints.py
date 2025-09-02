import json
import logging
import time

import requests as r
from pandas import json_normalize

from ...utils.utility import MOSException, validate_date
from ...utils.request_utility import get, post, delete


class UserDataPoint:
    """
        Upload and fetch user defined datapoints.
    """

    def __init__(self, base_url, headers, ssl_verify):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.headers = headers
        self.ssl_verify = ssl_verify

    def get_available_datapoints(self) -> list:
        """
        List datapoints available to be used within the strategy nodes.
        """
        resp_obj = get(url=self.base_url + "datapoints", headers=self.headers, ssl_verify=self.ssl_verify)
        if resp_obj.status_code == 200:
            resp = resp_obj.json()
        else:
            self.logger.error(f"Error in get available datapoint : {resp_obj.text}")
            raise MOSException(f"Error in get available datapoint : {resp_obj.text}")

        return resp

    def upload_userdata(self, date, dp, dp_type, asset_id_type, data_dict):
        """
        Update/write user data datapoint.

        Args:
            date (str) :  Date for which data is to be uploaded.
            dp (str) : Datapoint to be uploaded. Datapoint must start with 'userdata.' Eg: userdata.my_datapoint_name.
            dp_type (str) : Type of datapoint.
            asset_id_type (str) : Type of asset ID.
            data_dict (dict) : Dictionary of datapoint values.
                        eg: {
                            "x": 1000000,
                            "y": 2000000,
                            "z": 3000000
                            }

        """

        ## Validate if dp already registered

        resp_obj = get(url=self.base_url + "userdata/registration", headers=self.headers, ssl_verify=self.ssl_verify)
        if resp_obj.status_code != 200:
            self.logger.error(f"Error in fetching registered user datapoint : {resp_obj.text}")
            raise MOSException(f"Error in fetching registered user datapoint : {resp_obj.text}")

        if not eval(resp_obj.text):
            self.logger.info(f"No data fetched for existing registered datapoints.")
            self.__register_dp(dp, dp_type)
            self.__upload_dp(dp, asset_id_type, data_dict, date)

        else:
            registered_dp = json_normalize(json.loads(resp_obj.text))

            if dp in registered_dp['datapointName'].to_list():
                if registered_dp[registered_dp['datapointName'] == dp]['dataType'].item() == dp_type:
                    self.logger.info(
                        f"User datapoint {dp} with datatype {dp_type} is already registered. Skipping registration and uploading datapoint.")
                    self.__upload_dp(dp, asset_id_type, data_dict, date)
                else:
                    self.logger.error(
                        f"User datapoint {dp} is already registered with datatype {dp_type}. Cannot upload same datapoint with different datatype.")
                    raise MOSException(
                        f"Error in user datapoint registration. Cannot register datapoint with different datatype. Kindly provide new datapoint name.")

            else:
                self.__register_dp(dp, dp_type)
                self.__upload_dp(dp, asset_id_type, data_dict, date)

    def __register_dp(self, dp, dp_type):
        """
        Register the new datapoint
        """
        data = {
            "datapointName": dp,
            "dataType": dp_type
        }

        resp_obj = post(url=self.base_url + "userdata/registration", headers=self.headers, data=data, ssl_verify=self.ssl_verify)
        if resp_obj.status_code == 200:
            self.logger.info(f"User datapoint {dp} registered successfully.")
        else:
            self.logger.error(f"Error in user datapoint registration : {resp_obj.text}")
            raise MOSException(f"Error in user datapoint registration : {resp_obj.text}")

    def __upload_dp(self, dp, asset_id_type, data_dict, date):
        """
        Uploading new datapoint
        """

        dp_dict = {
            "idType": asset_id_type,
            "data": data_dict
        }
        resource = f"userdata/data/{dp}/date/{date}"

        resp_obj = post(url=self.base_url+resource, headers=self.headers, data=dp_dict, ssl_verify=self.ssl_verify)
        if resp_obj.status_code == 200:
            self.logger.info(f"User datapoint {dp} added successfully for date {date}.")
        else:
            self.logger.error(f"Error in user datapoint addition : {resp_obj.text}")
            raise MOSException(f"Error in user datapoint addition : {resp_obj.text}")

    def get_user_datapoints(self) -> list:
        """
        List datapoints previously uploaded.

        """
        resource = "userdata/data"
        resp_obj = get(self.base_url+resource, headers=self.headers, ssl_verify=self.ssl_verify)
        return resp_obj.json()

    def get_user_datapoint_dates(self, dp) -> list:
        """
        List uploaded dates for given datapoint.

        Args:
             dp (str) : Datapoint to retrieve.

        """
        resource = f"userdata/data/{dp}/date"
        resp_obj = get(self.base_url+resource, headers=self.headers, ssl_verify=self.ssl_verify)
        return resp_obj.json()

    def get_user_datapoint_details(self, dp, date) -> dict:
        """
        Read back the data uploaded for datapoint on the given date.

        Args:
             dp (str) : Datapoint to retrieve.
             date (str) :  Date to retrieve.
        """
        validate_date(date)
        resource = f"userdata/data/{dp}/date/{date}"
        resp_obj = get(self.base_url+resource, headers=self.headers, ssl_verify=self.ssl_verify)
        return resp_obj.json()


class UserRiskDataUpload:
    """
        Upload and fetch user risk data defined datapoints.
    """

    def __init__(self, base_url, headers, ssl_verify):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.headers = headers
        self.ssl_verify = ssl_verify

    def upload_user_risk_data(self, data_date, risk_model, factor_covariance, factor_exposure, specific_covariance, id_mappings=None):
        """
        Register and upload risk model data for factor covariance, factor exposure, and specific covariance

        Args:
            risk_model (str): The name of the datapoint the data block is for.
            data_date (str): The date of the data block being uploaded.
            id_mappings (List[IdMappings]): (Optional) A list of IdMappings that map asset identifiers to their respective types and reference IDs.
            factor_covariance (FactorCovariance): FactorCovariance defines the covariance between different factor ids given.
            factor_exposure (FactorExposure): FactorExposure defines the exposure of securities to different factor ids given.
            specific_covariance (SpecificCovariance): SpecificCovariance defines the specific covariance and the associated values between different security ids given.

        """

        combined_id_mappings = {}
        if id_mappings:
            for mapping in id_mappings:
                if mapping.asset_id_type not in combined_id_mappings:
                    combined_id_mappings[mapping.asset_id_type] = {}
                combined_id_mappings[mapping.asset_id_type][mapping.reference_id] = mapping.asset_id

        data_dict = {
            "idMappings": combined_id_mappings,
            "factorCovariance": factor_covariance.body,
            "factorExposure": factor_exposure.body,
            "specificCovariance": specific_covariance.body
        }


        validate_date(data_date)
        resp_obj = post(url=self.base_url + f"/userdata/riskData/{risk_model}/date/{data_date}",
                        headers=self.headers, data=data_dict, ssl_verify=self.ssl_verify)


        if resp_obj.status_code == 200:
            self.logger.info(f"User datapoint added successfully for date {data_date}.")
        else:
            self.logger.error(f"Error in user datapoint addition : {resp_obj.text}")
            raise MOSException(f"Error in user datapoint addition : {resp_obj.text}")


    def get_user_risk_data(self, data_date, risk_model) -> dict:
        """
        Read back the data uploaded for risk model on the given date.

        Args:
            risk_model (str): The name of the datapoint the data block is for.
            data_date (str): The date of the data block being uploaded.

        """
        validate_date(data_date)
        resp_obj = get(url=self.base_url + f"/userdata/riskData/{risk_model}/date/{data_date}",
                       headers=self.headers, ssl_verify=self.ssl_verify)

        print(resp_obj)
        return resp_obj.json()

    def delete_user_risk_data(self, data_date, risk_model):
        """
        Delete user risk data upload of dataset for a single day.

        Args:
            risk_model (str): The name of the datapoint the data block is for.
            data_date (str): The date of the data block being uploaded.

        """
        validate_date(data_date)
        response = delete(url=self.base_url + f"/userdata/riskData/{risk_model}/date/{data_date}",
                            headers=self.headers, ssl_verify=self.ssl_verify)

        if response.ok:
            return response
        else:
            self.logger.error(f"Error in delete_position_by_id {response.text}")
            raise MOSException(f"Error in delete_position_by_id {response.text}")

    def delete_user_risk_whole_data(self, risk_model):
        """
        Delete user risk data for all dates.

        Args:
            risk_model (str): The name of the datapoint the data block is for.

        """
        response = delete(url=self.base_url + f"/userdata/riskData/{risk_model}/deleteWholeData",
                            headers=self.headers, ssl_verify=self.ssl_verify)

        if response.ok:
            return response
        else:
            self.logger.error(f"Error in delete_position_by_id {response.text}")
            raise MOSException(f"Error in delete_position_by_id {response.text}")

    def get_risk_model_names(self) -> list:
        """
        List all user risk model names uploaded.

        """
        resp_obj = get(url=self.base_url + f"/userdata/riskData",
                       headers=self.headers, ssl_verify=self.ssl_verify)
        return resp_obj.json()


    def get_user_risk_data_dates(self, risk_model) -> list:
        """
        List uploaded dates for given risk model.

        Args:
            risk_model (str): The name of the datapoint the data block is for.

        """
        resp_obj = get(url=self.base_url + f"/userdata/riskData/{risk_model}/dates",
                       headers=self.headers, ssl_verify=self.ssl_verify)
        return resp_obj.json()

    def get_risk_model_raw_data(self, risk_model, data_date) -> dict:
        """
        Read back the raw data uploaded for risk model on the given date.

        Args:
            risk_model (str): The name of the datapoint the data block is for.
            data_date (str): The date of the data block being uploaded.

        """
        resp_obj = get(url=self.base_url + f"/userdata/riskData/{risk_model}/date/{data_date}/raw",
                       headers=self.headers, ssl_verify=self.ssl_verify)

        print(resp_obj.url)
        return resp_obj.json()


