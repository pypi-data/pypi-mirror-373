import logging

from eq_api_connector.connector_api import (
    set_tenant,
    set_public_client_id,
    set_scope,
    set_url_prod,
    set_url_dev,
    get_app_token,
    get_json,
    get_api_url,
    post_json,
)

__all__ = [
    "set_tenant",
    "set_public_client_id",
    "set_scope",
    "set_url_prod",
    "set_url_dev",
    "get_app_token",
    "get_json",
    "get_api_url",
    "post_json",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
