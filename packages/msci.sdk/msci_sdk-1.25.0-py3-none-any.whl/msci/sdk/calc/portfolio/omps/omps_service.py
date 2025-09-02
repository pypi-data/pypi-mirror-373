import requests
from os import environ
import pandas as pd
from typing import List
import json
import logging
from ..utils.utility import get_token, get_client_environ, generate_parameters, env_resolver, OMPSException
from ..utils import constants
from .... import settings


class OMPSSession:

    def __init__(self, client_id=None, client_secret=None, refresh_token: bool = False):
        settings.setup_logging()
        self.logger = logging.getLogger(__name__)
        env_dict = env_resolver('OMPS')

        client_id, client_secret = get_client_environ(client_id, client_secret)

        if not client_id or not client_secret:
            self.logger.error("MSCI_MOS_API_KEY and MSCI_MOS_API_SECRET not in the environment")
            raise ValueError("Please specify MSCI_MOS_API_KEY and  MSCI_MOS_API_SECRET in the environment.")

        self.client_id = client_id
        self.client_secret = client_secret

        self.omps_token_url = env_dict["omps_token_url"]
        self.omps_base_url = env_dict["omps_base_url"]
        self.ssl_verify = True

        token = get_token(self.omps_token_url, self.client_id, self.client_secret, env_dict["omps_audience"],
                          'omps', refresh_token=refresh_token)
        self._token = token
        self._headers = {'Authorization': f'Bearer {self._token}',
                         'Content-type': 'application/json',
                         "X-Src-System": "msci-sdk"
                         }

        self.logger.debug(f"OMPS session created with base url : {self.omps_base_url}")

    def health_check(self):
        """Ping the service to make sure its alive."""

        url = f'{self.omps_base_url}/health/alivecheck'
        response = requests.get(url, headers=self._headers, verify=self.ssl_verify)
        if response.status_code == 200:
            return response.text
        else:
            self.logger.error(f"Error in omps health check {response.text}")
            raise OMPSException(f"Error in omps health check {response.text}")

    def get_portfolios(self, **kwargs) -> pd.DataFrame:
        """
        Get the list of descriptions of portfolios

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios

        Args:
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of as-of-dates of the given portfolio.
        """
        parameter_str = generate_parameters(**kwargs)
        url = f'{self.omps_base_url}/portfolios{parameter_str}'
        response = requests.get(url, headers=self._headers, verify=self.ssl_verify)
        if response.status_code == 200:
            return pd.json_normalize(response.json())
        else:
            self.logger.error(f"Error in getting portfolios {response.text}")
            raise OMPSException(f"Error in getting portfolios {response.text}")

    def get_portfolio_asofdates_by_id(self, portfolio_id: str, **kwargs) -> pd.DataFrame:
        """
        Get the available as_of_date for portfolio by ID.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios/{portfolio_id}

        Args:
            portfolio_id: Portfolio ID.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of as-of-dates of the given portfolio.
        """

        if not portfolio_id:
            raise ValueError('portfolio_id must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}{parameter_str}'
        response = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            res_dict = json.loads(response.text)
            if 'asOfDates' in res_dict:
                asofdates = res_dict['asOfDates']
                return pd.DataFrame(asofdates)
            else:
                self.logger.info(f"No as of dates for portfolio {portfolio_id}")
                return pd.DataFrame()
        else:
            self.logger.error(f"Error in get portfolio  {response.text}")
            raise OMPSException(f"Error in get portfolio  {response.text}")

    def get_portfolio_of_date(self, portfolio_id: str, as_of_date: str, **kwargs) -> dict:
        """
        Get a portfolio as of a certain date.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not portfolio_id or not as_of_date:
            raise ValueError(constants.PORTFOLIO_ID_AS_OF_DATE_ERROR)

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}{parameter_str}'
        resp = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if resp.ok:
            portfolio = json.loads(resp.text)
            return portfolio
        else:
            self.logger.error(f"Error in get_portfolio_of_date {resp.text}")
            raise OMPSException(f"Error in get_portfolio_of_date {resp.text}")

    def get_positions_asofdate(self, portfolio_id: str, as_of_date: str, **kwargs) -> dict:
        """
        Get the set of positions for a portfolio snapshot as of a specific date.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/positions

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not portfolio_id or not as_of_date:
            raise ValueError(constants.PORTFOLIO_ID_AS_OF_DATE_ERROR)

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions{parameter_str}'
        response = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            portfolio = json.loads(response.text)
            return portfolio
        else:
            self.logger.error(f"Error in get_positions_asofdate {response.text}")
            raise OMPSException(f"Error in get_positions_asofdate {response.text}")

    def get_position_by_id(self, portfolio_id: str, position_id: str, as_of_date: str, **kwargs) -> dict:
        """
        Get a specific position from a portfolio as of a specific date.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}

        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not portfolio_id or not as_of_date:
            raise ValueError(constants.PORTFOLIO_ID_AS_OF_DATE_ERROR)

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}{parameter_str}'
        position_resp = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if position_resp.ok:
            portfolio = json.loads(position_resp.text)
            return portfolio
        else:
            self.logger.error(f"Error in get_position_by_id {position_resp.text}")
            raise OMPSException(f"Error in get_position_by_id {position_resp.text}")

    def get_taxlots_asofdate(self, portfolio_id: str, as_of_date: str, **kwargs) -> pd.DataFrame:
        """
        Get the set of taxlots for a portfolio snapshot as of a specific date.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/taxlots

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.

            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of positions.
        """

        if not portfolio_id or not as_of_date:
            raise ValueError(constants.PORTFOLIO_ID_AS_OF_DATE_ERROR)
        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/taxlots{parameter_str}'
        response = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return json.loads(response.text)
        else:
            self.logger.error(f"Error in get_taxlots_asofdate {response.text}")
            raise OMPSException(f"Error in get_taxlots_asofdate {response.text}")

    def get_instruments(self, **kwargs) -> pd.DataFrame:
        """
        Get the set of instruments.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/instruments

        Args:

            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of instruments.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/instruments{parameter_str}'
        response = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return json.loads(response.text)
        else:
            self.logger.error(f"Error in get_instruments {response.text}")
            raise OMPSException(f"Error in get_instruments {response.text}")

    def get_instruments_by_id(self, instrument_id: str, as_of_date: str, **kwargs) -> pd.DataFrame:
        """
        Get the set of instruments by ID.

        MSCI Portfolio Storage endpoint: GET /api/v3.0/instruments/{instrument_id}/as-of/{as_of_date}

        Args:
            instrument_id: Instrument ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of instruments.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/instruments/{instrument_id}/as-of/{as_of_date}{parameter_str}'
        response = requests.get(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return json.loads(response.text)
        else:
            self.logger.error(f"Error in get_instruments_by_id {response.text}")
            raise OMPSException(f"Error in get_instruments_by_id {response.text}")

    def upload_portfolio(self, portfolio_id: str, data: json, **kwargs):
        """
        Add single portfolio.

        MSCI Portfolio Storage endpoint: POST /api/v3.0/portfolios/{portfolio_id}

        Args:
            portfolio_id: Portfolio ID.
            data: JSON
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not portfolio_id or not data:
            raise ValueError('portfolio_id and data must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}{parameter_str}'
        upload_response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data),
                                        verify=self.ssl_verify)
        if upload_response.ok:
            return upload_response
        else:
            self.logger.error(f"Error in upload_portfolio {upload_response.text}")
            raise OMPSException(f"Error in upload_portfolio {upload_response.text}")

    def upload_portfolios(self, data: json, **kwargs):
        """
        Add portfolios in bulk.

        MSCI Portfolio Storage endpoint: POST /api/v3.0/portfolios

        Args:
            data: JSON
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not data:
            raise ValueError('Data must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios{parameter_str}'
        upload_response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data),
                                        verify=self.ssl_verify)
        if upload_response.ok:
            return upload_response
        else:
            self.logger.error(f"Error in upload_portfolios {upload_response.text}")
            raise OMPSException(f"Error in upload_portfolios {upload_response.text}")

    def upload_portfolio_positions(self, portfolio_id: str, as_of_date: str, data: json, **kwargs):
        """Add positions for a single date.

        Args:
            portfolio_id (str): Portfolio ID.
            as_of_date (str): As of date in the YYYY-MM-DD format.
            data (json): JSON
        """
        if not portfolio_id or not data or not as_of_date:
            raise ValueError('portfolio_id, as_of_date, and data must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions{parameter_str}'
        response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data), verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in upload_portfolio_positions {response.text}")
            raise OMPSException(f"Error in upload_portfolio_positions {response.text}")

    def upload_taxlot(self, portfolio_id: str, as_of_date: str, data: json, **kwargs):
        """
        Add single taxlot.

        MSCI Portfolio Storage endpoint: POST /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/taxlots?snapshotType=CLOSE

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            data: JSON
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """
        if not portfolio_id or not data or not as_of_date:
            raise ValueError('portfolio_id , as_of_date and data must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/taxlots{parameter_str}'
        response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data), verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in upload_taxlot {response.text}")
            raise OMPSException(f"Error in upload_taxlot {response.text}")

    def upload_instruments(self, data: List, **kwargs):
        """
        Add a set of instruments.

        MSCI Portfolio Storage endpoint: POST api/v3.0/instruments/

        Args:
            data: json
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            None
        """
        if not data:
            raise ValueError('instruments must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/instruments{parameter_str}'
        response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data), verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in upload_instruments {response.text}")
            raise OMPSException(f"Error in upload_instruments {response.text}")

    def add_position_by_id(self, portfolio_id: str, position_id: str, as_of_date: str, data: json, **kwargs):
        """
        Add a position to a portfolio as of a specific date.

        MSCI Portfolio Storage endpoint: POST /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}?snapshotType=OPEN'

        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            data: JSON
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}{parameter_str}'
        response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data), verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in add_position_by_id {response.text}")
            raise OMPSException(f"Error in add_position_by_id {response.text}")

    def add_positions(self, portfolio_id: str, as_of_date: str, data: List, **kwargs):
        """
        Add a set of positions.

        MSCI Portfolio Storage endpoint: POST /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/positions?snapshotType=OPEN'

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            data: JSON
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions{parameter_str}'
        add_response = requests.post(url=omps_url, headers=self._headers, data=json.dumps(data), verify=self.ssl_verify)
        if add_response.ok:
            return add_response
        else:
            self.logger.error(f"Error in add_positions {add_response.text}")
            raise OMPSException(f"Error in add_positions {add_response.text}")

    def delete_portfolios(self, portfolio_id: str, **kwargs):
        """
        Delete a portfolio across all as-of dates.

        MSCI Portfolio Storage endpoint: DELETE /api/v3.0/portfolios/{portfolio_id}

        Args:
            portfolio_id: Portfolio ID.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            None

        """
        if not portfolio_id:
            raise ValueError('portfolio_id must be provided!')

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}{parameter_str}'
        response = requests.delete(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in delete_portfolios {response.text}")
            raise OMPSException(f"Error in delete_portfolios {response.text}")

    def delete_portfolio_asofdate(self, portfolio_id: str, as_of_date: str, **kwargs):
        """
        Delete a portfolio as of a specific date.

        MSCI Portfolio Storage endpoint: DELETE /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}

        Args:
            portfolio_id: Portfolio ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            None

        """
        if not portfolio_id or not as_of_date:
            raise ValueError(constants.PORTFOLIO_ID_AS_OF_DATE_ERROR)

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}{parameter_str}'
        response = requests.delete(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in delete_portfolio_asofdate {response.text}")
            raise OMPSException(f"Error in delete_portfolio_asofdate {response.text}")

    def delete_position_by_id(self, portfolio_id: str, position_id: str, as_of_date: str, **kwargs):
        """
        Delete a specific position from a portfolio as of a specific date.

        MSCI Portfolio Storage endpoint: DELETE /api/v3.0/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}?snapshotType=OPEN'

        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            as_of_date: As of date in the YYYY-MM-DD format.
            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dictionary of the attributes and positions of the given portfolio.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/portfolios/{portfolio_id}/as-of/{as_of_date}/positions/{position_id}{parameter_str}'
        response = requests.delete(url=omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return response
        else:
            self.logger.error(f"Error in delete_position_by_id {response.text}")
            raise OMPSException(f"Error in delete_position_by_id {response.text}")

    def delete_instrument_asofdate(self, instrument_id: str, as_of_date: str, **kwargs) -> pd.DataFrame:
        """
        Delete a specific instrument at specific date.

        MSCI Portfolio Storage endpoint: DELETE /api/v3.0/instruments/{instrument_id}/as-of/{as_of_date}

        Args:
            instrument_id: Instrument ID.
            as_of_date: As of date in the YYYY-MM-DD format.

            **kwargs: Optional parameters supported by a MSCI Portfolio Storage endpoint. For example, `snapshotType`, use a keyword parameter like: ``snapshotType='OPEN'``.

        Returns:
            A dataframe of instruments.
        """

        parameter_str = generate_parameters(**kwargs)
        omps_url = f'{self.omps_base_url}/instruments/{instrument_id}/as-of/{as_of_date}{parameter_str}'
        response = requests.delete(omps_url, headers=self._headers, verify=self.ssl_verify)
        if response.ok:
            return json.loads(response.text)
        else:
            self.logger.error(f"Error in delete_instrument_asofdate {response.text}")
            raise OMPSException(f"Error in delete_instrument_asofdate {response.text}")
