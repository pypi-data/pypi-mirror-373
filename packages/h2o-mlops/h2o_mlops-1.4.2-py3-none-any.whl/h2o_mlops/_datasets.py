from __future__ import annotations

import mimetypes
from datetime import datetime
from os import PathLike
from typing import Any, Dict, List, Optional, Union

import h2o_mlops_autogen
from h2o_mlops import _artifacts, _core, _users, _utils, _workspaces

RESPONSE_METADATA_REQUEST = h2o_mlops_autogen.StorageKeySelection(
    pattern=["%"],
)


class MLOpsDataset:
    """Interact with a Dataset on H2O MLOps."""

    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        raw_info: Any,
    ):
        self._artifacts: Optional[_utils.Table] = None
        self._client = client
        self._workspace = workspace
        self._raw_info = raw_info

        self._creator_uid = raw_info.owner_id

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    name={self.name!r},\n"
            f"    row_count={self.row_count!r},\n"
            f"    column_count={self.column_count!r},\n"
            f"    size={self.size!r},\n"
            f"    creator_uid={self._creator_uid!r},\n"
            f"    created_time={self.created_time!r},\n"
            f"    last_modified_time={self.last_modified_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Name: {self.name}\n"
            f"Number of Rows: {self.row_count}\n"
            f"Number of Columns: {self.column_count}\n"
            f"Size: {self.size} bytes\n"
            f"Creator UID: {self._creator_uid}\n"
            f"Created Time: {self.created_time}\n"
            f"Last Modified Time: {self.last_modified_time}"
        )

    @property
    def uid(self) -> str:
        """Dataset unique ID."""
        return self._raw_info.id

    @property
    def name(self) -> str:
        """Dataset display name."""
        return self._raw_info.display_name

    @property
    def row_count(self) -> Dict[str, Any]:
        """Number of rows in the dataset."""
        return self._raw_info.row_count

    @property
    def column_count(self) -> str:
        """Number of columns in the dataset."""
        return self._raw_info.col_count

    @property
    def size(self) -> int:
        """Dataset file size in bytes."""
        return self._raw_info.size

    @property
    def creator(self) -> _users.MLOpsUser:
        """Dataset creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Dataset created time."""
        return self._raw_info.created_time

    @property
    def last_modified_time(self) -> datetime:
        """Dataset last modified time."""
        return self._raw_info.last_modified_time

    @property
    def metadata(self) -> _utils.Table:
        """Dataset metadata."""
        return _utils._convert_storage_metadata_to_table(
            storage_metadata=self._raw_info.metadata,
        )

    @property
    def statistics(self) -> Dict[str, Any]:
        """Dataset statistics."""
        return self._raw_info.statistics.to_dict()

    @property
    def artifacts(self) -> _artifacts.MLOpsArtifacts:
        """Interact with artifacts for the Dataset."""
        return _artifacts.MLOpsArtifacts(self._client, self)

    @property
    def tags(self) -> MLOpsDatasetTags:
        """Interact with Tags for the Dataset."""
        return MLOpsDatasetTags(self._client, self, self._workspace)

    def update(
        self,
        name: Optional[str] = None,
    ) -> None:
        """Update Dataset.

        Args:
            name: display name for the Dataset.
        """
        update_mask = []
        dataset = h2o_mlops_autogen.StorageDataset(id=self.uid)
        if name is not None:
            dataset.display_name = name
            update_mask.append("displayName")
        if update_mask:
            self._raw_info = self._client._backend.storage.dataset.update_dataset(
                h2o_mlops_autogen.StorageUpdateDatasetRequest(
                    dataset=dataset,
                    update_mask=",".join(update_mask),
                    response_metadata=RESPONSE_METADATA_REQUEST,
                )
            ).dataset

    def delete(self) -> None:
        """Delete Dataset from the Workspace in H2O MLOps."""
        self._client._backend.storage.dataset.delete_dataset(
            h2o_mlops_autogen.StorageDeleteDatasetRequest(
                id=self.uid, project_id=self._workspace.uid
            )
        )

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.storage.dataset.get_dataset(
            h2o_mlops_autogen.StorageGetDatasetRequest(
                id=self.uid,
                response_metadata=RESPONSE_METADATA_REQUEST,
            )
        ).dataset


class MLOpsDatasets:
    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._workspace = workspace

    def create(
        self,
        data: Union[str, PathLike[str]],
        name: str,
    ) -> MLOpsDataset:
        """Create a Dataset in H2O MLOps.

        Args:
            data: relative path to the CSV dataset artifact being uploaded
            name: display name for Dataset
        """
        artifact = self._workspace.artifacts.add(
            data=data, mime_type=mimetypes.types_map[".csv"]
        )
        raw_info = self._client._backend.storage.dataset.create_dataset(
            h2o_mlops_autogen.StorageCreateDatasetRequest(
                project_id=self._workspace.uid,
                dataset=h2o_mlops_autogen.StorageDataset(
                    display_name=name,
                ),
                response_metadata=RESPONSE_METADATA_REQUEST,
            )
        ).dataset
        dataset = MLOpsDataset(self._client, self._workspace, raw_info)
        artifact.update(name="dataset", parent_entity=dataset)
        return dataset

    def get(self, uid: str) -> MLOpsDataset:
        """Get the Dataset object corresponding to an H2O MLOps Dataset.

        Args:
            uid: H2O MLOps unique ID for the Dataset.
        """
        raw_info = self._client._backend.storage.dataset.get_dataset(
            h2o_mlops_autogen.StorageGetDatasetRequest(
                id=uid,
                response_metadata=RESPONSE_METADATA_REQUEST,
            )
        ).dataset
        return MLOpsDataset(self._client, self._workspace, raw_info)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Datasets available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.datasets.list(name="experiment-demo")

            # use an index to get an H2O MLOps entity referenced by the table
            dataset = workspace.datasets.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.datasets.list()[2,4]
            table = workspace.datasets.list()[2:4]
        """
        # construct tag filter if possible and asked for
        filtering_request = None
        tag_label = selectors.pop("tag", None)
        if tag_label and self._workspace.tags.list(label=tag_label):
            tag = self._workspace.tags.get(label=tag_label)
            filtering_request = h2o_mlops_autogen.StorageFilterRequest(
                query=h2o_mlops_autogen.StorageQuery(
                    clause=[
                        h2o_mlops_autogen.StorageClause(
                            tag_constraint=[
                                h2o_mlops_autogen.StorageTagConstraint(
                                    tag_id=tag.uid,
                                ),
                            ],
                        ),
                    ],
                ),
            )
        # no need to search datasets if tag asked for does not exist in workspace
        if filtering_request is None and tag_label:
            data = []
        else:
            datasets = []
            response = self._client._backend.storage.dataset.list_datasets(
                h2o_mlops_autogen.StorageListDatasetsRequest(
                    project_id=self._workspace.uid,
                    filter=filtering_request,
                    response_metadata=RESPONSE_METADATA_REQUEST,
                )
            )
            datasets += response.dataset
            while response.paging:
                response = self._client._backend.storage.dataset.list_datasets(
                    h2o_mlops_autogen.StorageListDatasetsRequest(
                        project_id=self._workspace.uid,
                        paging=h2o_mlops_autogen.StoragePagingRequest(
                            page_token=response.paging.next_page_token
                        ),
                        filter=filtering_request,
                        response_metadata=RESPONSE_METADATA_REQUEST,
                    )
                )
                datasets += response.dataset
            data = [
                {
                    "name": d.display_name,
                    "uid": d.id,
                    "tags": "\n".join(
                        [
                            t.display_name
                            for t in d.tag
                            if t.project_id == self._workspace.uid
                        ]
                    ),
                    "raw_info": d,
                }
                for d in datasets
            ]
        return _utils.Table(
            data=data,
            keys=["name", "uid", "tags"],
            get_method=lambda x: MLOpsDataset(
                self._client, self._workspace, x["raw_info"]
            ),
            **selectors,
        )

    def link(self, uid: str) -> None:
        """Link a Dataset to the Workspace in H2O MLOps.

        Args:
            uid: unique ID for the Dataset.
        """
        self._client._backend.storage.dataset.link_dataset_into_project(
            h2o_mlops_autogen.StorageLinkDatasetIntoProjectRequest(
                project_id=self._workspace.uid, dataset_id=uid
            )
        )

    def unlink(self, uid: str) -> None:
        """Unlink a Dataset from the Workspace in H2O MLOps.

        Args:
            uid: unique ID for the Dataset.
        """
        self._client._backend.storage.dataset.unlink_dataset_from_project(
            h2o_mlops_autogen.StorageUnlinkDatasetFromProjectRequest(
                project_id=self._workspace.uid, dataset_id=uid
            )
        )

    def delete(
        self,
        uids: Optional[List[str]] = None,
        datasets: Optional[Union[_utils.Table, List[MLOpsDataset]]] = None,
    ) -> _utils.Table:
        """Delete Datasets from H2O MLOps.

        Args:
            uids: list of unique H2O MLOps dataset IDs.
            datasets: list of MLOpsDataset instances
                or a _utils.Table containing datasets.
        """
        dataset_ids = set(uids or [])
        for d in datasets or []:
            if not isinstance(d, MLOpsDataset):
                raise TypeError(
                    "All elements in 'datasets' must be instances of MLOpsDataset."
                )
            dataset_ids.add(d.uid)
        deleted_datasets = self._client._backend.storage.dataset.batch_delete_dataset(
            h2o_mlops_autogen.StorageBatchDeleteDatasetRequest(
                dataset_request=[
                    h2o_mlops_autogen.StorageDeleteDatasetRequest(
                        id=d_id,
                        project_id=self._workspace.uid,
                    )
                    for d_id in dataset_ids
                ],
            )
        ).dataset_delete_response
        data = [
            {
                "dataset_uid": dd.id,
                "is_deleted": dd.status,
                "message": dd.message,
                "workspace_uid": dd.project_id,
            }
            for dd in deleted_datasets
        ]
        return _utils.Table(
            data=data,
            keys=[
                "dataset_uid",
                "is_deleted",
                "message",
                "workspace_uid",
            ],
            get_method=lambda x: x,
        )


class MLOpsDatasetTags:
    def __init__(
        self,
        client: _core.Client,
        dataset: MLOpsDataset,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._dataset = dataset
        self._workspace = workspace

    def add(self, label: str) -> None:
        """Add a Tag to the Dataset.

        Args:
            label: text displayed by the Tag.
        """
        tag = self._workspace.tags._get_or_create(label)
        self._client._backend.storage.dataset.tag_dataset(
            h2o_mlops_autogen.StorageTagDatasetRequest(
                dataset_id=self._dataset.uid, tag_id=tag.uid
            )
        )

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """List Tags for the Dataset.

        Examples::

            # filter on columns by using selectors
            dataset.tags.list(label="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            tag = dataset.tags.list()[0]

            # get a new Table using multiple indexes or slices
            table = dataset.tags.list()[2,4]
            table = dataset.tags.list()[2:4]
        """
        # refresh list of tags
        self._dataset._refresh()
        tags = self._dataset._raw_info.tag
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
            get_method=lambda x: _workspaces.MLOpsWorkspaceTag(
                client=self._client, raw_info=x["raw_info"]
            ),
            **selectors,
        )

    def remove(self, label: str) -> None:
        """Remove a Tag from the Dataset.

        Args:
            label: text displayed by the Tag.
        """
        tags = self._dataset.tags.list(label=label)
        if tags:
            self._client._backend.storage.dataset.untag_dataset(
                h2o_mlops_autogen.StorageUntagDatasetRequest(
                    dataset_id=self._dataset.uid, tag_id=tags[0].uid
                )
            )
