from typing import List
from azure.identity import DefaultAzureCredential

from msal_bearer import BearerAuth, get_user_name

# MSAL-settings
_tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"  # Equinor tenant
_public_client_id = ""
_scope = []


_token = ""
_user_name = ""


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


def get_app_token(username: str = "") -> str:
    """Getter for token using app registration authentication.

    Args:
        username (str, optional): User name (email address) of user to get token for.

    Returns:
        str: Token from app registration
    """
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
        tenantID=_tenantID, clientID=_public_client_id, scopes=_scope, username=username
    )
    return auth.token  # type: ignore
