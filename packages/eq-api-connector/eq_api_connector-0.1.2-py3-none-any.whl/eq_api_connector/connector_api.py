import json
import logging
from types import SimpleNamespace
from typing import Dict, List, Optional, Union
import requests

from io import BytesIO
import os

from eq_api_connector.connector_init import get_token


logger = logging.getLogger(__name__)


_use_dev = False
_url_prod = ""
_url_dev = ""

_raise_for_status = True


def set_url_prod(url: str) -> None:
    """Setter for global property _url_prod.

    Args:
        url (str): URL to set.
    """
    global _url_prod
    _url_prod = url


def set_url_dev(url: str) -> None:
    """Setter for global property _url_dev.

    Args:
        url (str): URL to set.
    """
    global _url_dev
    _url_dev = url


def get_object_from_json(text: str):
    if isinstance(text, list):
        obj = [json.loads(x, object_hook=lambda d: SimpleNamespace(**d)) for x in text]
    else:
        obj = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))
    return obj


def set_use_dev(use_dev: bool):
    """Setter for global property _use_dev.
    If _use_dev is True, the API URL will be set to the development URL,
    otherwise it will be set to the production URL.

    Args:
        use_dev (bool): Value to set _use_dev to.

    Raises:
        TypeError: In case input use_dev is not a boolean.
    """
    global _use_dev

    if not isinstance(use_dev, bool):
        raise TypeError("Input use_dev shall be boolean.")

    _use_dev = use_dev


def set_raise_for_status(raise_for_status: bool):
    """Setter for global property _raise_for_status.
    If _raise_for_status is True, the requests will raise an exception for HTTP errors,
    otherwise it will not.

    Args:
        raise_for_status (bool): Value to set _raise_for_status to.

    Raises:
        TypeError: In case input raise_for_status is not a boolean.
    """
    global _raise_for_status

    if not isinstance(raise_for_status, bool):
        raise TypeError("Input raise_for_status shall be boolean.")

    _raise_for_status = raise_for_status


def get_api_url() -> str:
    """Getter for API URL. Will return the dev URL if _use_dev is True, otherwise will return the production URL.
    Returns:
        str: API URL
    """
    if _use_dev:
        return _url_dev
    else:
        return _url_prod


def get_json(url: str, params: Optional[dict] = None) -> Union[dict, requests.Response]:
    """Get JSON from API endpoint.

    Args:
        url (str): _description_
        params (Optional[dict], optional): _description_. Defaults to None.

    Returns:
        Union[dict, requests.Response]: _description_
    """

    if url.startswith("/"):
        url = get_api_url() + url

    token = get_token()
    header = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=header, params=params)
    if _raise_for_status:
        response.raise_for_status()

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.warning(
                f"Warning: {str(url)} returned successfully, but not with a valid json response"
            )
    else:
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    return response


def get_file(url: str, file_name: str, stream=True) -> str:
    token = get_token()
    header = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=header, stream=stream)
    # try:
    if _raise_for_status:
        response.raise_for_status()

    if not (response.status_code == 200):
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    if file_name is not None and len(file_name) > 0:
        save_path = os.path.join(os.getcwd(), file_name)
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully and saved to {save_path}")
        return save_path
    else:
        return response.text
    # except requests.exceptions.RequestException as e:
    #     print(f"Error downloading schema: {e}")
    # except PermissionError as e:
    #     print(f"Permission error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


def post_json(url: str, upload: Dict[str, List[Dict[str, str]]]):
    header = {"Authorization": f"Bearer {get_token()}"}
    json_file = BytesIO(json.dumps(upload).encode("utf-8"))
    response = requests.post(
        url, headers=header, files={"file": ("upload_data.json", json_file)}
    )

    if _raise_for_status:
        response.raise_for_status()

    if not (response.status_code == 200):
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    return response
