from __future__ import annotations

import json
import mimetypes
import os
import pathlib
import tempfile
import time
import zipfile
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Dict, List, NamedTuple, Optional, Union

import httpx

import h2o_mlops_autogen
from h2o_mlops import (
    _artifacts,
    _core,
    _endpoints,
    _users,
    _utils,
    _workspaces,
    options,
    types,
)
from h2o_mlops._utils import UNSET, UnsetType
from h2o_mlops.errors import MLOpsDeploymentError

DEFAULT_HTTPX_READ_TIMEOUT = 5


class MLOpsScoringDeployment:
    """Interact with a scoring Deployment on H2O MLOps."""

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
        self._creator_uid = _utils._convert_resource_name_to_uid(
            resource_name=raw_info.creator,
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    name={self.name!r},\n"
            f"    description={self.description!r},\n"
            f"    mode={self.mode!r},\n"
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
            f"Mode: {self.mode}\n"
            f"Creator UID: {self._creator_uid}\n"
            f"Created Time: {self.created_time}\n"
            f"Last Modified Time: {self.last_modified_time}"
        )

    @property
    def uid(self) -> str:
        """Deployment unique ID."""
        return _utils._convert_resource_name_to_uid(
            resource_name=self._resource_name,
        )

    @property
    def name(self) -> str:
        """Deployment display name."""
        return self._raw_info.display_name

    @property
    def description(self) -> str:
        """Deployment description."""
        return self._raw_info.description

    @property
    def mode(self) -> types.DeploymentModeType:
        """Deployment mode."""
        return types.DeploymentModeType._from_raw_info(
            raw_info=self._raw_info,
        )

    @property
    def creator(self) -> _users.MLOpsUser:
        """Deployment creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Deployment created time."""
        return self._raw_info.create_time

    @property
    def last_modified_time(self) -> datetime:
        """Deployment last modified time."""
        return self._raw_info.update_time

    @property
    def revision_uid(self) -> datetime:
        """Deployment revision unique ID."""
        return self._raw_info.etag

    @property
    def state(self) -> str:
        """Deployment state."""
        return self._client._backend.deployer.status.get_deployment_status(
            name_2=f"{self._resource_name}/status"
        ).deployment_status.state

    @property
    def is_healthy(self) -> bool:
        """Indicates whether the deployment is in a Healthy state."""
        return self.state == "HEALTHY"

    @property
    def composition_options(self) -> List[options.CompositionOptions]:
        """Deployment composition(s) configuration."""
        composition_options = []
        elements = self._get_deployment_elements()
        for element in elements:
            c = element.deployment_composition
            (
                model,
                model_version,
            ) = self._workspace.experiments.get(c.experiment_id).registered_model
            scoring_runtime = self._client.runtimes.scoring.get(
                runtime_uid=c.runtime,
                artifact_type=c.deployable_artifact_type,
            )
            traffic_weight = getattr(element, "weight", None)
            composition_options.append(
                options.CompositionOptions(
                    model=model,
                    scoring_runtime=scoring_runtime,
                    model_version=model_version,
                    traffic_weight=traffic_weight,
                    primary=None,
                )
            )
        if self.mode == types.DeploymentModeType.CHAMPION_CHALLENGER:
            composition_options[0].primary = True
            composition_options[1].primary = False
        return composition_options

    @property
    def security_options(self) -> options.SecurityOptions:
        """Deployment security configuration."""
        return options.SecurityOptions._from_raw_info(
            raw_info=self._raw_info.security,
        )

    @property
    def kubernetes_options(self) -> options.KubernetesOptions:
        """Deployment Kubernetes resource configuration."""
        elements = self._get_deployment_elements()
        return options.KubernetesOptions._from_raw_info(
            raw_info=(
                elements[0].kubernetes_resource_spec,
                elements[0].kubernetes_config_shortcut,
            ),
        )

    @property
    def vpa_options(self) -> Optional[List[options.VPAOptions]]:
        """Deployment Vertical Pod Autoscaler configurations."""
        if raw_info := self._get_deployment_elements()[0].vpa_spec:
            return options.VPAOptions._from_raw_info(raw_info)
        return None

    @property
    def pdb_options(self) -> Optional[options.PDBOptions]:
        """Deployment Pod Disruption Budget configuration."""
        if raw_info := self._get_deployment_elements()[0].pod_disruption_budget:
            return options.PDBOptions._from_raw_info(raw_info)
        return None

    @property
    def environment_variables(self) -> Dict[str, str]:
        """Environment variables added to the scoring runtime."""
        return self._get_deployment_elements()[0].runtime_environment_variables

    @property
    def cors_origins(self) -> Optional[List[str]]:
        """Deployment allowed CORS origins."""
        if cors := self._raw_info.cors:
            return cors.origins
        return None

    @property
    def monitoring_options(self) -> Optional[options.MonitoringOptions]:
        """Deployment monitoring configuration."""
        if raw_info := self._raw_info.monitoring_options:
            return options.MonitoringOptions._from_raw_info(raw_info)
        return None

    @property
    def scorer(self) -> Optional[MLOpsDeploymentScorer]:
        """Deployment Scorer."""
        if metadata := self._client._backend.deployer.metadata.get_deployment_metadata(
            name=f"{self._resource_name}/metadata"
        ).deployment_metadata:
            if raw_info := metadata.scoring_interface:
                return MLOpsDeploymentScorer(
                    self._client,
                    self._workspace,
                    self.uid,
                    self.security_options,
                    raw_info,
                )
        return None

    @property
    def experiments(self) -> _utils.Table:
        """Experiments in the Deployment."""
        experiments = [
            self._workspace.experiments.get(
                element.deployment_composition.experiment_id
            )
            for element in self._get_deployment_elements()
        ]
        data = [
            {"name": e.name, "uid": e.uid, "mlops_experiment": e} for e in experiments
        ]
        return _utils.Table(
            data=data,
            keys=["name", "uid"],
            get_method=lambda x: x["mlops_experiment"],
        )

    @property
    def endpoints(self) -> _utils.Table:
        """Endpoints associated with the Deployment."""
        opts = options.ListOptions(
            filter_expression=options.FilterExpression(
                filters=[
                    options.FilterOptions(
                        field="target_deployment",
                        value=self._resource_name,
                    ),
                ],
            ),
        )
        return self._workspace.endpoints.list(opts=opts)

    @property
    def artifacts(self) -> _artifacts.MLOpsArtifacts:
        """Interact with artifacts for the Deployment."""
        return _artifacts.MLOpsArtifacts(self._client, self)

    def wait_for_healthy(self, timeout: int = 60, interval: int = 5) -> None:
        """
        Waits for the deployment to become healthy.

        Args:
            timeout: Maximum time to wait in seconds. Default is 60.
            interval: Time to wait between checks in seconds. Default is 5.
        """
        start_time = time.monotonic()
        while not self.is_healthy:
            self.raise_for_failure()
            if time.monotonic() - start_time > timeout:
                raise TimeoutError(
                    "Deployment did not become healthy within the timeout period."
                )
            time.sleep(interval)

    def raise_for_failure(self) -> None:
        """Raise an error if Deployment status is Failed."""
        if self.state == "FAILED":
            raise MLOpsDeploymentError("Deployment failed.")

    def logs(self, since_time: Optional[datetime] = None) -> Dict[str, List[str]]:
        """Retrieve the log entries for the deployment.

        Args:
            since_time: Timestamp from which to retrieve logs.
                Set to None to fetch all available logs.
        """
        artifact = self.artifacts.get(
            uid=self._client._backend.deployer.log.generate_logs(
                name=self._resource_name,
                body=h2o_mlops_autogen.InlineObject1(
                    since_time=since_time,
                ),
            ).artifact_id
        )

        logs: Dict[str, List[str]] = {}
        with tempfile.TemporaryDirectory() as workspace:
            workspace_path = pathlib.Path(workspace)
            file_name = f"deployment.{self.uid}.logs.zip"
            zip_path = workspace_path / file_name
            artifact.download(
                directory=str(workspace_path), file_name=file_name, overwrite=True
            )
            with zipfile.ZipFile(zip_path, "r") as archive:
                for entry in archive.infolist():
                    if entry.filename.endswith(".log"):
                        with archive.open(entry.filename) as f:
                            logs[entry.filename.strip(".log")] = (
                                f.read().decode("utf-8").splitlines()
                            )
        return logs

    def configure_endpoint(
        self,
        path: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        force: bool = False,
    ) -> _endpoints.MLOpsEndpoint:
        """Configure a static path for the MLOps Deployment REST endpoint.

        Args:
            path: Path to use for the target deployment URLs.
            name: Display name for the MLOps Endpoint.
                Only used if a new endpoint is created.
            description: Description for the MLOps Endpoint.
                Only used if a new endpoint is created.
            force: Attempt to reassign the path
                if it is already in use by another deployment.
        """
        try:
            endpoint = self._workspace.endpoints.get(path=path)
        except LookupError:
            endpoint = None
        if not endpoint:
            return self._workspace.endpoints.create(
                name=name or path,
                path=path,
                description=description,
                target_deployment=self,
            )
        if endpoint.target_deployment and not force:
            raise RuntimeError(
                f"Endpoint path '{path}' is already in use. "
                f"Please set `force=True` to reassign it."
            )
        endpoint.update(target_deployment=self)
        return endpoint

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[Union[str, UnsetType]] = UNSET,
        security_options: Optional[options.SecurityOptions] = None,
        kubernetes_options: Optional[options.KubernetesOptions] = None,
        vpa_options: Optional[Union[List[options.VPAOptions], UnsetType]] = UNSET,
        pdb_options: Optional[Union[options.PDBOptions, UnsetType]] = UNSET,
        environment_variables: Optional[Union[Dict[str, str], UnsetType]] = UNSET,
        cors_origins: Optional[Union[List[str], UnsetType]] = UNSET,
        monitoring_options: Optional[
            Union[options.MonitoringOptions, UnsetType]
        ] = UNSET,
    ) -> None:
        """Update Deployment.

        Args:
            name: display name for the Deployment
            description: description for the Deployment
            security_options: Security Options object
            kubernetes_options: Kubernetes Options object
            vpa_options: VPA Options objects
            pdb_options: PDB Options object
            environment_variables: Environment variables to add to the scoring runtime
            cors_origins: CORS origins to be allowed
            monitoring_options: Monitoring Options object
        """
        update_mask = []
        _raw_info = self._workspace.deployments.get(self.uid)._raw_info
        deployment = h2o_mlops_autogen.TheDeploymentToUpdate(
            etag=_raw_info.etag,
            **{
                attr: getattr(_raw_info, attr, None)
                for attr in ["single", "split", "shadow"]
            },
        )
        deployment_elements = self._get_deployment_elements(raw_info=deployment)
        if name is not None:
            deployment.display_name = name
            update_mask.append("display_name")
        if description is not UNSET:
            deployment.description = description
            update_mask.append("description")
        if security_options is not None:
            deployment.security = security_options._to_raw_info()
            update_mask.append("deployment.security")
        if kubernetes_options is not None:
            (
                kubernetes_resource_spec,
                kubernetes_config_shortcut,
            ) = kubernetes_options._to_raw_info()
            for element in deployment_elements:
                element.kubernetes_resource_spec = kubernetes_resource_spec
                element.kubernetes_config_shortcut = kubernetes_config_shortcut
            update_mask.append("deployment.kubernetes_resource_spec")
            update_mask.append("deployment.kubernetes_config_shortcut")
        if not isinstance(vpa_options, UnsetType):
            if vpa_options:
                vpa_spec = h2o_mlops_autogen.V2VpaResourceSpec(
                    **{
                        resource: vo._to_raw_info()
                        for vo in vpa_options
                        if (
                            resource := {
                                types.KubernetesResourceType.CPU: "cpu",
                                types.KubernetesResourceType.MEMORY: "memory",
                            }.get(vo.resource_type)
                        )
                    }
                )
            else:
                vpa_spec = None
            for element in deployment_elements:
                element.vpa_spec = vpa_spec
            update_mask.append("deployment.vpa_spec")
        if not isinstance(pdb_options, UnsetType):
            pod_disruption_budget = pdb_options._to_raw_info() if pdb_options else None
            for element in deployment_elements:
                element.pod_disruption_budget = pod_disruption_budget
            update_mask.append("deployment.pod_disruption_budget")
        if environment_variables is not UNSET:
            for element in deployment_elements:
                element.runtime_environment_variables = environment_variables
            update_mask.append("deployment.environment_variables")
        if cors_origins is not UNSET:
            deployment.cors = (
                h2o_mlops_autogen.V2Cors(origins=cors_origins) if cors_origins else None
            )
            update_mask.append("deployment.cors")
        if not isinstance(monitoring_options, UnsetType):
            deployment.monitoring_options = (
                monitoring_options._to_raw_info() if monitoring_options else None
            )
            update_mask.append("deployment.monitoring")
        if update_mask:
            self._raw_info = (
                self._client._backend.deployer.deployment.update_deployment(
                    deployment_name=self._resource_name,
                    deployment=deployment,
                    update_mask=",".join(update_mask),
                ).deployment
            )

    def delete(self) -> None:
        """Delete Deployment."""
        self._client._backend.deployer.deployment.delete_deployment(
            name=self._resource_name
        )

    def list_baselines(self, **selectors: Any) -> Dict[str, _utils.Table]:  # noqa A003
        """Retrieve Map of Tables with Baselines available for deployment.

        Examples::

            # filter on columns by using selectors
            workspace.deployment.list_baselines(column="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            job = workspace.deployment.list_baselines()["experiment_id"][0]

            # get a new Table using multiple indexes or slices
            table = workspace.deployment.list_baselines()["experiment_id"][2,4]
        """
        result: Dict[str, _utils.Table] = {}

        srv = self._client._backend.monitoring.aggregate
        elements = self._get_deployment_elements()
        for element in elements:
            experiment_id = element.deployment_composition.experiment_id
            parent = f"{self._resource_name}/experiments/{experiment_id}"
            baselines = []
            response = srv.list_baseline_aggregates(parent=parent)
            baselines += response.baseline_aggregates
            while response.next_page_token:
                response = srv.list_baseline_aggregates(
                    parent=parent,
                    page_token=response.next_page_token,
                )
                baselines += response.baseline_aggregates

            data_as_dicts = [
                {
                    "column": baseline.column,
                    "uid": baseline.id,
                    "baseline": baseline,
                }
                for baseline in baselines
            ]

            result[experiment_id] = _utils.Table(
                data=data_as_dicts,
                keys=["column", "uid"],
                get_method=lambda x: x,
                **selectors,
            )

        return result

    def list_aggregates(self, **selectors: Any) -> Dict[str, _utils.Table]:  # noqa A003
        """Retrieve Map of Tables with Monitored Aggregares available for deployment.

        Examples::

            # filter on columns by using selectors
            workspace.deployment.list_aggregates(column="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            job = workspace.deployment.list_aggregates()["experiment_id"][0]

            # get a new Table using multiple indexes or slices
            table = workspace.deployment.list_aggregates()["experiment_id"][2,4]
        """
        result: Dict[str, _utils.Table] = {}

        srv = self._client._backend.monitoring.aggregate
        elements = self._get_deployment_elements()
        for element in elements:
            experiment_id = element.deployment_composition.experiment_id
            parent = f"{self._resource_name}/experiments/{experiment_id}"
            aggregates = []
            response = srv.list_aggregates(parent=parent)
            aggregates += response.aggregates
            while response.next_page_token:
                response = srv.list_aggregates(
                    parent=parent,
                    page_token=response.next_page_token,
                )
                aggregates += response.aggregates

            data_as_dicts = [
                {
                    "column": agg.column,
                    "uid": agg.id,
                    "timestamp": agg.start_time,
                    "aggregate": agg,
                }
                for agg in aggregates
            ]

            result[experiment_id] = _utils.Table(
                data=data_as_dicts,
                keys=["column", "uid", "timestamp"],
                get_method=lambda x: x,
                **selectors,
            )

        return result

    def redeploy_if_failed(self) -> None:
        """
        Retry a failed deployment.

        This method checks the current status of a deployment and,
        if it is in a failed state, attempts to retry the deployment.
        """
        self._client._backend.deployer.deployment.retry_deployment(
            name=self._resource_name, body={}
        )

    def _get_deployment_elements(
        self,
        raw_info: Optional[
            Union[
                h2o_mlops_autogen.TheDeploymentToUpdate,
                h2o_mlops_autogen.V2Deployment,
            ]
        ] = None,
    ) -> List[
        Union[
            h2o_mlops_autogen.V2SingleDeployment,
            h2o_mlops_autogen.V2SplitDeployment,
            h2o_mlops_autogen.V2ShadowDeployment,
        ]
    ]:
        raw_info = raw_info or self._raw_info
        if raw_info.single:
            return [raw_info.single]
        if raw_info.split:
            return raw_info.split.split_elements
        if raw_info.shadow:
            return [
                raw_info.shadow.primary_element,
                raw_info.shadow.secondary_element,
            ]
        raise RuntimeError(
            "'raw_info' must include one of "
            "single, split, or shadow deployment types."
        )


class MLOpsScoringDeployments:
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
        composition_options: Union[
            options.CompositionOptions,
            List[options.CompositionOptions],
        ],
        security_options: options.SecurityOptions,
        mode: types.DeploymentModeType = types.DeploymentModeType.SINGLE_MODEL,
        description: Optional[str] = None,
        kubernetes_options: Optional[options.KubernetesOptions] = None,
        vpa_options: Optional[List[options.VPAOptions]] = None,
        pdb_options: Optional[options.PDBOptions] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        cors_origins: Optional[List[str]] = None,
        monitoring_options: Optional[options.MonitoringOptions] = None,
    ) -> MLOpsScoringDeployment:
        """Create a scoring Deployment in H2O MLOps.

        Args:
            name: Deployment display name
            composition_options: Composition Options objects
            security_options: Security Options object
            mode: Deployment mode
            description: Deployment description
            kubernetes_options: Kubernetes Options object
            vpa_options: VPA Options objects
            pdb_options: PDB Options object
            environment_variables: Environment variables to add to the scoring runtime
            cors_origins: CORS origins to be allowed
            monitoring_options: Monitoring Options object
        """
        single = split = shadow = None
        if mode == types.DeploymentModeType.SINGLE_MODEL:
            if isinstance(composition_options, list):
                if len(composition_options) != 1:
                    raise ValueError(
                        "Expected exactly one CompositionOptions object "
                        "for single-model mode."
                    )
                composition_options = composition_options[0]
            single = h2o_mlops_autogen.V2SingleDeployment(
                deployment_composition=composition_options._to_raw_info(),
            )
        elif isinstance(composition_options, list) and len(composition_options) == 2:
            if mode == types.DeploymentModeType.AB_TEST:
                split = h2o_mlops_autogen.V2SplitDeployment(
                    split_elements=[
                        h2o_mlops_autogen.V2SplitElement(
                            deployment_composition=co._to_raw_info(),
                            weight=co.traffic_weight,
                        )
                        for co in composition_options
                    ],
                )
            elif mode == types.DeploymentModeType.CHAMPION_CHALLENGER:
                primary_element, secondary_element = None, None
                for co in composition_options:
                    if co.primary:
                        primary_element = h2o_mlops_autogen.V2ShadowElement(
                            deployment_composition=co._to_raw_info(),
                        )
                    else:
                        secondary_element = h2o_mlops_autogen.V2ShadowElement(
                            deployment_composition=co._to_raw_info(),
                        )
                shadow = h2o_mlops_autogen.V2ShadowDeployment(
                    primary_element=primary_element,
                    secondary_element=secondary_element,
                )
            else:
                raise ValueError(f"Unsupported deployment mode: {mode}")
        else:
            raise ValueError(
                "Expected a list of two CompositionOptions objects "
                "for multi-model modes."
            )
        return self._create(
            name=name,
            security_options=security_options,
            description=description,
            kubernetes_options=kubernetes_options,
            vpa_options=vpa_options,
            pdb_options=pdb_options,
            environment_variables=environment_variables,
            cors_origins=cors_origins,
            monitoring_options=monitoring_options,
            single=single,
            split=split,
            shadow=shadow,
        )

    def get(self, uid: str) -> MLOpsScoringDeployment:
        """Get the Deployment object corresponding to a Deployment in H2O MLOps.

        Args:
            uid: H2O MLOps unique ID for the Deployment.
        """
        raw_info = self._client._backend.deployer.deployment.get_deployment(
            name_1=f"{self._parent_resource_name}/deployments/{uid}"
        ).deployment
        return MLOpsScoringDeployment(self._client, self._workspace, raw_info)

    def list(  # noqa A003
        self, opts: Optional[options.ListOptions] = None, **selectors: Any
    ) -> _utils.Table:
        """Retrieve Table of Deployments available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.deployments.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            deployment = workspace.deployments.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.deployments.list()[2,4]
            table = workspace.deployments.list()[2:4]
        """
        return self._list(opts=opts, **selectors)

    def statuses(
        self, opts: Optional[options.ListOptions] = None, **selectors: Any
    ) -> _utils.Table:
        """Retrieve Table of Deployments' Statuses available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.deployments.statuses(uid="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            status = workspace.deployments.statuses()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.deployments.statuses()[2,4]
            table = workspace.deployments.statuses()[2:4]
        """
        data = []
        ds_resource_names = [f"{d._resource_name}/status" for d in self.list(opts)]
        if ds_resource_names:
            statuses = (
                self._client._backend.deployer.status.batch_get_deployment_statuses(
                    parent=self._parent_resource_name,
                    names=ds_resource_names,
                ).deployment_statuses
            )
            data = [
                {
                    "uid": _utils._convert_resource_name_to_uid(
                        s.name.removesuffix("/status")
                    ),
                    "state": s.state,
                    "timestamp": s.update_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                    "message": s.message,
                }
                for s in statuses
            ]

        class MLOpsDeploymentStatus(NamedTuple):
            uid: str
            state: str
            timestamp: str
            message: str

        return _utils.Table(
            data=data,
            keys=["uid", "state"],
            get_method=lambda x: MLOpsDeploymentStatus(**x),
            **selectors,
        )

    def scorers(
        self, opts: Optional[options.ListOptions] = None, **selectors: Any
    ) -> _utils.Table:
        """Retrieve Table of Deployments' Scorers available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.deployments.scorers(deployment_uid="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            scorer = workspace.deployments.scorers()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.deployments.scorers()[2,4]
            table = workspace.deployments.scorers()[2:4]
        """
        data = []
        security_options_dict = {d.uid: d.security_options for d in self.list(opts)}
        dm_resource_names = [
            f"{self._parent_resource_name}/deployments/{uid}/metadata"
            for uid in security_options_dict.keys()
        ]
        if dm_resource_names:
            deployments_metadata = (
                self._client._backend.deployer.metadata.batch_get_deployments_metadata(
                    parent=self._parent_resource_name,
                    names=dm_resource_names,
                ).deployments_metadata
            )
            for dm in deployments_metadata:
                deployment_uid = _utils._convert_resource_name_to_uid(
                    dm.name.removesuffix("/metadata")
                )
                data += [
                    {
                        "uid": deployment_uid,
                        "scoring_endpoint": (
                            dm.scoring_interface.score.uri
                            if dm.scoring_interface
                            else None
                        ),
                        "security_options": security_options_dict[deployment_uid],
                        "raw_info": dm.scoring_interface,
                    }
                ]
        return _utils.Table(
            data=data,
            keys=["uid", "scoring_endpoint"],
            get_method=lambda x: (
                MLOpsDeploymentScorer(
                    self._client,
                    self._workspace,
                    x["uid"],
                    x["security_options"],
                    x["raw_info"],
                )
                if x["raw_info"]
                else None
            ),
            **selectors,
        )

    def _create(
        self,
        *,
        name: str,
        security_options: options.SecurityOptions,
        description: Optional[str] = None,
        kubernetes_options: Optional[options.KubernetesOptions] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        vpa_options: Optional[List[options.VPAOptions]] = None,
        pdb_options: Optional[options.PDBOptions] = None,
        cors_origins: Optional[List[str]] = None,
        monitoring_options: Optional[options.MonitoringOptions] = None,
        single: Optional[h2o_mlops_autogen.V2SingleDeployment] = None,
        shadow: Optional[h2o_mlops_autogen.V2ShadowDeployment] = None,
        split: Optional[h2o_mlops_autogen.V2SplitDeployment] = None,
    ) -> MLOpsScoringDeployment:
        kubernetes_options = kubernetes_options or options.KubernetesOptions()
        self._raise_for_unallowed_affinity(
            affinity=kubernetes_options.affinity,
        )
        self._raise_for_unallowed_toleration(
            toleration=kubernetes_options.toleration,
        )

        (
            kubernetes_resource_spec,
            kubernetes_config_shortcut,
        ) = kubernetes_options._to_raw_info()
        if vpa_options:
            vpa_spec = h2o_mlops_autogen.V2VpaResourceSpec(
                **{
                    resource: vo._to_raw_info()
                    for vo in vpa_options
                    if (
                        resource := {
                            types.KubernetesResourceType.CPU: "cpu",
                            types.KubernetesResourceType.MEMORY: "memory",
                        }.get(vo.resource_type)
                    )
                }
            )
        else:
            vpa_spec = None
        pod_disruption_budget = pdb_options._to_raw_info() if pdb_options else None

        def _add_common_configs(element: Any) -> None:
            element.kubernetes_resource_spec = kubernetes_resource_spec
            element.kubernetes_config_shortcut = kubernetes_config_shortcut
            element.runtime_environment_variables = environment_variables
            element.vpa_spec = vpa_spec
            element.pod_disruption_budget = pod_disruption_budget

        if single:
            _add_common_configs(single)
        if shadow:
            _add_common_configs(shadow.primary_element)
            _add_common_configs(shadow.secondary_element)
        if split:
            for split_element in split.split_elements:
                _add_common_configs(split_element)

        raw_info = self._client._backend.deployer.deployment.create_deployment(
            parent=self._parent_resource_name,
            deployment=h2o_mlops_autogen.V2Deployment(
                display_name=name,
                description=description,
                single=single,
                shadow=shadow,
                split=split,
                security=security_options._to_raw_info(),
                cors=(
                    h2o_mlops_autogen.V2Cors(origins=cors_origins)
                    if cors_origins
                    else None
                ),
                monitoring_options=(
                    monitoring_options._to_raw_info() if monitoring_options else None
                ),
            ),
        ).deployment
        return MLOpsScoringDeployment(self._client, self._workspace, raw_info)

    def _list(
        self,
        page_token: Optional[str] = None,
        opts: Optional[options.ListOptions] = None,
        **selectors: Any,
    ) -> _utils.Table:
        field_name_mapping = {
            "name": "display_name",
            "description": "description",
            "created_time": "create_time",
            "last_modified_time": "update_time",
            "creator": "creator",
        }
        args = (
            opts._to_raw_info_args(
                field_name_mapping=field_name_mapping,
            )
            if opts
            else {}
        )
        response = self._client._backend.deployer.deployment.list_deployments(
            parent=self._parent_resource_name,
            page_token=page_token,
            **args,
        )
        data = [
            {
                "name": d.display_name,
                "mode": types.DeploymentModeType._from_raw_info(raw_info=d),
                "uid": d.name.split("/")[-1],
                "raw_info": d,
            }
            for d in response.deployments
        ]
        return _utils.Table(
            data=data,
            keys=["name", "mode", "uid"],
            get_method=lambda x: MLOpsScoringDeployment(
                self._client, self._workspace, x["raw_info"]
            ),
            list_method=self._list,
            list_args={"opts": opts, **selectors},
            next_page_token=response.next_page_token,
            **selectors,
        )

    def _raise_for_unallowed_affinity(self, affinity: str) -> None:
        if affinity is not None and affinity not in [
            a.uid for a in self._client.configs.allowed_k8s_affinities
        ]:
            raise ValueError(f"Affinity '{affinity}' not allowed.")

    def _raise_for_unallowed_toleration(self, toleration: str) -> None:
        if toleration is not None and toleration not in [
            t.uid for t in self._client.configs.allowed_k8s_tolerations
        ]:
            raise ValueError(f"Toleration '{toleration}' not allowed.")


class MLOpsDeploymentScorer:
    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        deployment_uid: str,
        security_options: options.SecurityOptions,
        raw_info: Any,
    ):
        self._client = client
        self._workspace = workspace
        self._deployment_uid = deployment_uid
        self._security_options = security_options
        self._raw_info = raw_info

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    api_base_url={self.api_base_url!r},\n"
            f"    capabilities_endpoint={self.capabilities_endpoint!r},\n"
            f"    schema_endpoint={self.schema_endpoint!r},\n"
            f"    sample_request_endpoint={self.sample_request_endpoint!r},\n"
            f"    scoring_endpoint={self.scoring_endpoint!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"API Base URL: {self.api_base_url}\n"
            f"Capabilities Endpoint: {self.capabilities_endpoint}\n"
            f"Schema Endpoint: {self.schema_endpoint}\n"
            f"Sample Request Endpoint: {self.sample_request_endpoint}\n"
            f"Scoring Endpoint: {self.scoring_endpoint}"
        )

    @property
    def api_base_url(self) -> str:
        """Scorer API base URL."""
        return "/".join(self.scoring_endpoint.split("/")[:4])

    @property
    def readyz_endpoint(self) -> str:
        """Scorer readiness check endpoint."""
        return f"{self.api_base_url}/readyz"

    @property
    def capabilities_endpoint(self) -> str:
        """Scorer capabilities endpoint."""
        return self._raw_info.capabilities.uri

    @property
    def schema_endpoint(self) -> str:
        """Scorer schema endpoint."""
        return f"{self.api_base_url}/model/schema"

    @property
    def sample_request_endpoint(self) -> str:
        """Scorer sample request endpoint."""
        return self._raw_info.sample_request.uri

    @property
    def scoring_endpoint(self) -> str:
        """Scorer scoring endpoint."""
        return self._raw_info.score.uri

    @property
    def media_scoring_endpoint(self) -> str:
        """Scorer media scoring endpoint."""
        return f"{self.api_base_url}/model/media-score"

    @property
    def contributions_endpoint(self) -> str:
        """Scorer contributions endpoint."""
        return f"{self.api_base_url}/model/contribution"

    def state(
        self,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> str:
        """Check state of the scorer.

        Args:
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.readyz_endpoint,
            auth_value=auth_value,
            timeout=timeout,
            as_dict=False,
        )

    def is_ready(
        self,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> bool:
        """Check if the scorer is ready.

        Args:
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        try:
            return (
                self.state(
                    auth_value=auth_value,
                    timeout=timeout,
                ).lower()
                == "ready"
            )
        except Exception:
            return False

    def capabilities(
        self,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> List[str]:
        """Get capabilities supported by the Deployment, in JSON format.

        Args:
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.capabilities_endpoint, auth_value=auth_value, timeout=timeout
        )

    def schema(
        self,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Get schema for the Deployment, in JSON format.

        Args:
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.schema_endpoint, auth_value=auth_value, timeout=timeout
        )

    def sample_request(
        self,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> Dict[str, List[Any]]:
        """Get sample request for the Deployment, in JSON format.

        Args:
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.sample_request_endpoint,
            auth_value=auth_value,
            timeout=timeout,
        )

    def score(
        self,
        payload: Dict[str, Any],
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> Dict[str, Any]:
        """Send a scoring request to the Deployment.

        Args:
            payload: Input data for scoring.
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.scoring_endpoint,
            payload=payload,
            auth_value=auth_value,
            timeout=timeout,
        )

    def score_media(
        self,
        payload: Dict[str, Any],
        file_paths: List[str],
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> Dict[str, Any]:
        """Send a media scoring request to the Deployment.

        Args:
            payload: Input data for scoring.
            file_paths: Input media path for scoring.
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        if "scoreMediaRequest" not in payload:
            payload = {"scoreMediaRequest": json.dumps(payload)}
        else:
            payload["scoreMediaRequest"] = json.dumps(payload["scoreMediaRequest"])

        files = []
        opened_files = []
        for path in file_paths:
            filename = os.path.basename(path)
            mime_type, _ = mimetypes.guess_type(filename)
            mime_type = mime_type or "application/octet-stream"

            f = open(path, "rb")
            opened_files.append(f)

            files.append(
                (
                    "files",
                    (filename, f, mime_type),
                ),
            )

        response = self._call_endpoint(
            endpoint=self.media_scoring_endpoint,
            payload=payload,
            files=files,
            auth_value=auth_value,
            timeout=timeout,
        )

        for f in opened_files:
            f.close()

        return response

    def score_contributions(
        self,
        payload: Dict[str, Any],
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
    ) -> Dict[str, Any]:
        """Send a compute contribution scoring request to the Deployment.

        Args:
            payload: Input data to compute contribution score.
            auth_value: Deployment authorization value
                (passphrase or access token) (if required)
            timeout: Timeout in seconds for the HTTP request
                (optional, default is DEFAULT_HTTPX_READ_TIMEOUT)
        """
        return self._call_endpoint(
            endpoint=self.contributions_endpoint,
            payload=payload,
            auth_value=auth_value,
            timeout=timeout,
        )

    def _call_endpoint(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
        auth_value: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_HTTPX_READ_TIMEOUT,
        as_dict: bool = True,
    ) -> Any:
        headers = {}
        if auth_value is None:
            if self._security_options.security_type == types.SecurityType.OIDC_AUTH:
                auth_value = str(self._client._token_provider.token())

        if auth_value:
            headers["Authorization"] = f"Bearer {auth_value}"
        if files:
            response = httpx.post(
                endpoint,
                data=payload,
                files=files,
                headers=headers,
                timeout=timeout,
                verify=self._client._ssl_context,
            )
        elif payload:
            headers["Content-Type"] = "application/json"
            response = httpx.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=timeout,
                verify=self._client._ssl_context,
            )
        else:
            response = httpx.get(
                endpoint,
                headers=headers,
                timeout=timeout,
                verify=self._client._ssl_context,
            )

        try:
            r = response.json() if as_dict else response.text
        except JSONDecodeError:
            r = response.text

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            error_msg = r["detail"] if isinstance(r, dict) and "detail" in r else r
            message = f"{str(e)}\n\n`Caused` by\n\n{error_msg}"
            raise httpx.HTTPStatusError(
                message=message, request=e.request, response=e.response
            )

        return r
