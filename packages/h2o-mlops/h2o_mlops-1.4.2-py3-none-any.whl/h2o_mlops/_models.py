from __future__ import annotations

import io
from datetime import datetime
from os import PathLike
from typing import Any, List, NamedTuple
from typing import Optional
from typing import Union

import h2o_mlops_autogen
from h2o_mlops import (
    _core,
    _experiments,
    _users,
    _utils,
    _workspaces,
)
from h2o_mlops._utils import UNSET


class MLOpsModel:
    """Interact with a Registered Model on H2O MLOps."""

    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        raw_info: Any,
    ):
        self._client = client
        self._workspace = workspace
        self._raw_info = raw_info

        self._creator_uid = raw_info.created_by

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
        """Registered Model unique ID"""
        return self._raw_info.id

    @property
    def name(self) -> str:
        """Registered Model display name."""
        return self._raw_info.display_name

    @property
    def description(self) -> str:
        """Registered Model description."""
        return self._raw_info.description

    @property
    def creator(self) -> _users.MLOpsUser:
        """Registered Model creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Registered Model created time."""
        return self._raw_info.created_time

    @property
    def last_modified_time(self) -> datetime:
        """Registered Model last modified time."""
        return self._raw_info.updated_time

    @property
    def last_modified_by(self) -> _users.MLOpsUser:
        """Registered Model last modified by."""
        user_id = self._raw_info.updated_by
        return self._client.users.get(user_id)

    @property
    def state(self) -> str:
        """Registered Model state."""
        return self._raw_info.status

    @property
    def version_count(self) -> int:
        """Number of versions in the Registered Model."""
        return int(
            self._client._backend.storage.registered_model_version.count_model_versions(
                h2o_mlops_autogen.StorageCountModelVersionsRequest(
                    registered_model_id=self.uid,
                )
            ).count
        )

    def experiment(
        self, model_version: Union[int, str] = "latest"
    ) -> _experiments.MLOpsExperiment:
        """Get the Experiment object registered to an H2O MLOps Model Version.

        Args:
            model_version: Model Version number of the Experiment. Use "latest"
                to get the Experiment object of the latest Model Version.
        """
        if model_version == "latest":
            return self._workspace.experiments.get(self.versions()[0].experiment_uid)
        if isinstance(model_version, int):
            return self._workspace.experiments.get(
                self.versions(version=model_version)[0].experiment_uid
            )
        raise ValueError("'model_version' must be either `latest` or an integer value.")

    def register(
        self,
        experiment: Union[
            str,
            PathLike[str],
            io.BytesIO,
            _experiments.MLOpsExperiment,
        ],
        name: Optional[str] = None,
    ) -> None:
        """Register an H2O MLOps Experiment to a Model Version, either from an
        MLOpsExperiment instance or directly from the experiment data. An Experiment
        can only be registered to one Model Version.

        Args:
            experiment: experiment data or an MLOpsExperiment instance to be registered.
            name: name of the experiment to use when experiment data is provided
                directly, instead of an MLOpsExperiment instance.
        """
        self._client._backend.storage.registered_model_version.create_model_version(
            h2o_mlops_autogen.StorageCreateModelVersionRequest(
                registered_model_version=(
                    h2o_mlops_autogen.StorageRegisteredModelVersion(
                        registered_model_id=self.uid,
                        experiment_id=(
                            experiment.uid
                            if isinstance(experiment, _experiments.MLOpsExperiment)
                            else (
                                self._workspace.experiments.create(
                                    data=experiment,
                                    name=name,
                                ).uid
                            )
                        ),
                    )
                )
            )
        )

    def versions(self, **selectors: Any) -> _utils.Table:
        """Retrieve Table of the H2O Registered Model's Versions and
        corresponding Experiment unique IDs.

        Examples::

            # filter on columns by using selectors
            model.versions(version=1)

            # use an index to get an H2O MLOps entity referenced by the table
            model_version = model.versions()[0]

            # get a new Table using multiple indexes or slices
            table = model.versions()[2,4]
            table = model.versions()[2:4]
        """
        sorting_request = h2o_mlops_autogen.StorageSortingRequest(
            _property=[
                h2o_mlops_autogen.StorageSortProperty(
                    _property=h2o_mlops_autogen.StorageProperty(
                        field="version_number",
                    ),
                    order=h2o_mlops_autogen.StorageOrder.DESCENDING,
                ),
            ],
        )
        srv = self._client._backend.storage.registered_model_version
        model_versions = srv.list_model_versions_for_model(
            h2o_mlops_autogen.StorageListModelVersionsForModelRequest(
                registered_model_id=self.uid,
                sorting=sorting_request,
            )
        ).model_versions
        data = [
            {
                "uid": mv.id,
                "version": mv.version,
                "model_uid": mv.registered_model_id,
                "experiment_uid": mv.experiment_id,
                "creator_uid": mv.created_by,
                "created_time": mv.created_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "last_modified_time": mv.updated_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "last_modified_by": mv.updated_by,
                "state": mv.status,
            }
            for mv in model_versions
        ]

        class MLOpsModelVersion(NamedTuple):
            uid: str
            version: int
            model_uid: str
            experiment_uid: str
            creator_uid: str
            created_time: str
            last_modified_time: str
            last_modified_by: str
            state: str

        return _utils.Table(
            data=data,
            keys=["version", "experiment_uid"],
            get_method=lambda x: MLOpsModelVersion(**x),
            **selectors,
        )

    def unregister(
        self,
        experiment: Optional[_experiments.MLOpsExperiment] = None,
        unregister_all: bool = False,
    ) -> Optional[_utils.Table]:
        """Unregister an H2O MLOps Experiment from a Model Version.

        Args:
            experiment: a single Experiment object to be unregistered
            unregister_all: indicates whether to unregister
                all the experiments associated.
        """
        srv = self._client._backend.storage.registered_model_version
        if unregister_all:
            deleted_model_versions = srv.batch_delete_model_version(
                h2o_mlops_autogen.StorageBatchDeleteModelVersionRequest(
                    ids=[v.uid for v in self.versions()],
                )
            ).delete_model_version_response
            data = [
                {
                    "version_uid": dmv.id,
                    "is_unregistered": dmv.status,
                    "message": dmv.message,
                }
                for dmv in deleted_model_versions
            ]
            return _utils.Table(
                data=data,
                keys=["version_uid", "is_unregistered", "message"],
                get_method=lambda x: x,
            )
        if experiment:
            for v in self.versions(experiment_uid=experiment.uid):
                srv.delete_model_version(
                    h2o_mlops_autogen.StorageDeleteModelVersionRequest(
                        id=v.uid,
                    )
                )
            return None
        else:
            raise ValueError(
                "Either 'experiment' must be provided, "
                "or 'unregister_all' must be set to True to perform unregistering."
            )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[Union[str, object]] = UNSET,
    ) -> None:
        """Update Experiment.

        Args:
            name: name for the Registered Model.
            description: description for the Registered Model.
        """
        update_mask = []
        registered_model = h2o_mlops_autogen.StorageRegisteredModel(id=self.uid)
        if name is not None:
            registered_model.display_name = name
            update_mask.append("name")
        if description is not UNSET:
            registered_model.description = description
            update_mask.append("description")
        if update_mask:
            self._raw_info = (
                self._client._backend.storage.registered_model.update_registered_model(
                    h2o_mlops_autogen.StorageUpdateRegisteredModelRequest(
                        registered_model=registered_model,
                        update_mask=",".join(update_mask),
                    )
                ).registered_model
            )

    def delete(self) -> None:
        """Delete Registered Model from the Workspace in H2O MLOps.
        This deletes the registered model and all its associated versions.
        """
        self._client._backend.storage.registered_model.delete_registered_model(
            h2o_mlops_autogen.StorageDeleteRegisteredModelRequest(self.uid)
        )

    def _refresh(self) -> None:
        self._raw_info = (
            self._client._backend.storage.registered_model.get_registered_model(
                h2o_mlops_autogen.StorageGetRegisteredModelRequest(
                    model_id=self.uid,
                )
            ).registered_model
        )


class MLOpsModels:
    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._workspace = workspace

    def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> MLOpsModel:
        """Create a Registered Model in H2O MLOps.

        Args:
            name: display name for Registered Model
            description: description of Registered Model
        """
        raw_info = (
            self._client._backend.storage.registered_model.create_registered_model(
                h2o_mlops_autogen.StorageCreateRegisteredModelRequest(
                    registered_model=h2o_mlops_autogen.StorageRegisteredModel(
                        display_name=name,
                        description=description,
                        project_id=self._workspace.uid,
                    )
                )
            ).registered_model
        )
        return MLOpsModel(self._client, self._workspace, raw_info)

    def get(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> MLOpsModel:
        """Get the Registered Model object corresponding to an
        H2O MLOps Registered Model.

        Args:
            uid: H2O MLOps unique ID for the Registered Model.
            name: H2O MLOps Workspace-specific unique name for the Registered Model.
        """
        raw_info = None
        srv = self._client._backend.storage.registered_model
        if uid:
            raw_info = srv.get_registered_model(
                h2o_mlops_autogen.StorageGetRegisteredModelRequest(
                    model_id=uid,
                )
            ).registered_model
            if name and raw_info.display_name != name:
                raise ValueError(
                    "Provided 'uid' is associated with a different "
                    "'name' than the one given."
                )
        elif name:
            raw_info = srv.get_registered_model_by_name(
                h2o_mlops_autogen.StorageGetRegisteredModelByNameRequest(
                    model_name=name,
                    project_id=self._workspace.uid,
                )
            ).registered_model
        if raw_info:
            return MLOpsModel(self._client, self._workspace, raw_info)
        raise ValueError("Either 'uid' or 'name' must be provided to retrieve a model.")

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of H2O Registered Models available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.models.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            model = workspace.models.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.models.list()[2,4]
            table = workspace.models.list()[2:4]
        """
        registered_models = []
        srv = self._client._backend.storage.registered_model
        response = srv.list_registered_models(
            h2o_mlops_autogen.StorageListRegisteredModelsRequest(
                project_id=self._workspace.uid
            )
        )
        registered_models += response.registered_models
        while response.paging:
            response = srv.list_registered_models(
                h2o_mlops_autogen.StorageListRegisteredModelsRequest(
                    project_id=self._workspace.uid,
                    paging=h2o_mlops_autogen.StoragePagingRequest(
                        page_token=response.paging.next_page_token
                    ),
                )
            )
            registered_models += response.registered_models
        data = [
            {
                "name": rm.display_name,
                "uid": rm.id,
                "raw_info": rm,
            }
            for rm in registered_models
        ]
        return _utils.Table(
            data=data,
            keys=["name", "uid"],
            get_method=lambda x: MLOpsModel(
                self._client, self._workspace, x["raw_info"]
            ),
            **selectors,
        )

    def count(self) -> int:
        """Count the Registered Models available in the Workspace."""
        return int(
            self._client._backend.storage.registered_model.count_registered_models(
                h2o_mlops_autogen.StorageCountRegisteredModelRequest(
                    project_id=self._workspace.uid,
                )
            ).registered_model_count
        )

    def delete(
        self,
        uids: Optional[List[str]] = None,
        models: Optional[Union[_utils.Table, List[MLOpsModel]]] = None,
    ) -> _utils.Table:
        """Delete Registered Models from H2O MLOps.

        Args:
            uids: list of unique H2O MLOps model IDs.
            models: list of MLOpsModel instances
                or a _utils.Table containing models.
        """
        model_ids = set(uids or [])
        for m in models or []:
            if not isinstance(m, MLOpsModel):
                raise TypeError(
                    "All elements in 'models' " "must be instances of MLOpsModel."
                )
            model_ids.add(m.uid)
        srv = self._client._backend.storage.registered_model
        deleted_models = srv.batch_delete_registered_model(
            h2o_mlops_autogen.StorageBatchDeleteRegisteredModelRequest(
                model_ids=list(model_ids),
            )
        ).delete_registered_model_response
        data = [
            {
                "model_uid": dm.model_id,
                "is_deleted": dm.status,
                "message": dm.message,
            }
            for dm in deleted_models
        ]
        return _utils.Table(
            data=data,
            keys=["model_uid", "is_deleted", "message"],
            get_method=lambda x: x,
        )

    def register(
        self,
        experiment: Union[
            str,
            PathLike[str],
            io.BytesIO,
            _experiments.MLOpsExperiment,
        ],
        name: str,
    ) -> MLOpsModel:
        """Registers an H2O MLOps Experiment to a Model Version, either from an
        MLOpsExperiment instance or directly from the experiment data.

        Args:
            experiment: experiment data or an MLOpsExperiment instance to be registered.
            name: name of the model. If experiment data is provided instead
                of an MLOpsExperiment instance, this name is also used as the
                experiment name.
        """
        self._client._backend.storage.registered_model_version.create_model_version(
            h2o_mlops_autogen.StorageCreateModelVersionRequest(
                registered_model_version=(
                    h2o_mlops_autogen.StorageRegisteredModelVersion(
                        experiment_id=(
                            experiment.uid
                            if isinstance(experiment, _experiments.MLOpsExperiment)
                            else (
                                self._workspace.experiments.create(
                                    data=experiment,
                                    name=name,
                                ).uid
                            )
                        ),
                    )
                ),
                registered_model_display_name=name,
                project_id=self._workspace.uid,
            )
        )
        return self.get(name=name)
