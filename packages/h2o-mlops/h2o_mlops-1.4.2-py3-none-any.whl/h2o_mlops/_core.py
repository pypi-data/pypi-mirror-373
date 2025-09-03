from __future__ import annotations

import os
import ssl
from typing import Optional
from urllib.parse import urlparse

import certifi
import h2o_authn
import h2o_discovery

import h2o_mlops_autogen
from h2o_mlops import _configs, _connectors, _runtimes, _users, _workspaces


class Client:
    """Connect to and interact with H2O MLOps.

    Args:
        h2o_cloud_url: full URL of the H2O Cloud to connect to
            (needed when passing a refresh_token)
        refresh_token: client refresh token retrieved from H2O Cloud
            (needed when passing a h2o_cloud_url)
        token_provider: authentication token provider to authorize access on H2O Cloud
            (needed when initialising the MLOps client in environments
            where platform token is not directly available)
        verify_ssl: (Optional) Enables SSL/TLS verification. Set this as False
            to skip SSL certificate verification when calling the API from
            an HTTPS server. Defaults to True.
        ssl_cacert: (Optional) Path to a custom certificate file for verifying
            the peer's SSL/TLS certificate.

    Examples:

        ### Connect from H2O Cloud notebook
        ### (credentials are automatically discovered and used)

        >>> mlops = Client()

        ### Connect with h2o_cloud_url and refresh_token

        >>> mlops = Client(
        ...    h2o_cloud_url="https://...",
        ...    refresh_token="eyJhbGciOiJIUzI1N...",
        ...)

        ### Connect with h2o_cloud_url and token_provider

        >>> mlops = Client(
        ...    h2o_cloud_url="https://...",
        ...    token_provider=h2o_authn.TokenProvider(...),
        ...)
    """

    def __init__(
        self,
        h2o_cloud_url: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_provider: Optional[h2o_authn.TokenProvider] = None,
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ):
        self._backend = None
        self._discovery = None
        self._token_provider = None

        self._ssl_context = ssl.SSLContext()
        self._ssl_context.verify_mode = (
            ssl.CERT_REQUIRED if verify_ssl else ssl.CERT_NONE
        )
        self._ssl_context.load_verify_locations(
            cafile=(
                ssl_cacert
                or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
                or certifi.where()
            )
        )

        if h2o_cloud_url:
            self._h2o_cloud_url = urlparse(h2o_cloud_url)
            self._discovery = h2o_discovery.discover(
                environment=h2o_cloud_url,
                ssl_context=self._ssl_context,
            )
        else:
            self._discovery = h2o_discovery.discover(ssl_context=self._ssl_context)

        self._token_provider = token_provider or h2o_authn.TokenProvider(
            refresh_token=refresh_token or os.getenv("H2O_CLOUD_CLIENT_PLATFORM_TOKEN"),
            issuer_url=self._discovery.environment.issuer_url,
            client_id=self._discovery.clients["platform"].oauth2_client_id,
            http_ssl_context=self._ssl_context,
        )

        self._backend = h2o_mlops_autogen.Client(
            gateway_url=self._discovery.services["mlops-api"].uri,
            authz_gateway_url=self._discovery.services["authz-gateway"].uri,
            token_provider=self._token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )

    @property
    def users(self) -> _users.MLOpsUsers:
        """Interact with Users in H2O MLOps"""
        return _users.MLOpsUsers(self)

    @property
    def workspaces(self) -> _workspaces.Workspaces:
        """Interact with Workspaces in H2O"""
        return _workspaces.Workspaces(self)

    @property
    def runtimes(self) -> _runtimes.MLOpsRuntimes:
        """Interact with Scoring Runtimes in H2O MLOps"""
        return _runtimes.MLOpsRuntimes(self)

    @property
    def batch_connectors(self) -> _connectors.MLOpsBatchConnectors:
        """Interact with Batch Scoring Connectors in H2O MLOps"""
        return _connectors.MLOpsBatchConnectors(self)

    @property
    def configs(self) -> _configs.MLOpsConfigs:
        """Interact with configurations in H2O MLOps"""
        return _configs.MLOpsConfigs(self)
