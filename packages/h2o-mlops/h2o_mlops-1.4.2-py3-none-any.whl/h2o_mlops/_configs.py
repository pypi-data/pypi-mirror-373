from __future__ import annotations

from typing import Any, Dict, List, NamedTuple, Set

import h2o_mlops_autogen
from h2o_mlops import _core, _utils, types


class MLOpsConfigs:
    def __init__(self, client: _core.Client):
        self._client = client

        self.__k8s_resource_requirements = None
        self.__k8s_config_shortcuts = None

    @property
    def allowed_security_types(self) -> List[types.SecurityType]:
        """Allowed deployment security types in H2O MLOps"""
        response = self._client._backend.deployer.config.list_security_option_types()
        security_option_types = response.security_option_types or []

        security_types_mapping = {
            h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PLAINTEXT: (
                types.SecurityType.PLAIN_PASSPHRASE
            ),
            h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PBKDF2: (
                types.SecurityType.HASHED_PASSPHRASE
            ),
            h2o_mlops_autogen.AuthorizationAccessTokenAuthorizationProtocolSecurityType.OIDC: (  # noqa: E501
                types.SecurityType.OIDC_AUTH
            ),
        }
        security_types: Set[types.SecurityType] = set()
        for sot in security_option_types:
            for key in (
                "disable_security_type",
                "hash_algorithm",
                "authorization_protocol",
            ):
                value = getattr(sot, key, None)
                if value == {} and key == "disable_security_type":
                    security_types.add(types.SecurityType.DISABLED)
                elif st := security_types_mapping.get(value):
                    security_types.add(st)
        return list(security_types)

    @property
    def default_k8s_requests(self) -> Dict[str, str]:
        """Default kubernetes requests in H2O MLOps"""
        return self._k8s_resource_requirements.requests

    @property
    def default_k8s_limits(self) -> Dict[str, str]:
        """Default kubernetes limits in H2O MLOps"""
        return self._k8s_resource_requirements.limits

    @property
    def allowed_k8s_affinities(self) -> _utils.Table:
        """Allowed kubernetes affinities in H2O MLOps"""
        data = [
            {
                "uid": kas.name,
                "name": kas.display_name,
                "description": kas.description,
            }
            for kas in self._k8s_config_shortcuts.kubernetes_affinity_shortcuts
        ]

        class MLOpsK8sAffinity(NamedTuple):
            uid: str
            name: str
            description: str

        return _utils.Table(
            data=data,
            keys=["name", "uid", "description"],
            get_method=lambda x: MLOpsK8sAffinity(**x),
        )

    @property
    def allowed_k8s_tolerations(self) -> _utils.Table:
        """Allowed kubernetes tolerations in H2O MLOps"""
        data = [
            {
                "uid": kts.name,
                "name": kts.display_name,
                "description": kts.description,
            }
            for kts in self._k8s_config_shortcuts.kubernetes_toleration_shortcuts
        ]

        class MLOpsK8sToleration(NamedTuple):
            uid: str
            name: str
            description: str

        return _utils.Table(
            data=data,
            keys=["name", "uid", "description"],
            get_method=lambda x: MLOpsK8sToleration(**x),
        )

    @property
    def _k8s_resource_requirements(self) -> Any:
        if self.__k8s_resource_requirements is None:
            srv = self._client._backend.deployer.config
            response = srv.discover_default_runtime_kubernetes_resource_requirements()
            self.__k8s_resource_requirements = (
                response.default_runtime_kubernetes_resource_requirements
            )
        return self.__k8s_resource_requirements

    @property
    def _k8s_config_shortcuts(self) -> Any:
        if self.__k8s_config_shortcuts is None:
            srv = self._client._backend.deployer.config
            self.__k8s_config_shortcuts = srv.discover_kubernetes_config_shortcuts()
        return self.__k8s_config_shortcuts
