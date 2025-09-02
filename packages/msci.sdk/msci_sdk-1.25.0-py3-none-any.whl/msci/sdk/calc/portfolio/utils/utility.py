import os
from datetime import datetime, timedelta
import pandas as pd
import logging
import requests
import json
from os import environ
from os.path import dirname, basename, join
from ..utils import constants
from ..utils.constants import ALLOWED_ASSET_TYPES
from cryptography.fernet import Fernet
import base64
import tempfile

logger = logging.getLogger(__name__)


def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")


def validate_dataframe_date(df, date_col):
    try:
        pd.to_datetime(df[date_col], format='%Y-%m-%d', errors='raise')
    except ValueError:
        raise ValueError(f"Incorrect date format for {date_col}, should be YYYY-MM-DD")


def validate_portfolio_details(asset_id, not_null_cols, positions, positions_col, portfolio_id):
    if asset_id not in ALLOWED_ASSET_TYPES:
        logger.error(f"asset id not among {ALLOWED_ASSET_TYPES} for portfolio_id: {portfolio_id}")
        raise ValueError(f"asset_id should be one among {ALLOWED_ASSET_TYPES} for portfolio_id: {portfolio_id}")

    if asset_id not in positions_col:
        logger.error(f"asset_id: {asset_id} not present in the portfolio for portfolio_id: {portfolio_id}")
        raise ValueError(f"asset_id: {asset_id} not present in the portfolio for portfolio_id: {portfolio_id}")
    # To check whether a particular row is NULL(all columns of the row) and if all are NULL then drop them.
    if (positions.isnull().all(axis=1)).any():
        positions = positions.dropna()
    # To raise a value error if any mandatory fields or columns are NULL.
    null_cols = [column for column in not_null_cols if positions[column].isnull().any()]
    if null_cols:
        error_msg = "Missing value for: " + ", ".join(null_cols) + f" for portfolio_id: {portfolio_id}"
        raise ValueError(error_msg)


def csv_to_json(filepath):
    csv_port = pd.read_csv(filepath)
    filename = basename(filepath).split('.')[0] + '.json'
    fp = join(dirname(filepath), filename)
    csv_port.to_json(fp, orient='records')
    logger.info(f"JSON file created at path: {fp}")


def generate_parameters(**kwargs) -> str:
    p_list = []
    for key, value in kwargs.items():
        p_list.append(f'{key}={value}')
    if len(p_list) > 0:
        parameter_str = '?' + '&'.join(p_list)
    else:
        parameter_str = ''
    return parameter_str


def bulk_request_body(job_list, date=None, snapshot_list=None, account_id=None):
    key_list = []
    for job in job_list:
        key = {
            'jobId': job
        }
        if date:
            key['asOf'] = date
        if snapshot_list:
            key['snapshotTypes'] = snapshot_list
        if account_id:
            key['accountId'] = account_id

        key_list.append(key)

    return key_list


def get_token(url, client_id, client_secret, audience, service_name, refresh_token):
    """Get access token.

    Args:
        url: URL used for generating token.
        client_id: Client ID.
        client_secret: Client secret.
        audience: Purpose of generating the token.
        service_name : Name of the service for which token needs to be generated
        refresh_token(bool): Refresh the token.

    Returns:
        token: Generated access token.
    """
    token = __load_saved_tokens(client_id, client_secret, service_name)
    if not token or refresh_token:
        logger.info("Generating new bearer token for authentication of {}".format(service_name))
        auth_body = {'client_id': client_id, 'grant_type': 'client_credentials',
                     'client_secret': client_secret,
                     'audience': audience}
        token_resp = requests.post(url, data=auth_body, verify=True)
        if token_resp.status_code != 200:
            raise AuthException(
                "Unable to get access_token, status: " + str(token_resp.status_code) + " | text: " + token_resp.text)
        token = json.loads(token_resp.content)["access_token"]
        expiry_secs = json.loads(token_resp.content)["expires_in"]

        __save_generated_token(client_id, client_secret, token, expiry_secs, service_name)
    else:
        logger.info("Using the cached token for Authentication of {}".format(service_name))
    return token


def __load_saved_tokens(client_id, client_secret, service_name):
    file_data = read_saved_token(service_name, client_id)
    if file_data:
        data_arr = file_data.split("|")

        if len(data_arr) != 4:
            logger.info("No saved tokens found")
            return

        file_client_id = data_arr[0]
        encrypt_token = data_arr[1]
        validity_time = data_arr[3]

        if file_client_id == client_id:
            key = _generate_key(client_id, client_secret)
            validity_time = datetime.strptime(validity_time, "%d-%m-%y %H:%M:%S")
            if datetime.now() <= validity_time:
                return run_decryption(encrypt_token, key)
            else:
                logger.info("Saved token expired, generating new token")
                return


def read_saved_token(service_name, client_id):
    file_path = get_token_file_path(service_name, client_id)
    if os.path.isfile(file_path):
        f = open(file_path, "r")
        file_read_data = f.read()
        return file_read_data


def write_to_file(client_id, encrypted_token, expiry_secs, service_name):
    file_path = get_token_file_path(service_name, client_id)
    if file_path:
        f = open(file_path, "w")
        file_data = prepare_file_data(client_id, encrypted_token, expiry_secs)
        f.write(file_data)
        f.close()


def get_token_file_path(service_name, client_id):
    prefix = service_name + "-" + environ.get('ENV', 'PROD') + "_" + client_id

    token_dir = tempfile.gettempdir() + "/" + constants.SDK_DIR
    if not os.path.exists(token_dir):
        try:
            os.mkdir(token_dir)
        except OSError as excep:
            logger.error(f"Error while creating token cache directory. Error code : {excep.errno}")
            return ""

    file_name = prefix + "_" + constants.TOKEN_FILE_NAME
    file_path = token_dir + "/" + file_name
    return file_path


def prepare_file_data(client_id, encrypted_token, expiry_secs):
    curr_date = datetime.now()
    new_date = curr_date + timedelta(0, expiry_secs)
    file_data = client_id + "|" + encrypted_token.decode() + "|" + curr_date.strftime(
        '%d-%m-%y %H:%M:%S') + "|" + new_date.strftime('%d-%m-%y %H:%M:%S')
    return file_data


def __save_generated_token(client_id, client_secret, token, expiry_secs, service_name):
    key = _generate_key(client_id, client_secret)
    encrypted_token = run_encryption(token, key)
    write_to_file(client_id, encrypted_token, expiry_secs, service_name)


def run_encryption(token, key):
    fernet = Fernet(key)
    return fernet.encrypt(token.encode())


def run_decryption(encrypt_token, key):
    fernet = Fernet(key)
    return fernet.decrypt(bytes(encrypt_token, 'utf-8')).decode()


def _generate_key(client_id, client_secret):
    key = client_id[0:16] + client_secret[0:16]
    key = base64.urlsafe_b64encode(key.encode())
    return key


def env_resolver(service):
    _env = environ.get('ENV', 'PROD')
    cred = eval(f'constants.{service.upper()}_{_env}')
    return cred


def get_version():
    version = environ.get('MOS_VERSION', constants.MOS_DEFAULT_VERSION)
    if version not in constants.MOS_VERSIONS_SUPPORTED:
        raise ValueError(f"MOS version {version} not supported. Supported versions are {constants.MOS_VERSIONS_SUPPORTED}")
    return version


def get_client_environ(client_id, client_secret):
    """
    Get client keys MSCI_MOS_API_KEY and MSCI_MOS_API_SECRET from environment.
    """
    if client_id is None:
        client_id = environ.get('MSCI_MOS_API_KEY')
    if client_secret is None:
        client_secret = environ.get('MSCI_MOS_API_SECRET')
    return client_id, client_secret


def get_default_universe_and_benchmark():
    return pd.DataFrame([{'name': 'MSCI USA - DAILY', 'returnType': 'GRS', 'currency': 'USD',
                        'mdsId': 'UNX000000034908161'}])


class MOSException(Exception):
    """Raised when any exception occurs in MOS service endpoints"""
    pass


class OMPSException(Exception):
    """Raised when any exception occurs in OMPS service endpoints"""
    pass


class AuthException(Exception):
    """Raised when any exception occurs in AUTH service endpoints"""
    pass


class APIException(Exception):
    ""
