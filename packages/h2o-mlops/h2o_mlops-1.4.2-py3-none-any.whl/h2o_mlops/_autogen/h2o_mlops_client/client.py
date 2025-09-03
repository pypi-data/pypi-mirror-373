from typing import Callable, Optional

import yarl

import h2o_mlops_client.authz
import h2o_mlops_client.batch
import h2o_mlops_client.deployer
import h2o_mlops_client.ingest
import h2o_mlops_client.monitoring
import h2o_mlops_client.storage


class Client:
    """The composite client for accessing all MLOps services."""

    def __init__(
        self,
        gateway_url: str,
        authz_gateway_url: str,
        token_provider: Callable[[], str],
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ) -> None:
        """Initializes MLOps client.

        Args:
            gateway_url: The base URL where the MLOps gRPC Gateway is accessible.
            authz_gateway_url: The base URL where the authz gateway is accessible.
            token_provider: A function that returns an access token. This function
                is called with every request, and the token is passed in the
                'Authorization' header as a bearer token.
            verify_ssl: (Optional) Enables SSL/TLS verification. Set this as False
                to skip SSL certificate verification when calling the API from
                an HTTPS server. Defaults to True.
            ssl_cacert: (Optional) Path to a custom certificate file for verifying
                the peer's SSL/TLS certificate.

        Returns:
            A new instance of the MLOps client.
        """
        url = yarl.URL(gateway_url)
        if not url.scheme:
            raise ValueError(
                "Gateway URL is missing a protocol. "
                "Please include 'http://' or 'https://'."
            )
        if url.scheme not in ["http", "https"]:
            raise ValueError(
                "Invalid protocol in Gateway URL. "
                "Only 'http' and 'https' are allowed."
            )

        authz_url = yarl.URL(authz_gateway_url)
        if not authz_url.scheme:
            raise ValueError(
                "Gateway URL is missing a protocol. "
                "Please include 'http://' or 'https://'."
            )
        if authz_url.scheme not in ["http", "https"]:
            raise ValueError(
                "Invalid protocol in Gateway URL. "
                "Only 'http' and 'https' are allowed."
            )
        self._storage = h2o_mlops_client.storage.Client(
            host=str(url / "storage"),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )
        self._deployer = h2o_mlops_client.deployer.Client(
            host=str(url / "deployer"),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )
        self._batch = h2o_mlops_client.batch.Client(
            host=str(url / "deploymentServer/batch"),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )
        self._ingest = h2o_mlops_client.ingest.Client(
            host=str(url / "ingest"),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )
        self._monitoring = h2o_mlops_client.monitoring.Client(
            host=str(url / "monitoring"),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )

        self._authz = h2o_mlops_client.authz.Client(
            host=str(authz_url),
            mlops_host=str(url),
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )

    @property
    def storage(self) -> h2o_mlops_client.storage.Client:
        return self._storage

    @property
    def deployer(self) -> h2o_mlops_client.deployer.Client:
        return self._deployer

    @property
    def authz(self) -> h2o_mlops_client.authz.Client:
        return self._authz

    @property
    def batch(self) -> h2o_mlops_client.batch.Client:
        return self._batch

    @property
    def ingest(self) -> h2o_mlops_client.ingest.Client:
        return self._ingest

    @property
    def monitoring(self) -> h2o_mlops_client.monitoring.Client:
        return self._monitoring
