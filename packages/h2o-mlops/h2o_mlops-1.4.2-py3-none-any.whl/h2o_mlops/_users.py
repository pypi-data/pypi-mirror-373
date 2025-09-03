from __future__ import annotations

from typing import Any, Optional

from h2o_mlops import _core, _utils


class MLOpsUser:
    def __init__(self, raw_info: Any):
        self._raw_info = raw_info

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__module__}.{self.__class__.__name__}(\n"
            f"    uid={self.uid!r},\n"
            f"    username={self.username!r},\n"
            f"    name={self.name!r},\n"
            f"    email={self.email!r},\n"
            f")'>"
        )

    def __str__(self) -> str:
        return (
            f"UID: {self.uid}\n"
            f"Username: {self.username}\n"
            f"Name: {self.name}\n"
            f"Email: {self.email}\n"
        )

    @property
    def uid(self) -> str:
        """User unique ID."""
        return self._raw_info.name.split("/")[-1]

    @property
    def username(self) -> str:
        """User username."""
        return self._raw_info.login_principal

    @property
    def name(self) -> str:
        """User display name."""
        return self._raw_info.display_name

    @property
    def email(self) -> Optional[str]:
        """User primary Email."""
        return self._raw_info.emails[0].address if self._raw_info.emails else None


class MLOpsUsers:
    def __init__(self, client: _core.Client):
        self._client = client

    def get(self, uid: str) -> MLOpsUser:
        """Get the User object corresponding to a User in H2O MLOps.

        Args:
            uid: H2O MLOps unique ID for the User.
        """
        return MLOpsUser(
            self._client._backend.authz.user.get_user(name_1="users/" + uid).user
        )

    def get_me(self) -> MLOpsUser:
        """Get the User object corresponding to
        the currently authenticated User in H2O MLOps.
        """

        return MLOpsUser(self._client._backend.authz.user.get_me().user)

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        """Retrieve Table of Users available in the H2O MLOps.

        Examples::

            # filter on columns by using selectors
            mlops.users.list(username="demo@h2o.ai")

            # use an index to get an H2O MLOps entity referenced by the table
            user = mlops.users.list()[0]

            # get a new Table using multiple indexes or slices
            table = mlops.users.list()[2,4]
            table = mlops.users.list()[2:4]
        """
        users = []

        response = self._client._backend.authz.user.list_users()
        users += response.users
        while response.next_page_token is not None:
            response = self._client._backend.authz.user.list_users(
                page_token=response._next_page_token
            )
            users += response.users
        data = [
            {
                "username": u.login_principal,
                "name": u.display_name,
                "uid": u.name.split("/")[-1],
                "raw_info": u,
            }
            for u in users
        ]
        return _utils.Table(
            data=data,
            keys=["username", "name", "uid"],
            get_method=lambda x: MLOpsUser(x["raw_info"]),
            **selectors,
        )
