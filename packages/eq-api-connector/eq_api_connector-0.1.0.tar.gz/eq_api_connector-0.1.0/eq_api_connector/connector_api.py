import json
import logging
from types import SimpleNamespace
from typing import Dict, List, Optional, Union
from azure.identity import DefaultAzureCredential
import requests
from msal_bearer import BearerAuth, get_user_name
from io import BytesIO
import os


logger = logging.getLogger(__name__)

# MSAL-settings
_tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"  # Equinor tenant
_public_client_id = ""
_scope = []


_token = ""
_user_name = ""

_raise_for_status = True

_use_dev = False
_url_prod = ""
_url_dev = ""


def set_tenant(tenant_id: str) -> None:
    """Setter for global property _tenantID.

    Args:
        tenant_id (str): Tenant ID to set.
    """
    global _tenantID
    _tenantID = tenant_id


def set_public_client_id(client_id: str) -> None:
    """Setter for global property _public_client_id.

    Args:
        client_id (str): Client ID to set.
    """
    global _public_client_id
    _public_client_id = client_id


def set_scope(scope: List[str]) -> None:
    """Setter for global property _scope.

    Args:
        scope (str): Scope to set.
    """
    global _scope
    _scope = scope


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


def set_token(token: str) -> None:
    """Setter for global property token.

    Args:
        token (str): Token to set.
    """
    global _token
    _token = token


def get_token() -> str:
    """Getter for token. Will first see if a global token has been set, then try to get a token using app registration, then last try to get via azure authentication.

    Returns:
        str: Authentication token
    """
    if _token:

        return _token

    token = get_app_token()

    if token:
        return token

    return get_az_token()


def get_az_token() -> str:
    """Getter for token uzing azure authentication.

    Returns:
        str: Token from azure authentication
    """
    credential = DefaultAzureCredential()
    databaseToken = credential.get_token(_public_client_id)
    return databaseToken[0]


def get_app_bearer(username: str = "") -> str:
    global _user_name

    if not username:
        if not _user_name:
            _user_name = get_user_name()
        username = _user_name  # type: ignore
    else:
        _user_name = username

    # SHORTNAME@equinor.com -- short name shall be capitalized
    if not username.endswith("@EQUINOR.COM"):
        username = username + "@EQUINOR.COM"
    username = username.upper()  # Also capitalize equinor.com

    auth = BearerAuth.get_auth(
        tenantID=_tenantID,
        clientID=_public_client_id,
        scopes=_scope,
        username=username,
        token_location="api_token_cache.bin",
    )
    return auth.token  # type: ignore


def get_app_token(username: str = "") -> str:
    """Getter for token using app registration authentication.

    Args:
        username (str, optional): User name (email address) of user to get token for.

    Returns:
        str: Token from app registration
    """
    return get_app_bearer(username=username)


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
