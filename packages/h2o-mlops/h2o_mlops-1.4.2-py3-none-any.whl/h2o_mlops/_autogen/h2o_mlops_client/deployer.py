import os
from typing import Any, Optional
from typing import Callable

from _h2o_mlops_client.deployer.v2 import api
from _h2o_mlops_client.deployer.v2 import api_client
from _h2o_mlops_client.deployer.v2.exceptions import *  # noqa: F403, F401


class ApiClient(api_client.ApiClient):
    def __init__(
        self, configuration: api_client.Configuration, token_provider: Callable[[], str]
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self, headers: Any, querys: Any, auth_settings: Any, request_auth: Any = None
    ) -> None:
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"


class Client:
    """The composite client for accessing Deployer services."""

    def __init__(
        self,
        host: str,
        token_provider: Callable[[], str],
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ):
        configuration = api_client.Configuration(
            host=host,
        )
        configuration.verify_ssl = verify_ssl
        ssl_ca_cert = ssl_cacert or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
        if ssl_ca_cert:
            configuration.ssl_ca_cert = ssl_ca_cert

        client = ApiClient(
            configuration=configuration,
            token_provider=token_provider,
        )
        self._composition = api.ArtifactCompositionServiceApi(
            api_client=client,
        )
        self._deployment = api.DeploymentServiceApi(api_client=client)
        self._status = api.DeploymentStatusServiceApi(api_client=client)
        self._metadata = api.DeploymentMetadataServiceApi(api_client=client)
        self._endpoint = api.EndpointServiceApi(api_client=client)
        self._log = api.LogServiceApi(api_client=client)
        self._config = api.ConfigServiceApi(api_client=client)
        self._profiling = api.DeploymentProfilingServiceApi(
            api_client=client,
        )

    @property
    def composition(self) -> api.ArtifactCompositionServiceApi:
        return self._composition

    @property
    def deployment(self) -> api.DeploymentServiceApi:
        return self._deployment

    @property
    def status(self) -> api.DeploymentStatusServiceApi:
        return self._status

    @property
    def metadata(self) -> api.DeploymentMetadataServiceApi:
        return self._metadata

    @property
    def endpoint(self) -> api.EndpointServiceApi:
        return self._endpoint

    @property
    def log(self) -> api.LogServiceApi:
        return self._log

    @property
    def config(self) -> api.ConfigServiceApi:
        return self._config

    @property
    def profiling(self) -> api.DeploymentProfilingServiceApi:
        return self._profiling
