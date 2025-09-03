from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, NamedTuple, Optional, Union

import h2o_mlops_autogen
from h2o_mlops import (
    _artifacts,
    _batch_scoring_jobs,
    _core,
    _datasets,
    _deployments,
    _endpoints,
    _events,
    _experiments,
    _models,
    _users,
    _utils,
)
from h2o_mlops._utils import UNSET, UnsetType


class Workspace:
    def __init__(self, client: _core.Client, raw_info: Any):
        self._client = client
        self._raw_info = raw_info

        self._creator_uid = _utils._convert_resource_name_to_uid(
            resource_name=raw_info.creator,
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    name={self.name!r},\n"
            f"    description={self.description!r},\n"
            f"    creator_uid={self._creator_uid!r},\n"
            f"    created_time={self.created_time!r},\n"
            f"    last_modified_time={self.last_modified_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Creator UID: {self._creator_uid}\n"
            f"Created Time: {self.created_time}\n"
            f"Last Modified Time: {self.last_modified_time}"
        )

    @property
    def uid(self) -> str:
        """Workspace unique ID."""
        return _utils._convert_resource_name_to_uid(
            resource_name=self._raw_info.name,
        )

    @property
    def name(self) -> str:
        """Workspace display name."""
        return self._raw_info.display_name

    @property
    def description(self) -> str:
        """Workspace description."""
        return self._raw_info.description

    @property
    def creator(self) -> _users.MLOpsUser:
        """Workspace creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Workspace created time."""
        return self._raw_info.create_time

    @property
    def last_modified_time(self) -> datetime:
        """Workspace last modified time."""
        return self._raw_info.update_time

    @property
    def last_modified_by(self) -> Optional[_users.MLOpsUser]:
        """Workspace last modified by."""
        if updater := self._raw_info.updater:
            user_id = _utils._convert_resource_name_to_uid(
                resource_name=updater,
            )
            return self._client.users.get(user_id)
        return None

    @property
    def annotations(self) -> Dict[str, str]:
        """Workspace annotations."""
        return self._raw_info.annotations

    @property
    def aggregate(self) -> _utils.Table:
        """Workspace aggregate."""
        project_info = self._get_raw_project_info()
        count_attr_mapping = {
            "versions": "registered_model_version_count",
            "models": "registered_model_count",
            "experiments": "experiment_count",
        }
        data = [
            {
                "entity": entity,
                "count": int(getattr(project_info, attr)),
            }
            for entity, attr in count_attr_mapping.items()
        ]
        return _utils.Table(
            data=data,
            keys=["entity", "count"],
            get_method=lambda x: x,
        )

    @property
    def artifacts(self) -> _artifacts.MLOpsArtifacts:
        """Artifacts in the Workspace."""
        return _artifacts.MLOpsArtifacts(self._client, self)

    @property
    def datasets(self) -> _datasets.MLOpsDatasets:
        """Datasets linked to the Workspace."""
        return _datasets.MLOpsDatasets(self._client, self)

    @property
    def experiments(self) -> _experiments.MLOpsExperiments:
        """Experiments linked to the Workspace."""
        return _experiments.MLOpsExperiments(self._client, self)

    @property
    def models(self) -> _models.MLOpsModels:
        """Registered Models in the Workspace."""
        return _models.MLOpsModels(self._client, self)

    @property
    def deployments(self) -> _deployments.MLOpsScoringDeployments:
        """Real-time scoring Deployments in the Workspace."""
        return _deployments.MLOpsScoringDeployments(self._client, self)

    @property
    def endpoints(self) -> _endpoints.MLOpsEndpoints:
        """Configurable deployment endpoints in the Workspace."""
        return _endpoints.MLOpsEndpoints(self._client, self)

    @property
    def batch_scoring_jobs(self) -> _batch_scoring_jobs.MLOpsBatchScoringJobs:
        """Batch scoring jobs in the Workspace."""
        return _batch_scoring_jobs.MLOpsBatchScoringJobs(self._client, self)

    @property
    def tags(self) -> MLOpsWorkspaceTags:
        """Manage Tags for the Workspace."""
        return MLOpsWorkspaceTags(self._client, self)

    @property
    def events(self) -> _events.MLOpsWorkspaceEvents:
        """Events associated with the Workspace."""
        return _events.MLOpsWorkspaceEvents(self._client, self)

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[Union[str, UnsetType]] = UNSET,
    ) -> None:
        """Update Workspace.

        Args:
            name: display name for the Workspace.
            description: description for the Workspace.
        """
        update_mask = []
        workspace = h2o_mlops_autogen.WorkspaceInlineObject()
        if name is not None:
            workspace.display_name = name
            update_mask.append("display_name")
        if description is not UNSET:
            workspace.description = description
            update_mask.append("description")
        if update_mask:
            self._raw_info = self._client._backend.authz.workspace.update_workspace(
                workspace_name=self._raw_info.name,
                workspace=workspace,
                update_mask=",".join(update_mask),
            ).workspace

    def delete(self) -> None:
        """Delete Workspace from H2O MLOps."""
        self._client._backend.authz.workspace.delete_workspace(name=self._raw_info.name)

    def _get_raw_project_info(self) -> h2o_mlops_autogen.StorageProjectInfo:
        srv = self._client._backend.storage.gateway_aggregator
        return srv.get_project_with_aggregated_info(
            h2o_mlops_autogen.StorageGetProjectWithAggregatedInfoRequest(
                project_id=self.uid,
            ),
        ).project_info

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.authz.workspace.get_workspace(
            name=self._raw_info.name
        ).workspace


class Workspaces:
    def __init__(self, client: _core.Client):
        self._client = client

    def create(self, name: str, description: Optional[str] = None) -> Workspace:
        """Create a Workspace in H2O.

        Args:
            name: display name for Workspace
            description: description of Workspace
        """
        raw_info = self._client._backend.authz.workspace.create_workspace(
            h2o_mlops_autogen.V1Workspace(
                display_name=name,
                description=description,
            )
        ).workspace
        return Workspace(client=self._client, raw_info=raw_info)

    def get(self, uid: str) -> Workspace:
        """Get the Workspace object corresponding to a Workspace in H2O.

        Args:
            uid: H2O unique ID for the Workspace.
        """
        raw_info = self._client._backend.authz.workspace.get_workspace(
            name="workspaces/" + uid
        ).workspace
        return Workspace(client=self._client, raw_info=raw_info)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Workspaces available to the user.

        Examples::

            # filter on columns by using selectors
            mlops.workspaces.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            workspace = mlops.workspaces.list()[0]

            # get a new Table using multiple indexes or slices
            table = mlops.workspaces.list()[2,4]
            table = mlops.workspaces.list()[2:4]
        """
        workspaces = []

        response = self._client._backend.authz.workspace.list_workspaces()
        workspaces += response.workspaces
        while response.next_page_token:
            response = self._client._backend.authz.workspace.list_workspaces(
                page_token=response.next_page_token
            )
            workspaces += response.workspaces
        data = [
            {
                "name": w.display_name,
                "uid": _utils._convert_resource_name_to_uid(w.name),
                "raw_info": w,
            }
            for w in workspaces
        ]
        return _utils.Table(
            data=data,
            keys=["name", "uid"],
            get_method=lambda x: Workspace(
                client=self._client,
                raw_info=x["raw_info"],
            ),
            **selectors,
        )

    def count(self) -> int:
        """Count the Workspaces available to the User."""
        return int(self._client._backend.authz.workspace.count_workspaces().total_size)

    def aggregates(self, **selectors: Any) -> _utils.Table:
        """Retrieve Table of Workspaces' aggregates.

        Examples::

            # filter on columns by using selectors
            mlops.workspaces.aggregates(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            workspace_aggregates = mlops.workspaces.aggregates()[0]

            # get a new Table using multiple indexes or slices
            table = mlops.workspaces.aggregates()[2,4]
            table = mlops.workspaces.aggregates()[2:4]
        """
        project_aggregates = []
        srv = self._client._backend.storage.gateway_aggregator
        response = srv.list_projects_with_aggregated_info(
            h2o_mlops_autogen.StorageListProjectsWithAggregatedInfoRequest(),
        )
        project_aggregates += response.project_info
        while response.paging:
            response = srv.list_projects_with_aggregated_info(
                h2o_mlops_autogen.StorageListProjectsWithAggregatedInfoRequest(
                    paging=h2o_mlops_autogen.StoragePagingRequest(
                        page_token=response.paging.next_page_token
                    ),
                )
            )
            project_aggregates += response.project_info
        data = [
            {
                "uid": pa.project.id,
                "name": pa.project.display_name,
                "versions": pa.registered_model_version_count,
                "models": pa.registered_model_count,
                "experiments": int(pa.experiment_count),
            }
            for pa in project_aggregates
        ]

        class MLOpsWorkspaceAggregate(NamedTuple):
            uid: str
            name: str
            versions: int
            models: int
            experiments: int

        return _utils.Table(
            data=data,
            keys=["name", "versions", "models", "experiments", "uid"],
            get_method=lambda x: MLOpsWorkspaceAggregate(**x),
            **selectors,
        )


class MLOpsWorkspaceTag:
    def __init__(
        self,
        client: _core.Client,
        raw_info: Any,
    ):
        self._client = client
        self._raw_info = raw_info

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    label={self.label!r},\n"
            f"    parent_workspace_uid={self.parent_workspace.uid!r},\n"
            f"    created_time={self.created_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Label: {self.label}\n"
            f"Parent Workspace UID: {self.parent_workspace.uid}\n"
            f"Created Time: {self.created_time}"
        )

    @property
    def uid(self) -> str:
        """Tag unique ID."""
        return self._raw_info.id

    @property
    def label(self) -> str:
        """Text displayed by the Tag."""
        return self._raw_info.display_name

    @property
    def parent_workspace(self) -> Workspace:
        """Parent Workspace the Tag belongs to."""
        project_id = self._raw_info.project_id
        return self._client.workspaces.get(project_id)

    @property
    def created_time(self) -> datetime:
        """Tag created time."""
        return self._raw_info.created_time

    def update(self, label: str) -> None:
        """Update Tag.

        Args:
           label: text displayed by the Tag.
        """
        update_mask = []
        tag = h2o_mlops_autogen.StorageTag(id=self.uid)
        if label is not None:
            tag.display_name = label
            update_mask.append("displayName")
        if update_mask:
            self._raw_info = self._client._backend.storage.tag.update_tag(
                h2o_mlops_autogen.StorageUpdateTagRequest(
                    tag=tag, update_mask=",".join(update_mask)
                )
            ).tag

    def delete(self) -> None:
        """Delete Tag from the Workspace it belongs to."""
        self._client._backend.storage.tag.delete_tag(
            h2o_mlops_autogen.StorageDeleteTagRequest(
                id=self.uid, project_id=self.parent_workspace.uid
            )
        )

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.storage.tag.get_tag(
            h2o_mlops_autogen.StorageGetTagRequest(
                id=self.uid, project_id=self.parent_workspace.uid
            )
        ).tag


class MLOpsWorkspaceTags:
    def __init__(
        self,
        client: _core.Client,
        workspace: Workspace,
    ):
        self._client = client
        self._workspace = workspace

    def create(self, label: str) -> MLOpsWorkspaceTag:
        """Create a Tag for the Workspace.

        Args:
            label: text displayed by the Tag.
        """
        raw_info = self._client._backend.storage.tag.create_tag(
            h2o_mlops_autogen.StorageCreateTagRequest(
                tag=h2o_mlops_autogen.StorageTag(display_name=label),
                project_id=self._workspace.uid,
            )
        ).tag
        return MLOpsWorkspaceTag(client=self._client, raw_info=raw_info)

    def get(self, label: str) -> MLOpsWorkspaceTag:
        """Get the Tag object corresponding to an H2O MLOps Workspace Tag.

        Args:
            label: text displayed by the Tag.
        """
        filtering_request = h2o_mlops_autogen.StorageFilterRequest(
            query=h2o_mlops_autogen.StorageQuery(
                clause=[
                    h2o_mlops_autogen.StorageClause(
                        property_constraint=[
                            h2o_mlops_autogen.StoragePropertyConstraint(
                                _property=h2o_mlops_autogen.StorageProperty(
                                    field="display_name",
                                ),
                                operator=h2o_mlops_autogen.StorageOperator.EQUAL_TO,
                                value=h2o_mlops_autogen.StorageValue(
                                    string_value=label,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
        raw_info = self._client._backend.storage.tag.list_tags(
            h2o_mlops_autogen.StorageListTagsRequest(
                project_id=self._workspace.uid,
                filter=filtering_request,
            )
        ).tag[0]
        return MLOpsWorkspaceTag(client=self._client, raw_info=raw_info)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Tags available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.tags.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            tag = workspace.tags.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.tags.list()[2,4]
            table = workspace.tags.list()[2:4]
        """
        tags = []
        response = self._client._backend.storage.tag.list_tags(
            h2o_mlops_autogen.StorageListTagsRequest(project_id=self._workspace.uid)
        )
        tags += response.tag
        while response.paging:
            response = self._client._backend.storage.tag.list_tags(
                h2o_mlops_autogen.StorageListTagsRequest(
                    project_id=self._workspace.uid,
                    paging=h2o_mlops_autogen.StoragePagingRequest(
                        page_token=response.paging.next_page_token
                    ),
                )
            )
            tags += response.workspace
        data = [
            {
                "label": t.display_name,
                "uid": t.id,
                "raw_info": t,
            }
            for t in tags
            if t.project_id == self._workspace.uid
        ]
        return _utils.Table(
            data=data,
            keys=["label", "uid"],
            get_method=lambda x: MLOpsWorkspaceTag(
                client=self._client, raw_info=x["raw_info"]
            ),
            **selectors,
        )

    def _get_or_create(self, label: str) -> MLOpsWorkspaceTag:
        """Get if exists, otherwise create, a Tag for the Workspace and return a
        corresponding Tag object.

        Args:
            label: text displayed by the Tag.
        """
        tag_table = self.list(label=label)
        return tag_table[0] if tag_table else self.create(label)
