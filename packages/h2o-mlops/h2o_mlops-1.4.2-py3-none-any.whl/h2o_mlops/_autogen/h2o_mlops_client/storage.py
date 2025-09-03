import os
import warnings
from typing import Any, Optional
from typing import BinaryIO
from typing import Callable

from _h2o_mlops_client.storage import api
from _h2o_mlops_client.storage import api_client
from _h2o_mlops_client.storage.exceptions import *  # noqa: F403, F401
from h2o_mlops_client import bytestream


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


class _DeprecatedDeploymentEnvironmentServiceApi(api.DeploymentEnvironmentServiceApi):
    def deploy_with_http_info(self, body: Any, **kwargs: Any) -> None:
        warnings.warn(
            "Using the .storage.deployment_environment for deploying models is"
            " deprecated. Use .deployer.deployment.create_deployment instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().deploy_with_http_info(body, **kwargs)


class _DeprecatedDeploymentServiceApi(api.DeploymentServiceApi):
    def undeploy_with_http_info(self, body: Any, **kwargs: Any) -> None:
        warnings.warn(
            "Using the .storage.deployment.undeploy is deprecated."
            " Use .deployer.deployment.delete_deployment instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().undeploy_with_http_info(body, **kwargs)


class ExtendedArtifactServiceApi(api.ArtifactServiceApi):
    """Extends generated api.ByteStreamApi with methods implementing streamed
    upload and download of the artifact.
    """

    def __init__(
        self, api_client: ApiClient, bytestream_client: bytestream.Client
    ) -> None:
        super().__init__(api_client=api_client)
        self._bytestream_client = bytestream_client

    def upload_artifact(
        self, artifact_id: str, file: BinaryIO, *, chunk_size: int = 32 * 1024
    ) -> None:
        """Uploads the content of the file as a blob for the artifact.

        Data are streamed to the gateway in chunks.

        Args:
            artifact_id: ID of artifact.
            file: Readable BinaryIO with the content to be uploaded.
            chunk_size: Size of the chunk used for the streaming upload.
        """

        self._bytestream_client.bytestream.upload_file(
            resource_name=artifact_id, file=file, chunk_size=chunk_size
        )

    def download_artifact(self, artifact_id: str, file: BinaryIO) -> None:
        """Downloads the artifact's data from the server and saves it to the file.

        Args:
            artifact_id: ID of artifact.
            file: Writable BinaryIO that will be used to save the blob content.
        """

        self._bytestream_client.bytestream.download_file(
            resource_name=artifact_id, file=file
        )


class Client:
    """The composite client for accessing Storage services."""

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

        self._dataset = api.DatasetServiceApi(api_client=client)
        self._deployment = _DeprecatedDeploymentServiceApi(api_client=client)
        self._deployment_environment = _DeprecatedDeploymentEnvironmentServiceApi(
            api_client=client
        )
        self._experiment = api.ExperimentServiceApi(api_client=client)
        self._project = api.ProjectServiceApi(api_client=client)
        self._role = api.RoleServiceApi(api_client=client)
        self._tag = api.TagServiceApi(api_client=client)
        self._registered_model = api.RegisteredModelServiceApi(api_client=client)
        self._registered_model_version = api.RegisteredModelVersionServiceApi(
            api_client=client
        )
        self._gateway_aggregator = api.GatewayAggregatorServicesApi(api_client=client)

        self._bytestream_client = bytestream.Client(
            host=host,
            token_provider=token_provider,
            verify_ssl=verify_ssl,
            ssl_cacert=ssl_cacert,
        )

        self._artifact = ExtendedArtifactServiceApi(
            api_client=client, bytestream_client=self._bytestream_client
        )

    @property
    def artifact(self) -> ExtendedArtifactServiceApi:
        return self._artifact

    @property
    def dataset(self) -> api.DatasetServiceApi:
        return self._dataset

    @property
    def deployment(self) -> api.DeploymentServiceApi:
        warnings.warn(
            "Using the .storage.deployment interface is being deprecated in future"
            " versions. .deployer.deployment will suprecede this.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._deployment

    @property
    def deployment_environment(self) -> api.DeploymentEnvironmentServiceApi:
        return self._deployment_environment

    @property
    def experiment(self) -> api.ExperimentServiceApi:
        return self._experiment

    @property
    def project(self) -> api.ProjectServiceApi:
        return self._project

    @property
    def role(self) -> api.RoleServiceApi:
        return self._role

    @property
    def tag(self) -> api.TagServiceApi:
        return self._tag

    @property
    def registered_model(self) -> api.RegisteredModelServiceApi:
        return self._registered_model

    @property
    def registered_model_version(self) -> api.RegisteredModelVersionServiceApi:
        return self._registered_model_version

    @property
    def gateway_aggregator(self) -> api.GatewayAggregatorServicesApi:
        return self._gateway_aggregator

    @property
    def bytestream(
        self,
    ) -> bytestream.ExtendedByteStreamApi:
        return self._bytestream_client.bytestream
