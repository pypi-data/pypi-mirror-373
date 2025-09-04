import json.decoder
import typing as t
import urllib.parse

import requests
from requests.exceptions import RequestException

from meili_sdk.clients.apitoken_client import APITokenClient
from meili_sdk.clients.persistent_token_client import PersistentTokenClient
from meili_sdk.clients.sdk_client import SDKClient
from meili_sdk.token import get_authentication_token

__all__ = (
    "APITokenClient",
    "PersistentTokenClient",
    "SDKClient",
    "get_client",
)


def get_client(
    token=None,
    override_host=None,
) -> t.Union[SDKClient, APITokenClient, PersistentTokenClient]:
    """
    Get client that will work with the token provided

    If an error occurs somewhere a default APITokenClient will be returned
    """
    from meili_sdk.site import get_host

    host = override_host or get_host()
    url = urllib.parse.urljoin(host, "api/key/validation/")

    token = token or get_authentication_token()

    if not token:
        raise ValueError(
            "Could not figure out token, please provide it in  "
            "code or via environment variable MEILI_TOKEN"
        )

    try:
        response = requests.post(url, data={"key": token}, timeout=10)
        if not response.ok:
            raise ValueError
        response_data = response.json()
        key_type = response_data["key_type"]
    except (RequestException, ValueError, json.decoder.JSONDecodeError, KeyError):
        return APITokenClient(token, host)

    return {
        "SDKToken": SDKClient,
        "APIToken": APITokenClient,
        "PersistentToken": PersistentTokenClient,
    }[key_type](token, host)
