from __future__ import annotations

import io
import json
import mimetypes
import pathlib
from datetime import datetime
from os import PathLike
from typing import Any, Dict, Optional, Union

import h2o_mlops_autogen
from h2o_mlops import _core, _datasets, _deployments, _experiments, _utils, _workspaces
from h2o_mlops._utils import UNSET, UnsetType


class MLOpsArtifact:
    def __init__(self, client: _core.Client, raw_info: Any):
        self._client = client
        self._raw_info = raw_info

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    parent_entity_uid={self.parent_entity_uid!r},\n"
            f"    name={self.name!r},\n"
            f"    state={self.state!r},\n"
            f"    mime_type={self.mime_type!r},\n"
            f"    size={self.size},\n"
            f"    md5_digest={self.md5_digest!r},\n"
            f"    created_time={self.created_time!r},\n"
            f"    uploaded_time={self.uploaded_time!r},\n"
            f"    last_modified_time={self.last_modified_time!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Parent Entity UID: {self.parent_entity_uid}\n"
            f"Name: {self.name}\n"
            f"State: {self.state}\n"
            f"MIME Type: {self.mime_type}\n"
            f"Size: {self.size} bytes\n"
            f"MD5 Digest: {self.md5_digest}\n"
            f"Created Time: {self.created_time}\n"
            f"Uploaded Time: {self.uploaded_time}\n"
            f"Last Modified Time: {self.last_modified_time}"
        )

    @property
    def uid(self) -> str:
        """Artifact unique ID."""
        return self._raw_info.id

    @property
    def parent_entity_uid(self) -> str:
        """Associated parent entity unique ID."""
        return self._raw_info.entity_id

    @property
    def name(self) -> str:
        """Artifact display name."""
        return self._raw_info.type

    @property
    def state(self) -> str:
        """Artifact state."""
        return self._raw_info.state

    @property
    def mime_type(self) -> str:
        """Artifact MIME type."""
        return self._raw_info.mime_type

    @property
    def size(self) -> int:
        """Artifact size."""
        return self._raw_info.size

    @property
    def md5_digest(self) -> str:
        """Artifact MD5 Digest."""
        return self._raw_info.md5_digest

    @property
    def created_time(self) -> datetime:
        """Artifact created time."""
        return self._raw_info.created_time

    @property
    def uploaded_time(self) -> datetime:
        """Artifact uploaded time."""
        return self._raw_info.uploaded_time

    @property
    def last_modified_time(self) -> datetime:
        """Artifact last modified time."""
        return self._raw_info.last_modified_time

    @property
    def model_info(self) -> Optional[Dict[str, Any]]:
        """Model based details of Artifact."""
        try:
            return self._create_model_ingestion().to_dict()
        except Exception:
            return None

    def download(
        self,
        directory: Optional[str] = None,
        file_name: Optional[str] = None,
        overwrite: bool = False,
        buffer: Optional[io.BytesIO] = None,
    ) -> Union[str, io.BytesIO]:
        """Download an Artifact.

        Args:
            directory: path to the directory where the file should be saved.
                By default, the current working directory is used.
            file_name: set the name of the file the artifact is saved to.
                By default, the artifact name is used.
            overwrite: overwrite existing files.
            buffer: in-memory buffer to store the downloaded artifact
                instead of saving it to a file.
        """
        if buffer:
            self._client._backend.storage.artifact.download_artifact(
                artifact_id=self.uid,
                file=buffer,
            )
            return buffer

        if directory:
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            directory = "./"
        if not file_name:
            file_name = self.name.replace("/", "_")
        dst_path = str(pathlib.Path(directory, file_name))

        try:
            if overwrite:
                mode = "wb"
            else:
                mode = "xb"
            with open(dst_path, mode) as f:
                self._client._backend.storage.artifact.download_artifact(
                    artifact_id=self.uid, file=f
                )
        except FileExistsError:
            print(f"{dst_path} already exists. Use `overwrite` to force download.")
            raise

        return dst_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Artifact to a Python dictionary, if possible."""
        if self.mime_type not in ["application/json"]:
            raise RuntimeError(
                f"Artifact with mime_type '{self.mime_type}' "
                "cannot be converted to a dictionary."
            )
        return json.loads(self.to_string())

    def to_string(self) -> str:
        """Convert the Artifact to a Python string, if possible."""
        srv = self._client._backend.storage.artifact
        if self.mime_type not in ["application/json", "text/plain"]:
            raise RuntimeError(
                f"Artifact with mime_type '{self.mime_type}' "
                "cannot be converted to a string."
            )
        with io.BytesIO() as f:
            srv.download_artifact(artifact_id=self.uid, file=f)
            return f.getvalue().decode()

    def update(
        self,
        name: Optional[str] = None,
        parent_entity: Optional[
            Union[
                _datasets.MLOpsDataset,
                _deployments.MLOpsScoringDeployment,
                _experiments.MLOpsExperiment,
                _workspaces.Workspace,
                UnsetType,
            ]
        ] = UNSET,
    ) -> None:
        """Update Artifact.

        Args:
            name: display name for the Artifact.
            parent_entity: the parent entity.
        """
        update_mask = []
        artifact = h2o_mlops_autogen.StorageArtifact(
            id=self.uid,
            entity_id=self.parent_entity_uid,
        )
        if name is not None:
            artifact.type = name
            update_mask.append("type")
        if not isinstance(parent_entity, UnsetType):
            if parent_entity:
                artifact.entity_id = parent_entity.uid
                artifact.entity_type = _get_entity_type(parent_entity)
            else:
                artifact.entity_id = None
            update_mask.append("entityId")
        if update_mask:
            self._raw_info = self._client._backend.storage.artifact.update_artifact(
                h2o_mlops_autogen.StorageUpdateArtifactRequest(
                    artifact=artifact, update_mask=",".join(update_mask)
                )
            ).artifact

    def delete(self) -> None:
        """Delete Artifact."""
        self._client._backend.storage.artifact.delete_artifact(
            h2o_mlops_autogen.StorageDeleteArtifactRequest(self.uid)
        )

    def _create_model_ingestion(self) -> h2o_mlops_autogen.IngestModelIngestion:
        return self._client._backend.ingest.model.create_model_ingestion(
            h2o_mlops_autogen.IngestModelIngestion(
                artifact_id=self.uid,
            )
        ).ingestion

    def _refresh(self) -> None:
        self._raw_info = self._client._backend.storage.artifact.get_artifact(
            h2o_mlops_autogen.StorageGetArtifactRequest(id=self.uid)
        ).artifact


class MLOpsArtifacts:
    def __init__(
        self,
        client: _core.Client,
        parent_entity: Union[
            _datasets.MLOpsDataset,
            _deployments.MLOpsScoringDeployment,
            _experiments.MLOpsExperiment,
            _workspaces.Workspace,
        ],
    ):
        self._client = client
        self._parent_entity = parent_entity

    def add(
        self,
        data: Union[str, PathLike[str], io.BytesIO],
        mime_type: Optional[str] = None,
    ) -> MLOpsArtifact:
        """Add a new artifact to an Entity.

        Args:
            data: relative path to the artifact file or
                an in-memory buffer (`io.BytesIO`) containing the artifact data.
            mime_type: specify the data's media type in the MIME type format.
                If not specified, auto-detection of the media type will be attempted.
        """
        if isinstance(data, io.BytesIO):
            artifact_type = "in-memory buffer"
            mime_type = mime_type or mimetypes.types_map[".zip"]
        else:
            artifact_type = pathlib.Path(data).name
            try:
                mime_type = mime_type or mimetypes.types_map[pathlib.Path(data).suffix]
            except KeyError:
                raise RuntimeError("File MIME type not recognized.")
        entity_type = _get_entity_type(self._parent_entity)
        artifact = self._client._backend.storage.artifact.create_artifact(
            h2o_mlops_autogen.StorageCreateArtifactRequest(
                artifact=h2o_mlops_autogen.StorageArtifact(
                    entity_id=self._parent_entity.uid,
                    entity_type=entity_type,
                    mime_type=mime_type,
                    type=artifact_type,
                )
            )
        ).artifact
        if isinstance(data, io.BytesIO):
            self._client._backend.storage.artifact.upload_artifact(
                file=data, artifact_id=artifact.id
            )
        else:
            with open(data, mode="rb") as f:
                self._client._backend.storage.artifact.upload_artifact(
                    file=f, artifact_id=artifact.id
                )
        return self.get(uid=artifact.id)

    def get(self, uid: str) -> MLOpsArtifact:
        """Get the Artifact object corresponding to an H2O MLOps Artifact.

        Args:
            uid: H2O MLOps unique ID for the Artifact.
        """
        raw_info = self._client._backend.storage.artifact.get_artifact(
            h2o_mlops_autogen.StorageGetArtifactRequest(id=uid)
        ).artifact
        if raw_info.entity_id != self._parent_entity.uid:
            raise LookupError(
                f"Artifact not found for UID '{uid}' in the specified entity."
            )
        return MLOpsArtifact(client=self._client, raw_info=raw_info)

    def list(  # noqa A003
        self, exclude_deleted: bool = True, **selectors: Any
    ) -> _utils.Table:
        """List all Artifacts for the Entity.

        Examples::

            # filter on columns by using selectors
            entity.artifacts.list(name="demo")

            # use an index to get an H2O MLOps entity referenced by the table
            artifact = entity.artifacts.list()[0]

            # get a new Table using multiple indexes or slices
            table = entity.artifacts.list()[2,4]
            table = entity.artifacts.list()[2:4]
        """
        entity_type = _get_entity_type(self._parent_entity)
        artifacts = self._client._backend.storage.artifact.list_entity_artifacts(
            h2o_mlops_autogen.StorageListEntityArtifactsRequest(
                entity_id=self._parent_entity.uid,
                entity_type=entity_type,
            )
        ).artifact
        data_as_dicts = [
            {
                "name": a.type,
                "mime_type": a.mime_type[:25],
                "uid": a.id,
                "raw_info": a,
            }
            for a in artifacts
            if not (
                exclude_deleted
                and a.state == h2o_mlops_autogen.ArtifactArtifactState.DELETED
            )
        ]
        return _utils.Table(
            data=data_as_dicts,
            keys=["name", "mime_type", "uid"],
            get_method=lambda x: MLOpsArtifact(
                client=self._client, raw_info=x["raw_info"]
            ),
            **selectors,
        )


def _get_entity_type(
    parent_entity: Union[
        _datasets.MLOpsDataset,
        _deployments.MLOpsScoringDeployment,
        _experiments.MLOpsExperiment,
        _workspaces.Workspace,
    ],
) -> h2o_mlops_autogen.StorageEntityType:
    if isinstance(parent_entity, _datasets.MLOpsDataset):
        entity_type = h2o_mlops_autogen.StorageEntityType.DATASET
    elif isinstance(parent_entity, _deployments.MLOpsScoringDeployment):
        entity_type = h2o_mlops_autogen.StorageEntityType.DEPLOYMENT
    elif isinstance(parent_entity, _experiments.MLOpsExperiment):
        entity_type = h2o_mlops_autogen.StorageEntityType.EXPERIMENT
    elif isinstance(parent_entity, _workspaces.Workspace):
        entity_type = h2o_mlops_autogen.StorageEntityType.PROJECT
    else:
        entity_type = h2o_mlops_autogen.StorageEntityType.ENTITY_TYPE_UNSPECIFIED
    return entity_type
