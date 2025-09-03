import abc
import datetime
import json
import os
import ssl
from typing import Any
from typing import Mapping
from typing import NamedTuple
from typing import Optional

import certifi  # type: ignore
import urllib3  # type: ignore


_DEFAULT_EXPIRY_THRESHOLD_BAND = datetime.timedelta(seconds=5)


class Token(NamedTuple):
    """Represents Token object."""

    refresh_token: str
    access_token: Optional[str]
    expiry: Optional[datetime.datetime]


# TODO(@zoido): Replace with typing.Protocol when the target version of Python is
# at least 3.8
class TokenClient(abc.ABC):
    """Protocol definition for the clients that can be used to exchange refresh token
    for access token.
    """

    @abc.abstractmethod
    def get_token(
        self,
        refresh_token: str,
        client_id: str,
        token_endpoint_url: str,
        client_secret: Optional[str] = None,
    ) -> Token:
        """Exchanges  refresh token for access token using 'refresh_token' grant type
        exchange.

        Args:
            refresh_token: Refresh token that'll be used for initial exchange of
                access token.
            client_id: ID of the client we should act as.
            token_endpoint_url: Url of the OAuth 2.0 token endpoint where we can
                exchange refresh token using the 'refresh_token' grant type.
            client_secret: (optional) Client secret for the use with confidential
                clients.

        Returns:
            Obtained tokens as Token.
        """


class Urllib3TokenClient:
    """Implements TokenClient protocol using the urllib3."""

    def __init__(
        self,
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ) -> None:
        self._http = urllib3.PoolManager(
            cert_reqs=ssl.CERT_REQUIRED if verify_ssl else ssl.CERT_NONE,
            ca_certs=ssl_cacert
            or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
            or certifi.where(),
        )

    def get_token(
        self,
        refresh_token: str,
        client_id: str,
        token_endpoint_url: str,
        client_secret: Optional[str] = None,
    ) -> Token:
        data = dict(
            client_id=client_id,
            grant_type="refresh_token",
            refresh_token=refresh_token,
        )
        if client_secret:
            data["client_secret"] = client_secret

        resp = self._http.request(
            method="POST", url=token_endpoint_url, fields=data, encode_multipart=False
        )

        if not (200 <= resp.status <= 299):
            raise Exception(resp.status, resp.data)

        return token_from_response(json.loads(resp.data))


class TokenProvider:
    """Provides the token and make sure it's fresh when required."""

    def __init__(
        self,
        refresh_token: str,
        client_id: str,
        token_endpoint_url: str,
        client_secret: Optional[str] = None,
        *,
        expiry_threshold_band: datetime.timedelta = _DEFAULT_EXPIRY_THRESHOLD_BAND,
        token_client: Optional[TokenClient] = None,
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ) -> None:
        """Initializes instance of the TokenProvider.

        Args:
            refresh_token: Refresh token that'll be used for initial exchange of
                access token.
            client_id: ID of the client we should act as.
            token_endpoint_url: Url of the OAuth 2.0 token endpoint where we can
                exchange refresh token using the 'refresh_token' grant type.
            expiry_threshold_band: How much time before effective
                expiration of the client access token we should exchange the new one.
            client_secret: (optional) Client secret for the use with confidential
                clients.
            token_client: (optional) Implementation of the TokenClient protocol
                that will be used for token exchange. Uses Urllib3TokenClient
                by default.
            verify_ssl: (Optional) Enables SSL/TLS verification. Set this as False
                to skip SSL certificate verification when calling the API from
                an HTTPS server. Defaults to True.
            ssl_cacert: (Optional) Path to a custom certificate file for verifying
                the peer's SSL/TLS certificate.

        """
        self._access_token: Optional[str] = None
        self._refresh_token = refresh_token
        self._token_expiry: Optional[datetime.datetime] = None

        self._client_id = client_id
        self._client_secret = client_secret

        self._token_endpoint_url = token_endpoint_url

        self._expiry_threshold_band = expiry_threshold_band

        self._token_client = token_client or Urllib3TokenClient(
            verify_ssl=verify_ssl, ssl_cacert=ssl_cacert
        )

    def __call__(self) -> str:
        return self.ensure_fresh_token()

    def ensure_fresh_token(self) -> str:
        if self.refresh_possible() and self.refresh_required():
            self.do_refresh()
        if not self._access_token:
            raise LookupError("Could not obtain access token")
        return self._access_token or ""

    def refresh_required(self) -> bool:
        if self._access_token is None:
            return True

        now = datetime.datetime.now(datetime.timezone.utc)
        return self._token_expiry is None or (
            self._token_expiry <= (now + self._expiry_threshold_band)
        )

    def refresh_possible(self) -> bool:
        return self._refresh_token is not None

    def do_refresh(self) -> None:
        token = self._token_client.get_token(
            refresh_token=self._refresh_token,
            client_id=self._client_id,
            token_endpoint_url=self._token_endpoint_url,
            client_secret=self._client_secret,
        )
        self._access_token = token.access_token
        self._refresh_token = token.refresh_token
        self._token_expiry = token.expiry or None


def token_from_response(resp: Mapping[str, Any]) -> Token:
    """Converts JSON response from token endpoint to the internal representation
    tuple.
    """

    access_token: str = resp["access_token"]
    expires_in: int = resp["expires_in"]
    refresh_token: str = resp["refresh_token"]
    expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=expires_in
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expiry=expiry,
    )
