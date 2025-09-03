import sys
from enum import auto, Enum

import h2o_mlops_autogen

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DeploymentModeType(str, Enum):
    SINGLE_MODEL = "Single Model"
    AB_TEST = "A/B Test"
    CHAMPION_CHALLENGER = "Champion/Challenger"

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2Deployment,
    ) -> "DeploymentModeType":
        if raw_info.single:
            return DeploymentModeType.SINGLE_MODEL
        if raw_info.split:
            return DeploymentModeType.AB_TEST
        if raw_info.shadow:
            return DeploymentModeType.CHAMPION_CHALLENGER
        raise ValueError("Deployment mode type not found.")


class SecurityType(Enum):
    DISABLED = auto()
    PLAIN_PASSPHRASE = auto()
    HASHED_PASSPHRASE = auto()
    OIDC_AUTH = auto()

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2Security,
    ) -> "SecurityType":
        if raw_info.disabled_security == {}:
            return SecurityType.DISABLED
        if raw_info.passphrase:
            if (
                raw_info.passphrase.hash_algorithm
                == h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PLAINTEXT
            ):
                return SecurityType.PLAIN_PASSPHRASE
            if raw_info.passphrase.hash_algorithm in [
                h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PBKDF2,
                h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.BCRYPT,
            ]:
                return SecurityType.HASHED_PASSPHRASE
        if (
            raw_info.token_auth
            and raw_info.token_auth.authentication_protocol
            == h2o_mlops_autogen.AuthorizationAccessTokenAuthorizationProtocolSecurityType.OIDC  # noqa: E501
        ):
            return SecurityType.OIDC_AUTH
        raise ValueError("Security type not found.")


class KubernetesResourceType(Enum):
    CPU = auto()
    MEMORY = auto()


class KubernetesResourceUnitType(Enum):
    MILLI_CORES = auto()
    CORES = auto()
    MIB = auto()
    GIB = auto()
    UNKNOWN = auto()

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2ResourceUnit,
    ) -> "KubernetesResourceUnitType":
        return _K8S_RESOURCE_UNIT_TYPE_FROM_RAW_MAPPING.get(
            raw_info, KubernetesResourceUnitType.UNKNOWN
        )

    def _to_raw_info(self) -> h2o_mlops_autogen.V2ResourceUnit:
        return _K8S_RESOURCE_UNIT_TYPE_TO_RAW_MAPPING.get(
            self, h2o_mlops_autogen.V2ResourceUnit.RESOURCE_UNIT_UNSPECIFIED
        )


class DisruptionPolicyType(Enum):
    MIN_AVAILABLE = auto()
    MAX_UNAVAILABLE = auto()

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2PodDisruptionBudgetSpec,
    ) -> "DisruptionPolicyType":
        if raw_info.min_available:
            return DisruptionPolicyType.MIN_AVAILABLE
        if raw_info.max_unavailable:
            return DisruptionPolicyType.MAX_UNAVAILABLE
        raise ValueError("Disruption policy type not found.")


class ColumnLogicalType(Enum):
    """
    Enum representing the possible logical types for columns.

    Attributes:
        CATEGORICAL: Categorical/nominal data type
        NUMERICAL: Numerical/continuous data type
        DATETIME: DateTime column type
        TEXT: Text/string column type
        IMAGE: Image data type
        UNKNOWN: Unknown or undefined data type
    """

    CATEGORICAL = auto()
    NUMERICAL = auto()
    DATETIME = auto()
    TEXT = auto()
    IMAGE = auto()
    TIMESTAMP = auto()
    ID = auto()
    UNKNOWN = auto()

    def _to_raw_info(self) -> h2o_mlops_autogen.V2LogicalType:
        return {
            self.CATEGORICAL.value: h2o_mlops_autogen.V2LogicalType.CATEGORICAL,
            self.NUMERICAL.value: h2o_mlops_autogen.V2LogicalType.NUMERICAL,
            self.DATETIME.value: h2o_mlops_autogen.V2LogicalType.DATETIME,
            self.TEXT.value: h2o_mlops_autogen.V2LogicalType.TEXT,
            self.IMAGE.value: h2o_mlops_autogen.V2LogicalType.IMAGE,
            self.TIMESTAMP.value: h2o_mlops_autogen.V2LogicalType.TIMESTAMP,
            self.ID.value: h2o_mlops_autogen.V2LogicalType.ID,
        }.get(
            self.value,
            h2o_mlops_autogen.V2LogicalType.LOGICAL_TYPE_UNSPECIFIED,
        )

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2LogicalType,
    ) -> "ColumnLogicalType":
        return {
            "CATEGORICAL": ColumnLogicalType.CATEGORICAL,
            "NUMERICAL": ColumnLogicalType.NUMERICAL,
            "DATETIME": ColumnLogicalType.DATETIME,
            "TEXT": ColumnLogicalType.TEXT,
            "IMAGE": ColumnLogicalType.IMAGE,
            "TIMESTAMP": ColumnLogicalType.TIMESTAMP,
            "ID": ColumnLogicalType.ID,
        }.get(raw_info, ColumnLogicalType.UNKNOWN)


class ContributionType(Enum):
    NONE = h2o_mlops_autogen.ModelRequestParametersShapleyType.NONE
    ORIGINAL = h2o_mlops_autogen.ModelRequestParametersShapleyType.ORIGINAL
    TRANSFORMED = h2o_mlops_autogen.ModelRequestParametersShapleyType.TRANSFORMED


class MimeType(StrEnum):
    """
    Enum for specifying the MIME type.

    Attributes:
        CSV (str): The MIME type for CSV files.
        CSV_WITH_HEADER (str): The MIME type for CSV files with headers.
        JSONL (str): The MIME type for JSONL files.
        IMAGE (str): The MIME type for image files.
        VIDEO (str): The MIME type for video files.
        OCTET_STREAM (str): The MIME type for OCTET streams.
        JDBC (str): The MIME type for JDBC connection.
    """

    CSV = "text/csv"
    CSV_WITH_HEADER = "text/csv; header=present"
    JSONL = "text/jsonl"
    IMAGE = "image/*"
    AUDIO = "audio/*"
    VIDEO = "video/*"
    OCTET_STREAM = "application/octet-stream"
    JDBC = "jdbc"


class OrderType(Enum):
    ASC = auto()
    DESC = auto()


class OperatorType(Enum):
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    IN = auto()
    CONTAINS = auto()

    def _to_string(self) -> str:
        return {
            self.EQ.value: "=",
            self.NEQ.value: "!=",
            self.LT.value: "<",
            self.LTE.value: "<=",
            self.GT.value: ">",
            self.GTE.value: ">=",
            self.IN.value: "in",
            self.CONTAINS.value: ":",
        }[self.value]


class LogicalOperatorType(Enum):
    AND = auto()
    OR = auto()
    NOT = auto()

    def _to_string(self) -> str:
        return {
            self.AND.value: "AND",
            self.OR.value: "OR",
            self.NOT.value: "NOT",
        }[self.value]


# Maps
_K8S_RESOURCE_UNIT_TYPE_TO_RAW_MAPPING = {
    KubernetesResourceUnitType.MILLI_CORES: (
        h2o_mlops_autogen.V2ResourceUnit.MILLICORES
    ),
    KubernetesResourceUnitType.CORES: h2o_mlops_autogen.V2ResourceUnit.CORES,
    KubernetesResourceUnitType.MIB: h2o_mlops_autogen.V2ResourceUnit.MIB,
    KubernetesResourceUnitType.GIB: h2o_mlops_autogen.V2ResourceUnit.GIB,
}

_K8S_RESOURCE_UNIT_TYPE_FROM_RAW_MAPPING = {
    v: k for k, v in _K8S_RESOURCE_UNIT_TYPE_TO_RAW_MAPPING.items()
}
