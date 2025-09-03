from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Union

import h2o_mlops_autogen
from h2o_mlops import (
    _core,
    _deployments,
    _utils,
    _workspaces,
    options,
)
from h2o_mlops._utils import UNSET, UnsetType


class MLOpsEndpoint:
    """Interact with an Endpoint on H2O MLOps."""

    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        raw_info: Any,
    ):
        self._client = client
        self._workspace = workspace
        self._raw_info = raw_info

        self._resource_name = raw_info.name
        self._parent_resource_name = raw_info.name.rsplit("/", 2)[0]

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    name={self.name!r},\n"
            f"    description={self.description!r},\n"
            f"    path={self.path!r},\n"
            f"    created_time={self.created_time!r},\n"
            f"    last_modified_time={self.last_modified_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Path: {self.path}\n"
            f"Created Time: {self.created_time}\n"
            f"Last Modified Time: {self.last_modified_time}"
        )

    @property
    def uid(self) -> str:
        """Endpoint unique ID."""
        return _utils._convert_resource_name_to_uid(
            resource_name=self._resource_name,
        )

    @property
    def name(self) -> str:
        """Endpoint display name."""
        return self._raw_info.display_name

    @property
    def description(self) -> str:
        """Endpoint description."""
        return self._raw_info.description

    @property
    def path(self) -> str:
        """Path of the Endpoint appends to the MLOps URL."""
        return self._raw_info.path

    @property
    def created_time(self) -> datetime:
        """Endpoint created time."""
        return self._raw_info.create_time

    @property
    def last_modified_time(self) -> datetime:
        """Endpoint last modified time."""
        return self._raw_info.update_time

    @property
    def target_deployment(self) -> Optional[_deployments.MLOpsScoringDeployment]:
        """MLOps deployment the Endpoint points to."""
        self._refresh()
        if self._raw_info.target:
            target_uid = self._raw_info.target.split("/")[-1]
            return self._workspace.deployments.get(target_uid)
        return None

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[Union[str, UnsetType]] = UNSET,
        target_deployment: Optional[
            Union[_deployments.MLOpsScoringDeployment, UnsetType]
        ] = UNSET,
    ) -> None:
        """Change Endpoint settings.

        Args:
           name: display name for the Endpoint
           description: description for the Endpoint
           target_deployment: MLOps deployment the Endpoint points to.
               Set to empty string to disable the Endpoint.
        """
        from _h2o_mlops_client.deployer.v2.configuration import Configuration

        local_vars_configuration = Configuration()
        local_vars_configuration.client_side_validation = False

        update_mask = []
        endpoint = h2o_mlops_autogen.TheEndpointToUpdateWhereTheEndpointSNameFieldIsUsedToIdentifyTheOneToUpdate(  # noqa E501
            local_vars_configuration=local_vars_configuration
        )
        if name is not None:
            endpoint.display_name = name
            update_mask.append("display_name")
        if description is not UNSET:
            endpoint.description = description
            update_mask.append("description")
        if not isinstance(target_deployment, UnsetType):
            if target_deployment:
                deployment_resource_name = (
                    f"{self._parent_resource_name}/deployments/{target_deployment.uid}"
                )
                endpoint.target = deployment_resource_name
            else:
                endpoint.target = target_deployment
            update_mask.append("target")
        if update_mask:
            self._raw_info = self._client._backend.deployer.endpoint.update_endpoint(
                endpoint_name=self._resource_name,
                endpoint=endpoint,
                update_mask=",".join(update_mask),
            ).endpoint

    def delete(self) -> None:
        """Delete Endpoint from the H2O MLOps."""
        self._client._backend.deployer.endpoint.delete_endpoint(
            name_1=self._resource_name
        )

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.deployer.endpoint.get_endpoint(
            name_3=self._resource_name
        ).endpoint


class MLOpsEndpoints:
    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._workspace = workspace
        self._parent_resource_name = f"workspaces/{self._workspace.uid}"

    def create(
        self,
        name: str,
        path: str,
        description: Optional[str] = None,
        target_deployment: Optional[_deployments.MLOpsScoringDeployment] = None,
    ) -> MLOpsEndpoint:
        """Create an Endpoint in H2O MLOps.

        Args:
           name: display name for the Endpoint
           path: path to use for the target deployment URLs
           description: description for the Endpoint
           target_deployment: MLOps deployment the Endpoint points to
        """
        raw_info = self._client._backend.deployer.endpoint.create_endpoint(
            parent=self._parent_resource_name,
            endpoint=h2o_mlops_autogen.V2Endpoint(
                display_name=name,
                description=description or "",
                path=path,
                target=(
                    f"{self._parent_resource_name}/deployments/{target_deployment.uid}"  # noqa E501
                    if target_deployment
                    else None
                ),
            ),
        ).endpoint
        return MLOpsEndpoint(self._client, self._workspace, raw_info)

    def get(
        self,
        uid: Optional[str] = None,
        path: Optional[str] = None,
    ) -> MLOpsEndpoint:
        """Get the Endpoint object corresponding to an H2O MLOps Endpoint.

        Args:
            uid: H2O MLOps unique ID for the Endpoint.
            path: H2O MLOps unique Endpoint path to use for
                the target deployment URLs.
        """
        if uid:
            raw_info = self._client._backend.deployer.endpoint.get_endpoint(
                name_3=f"{self._parent_resource_name}/endpoints/{uid}"
            ).endpoint

            if path and raw_info.path != path:
                raise ValueError(
                    "Provided 'uid' is associated with a different "
                    "'path' than the one given."
                )
            return MLOpsEndpoint(self._client, self._workspace, raw_info)
        if path:
            endpoint_table = self.list(
                opts=options.ListOptions(
                    filter_expression=options.FilterExpression(
                        filters=[
                            options.FilterOptions(field="path", value=path),
                        ],
                    )
                )
            )
            if not endpoint_table:
                raise LookupError(f"Endpoint not found for path '{path}'.")
            return endpoint_table[0]
        raise ValueError(
            "Either 'uid' or 'path' must be provided to retrieve an endpoint."
        )

    def list(  # noqa A003
        self, opts: Optional[options.ListOptions] = None, **selectors: Any
    ) -> _utils.Table:
        """Retrieve Table of Endpoint available in the Environment.

        Examples::

            # filter on columns by using selectors
            workspace.endpoints.list(name="endpoint-demo")

            # use an index to get an H2O MLOps entity referenced by the table
            endpoint = workspace.endpoints.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.endpoints.list()[2,4]
            table = workspace.endpoints.list()[2:4]
        """
        return self._list(opts=opts, **selectors)

    def _list(
        self,
        page_token: Optional[str] = None,
        opts: Optional[options.ListOptions] = None,
        **selectors: Any,
    ) -> _utils.Table:
        field_name_mapping = {
            "name": "display_name",
            "description": "description",
            "path": "path",
            "target_deployment": "target",
            "created_time": "create_time",
            "last_modified_time": "update_time",
        }
        args = (
            opts._to_raw_info_args(
                field_name_mapping=field_name_mapping,
            )
            if opts
            else {}
        )
        response = self._client._backend.deployer.endpoint.list_endpoints(
            parent=self._parent_resource_name,
            page_token=page_token,
            **args,
        )
        data = [
            {
                "name": e.display_name,
                "path": e.path,
                "uid": e.name.split("/")[-1],
                "target_deployment_uid": e.target.split("/")[-1] if e.target else "",
                "raw_info": e,
            }
            for e in response.endpoints
        ]
        return _utils.Table(
            data=data,
            keys=["name", "path", "uid", "target_deployment_uid"],
            get_method=lambda x: MLOpsEndpoint(
                self._client, self._workspace, x["raw_info"]
            ),
            list_method=self._list,
            list_args={"opts": opts, **selectors},
            next_page_token=response.next_page_token,
            **selectors,
        )
