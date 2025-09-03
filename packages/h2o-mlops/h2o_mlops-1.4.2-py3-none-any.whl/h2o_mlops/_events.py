from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

import h2o_mlops_autogen
from h2o_mlops import _core, _users, _utils


class MLOpsWorkspaceEvent:
    def __init__(self, client: _core.Client, raw_info: Any):
        self._client = client
        self._raw_info = raw_info

        self._actor_uid = raw_info.actor_id

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    operation={self.operation!r},\n"
            f"    actor_uid={self._actor_uid!r},\n"
            f"    message={self.message!r},\n"
            f"    related_entity_uids={json.dumps(self.related_entity_uids, indent=4)},\n"  # noqa: E501
            f"    timestamp={self.timestamp!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Operation: {self.operation}\n"
            f"Actor UID: {self._actor_uid}\n"
            f"Message: {self.message}\n"
            f"Related Entity UIDs: {json.dumps(self.related_entity_uids, indent=4)}\n"
            f"Timestamp: {self.timestamp}"
        )

    @property
    def uid(self) -> str:
        """Event unique ID."""
        return self._raw_info.id

    @property
    def operation(self) -> str:
        """Event operation."""
        return self._raw_info.operation

    @property
    def actor(self) -> _users.MLOpsUser:
        """User who triggered the event."""
        return self._client.users.get(self._actor_uid)

    @property
    def message(self) -> str:
        """Event message."""
        return self._raw_info.message

    @property
    def related_entity_uids(self) -> Dict[str, str]:
        """UIDs of entities related to the event."""
        return {
            f: getattr(self._raw_info, _f, None)
            for _f, f in [
                ("project_id", "workspace_uid"),
                ("dataset_id", "dataset_uid"),
                ("experiment_id", "experiment_uid"),
                ("tag_id", "tag_uid"),
                ("comment_id", "comment_uid"),
                ("registered_model_id", "model_uid"),
                ("registered_model_version_id", "model_version_uid"),
                ("deployment_id", "deployment_uid"),
                ("group_id", "group_uid"),
                ("user_id", "user_uid"),
                ("restriction_role_id", "sharing_role_uid"),
            ]
            if getattr(self._raw_info, _f, None)
        }

    @property
    def timestamp(self) -> datetime:
        """Event timestamp."""
        return self._raw_info.timestamp


class MLOpsWorkspaceEvents:
    def __init__(self, client: _core.Client, workspace: Any):
        self._client = client
        self._workspace = workspace

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Events associated with the Workspace.

        Examples::

            # filter on columns by using selectors
            workspace.events.list(actor="demo@h2o.ai")

            # use an index to get an H2O MLOps entity referenced by the table
            event = workspace.events.list()[0]

            # get a new Table using multiple indexes or slices
            table = workspace.events.list()[2,4]
            table = workspace.events.list()[2:4]
        """
        events = []
        sorting_request = h2o_mlops_autogen.StorageSortingRequest(
            _property=[
                h2o_mlops_autogen.StorageSortProperty(
                    _property=h2o_mlops_autogen.StorageProperty(
                        field="timestamp",
                    ),
                    order=h2o_mlops_autogen.StorageOrder.DESCENDING,
                ),
            ],
        )
        response = self._client._backend.storage.project.list_project_events(
            h2o_mlops_autogen.StorageListProjectEventsRequest(
                project_id=self._workspace.uid,
                sorting=sorting_request,
            )
        )
        events += response.event
        while response.paging:
            response = self._client._backend.storage.project.list_project_events(
                h2o_mlops_autogen.StorageListProjectEventsRequest(
                    project_id=self._workspace.uid,
                    sorting=sorting_request,
                    paging=h2o_mlops_autogen.StoragePagingRequest(
                        page_token=response.paging.next_page_token
                    ),
                )
            )
            events += response.event
        data = [
            {
                "timestamp": e.timestamp.strftime("%Y-%m-%d %I:%M:%S %p"),
                "operation": e.operation,
                "actor_username": self._client.users.get(e.actor_id).username,
                "raw_info": e,
            }
            for e in events
        ]
        return _utils.Table(
            data=data,
            keys=["timestamp", "operation", "actor_username"],
            get_method=lambda x: MLOpsWorkspaceEvent(
                client=self._client,
                raw_info=x["raw_info"],
            ),
            **selectors,
        )

    def count(self) -> int:
        """Count the Events associated with the Workspace."""
        return int(
            self._client._backend.storage.project.list_project_events(
                h2o_mlops_autogen.StorageListProjectEventsRequest(
                    project_id=self._workspace.uid,
                )
            ).event_count
        )
