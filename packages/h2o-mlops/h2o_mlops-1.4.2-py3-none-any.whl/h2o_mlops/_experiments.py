from __future__ import annotations

import io
import mimetypes
from datetime import datetime
from os import PathLike
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

import h2o_mlops_autogen
from h2o_mlops import (
    _artifacts,
    _core,
    _datasets,
    _models,
    _runtimes,
    _users,
    _utils,
    _workspaces,
    options,
)

RESPONSE_METADATA_REQUEST = h2o_mlops_autogen.StorageKeySelection(
    pattern=["%"],
)


class MLOpsExperiment:
    """Interact with an Experiment on H2O MLOps."""

    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        raw_info: Any,
    ):
        self._client = client
        self._workspace = workspace
        self._raw_info = raw_info

        self._creator_uid = raw_info.owner_id

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
        """Experiment unique ID."""
        return self._raw_info.id

    @property
    def name(self) -> str:
        """Experiment display name."""
        return self._raw_info.display_name

    @property
    def description(self) -> str:
        """Experiment description."""
        return self._raw_info.description

    @property
    def creator(self) -> _users.MLOpsUser:
        """Experiment creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Experiment created time."""
        return self._raw_info.created_time

    @property
    def last_modified_time(self) -> datetime:
        """Experiment last modified time."""
        return self._raw_info.last_modified_time

    @property
    def state(self) -> str:
        """Experiment state."""
        return self._raw_info.status

    @property
    def is_registered(self) -> bool:
        """Indicates whether the Experiment is registered as a Model."""
        return self._client._backend.storage.experiment.is_experiment_registered(
            h2o_mlops_autogen.StorageIsExperimentRegisteredRequest(
                experiment_id=self.uid, project_id=self._workspace.uid
            )
        ).is_registered

    @property
    def registered_model(self) -> Optional[Tuple[_models.MLOpsModel, int]]:
        """Registered Model of the Experiment."""
        if raw_info := self._get_raw_registered_model_version():
            return (
                self._workspace.models.get(
                    uid=raw_info.registered_model_id,
                ),
                raw_info.version,
            )
        return None

    @property
    def metadata(self) -> _utils.Table:
        """Experiment metadata."""
        return _utils._convert_storage_metadata_to_table(
            storage_metadata=self._raw_info.metadata,
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """Experiment parameters."""
        return self._raw_info.parameters.to_dict()

    @property
    def statistics(self) -> Dict[str, Any]:
        """Experiment statistics."""
        return self._raw_info.statistics.to_dict()

    @property
    def input_schema(self) -> _utils.Table:
        """Experiment input schema."""
        input_schema_table = _utils._convert_storage_metadata_to_table(
            storage_metadata=self._raw_info.metadata,
            key="input_schema",
        )
        return _utils.Table(
            data=(
                input_schema_table[0].get("input_schema", [])
                if input_schema_table
                else []
            ),
            keys=["name", "type"],
            get_method=lambda x: x,
        )

    @property
    def output_schema(self) -> _utils.Table:
        """Experiment output schema."""
        output_schema_table = _utils._convert_storage_metadata_to_table(
            storage_metadata=self._raw_info.metadata,
            key="output_schema",
        )
        return _utils.Table(
            data=(
                output_schema_table[0].get("output_schema", [])
                if output_schema_table
                else []
            ),
            keys=["name", "type"],
            get_method=lambda x: x,
        )

    @property
    def scoring_runtimes(self) -> _utils.Table:
        """Retrieve Table of Scoring Runtimes available for scoring."""
        srv = self._client._backend.deployer.composition
        compositions = srv.list_experiment_artifact_compositions(
            parent=f"workspaces/{self._workspace.uid}/experiments/{self.uid}",
        ).experiment_artifact_compositions
        data = [
            {
                "artifact_type": c.deployable_artifact_type.name,
                "runtime_uid": c.runtime.name,
                "runtime_name": c.runtime.display_name,
                "raw_info": c,
            }
            for c in compositions
        ]
        return _utils.Table(
            data=data,
            keys=["artifact_type", "runtime_uid", "runtime_name"],
            get_method=lambda x: _runtimes.MLOpsScoringRuntime(x["raw_info"]),
        )

    @property
    def artifacts(self) -> _artifacts.MLOpsArtifacts:
        """Interact with artifacts for the Experiment."""
        return _artifacts.MLOpsArtifacts(self._client, self)

    @property
    def dataset_metrics(self) -> MLOpsExperimentDatasetMetrics:
        """Interact with datasets-specific metrics for the Experiment."""
        return MLOpsExperimentDatasetMetrics(self._client, self)

    @property
    def tags(self) -> MLOpsExperimentTags:
        """Interact with Tags for the Experiment."""
        return MLOpsExperimentTags(self._client, self, self._workspace)

    @property
    def comments(self) -> MLOpsExperimentComments:
        """Interact with comments for the Experiment."""
        return MLOpsExperimentComments(self._client, self)

    def compute_k8s_options(
        self,
        runtime_uid: str,
        workers: int = 1,
    ) -> options.KubernetesOptions:
        """
        Compute KubernetesOptions for deploying the Experiment.

        Args:
            runtime_uid: H2O MLOps unique ID of the Runtime.
            workers: Number of runtime worker processes,
                only applicable to python based scorers. Defaults to 1.
        """
        srv = self._client._backend.deployer.profiling
        krr = srv.compute_suggested_scoring_resource_requirements(
            experiment=f"workspaces/{self._workspace.uid}/experiments/{self.uid}",
            body=h2o_mlops_autogen.V2InlineObject(
                runtime=runtime_uid,
                workers=workers,
            ),
        ).kubernetes_resource_requirements
        return options.KubernetesOptions(requests=krr.requests, limits=krr.limits)

    def update(
        self,
        name: Optional[str] = None,
    ) -> None:
        """Update Experiment.

        Args:
            name: display name for the Experiment.
        """
        update_mask = []
        experiment = h2o_mlops_autogen.StorageExperiment(id=self.uid)
        if name is not None:
            experiment.display_name = name
            update_mask.append("displayName")
        if update_mask:
            self._raw_info = self._client._backend.storage.experiment.update_experiment(
                h2o_mlops_autogen.StorageUpdateExperimentRequest(
                    experiment=experiment,
                    update_mask=",".join(update_mask),
                    response_metadata=RESPONSE_METADATA_REQUEST,
                )
            ).experiment

    def delete(self) -> None:
        """Delete Experiment from the Workspace in H2O MLOps."""
        self._client._backend.storage.experiment.delete_experiment(
            h2o_mlops_autogen.StorageDeleteExperimentRequest(
                id=self.uid, project_id=self._workspace.uid
            )
        )

    def restore(self) -> None:
        """Restore the deleted Experiment to the Workspace in H2O MLOps."""
        self._client._backend.storage.experiment.recover_deleted_experiment(
            h2o_mlops_autogen.StorageRecoverDeletedExperimentRequest(
                experiment_id=self.uid, project_id=self._workspace.uid
            )
        )

    def _get_raw_registered_model_version(
        self,
    ) -> Optional[h2o_mlops_autogen.StorageRegisteredModelVersion]:
        filtering_request = h2o_mlops_autogen.StorageFilterRequest(
            query=h2o_mlops_autogen.StorageQuery(
                clause=[
                    h2o_mlops_autogen.StorageClause(
                        property_constraint=[
                            h2o_mlops_autogen.StoragePropertyConstraint(
                                _property=h2o_mlops_autogen.StorageProperty(
                                    field="project_id",
                                ),
                                operator=h2o_mlops_autogen.StorageOperator.EQUAL_TO,
                                value=_utils._convert_to_storage_value(
                                    value=self._workspace.uid, is_id_value=True
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
        try:
            srv = self._client._backend.storage.registered_model_version
            raw_info = srv.get_model_version_for_experiment(
                h2o_mlops_autogen.StorageGetModelVersionForExperimentRequest(
                    experiment_id=self.uid, filter=filtering_request
                )
            ).registered_model_version[0]
        except Exception:
            return None
        return raw_info

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.storage.experiment.get_experiment(
            h2o_mlops_autogen.StorageGetExperimentRequest(
                id=self.uid,
                response_metadata=RESPONSE_METADATA_REQUEST,
            )
        ).experiment


class MLOpsExperiments:
    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._workspace = workspace

    def create(
        self,
        data: Union[str, PathLike[str], io.BytesIO],
        name: str,
        description: Optional[str] = None,
    ) -> MLOpsExperiment:
        """Create an Experiment in H2O MLOps.

        Args:
            data: relative path to the experiment artifact being uploaded
            name: display name for Experiment
            description: description for Experiment
        """
        artifact = self._workspace.artifacts.add(
            data=data, mime_type=mimetypes.types_map[".zip"]
        )
        ingestion = artifact._create_model_ingestion()
        model_metadata = _utils._convert_metadata(ingestion.model_metadata)
        model_params = h2o_mlops_autogen.StorageExperimentParameters()
        if ingestion.model_parameters is not None:
            model_params.target_column = ingestion.model_parameters.target_column
        raw_info = self._client._backend.storage.experiment.create_experiment(
            h2o_mlops_autogen.StorageCreateExperimentRequest(
                project_id=self._workspace.uid,
                experiment=h2o_mlops_autogen.StorageExperiment(
                    display_name=name,
                    description=description,
                    metadata=model_metadata,
                    parameters=model_params,
                ),
                response_metadata=RESPONSE_METADATA_REQUEST,
                disable_model_registration=True,
            )
        ).experiment
        experiment = MLOpsExperiment(self._client, self._workspace, raw_info)
        artifact.update(name=ingestion.artifact_type, parent_entity=experiment)
        return experiment

    def get(self, uid: str) -> MLOpsExperiment:
        """Get the Experiment object corresponding to an H2O MLOps Experiment.

        Args:
            uid: H2O MLOps unique ID for the Experiment.
        """
        raw_info = self._client._backend.storage.experiment.get_experiment(
            h2o_mlops_autogen.StorageGetExperimentRequest(
                id=uid,
                response_metadata=RESPONSE_METADATA_REQUEST,
            )
        ).experiment
        return MLOpsExperiment(self._client, self._workspace, raw_info)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Experiments available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.experiments.list(name="experiment-demo")

            # use an index to get an H2O MLOps entity referenced by the table
            experiment = workspace.experiments.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.experiments.list()[2,4]
            table = workspace.experiments.list()[2:4]
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
        # no need to search experiments if tag asked for does not exist in project
        if filtering_request is None and tag_label:
            data = []
        else:
            experiments = []
            response = self._client._backend.storage.experiment.list_experiments(
                h2o_mlops_autogen.StorageListExperimentsRequest(
                    project_id=self._workspace.uid,
                    filter=filtering_request,
                    response_metadata=RESPONSE_METADATA_REQUEST,
                )
            )
            experiments += response.experiment
            while response.paging:
                response = self._client._backend.storage.experiment.list_experiments(
                    h2o_mlops_autogen.StorageListExperimentsRequest(
                        project_id=self._workspace.uid,
                        paging=h2o_mlops_autogen.StoragePagingRequest(
                            page_token=response.paging.next_page_token
                        ),
                        filter=filtering_request,
                        response_metadata=RESPONSE_METADATA_REQUEST,
                    )
                )
                experiments += response.experiment
            data = [
                {
                    "name": e.display_name,
                    "uid": e.id,
                    "tags": "\n".join(
                        [
                            t.display_name
                            for t in e.tag
                            if t.project_id == self._workspace.uid
                        ]
                    ),
                    "raw_info": e,
                }
                for e in experiments
            ]
        return _utils.Table(
            data=data,
            keys=["name", "uid", "tags"],
            get_method=lambda x: MLOpsExperiment(
                self._client, self._workspace, x["raw_info"]
            ),
            **selectors,
        )

    def count(self) -> int:
        """Count the Experiments available in the Workspace."""
        return int(
            self._client._backend.storage.experiment.count_experiments(
                h2o_mlops_autogen.StorageCountExperimentsRequest(
                    project_id=self._workspace.uid,
                    filter=None,
                )
            ).count
        )

    def link(self, uid: str) -> None:
        """Link an Experiment to the Workspace in H2O MLOps.

        Args:
            uid: unique ID for the Experiment.
        """
        self._client._backend.storage.experiment.link_experiment_into_project(
            h2o_mlops_autogen.StorageLinkExperimentIntoProjectRequest(
                project_id=self._workspace.uid, experiment_id=uid
            )
        )

    def unlink(self, uid: str) -> None:
        """Unlink an Experiment from the Workspace in H2O MLOps.

        Args:
            uid: unique ID for the Experiment.
        """
        self._client._backend.storage.experiment.unlink_experiment_from_project(
            h2o_mlops_autogen.StorageUnlinkExperimentFromProjectRequest(
                project_id=self._workspace.uid, experiment_id=uid
            )
        )

    def delete(
        self,
        uids: Optional[List[str]] = None,
        experiments: Optional[Union[_utils.Table, List[MLOpsExperiment]]] = None,
    ) -> _utils.Table:
        """Delete Experiments from H2O MLOps.

        Args:
            uids: list of unique H2O MLOps experiment IDs.
            experiments: list of MLOpsExperiment instances
                or a _utils.Table containing experiments.
        """
        experiment_ids = set(uids or [])
        for e in experiments or []:
            if not isinstance(e, MLOpsExperiment):
                raise TypeError(
                    "All elements in 'experiments' "
                    "must be instances of MLOpsExperiment."
                )
            experiment_ids.add(e.uid)
        deleted_experiments = (
            self._client._backend.storage.experiment.batch_delete_experiment(
                h2o_mlops_autogen.StorageBatchDeleteExperimentRequest(
                    experiment_request=[
                        h2o_mlops_autogen.StorageDeleteExperimentRequest(
                            id=e_id,
                            project_id=self._workspace.uid,
                        )
                        for e_id in experiment_ids
                    ],
                )
            ).experiment_delete_response
        )
        data = [
            {
                "experiment_uid": de.id,
                "is_deleted": de.status,
                "message": de.message,
                "workspace_uid": de.project_id,
            }
            for de in deleted_experiments
        ]
        return _utils.Table(
            data=data,
            keys=[
                "experiment_uid",
                "is_deleted",
                "message",
                "workspace_uid",
            ],
            get_method=lambda x: x,
        )

    def restore(
        self,
        uids: Optional[List[str]] = None,
        experiments: Optional[Union[_utils.Table, List[MLOpsExperiment]]] = None,
    ) -> _utils.Table:
        """Restore Experiments to H2O MLOps.

        Args:
            uids: list of unique H2O MLOps experiment IDs.
            experiments: list of MLOpsExperiment instances
                or a _utils.Table containing experiments.
        """
        experiment_ids = set(uids or [])
        for e in experiments or []:
            if not isinstance(e, MLOpsExperiment):
                raise TypeError(
                    "All elements in 'experiments' "
                    "must be instances of MLOpsExperiment."
                )
            experiment_ids.add(e.uid)
        restored_experiments = (
            self._client._backend.storage.experiment.batch_recover_deleted_experiment(
                h2o_mlops_autogen.StorageBatchRecoverDeletedExperimentRequest(
                    recover_experiment_requests=[
                        h2o_mlops_autogen.StorageRecoverDeletedExperimentRequest(
                            experiment_id=e_id,
                            project_id=self._workspace.uid,
                        )
                        for e_id in experiment_ids
                    ],
                )
            ).recover_experiment_responses
        )
        data = [
            {
                "experiment_uid": re.experiment_id,
                "is_restored": re.status,
                "message": re.message,
                "workspace_uid": re.project_id,
            }
            for re in restored_experiments
        ]
        return _utils.Table(
            data=data,
            keys=[
                "experiment_uid",
                "is_restored",
                "message",
                "workspace_uid",
            ],
            get_method=lambda x: x,
        )


class MLOpsExperimentDatasetMetrics:
    def __init__(
        self,
        client: _core.Client,
        experiment: MLOpsExperiment,
    ):
        self._client = client
        self._experiment = experiment

    def add(
        self,
        dataset: _datasets.MLOpsDataset,
        key: str,
        value: Union[str, int, float, bool, datetime, Dict, List[Dict]],
    ) -> None:
        """Add a Dataset-specific Metric to the Experiment.

        Args:
            dataset: Dataset associated with the Metric.
            key: unique key for the metric within the given Dataset.
            value: value of the Metric.
        """
        self._client._backend.storage.experiment.create_experiment_metric(
            h2o_mlops_autogen.StorageCreateExperimentMetricRequest(
                experiment_id=self._experiment.uid,
                dataset_id=dataset.uid,
                key=key,
                value=_utils._convert_to_storage_value(value),
            )
        )

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """List Datasets-specific Metrics for the Experiment.

        Examples::

            # filter on columns by using selectors
            experiment.dataset_metrics.list(dataset_uid="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            dataset_metric = experiment.dataset_metrics.list()[0]

            # get a new Table using multiple indexes or slices
            table = experiment.dataset_metrics.list()[2,4]
            table = experiment.dataset_metrics.list()[2:4]
        """
        dataset_metrics = []
        response = self._client._backend.storage.experiment.list_experiment_metrics(
            h2o_mlops_autogen.StorageListExperimentMetricsRequest(
                experiment_id=self._experiment.uid,
            )
        )
        dataset_metrics += response.metric
        while response.paging:
            response = self._client._backend.storage.experiment.list_experiment_metrics(
                h2o_mlops_autogen.StorageListExperimentMetricsRequest(
                    experiment_id=self._experiment.uid,
                    paging=h2o_mlops_autogen.StoragePagingRequest(
                        page_token=response.paging.next_page_token
                    ),
                )
            )
            dataset_metrics += response.metric
        data = [
            {
                "dataset_uid": dm.dataset_id,
                "key": dm.key,
                "value": _utils._convert_from_storage_value(dm.value),
            }
            for dm in dataset_metrics
        ]

        class MLOpsExperimentDatasetMetric(NamedTuple):
            dataset_uid: str
            key: str
            value: str

        return _utils.Table(
            data=data,
            keys=["dataset_uid", "key", "value"],
            get_method=lambda x: MLOpsExperimentDatasetMetric(**x),
            **selectors,
        )


class MLOpsExperimentComments:
    def __init__(
        self,
        client: _core.Client,
        experiment: MLOpsExperiment,
    ):
        self._client = client
        self._experiment = experiment

    def add(self, message: str) -> None:
        """Add a new Comment to the Experiment.

        Args:
            message: text displayed by the Comment.
        """
        self._client._backend.storage.experiment.create_experiment_comment(
            h2o_mlops_autogen.StorageCreateExperimentCommentRequest(
                experiment_id=self._experiment.uid, comment_message=message
            )
        )

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """List Comments for the Experiment.

        Examples::

            # filter on columns by using selectors
            experiment.comments.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            comment = experiment.comments.list()[0]

            # get a new Table using multiple indexes or slices
            table = experiment.comments.list()[2,4]
            table = experiment.comments.list()[2:4]
        """
        comments = []
        sorting_request = h2o_mlops_autogen.StorageSortingRequest(
            _property=[
                h2o_mlops_autogen.StorageSortProperty(
                    _property=h2o_mlops_autogen.StorageProperty(
                        field="created_time",
                    ),
                    order=h2o_mlops_autogen.StorageOrder.ASCENDING,
                ),
            ],
        )
        response = self._client._backend.storage.experiment.list_experiment_comments(
            h2o_mlops_autogen.StorageListExperimentCommentsRequest(
                experiment_id=self._experiment.uid,
                sorting=sorting_request,
            )
        )
        comments += response.comment
        while response.paging:
            response = (
                self._client._backend.storage.experiment.list_experiment_comments(
                    h2o_mlops_autogen.StorageListExperimentCommentsRequest(
                        experiment_id=self._experiment.uid,
                        sorting=sorting_request,
                        paging=h2o_mlops_autogen.StoragePagingRequest(
                            page_token=response.paging.next_page_token
                        ),
                    )
                )
            )
            comments += response.comment
        data = [
            {
                "uid": c.id,
                "created_time": c.created_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "author_username": self._client.users.get(c.author_id).username,
                "message": c.message,
            }
            for c in comments
        ]

        class MLOpsExperimentComment(NamedTuple):
            uid: str
            created_time: str
            author_username: str
            message: str

        return _utils.Table(
            data=data,
            keys=[
                "created_time",
                "author_username",
                "message",
            ],
            get_method=lambda x: MLOpsExperimentComment(**x),
            **selectors,
        )


class MLOpsExperimentTags:
    def __init__(
        self,
        client: _core.Client,
        experiment: MLOpsExperiment,
        workspace: _workspaces.Workspace,
    ):
        self._client = client
        self._experiment = experiment
        self._workspace = workspace

    def add(self, label: str) -> None:
        """Add a Tag to the Experiment.

        Args:
            label: text displayed by the Tag.
        """
        tag = self._workspace.tags._get_or_create(label)
        self._client._backend.storage.experiment.tag_experiment(
            h2o_mlops_autogen.StorageTagExperimentRequest(
                experiment_id=self._experiment.uid, tag_id=tag.uid
            )
        )

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """List Tags for the Experiment.

        Examples::

            # filter on columns by using selectors
            experiment.tags.list(label="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            tag = experiment.tags.list()[0]

            # get a new Table using multiple indexes or slices
            table = experiment.tags.list()[2,4]
            table = experiment.tags.list()[2:4]
        """
        # refresh list of tags
        self._experiment._refresh()
        tags = self._experiment._raw_info.tag
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
        """Remove a Tag from the Experiment.

        Args:
            label: text displayed by the Tag.
        """
        tags = self._experiment.tags.list(label=label)
        if tags:
            self._client._backend.storage.experiment.untag_experiment(
                h2o_mlops_autogen.StorageUntagExperimentRequest(
                    experiment_id=self._experiment.uid, tag_id=tags[0].uid
                )
            )
