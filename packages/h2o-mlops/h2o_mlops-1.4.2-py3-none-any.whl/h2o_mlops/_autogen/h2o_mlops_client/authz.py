import os
from typing import Any, Optional
from typing import Callable

from _h2o_mlops_client.user import api as user_api
from _h2o_mlops_client.user import api_client as user_api_client
from _h2o_mlops_client.user import models as user_models
from _h2o_mlops_client.user.exceptions import *  # noqa: F401, F403
from _h2o_mlops_client.workspace import api as workspace_api
from _h2o_mlops_client.workspace import api_client as workspace_api_client
from _h2o_mlops_client.workspace.exceptions import *  # noqa: F401, F403


class UserApiClient(user_api_client.ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

    def __init__(
        self,
        configuration: user_api_client.Configuration,
        token_provider: Callable[[], str],
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self, headers: Any, querys: Any, auth_settings: Any, request_auth: Any = None
    ) -> None:
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"


class WorkspaceApiClient(workspace_api_client.ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

    def __init__(
        self,
        configuration: workspace_api_client.Configuration,
        token_provider: Callable[[], str],
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self, headers: Any, querys: Any, auth_settings: Any, request_auth: Any = None
    ) -> None:
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"


class UserServiceApi(user_api.UserServiceApi):

    def __init__(self, api_client: UserApiClient, mlops_host: str):
        super().__init__(api_client=api_client)
        self._mlops_host = mlops_host

    def get_me(self) -> user_models.V1GetUserResponse:

        headers: Any = {}
        self.api_client.update_params_for_auth(headers, None, None)
        response = self.api_client.rest_client.GET(
            url=f"{self._mlops_host}/me", headers=headers, _preload_content=False
        )

        user_id = response.headers["X-User-Id"]

        return self.get_user("users/" + user_id)


class Client:
    """The composite client for accessing Authz services."""

    def __init__(
        self,
        host: str,
        mlops_host: str,
        token_provider: Callable[[], str],
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ):

        user_configuration = user_api_client.Configuration(
            host=host,
        )
        user_configuration.safe_chars_for_path_param = "/"
        user_configuration.verify_ssl = verify_ssl
        ssl_ca_cert = ssl_cacert or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
        if ssl_ca_cert:
            user_configuration.ssl_ca_cert = ssl_ca_cert

        user_client = UserApiClient(
            configuration=user_configuration,
            token_provider=token_provider,
        )

        self._user = UserServiceApi(api_client=user_client, mlops_host=mlops_host)

        workspace_configuration = workspace_api_client.Configuration(
            host=host,
        )
        workspace_configuration.safe_chars_for_path_param = "/"
        workspace_configuration.verify_ssl = verify_ssl
        ssl_ca_cert = ssl_cacert or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
        if ssl_ca_cert:
            workspace_configuration.ssl_ca_cert = ssl_ca_cert

        workspace_client = WorkspaceApiClient(
            configuration=workspace_configuration,
            token_provider=token_provider,
        )

        self._workspace = workspace_api.WorkspaceServiceApi(api_client=workspace_client)

    @property
    def user(self) -> UserServiceApi:
        return self._user

    @property
    def workspace(self) -> workspace_api.WorkspaceServiceApi:
        return self._workspace
