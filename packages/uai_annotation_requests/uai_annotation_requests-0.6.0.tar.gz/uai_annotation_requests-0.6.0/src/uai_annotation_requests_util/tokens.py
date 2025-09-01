from typing import Callable, Optional

import httpx

from uai_annotation_requests_util.errors import UaiAuthenticationError


def get_token(client_id: str, client_secret: str, token_url: Optional[str] = None) -> str:
    """retrieves a UAI OAuth2 token from the signin service

    Raises
    ------
    UaiAuthenticationError
        if a bearer token cannot be retrieved from the UAI signing services because of
        an authentication failure

    """
    if token_url is None:
        token_url = "https://signin.services.understand.ai/auth/realms/understand.ai/protocol/openid-connect/token"

    res = httpx.request(
        method="POST",
        url=token_url,
        data={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
    )

    if res.status_code == 200:
        json_data = res.json()
        return str(json_data["access_token"])

    raise UaiAuthenticationError("Authentication failure. Failed to retrieve token from UAI signin service.")


def uai_oauth2(client_id: str, client_secret: str, token_url: Optional[str] = None) -> Callable[[], str]:
    """creates a token handler that will retrieve a UAI OAuth2 token on demand
    based on the provided client_id and client_secret."""
    return lambda: get_token(client_id, client_secret, token_url)
