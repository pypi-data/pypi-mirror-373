from __future__ import annotations

import io
import json
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, NamedTuple, Optional, Union

import h2o_mlops_autogen
from h2o_mlops import (
    _core,
    _experiments,
    _models,
    _runtimes,
    _users,
    _utils,
    _workspaces,
    options,
    types,
)


class MLOpsBatchScoringJob:

    def __init__(
        self,
        client: _core.Client,
        workspace: _workspaces.Workspace,
        job: h2o_mlops_autogen.V1Job,
    ):
        self._client = client
        self._workspace = workspace
        self._job = job

        self._resource_name = job.name
        self._creator_uid = _utils._convert_resource_name_to_uid(
            resource_name=job.creator,
        )
        self._experiment: Optional[_experiments.MLOpsExperiment] = None
        self._last_seen_output_log_time = None
        self._scoring_runtime: Optional[_runtimes.MLOpsScoringRuntime] = None

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    name={self.name!r},\n"
            f"    state={self.state!r},\n"
            f"    creator_uid={self._creator_uid!r},\n"
            f"    created_time={self.created_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Name: {self.name}\n"
            f"State: {self.state}\n"
            f"Creator UID: {self._creator_uid}\n"
            f"Created Time: {self.created_time}"
        )

    @property
    def uid(self) -> str:
        """Batch scoring job unique ID."""
        return _utils._convert_resource_name_to_uid(
            resource_name=self._resource_name,
        )

    @property
    def name(self) -> str:
        """Batch scoring job display name."""
        return self._job.display_name

    @property
    def state(self) -> str:
        """Batch scoring job state."""
        return self._job.state

    @property
    def creator(self) -> _users.MLOpsUser:
        """Batch scoring job creator."""
        return self._client.users.get(self._creator_uid)

    @property
    def created_time(self) -> datetime:
        """Batch scoring job created time."""
        return self._job.create_time

    @property
    def source(self) -> options.BatchSourceOptions:
        """Batch scoring job source."""
        source = self._job.source
        return options.BatchSourceOptions(
            spec_uid=source.spec.split("/")[-1],
            config=json.loads(source.config),
            mime_type=types.MimeType(source.mime_type),
            location=source.location,
        )

    @property
    def sink(self) -> options.BatchSinkOptions:
        """Batch scoring job sink."""
        sink = self._job.sink
        return options.BatchSinkOptions(
            spec_uid=sink.spec.split("/")[-1],
            config=json.loads(sink.config),
            mime_type=types.MimeType(sink.mime_type),
            location=sink.location,
        )

    @property
    def scoring_runtime(self) -> _runtimes.MLOpsScoringRuntime:
        """Batch scoring job scoring runtime."""
        if self._scoring_runtime is None:
            c = self._job.instance_spec.deployment_composition
            self._scoring_runtime = self._client.runtimes.scoring.get(
                runtime_uid=c.runtime,
                artifact_type=c.artifact_type,
            )
        return self._scoring_runtime

    @property
    def experiment(self) -> _experiments.MLOpsExperiment:
        """Experiment in the batch scoring job."""
        if self._experiment is None:
            self._experiment = self._workspace.experiments.get(
                self._job.instance_spec.deployment_composition.experiment_id
            )
        return self._experiment

    @property
    def kubernetes_options(self) -> options.BatchKubernetesOptions:
        """Batch scoring job Kubernetes resource configuration."""
        resource_spec = self._job.instance_spec.resource_spec
        k8s_config_shortcut = self._job.instance_spec.kubernetes_config_shortcut
        return options.BatchKubernetesOptions(
            replicas=resource_spec.replicas,
            min_replicas=resource_spec.minimal_available_replicas,
            requests=resource_spec.resource_requirement.requests,
            limits=resource_spec.resource_requirement.limits,
            affinity=k8s_config_shortcut.kubernetes_affinity_shortcut,
            toleration=k8s_config_shortcut.kubernetes_toleration_shortcut,
        )

    @property
    def model_request_parameters(self) -> options.ModelRequestParameters:
        """Batch scoring job model request parameters."""
        mrp = self._job.model_request_parameters
        return options.ModelRequestParameters(
            id_field=mrp.id_field,
            contributions=types.ContributionType(mrp.request_contributions),
            prediction_intervals=mrp.request_prediction_intervals,
        )

    @property
    def start_time(self) -> datetime:
        """Batch scoring job start time."""
        return self._job.start_time

    @property
    def end_time(self) -> datetime:
        """Batch scoring job end time."""
        return self._job.end_time

    @property
    def completion_stats(self) -> CompletionStats:
        """Batch scoring job completion stats."""
        stats = self._job.completion_stats
        return CompletionStats(
            processed_row_count=int(stats.processed_rows),
            finished_pipeline_count=stats.finished_pipeline_count,
            failed_pipelines=stats.failed_pipelines,
            error_row_count=int(stats.error_rows_count),
        )

    @property
    def job_start_timeout(self) -> str:
        """
        Timeout for starting a batch scoring job.
        Specifies how long the job will wait before being scheduled and started in Kubernetes. # noqa: E501
        If the job fails to start within the configured timeout,
        it will be stopped and its state will be set to `TIMEOUT`.
        """
        return self._job.job_timeout

    def cancel(self, wait: bool = True) -> None:
        """Cancel batch scoring job."""
        srv = self._client._backend.batch.job
        srv.cancel_job(self._resource_name)
        if wait:
            self.wait()

    def delete(self) -> None:
        """Delete batch scoring job."""
        srv = self._client._backend.batch.job
        srv.delete_job(self._resource_name)

    def refresh(self) -> None:
        """Refresh batch scoring job's state"""
        srv = self._client._backend.batch.job
        response = srv.get_job(self._resource_name)
        self._job = response.job

    def logs(self, since_time: Optional[datetime] = None) -> None:
        """Start printing logs since select time."""
        if since_time is None:
            since_time = self._last_seen_output_log_time

        srv = self._client._backend.batch.job
        response = srv.get_job_output(
            self._resource_name, since_time=since_time, _preload_content=False
        )
        try:
            with response:
                for line in io.TextIOWrapper(response):

                    class DataWrapper:
                        def __init__(self, data: Any):
                            self.data = data

                    output = srv.api_client.deserialize(
                        DataWrapper(line), "StreamResultOfV1JobOutputResponse"
                    )
                    if output.error:
                        print(f"Error: {output.error}")
                    else:
                        result = output.result
                        if result.error:
                            print(f"Error: {result.error}")
                        else:
                            print(
                                f"[{result.pod}.{result.container}] " f"{result.line}"
                            )

                    if output.result is not None and output.result.log_time is not None:
                        self._last_seen_output_log_time = output.result.log_time
        finally:
            response.release_conn()

    def wait(self, logs: bool = True) -> None:
        """Wait for job to complete.
        If logs is set to True, the job's logs will be printed out."""
        while self._job.end_time is None:
            if logs:
                self.logs()
            else:
                sleep(5)
            self.refresh()


class MLOpsBatchScoringJobs:
    """
    Class for managing batch scoring jobs.
    """

    def __init__(self, client: _core.Client, workspace: _workspaces.Workspace):
        self._client = client
        self._workspace = workspace

    def create(
        self,
        *,
        source: options.BatchSourceOptions,
        sink: options.BatchSinkOptions,
        model: _models.MLOpsModel,
        model_version: Union[int, str] = "latest",
        scoring_runtime: _runtimes.MLOpsScoringRuntime,
        environment_variables: Optional[Dict[str, str]] = None,
        kubernetes_options: Optional[options.BatchKubernetesOptions] = None,
        mini_batch_size: Optional[int] = None,
        model_request_parameters: Optional[options.ModelRequestParameters] = None,
        name: Optional[str] = None,
        job_start_timeout: Optional[str] = None,
    ) -> MLOpsBatchScoringJob:
        """Create a new batch scoring job."""
        experiment = model.experiment(model_version=model_version)
        composition = h2o_mlops_autogen.V1DeploymentComposition(
            artifact_processor=scoring_runtime.artifact_processor.uid,
            experiment_id=experiment.uid,
            artifact_type=scoring_runtime.artifact_type.uid,
            runtime=scoring_runtime.runtime.uid,
        )

        api_resource_spec = None
        api_kubernetes_config_shortcut = None
        if kubernetes_options is not None:
            kubernetes_resource_requirement = h2o_mlops_autogen.V1ResourceRequirement(
                limits=kubernetes_options.limits,
                requests=kubernetes_options.requests,
            )

            api_resource_spec = h2o_mlops_autogen.V1ResourceSpec(
                resource_requirement=kubernetes_resource_requirement,
                replicas=kubernetes_options.replicas,
                minimal_available_replicas=kubernetes_options.min_replicas,
            )

            api_kubernetes_config_shortcut = (
                h2o_mlops_autogen.V1KubernetesConfigShortcut(  # noqa E501
                    kubernetes_affinity_shortcut=kubernetes_options.affinity,
                    kubernetes_toleration_shortcut=kubernetes_options.toleration,
                )
            )

        instance_spec = h2o_mlops_autogen.V1InstanceSpec(
            deployment_composition=composition,
            resource_spec=api_resource_spec,
            environment_variables=environment_variables,
            kubernetes_config_shortcut=api_kubernetes_config_shortcut,
        )

        batch_parameters = h2o_mlops_autogen.V1BatchParameters(
            mini_batch_size=mini_batch_size,
        )

        api_model_request_parameters = None
        if model_request_parameters is not None:
            api_model_request_parameters = h2o_mlops_autogen.V1ModelRequestParameters(
                id_field=model_request_parameters.id_field,
                request_contributions=(
                    model_request_parameters.contributions.value
                    if model_request_parameters.contributions
                    else None
                ),
                request_prediction_intervals=model_request_parameters.prediction_intervals,  # noqa: E501
            )

        api_source = h2o_mlops_autogen.V1Source(
            spec=f"sourceSpecs/{source.spec_uid}",
            config=json.dumps(source.config),
            mime_type=source.mime_type.value,
            location=source.location,
        )

        api_sink = h2o_mlops_autogen.V1Sink(
            spec=f"sinkSpecs/{sink.spec_uid}",
            config=json.dumps(sink.config),
            mime_type=sink.mime_type.value,
            location=sink.location,
        )

        job = h2o_mlops_autogen.V1Job(
            display_name=name,
            source=api_source,
            sink=api_sink,
            instance_spec=instance_spec,
            batch_parameters=batch_parameters,
            model_request_parameters=api_model_request_parameters,
            job_timeout=job_start_timeout,
        )

        srv = self._client._backend.batch.job
        result = srv.create_job(f"workspaces/{self._workspace.uid}", job)
        return MLOpsBatchScoringJob(self._client, self._workspace, result.job)

    def get(self, uid: str) -> MLOpsBatchScoringJob:
        """Get a batch scoring job by ID."""
        srv = self._client._backend.batch.job
        response = srv.get_job(f"workspaces/{self._workspace.uid}/jobs/{uid}")

        return MLOpsBatchScoringJob(self._client, self._workspace, response.job)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Batch Scoring Jobs available in the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.jobs.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            job = workspace.jobs.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.jobs.list()[2,4]
            table = workspace.jobs.list()[2:4]
        """
        srv = self._client._backend.batch.job
        jobs = []
        response = srv.list_jobs(parent=f"workspaces/{self._workspace.uid}")

        jobs += response.jobs
        while response.next_page_token:
            response = srv.list_jobs(
                parent=f"workspaces/{self._workspace.uid}",
                page_token=response.next_page_token,
            )
            jobs += response.jobs

        data_as_dicts = [
            {
                "name": job.display_name,
                "uid": job.name.split("/")[-1],
                "job": job,
            }
            for job in jobs
        ]

        return _utils.Table(
            data=data_as_dicts,
            keys=["name", "uid"],
            get_method=lambda x: MLOpsBatchScoringJob(
                self._client, self._workspace, x["job"]
            ),
            **selectors,
        )


class CompletionStats(NamedTuple):
    processed_row_count: int
    finished_pipeline_count: int
    failed_pipelines: List[str]
    error_row_count: int
