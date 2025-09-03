from __future__ import annotations

from typing import Any, NamedTuple

from h2o_mlops import _core
from h2o_mlops import _utils


class MLOpsRuntimes:
    def __init__(self, client: _core.Client):
        self._client = client

    @property
    def scoring(self) -> MLOpsScoringRuntimes:
        return MLOpsScoringRuntimes(client=self._client)


class MLOpsScoringRuntime:
    def __init__(self, raw_info: Any):
        self._raw_info = raw_info

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    runtime={self.runtime.uid!r},\n"
            f"    artifact_type={self.artifact_type.uid!r},\n"
            f"    artifact_processor={self.artifact_processor.uid!r},\n"
            f"    model_type={self.model_type.uid!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"Runtime: {self.runtime.name}\n"
            f"Artifact Type: {self.artifact_type.name}\n"
            f"Artifact Processor: {self.artifact_processor.name}\n"
            f"Model Type: {self.model_type.name}"
        )

    @property
    def runtime(self) -> MLOpsRuntime:
        r = self._raw_info.runtime
        return MLOpsRuntime(
            uid=r.name,
            name=r.display_name,
            model_type=r.model_type,
            image=r.image,
        )

    @property
    def artifact_type(self) -> MLOpsArtifactType:
        at = self._raw_info.deployable_artifact_type
        return MLOpsArtifactType(
            uid=at.name,
            name=at.display_name,
            artifact_type=at.artifact_type,
        )

    @property
    def artifact_processor(self) -> MLOpsArtifactProcessor:
        ap = self._raw_info.artifact_processor
        return MLOpsArtifactProcessor(
            uid=ap.name,
            name=ap.display_name,
            artifact_type=ap.deployable_artifact_type,
            model_type=ap.model_type,
            image=ap.image,
        )

    @property
    def model_type(self) -> MLOpsModelType:
        mt = self._raw_info.model_type
        return MLOpsModelType(uid=mt.name, name=mt.display_name)


class MLOpsScoringRuntimes:
    def __init__(self, client: _core.Client):
        self._client = client

    def get(self, artifact_type: str, runtime_uid: str) -> MLOpsScoringRuntime:
        """Get the Scoring Runtime object corresponding
        to a Scoring Runtime in H2O MLOps.

        Args:
            artifact_type: H2O MLOps unique ID of the Artifact Type.
            runtime_uid: H2O MLOps unique ID of the Runtime.
        """
        scoring_runtime_table = self.list(
            artifact_type=artifact_type, runtime_uid=runtime_uid
        )
        if not scoring_runtime_table:
            raise LookupError(
                f"Scoring runtime for artifact_type='{artifact_type}' and "
                f"runtime_uid='{runtime_uid}' not found."
            )
        return scoring_runtime_table[0]

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Scoring Runtimes available in the H2O MLOps.

        Examples::

            # filter on columns by using selectors
            mlops.runtimes.scoring.list(runtime_uid="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            scoring_runtime = mlops.runtimes.scoring.list()[0]

            # get a new Table using multiple indexes or slices
            table = mlops.runtimes.scoring.list()[2,4]
            table = mlops.runtimes.scoring.list()[2:4]
        """
        srv = self._client._backend.deployer.composition
        compositions = srv.list_artifact_compositions().artifact_compositions
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
            get_method=lambda x: MLOpsScoringRuntime(x["raw_info"]),
            **selectors,
        )


class MLOpsRuntime(NamedTuple):
    uid: str
    name: str
    model_type: str
    image: str


class MLOpsArtifactType(NamedTuple):
    uid: str
    name: str
    artifact_type: str


class MLOpsArtifactProcessor(NamedTuple):
    uid: str
    name: str
    artifact_type: str
    model_type: str
    image: str


class MLOpsModelType(NamedTuple):
    uid: str
    name: str
