import requests as r
import logging
import json
from .utility import MOSException

logger = logging.getLogger(__name__)


def get(url: str, headers: dict, params: dict = None, ssl_verify: bool = True, check_200: bool = True):
    """
    Retrieve the specified resource with the passed parameters.

    Args:
        url(str): The service URL.
        headers(dict): Dictionary for request header
        params(dict): Dictionary of additional parameters in the request.
        ssl_verify: SSL verification flag . Default true
        check_200(bool): Default value is True. Raise exception if status code <> 200.

    Returns:
        Response object from requests library including status_code and content.
    """

    logger.debug(f"GET : {url} with params {params}")
    try:
        response = r.get(url=url, headers=headers, params=params, verify=ssl_verify)
        if check_200 and response.status_code != 200:
            logger.error(f"Error in get : {url} with exception : {response.text}")
            raise MOSException(f"Error in get : {url} with exception : {response.text}")
    except r.exceptions.RequestException as e:
        raise MOSException(f"Error while connecting to requested URL : {e} ")
    return response


def post(url: str, headers: dict, data, params: dict = None, ssl_verify: bool = True, check_200: bool = True):
    """
    Post content to the specified resource.

    Args:
        url(str): The service URL.
        headers(dict): Dictionary for request header
        data: Data dictionary that needs to be posted.
        params(dict): Dictionary of additional parameters in the request.
        ssl_verify: SSL verification flag . Default true
        check_200(bool): Default value is True. Raise exception if status code <> 200.

    Returns:
        Response object from requests library including status_code and content.
    """
    logger.debug(f"POST : {url} with {data} and params {params}")
    try:
        response = r.post(url=url, headers=headers, data=json.dumps(data), verify=ssl_verify, params=params)
        if check_200 and response.status_code != 200:
            logger.error(f"Error in post : {url} with exception : {response.text}")
            raise MOSException(f"Error in post : {url} with exception : {response.text}")
    except r.exceptions.RequestException as e:
        raise MOSException(f"Error while connecting to requested URL : {e} ")
    return response


def put(url: str, headers: dict, data, ssl_verify: bool = True, check_200: bool = True):
    """
    Updates instance of specified resource.

    Args:
        url(str): The service URL.
        headers(dict): Dictionary for request header
        data: Data dictionary that needs to be posted.
        ssl_verify: SSL verification flag . Default true
        check_200(bool): Default value is True. Raise exception if status code <> 200.

    Returns:
        Response object from requests library including status_code and content.
    """

    logger.debug(f"PUT : {url} with {data}")
    try:
        response = r.put(url=url, headers=headers, data=json.dumps(data), verify=ssl_verify)
        if check_200 and response.status_code != 200:
            logger.error(f"Error in put : {url} with exception : {response.text}")
            raise MOSException(f"Error in put : {url} with exception : {response.text}")
    except r.exceptions.RequestException as e:
        raise MOSException(f"Error while connecting to requested URL : {e} ")
    return response


def delete(url: str, headers: dict, params: dict = None, check_200: bool = True, ssl_verify: bool = True):
    """
    Delete the specified resource.

    Args:
        url(str): The service URL.
        headers(dict): Dictionary for request header
        params(dict): Dictionary of additional parameters in the request.
        check_200(bool): Default value is True. Raise exception if status code <> 200.
        ssl_verify(bool): SSL verification flag . Default true

    Returns:
        Response object from requests library including status_code and content.
    """

    logger.debug(f"DELETE: {url} with params {params}")
    try:
        response = r.delete(url=url, headers=headers, params=params, verify=ssl_verify)
        if check_200 and response.status_code != 200:
            logger.error(f"Error in delete : {url} with exception : {response.text}")
            raise MOSException(f"Error in delete : {url} with exception : {response.text}")
    except r.exceptions.RequestException as e:
        raise MOSException(f"Error while connecting to requested URL : {e} ")
    return response
