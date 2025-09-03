import os
from typing import Any, Optional
from typing import Callable

from _h2o_mlops_client.batch import api
from _h2o_mlops_client.batch import api_client
from _h2o_mlops_client.batch.exceptions import *  # noqa: F403, F401


class ApiClient(api_client.ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

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
    """The composite client for accessing Batch services."""

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
        self._job = api.JobServiceApi(api_client=client)
        self._source_spec = api.SourceSpecServiceApi(api_client=client)
        self._sink_spec = api.SinkSpecServiceApi(api_client=client)

    @property
    def job(self) -> api.JobServiceApi:
        return self._job

    @property
    def source_spec(self) -> api.SourceSpecServiceApi:
        return self._source_spec

    @property
    def sink_spec(self) -> api.SinkSpecServiceApi:
        return self._sink_spec
