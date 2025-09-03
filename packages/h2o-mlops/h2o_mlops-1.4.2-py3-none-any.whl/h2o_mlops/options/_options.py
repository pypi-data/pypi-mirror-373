from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Union
from typing import Optional

import h2o_mlops_autogen
from h2o_mlops import _models, _runtimes
from h2o_mlops.types import (
    ColumnLogicalType,
    ContributionType,
    DisruptionPolicyType,
    KubernetesResourceType,
    KubernetesResourceUnitType,
    LogicalOperatorType,
    MimeType,
    OperatorType,
    OrderType,
    SecurityType,
)


@dataclass
class CompositionOptions:
    model: _models.MLOpsModel
    scoring_runtime: _runtimes.MLOpsScoringRuntime
    model_version: Union[int, str] = "latest"
    traffic_weight: Optional[int] = None
    primary: Optional[bool] = None

    def _to_raw_info(self) -> h2o_mlops_autogen.V2DeploymentComposition:
        return h2o_mlops_autogen.V2DeploymentComposition(
            experiment_id=self.model.experiment(model_version=self.model_version).uid,
            deployable_artifact_type=self.scoring_runtime.artifact_type.uid,
            artifact_processor=self.scoring_runtime.artifact_processor.uid,
            runtime=self.scoring_runtime.runtime.uid,
        )


@dataclass
class SecurityOptions:
    security_type: SecurityType
    passphrase: Optional[str] = None

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2Security,
    ) -> "SecurityOptions":
        return SecurityOptions(
            security_type=SecurityType._from_raw_info(raw_info),
            passphrase=raw_info.passphrase.passphrase if raw_info.passphrase else None,
        )

    def _to_raw_info(self) -> h2o_mlops_autogen.V2Security:
        if self.security_type == SecurityType.DISABLED:
            return h2o_mlops_autogen.V2Security(disabled_security={})
        if self.security_type == SecurityType.PLAIN_PASSPHRASE:
            return h2o_mlops_autogen.V2Security(
                passphrase=h2o_mlops_autogen.V2AuthenticationPassphrase(
                    passphrase=self.passphrase,
                    hash_algorithm=(
                        h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PLAINTEXT  # noqa: E501
                    ),
                )
            )
        if self.security_type == SecurityType.HASHED_PASSPHRASE:
            return h2o_mlops_autogen.V2Security(
                passphrase=h2o_mlops_autogen.V2AuthenticationPassphrase(
                    passphrase=self.passphrase,
                    hash_algorithm=(
                        h2o_mlops_autogen.AuthenticationPassphraseHashAlgorithm.PBKDF2
                    ),
                )
            )
        if self.security_type == SecurityType.OIDC_AUTH:
            return h2o_mlops_autogen.V2Security(
                token_auth=h2o_mlops_autogen.V2AuthorizationAccessToken(
                    authentication_protocol=(
                        h2o_mlops_autogen.AuthorizationAccessTokenAuthorizationProtocolSecurityType.OIDC  # noqa: E501
                    ),
                )
            )
        raise ValueError(f"Unsupported `security_type`: {self.security_type}")


@dataclass
class KubernetesOptions:
    replicas: int = 1
    requests: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, str]] = None
    affinity: Optional[str] = None
    toleration: Optional[str] = None

    @staticmethod
    def _from_raw_info(
        raw_info: Tuple[
            h2o_mlops_autogen.V2KubernetesResourceSpec,
            h2o_mlops_autogen.V2KubernetesConfigShortcut,
        ],
    ) -> "KubernetesOptions":
        krs, kcs = raw_info
        return KubernetesOptions(
            replicas=krs.replicas,
            requests=krs.kubernetes_resource_requirements.requests,
            limits=krs.kubernetes_resource_requirements.limits,
            affinity=kcs.kubernetes_affinity_shortcut,
            toleration=kcs.kubernetes_toleration_shortcut,
        )

    def _to_raw_info(self) -> Tuple[
        h2o_mlops_autogen.V2KubernetesResourceSpec,
        h2o_mlops_autogen.V2KubernetesConfigShortcut,
    ]:
        kubernetes_resource_spec = h2o_mlops_autogen.V2KubernetesResourceSpec(
            kubernetes_resource_requirements=(
                h2o_mlops_autogen.V2KubernetesResourceRequirements(
                    limits=self.limits, requests=self.requests
                )
            ),
            replicas=self.replicas,
        )
        kubernetes_config_shortcut = h2o_mlops_autogen.V2KubernetesConfigShortcut(
            kubernetes_affinity_shortcut=self.affinity,
            kubernetes_toleration_shortcut=self.toleration,
        )
        return kubernetes_resource_spec, kubernetes_config_shortcut


@dataclass
class VPAOptions:
    resource_type: KubernetesResourceType
    unit: KubernetesResourceUnitType
    min_bound: float
    max_bound: float

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2VpaResourceSpec,
    ) -> List["VPAOptions"]:
        vpa_options = []
        resource_mappings = [
            ("cpu", KubernetesResourceType.CPU),
            ("memory", KubernetesResourceType.MEMORY),
        ]
        for attr_name, resource_type in resource_mappings:
            if attr := getattr(raw_info, attr_name, None):
                vpa_options.append(
                    VPAOptions(
                        resource_type=resource_type,
                        unit=KubernetesResourceUnitType._from_raw_info(attr.unit),
                        min_bound=attr.min,
                        max_bound=attr.max,
                    )
                )
        return vpa_options

    def _to_raw_info(self) -> h2o_mlops_autogen.V2VpaResourceBounds:
        return h2o_mlops_autogen.V2VpaResourceBounds(
            unit=self.unit._to_raw_info(),
            min=self.min_bound,
            max=self.max_bound,
        )


@dataclass
class PDBOptions:
    pods: int
    disruption_policy: DisruptionPolicyType
    is_percentage: bool = False

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2PodDisruptionBudgetSpec,
    ) -> "PDBOptions":
        disruption_policy = DisruptionPolicyType._from_raw_info(
            raw_info=raw_info,
        )
        disruption_element = (
            raw_info.min_available
            if disruption_policy == DisruptionPolicyType.MIN_AVAILABLE
            else (
                raw_info.max_unavailable
                if disruption_policy == DisruptionPolicyType.MAX_UNAVAILABLE
                else None
            )
        )
        return PDBOptions(
            pods=disruption_element.percentage or disruption_element.pods,
            disruption_policy=disruption_policy,
            is_percentage=isinstance(disruption_element.percentage, int),
        )

    def _to_raw_info(self) -> h2o_mlops_autogen.V2PodDisruptionBudgetSpec:
        kwargs = (
            {"percentage": self.pods} if self.is_percentage else {"pods": self.pods}
        )
        if self.disruption_policy == DisruptionPolicyType.MIN_AVAILABLE:
            return h2o_mlops_autogen.V2PodDisruptionBudgetSpec(
                min_available=h2o_mlops_autogen.V2MinAvailable(**kwargs),
            )
        if self.disruption_policy == DisruptionPolicyType.MAX_UNAVAILABLE:
            return h2o_mlops_autogen.V2PodDisruptionBudgetSpec(
                max_unavailable=h2o_mlops_autogen.V2MaxUnavailable(**kwargs),
            )
        raise ValueError(f"Unsupported `disruption_policy`: {self.disruption_policy}")


@dataclass
class MonitoringOptions:
    """
    Dataclass for specifying a monitoring options.

    Attributes:
        timestamp_column (Optional[str]): The name of timestamp column
            to use in monitoring.
        input_columns (Optional[List[Column]]): The list of input columns to monitor.
        output_columns (Optional[List[Column]]): The list of output columns to monitor.
        baseline_data (Optional[List[BaselineData]]): The list of baseline
        kafka_topic (Optional[str]): The name of the Kafka topic where raw
          scoring input is forward to. It is a no-op if the Kafka forwarding
          is not enabled in MLOPs cluster. If Kafka forwarding is enabled
          and not provided then default Kafka monitoring topic will be used.
    """

    timestamp_column: Optional[str] = None
    input_columns: Optional[List["Column"]] = None
    output_columns: Optional[List["Column"]] = None
    baseline_data: Optional[List["BaselineData"]] = None
    kafka_topic: Optional[str] = None
    enabled: bool = False

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2MonitoringOptions,
    ) -> "MonitoringOptions":
        columns = [Column._from_raw_info(c) for c in raw_info.columns or []]
        input_columns = [c for c in columns if not c.is_model_output]
        output_columns = [c for c in columns if c.is_model_output]

        return MonitoringOptions(
            enabled=raw_info.enabled,
            timestamp_column=raw_info.timestamp_column,
            input_columns=input_columns if input_columns else None,
            output_columns=output_columns if output_columns else None,
            baseline_data=[
                BaselineData._from_raw_info(b)
                for b in raw_info.baseline_aggregations or []
            ],
        )

    def _to_raw_info(self) -> h2o_mlops_autogen.V2MonitoringOptions:
        columns = []
        if self.input_columns:
            columns.extend(self.input_columns)
        if self.output_columns:
            columns.extend(self.output_columns)

        return h2o_mlops_autogen.V2MonitoringOptions(
            enabled=self.enabled,
            timestamp_column=self.timestamp_column or "",
            columns=[c._to_raw_info() for c in columns],
            baseline_aggregations=[
                bd._to_raw_info() for bd in self.baseline_data or []
            ],
            kafka_topic=self.kafka_topic or "",
        )


@dataclass
class BatchSourceOptions:
    """
    Dataclass for specifying a batch source.

    Attributes:
        spec_uid (str): The unique identifier for the batch source specification.
        config (Dict[str, Any]): The configuration for the batch source.
        mime_type (MimeType): The MIME type of the batch source.
        location (str): The location of the batch source.
    """

    spec_uid: str
    config: Dict[str, Any]
    mime_type: MimeType
    location: str


@dataclass
class BatchSinkOptions:
    """
    Dataclass for specifying a batch sink.

    Attributes:
        spec_uid (str): The unique identifier for the batch sink specification.
        config (Dict[str, str]): The configuration for the batch sink.
        mime_type (MimeType): The MIME type of the batch sink.
        location (str): The location of the batch sink.
    """

    spec_uid: str
    config: Dict[str, Any]
    mime_type: MimeType
    location: str


@dataclass
class BatchKubernetesOptions:
    replicas: int = 1
    min_replicas: int = 1
    requests: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, str]] = None
    affinity: Optional[str] = None
    toleration: Optional[str] = None


@dataclass
class ModelRequestParameters:
    id_field: Optional[str] = None
    contributions: Optional[ContributionType] = None
    prediction_intervals: bool = False


@dataclass
class Column:
    """
    Dataclass for specifying a column in the deployment that will be monitored.

    Attributes:
    column (str): The name of the column
    logicalType (LogicalType): The logical type of the column
    is_model_output (bool): A flag indicating whether the column represents
        the output of a model (default is False)
    """

    name: str
    logical_type: ColumnLogicalType
    is_model_output: bool = False

    def _to_raw_info(self) -> h2o_mlops_autogen.V2Column:
        return h2o_mlops_autogen.V2Column(
            column=self.name,
            logical_type=self.logical_type._to_raw_info(),
            is_model_output=self.is_model_output,
        )

    @staticmethod
    def _from_raw_info(raw_info: h2o_mlops_autogen.V2Column) -> "Column":
        return Column(
            name=raw_info.column,
            logical_type=ColumnLogicalType._from_raw_info(raw_info.logical_type),
            is_model_output=raw_info.is_model_output,
        )


@dataclass
class NumericalAggregate:
    bin_edges: List[float]
    bin_count: List[int]
    mean_value: float
    standard_deviation: float
    min_value: float
    max_value: float
    sum_value: float

    def _to_raw_info(self) -> h2o_mlops_autogen.V2NumericalAggregate:
        return h2o_mlops_autogen.V2NumericalAggregate(
            bin_edges=self.__infinity_edges(self.bin_edges),
            bin_count=self.bin_count,
            mean=self.mean_value,
            standard_deviation=self.standard_deviation,
            min=self.min_value,
            max=self.max_value,
            sum=self.sum_value,
        )

    @staticmethod
    def __infinity_edges(infinity_edges: List[float]) -> List[float]:
        return [x for x in infinity_edges if x not in {float("-inf"), float("inf")}]

    @staticmethod
    def __infinite_edges_add(edges: List[float]) -> List[float]:
        return [float("-inf")] + edges + [float("inf")]

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2NumericalAggregate,
    ) -> "NumericalAggregate":
        return NumericalAggregate(
            bin_edges=NumericalAggregate.__infinite_edges_add(raw_info.bin_edges),
            bin_count=raw_info.bin_count,
            mean_value=raw_info.mean,
            standard_deviation=raw_info.standard_deviation,
            min_value=raw_info.min,
            max_value=raw_info.max,
            sum_value=raw_info.sum,
        )


@dataclass
class CategoricalAggregate:
    value_counts: Optional[Dict[str, int]] = None

    def _to_raw_info(self) -> h2o_mlops_autogen.V2CategoricalAggregate:
        return h2o_mlops_autogen.V2CategoricalAggregate(
            value_counts=self.value_counts,
        )

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2CategoricalAggregate,
    ) -> "CategoricalAggregate":
        return CategoricalAggregate(
            value_counts=raw_info.value_counts,
        )


@dataclass
class MissingValues:
    row_count: int

    def _to_raw_info(self) -> h2o_mlops_autogen.V2MissingValues:
        return h2o_mlops_autogen.V2MissingValues(
            row_count=self.row_count,
        )

    @staticmethod
    def _from_raw_info(raw_info: h2o_mlops_autogen.V2MissingValues) -> "MissingValues":
        return MissingValues(
            row_count=raw_info.row_count,
        )


@dataclass
class BaselineData:
    column_name: str
    logical_type: ColumnLogicalType
    numerical_aggregate: Optional[NumericalAggregate] = None
    categorical_aggregate: Optional[CategoricalAggregate] = None
    missing_values: Optional[MissingValues] = None
    is_model_output: bool = False

    def _to_raw_info(self) -> h2o_mlops_autogen.V2BaselineAggregation:
        return h2o_mlops_autogen.V2BaselineAggregation(
            column=self.column_name,
            logical_type=self.logical_type._to_raw_info(),
            numerical_aggregate=(
                self.numerical_aggregate._to_raw_info()
                if self.numerical_aggregate
                else None
            ),
            categorical_aggregate=(
                self.categorical_aggregate._to_raw_info()
                if self.categorical_aggregate
                else None
            ),
            missing_values=(
                self.missing_values._to_raw_info() if self.missing_values else None
            ),
            is_model_output=self.is_model_output,
        )

    @staticmethod
    def _from_raw_info(
        raw_info: h2o_mlops_autogen.V2BaselineAggregation,
    ) -> "BaselineData":
        return BaselineData(
            column_name=raw_info.column,
            logical_type=ColumnLogicalType._from_raw_info(raw_info.logical_type),
            numerical_aggregate=(
                NumericalAggregate._from_raw_info(raw_info.numerical_aggregate)
                if raw_info.numerical_aggregate
                else None
            ),
            categorical_aggregate=(
                CategoricalAggregate._from_raw_info(raw_info.categorical_aggregate)
                if raw_info.categorical_aggregate
                else None
            ),
            missing_values=(
                MissingValues._from_raw_info(raw_info.missing_values)
                if raw_info.missing_values
                else None
            ),
            is_model_output=raw_info.is_model_output,
        )


@dataclass
class SortOptions:
    sort_by: str
    order: OrderType = OrderType.ASC

    def _to_string(self, field_name_mapping: Dict[str, str]) -> str:
        _sort_by = field_name_mapping.get(self.sort_by, self.sort_by)
        return {OrderType.ASC: _sort_by, OrderType.DESC: f"{_sort_by} desc"}[self.order]


@dataclass
class FilterOptions:
    field: str
    value: Any
    operator: OperatorType = OperatorType.EQ

    def _to_string(self, field_name_mapping: Dict[str, str]) -> str:
        v = self.value
        if isinstance(v, datetime):
            timestamp = v.astimezone(tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ",
            )
            _value = f"timestamp('{timestamp}')"
        elif isinstance(v, str):
            _value = f"'{v}'"
        elif isinstance(v, bool):
            _value = "true" if v else "false"
        else:
            _value = v

        _field = field_name_mapping.get(self.field, self.field)
        if self.operator == OperatorType.CONTAINS:
            return f"{_field}{self.operator._to_string()}{_value}"
        return f"{_field} {self.operator._to_string()} {_value}"


@dataclass
class FilterExpression:
    filters: List[Union[FilterOptions, "FilterExpression"]]
    logical_operator: LogicalOperatorType = LogicalOperatorType.AND

    def _to_string(self, field_name_mapping: Dict[str, str]) -> str:
        _filters = []
        for f in self.filters:
            _f = f._to_string(field_name_mapping)
            if isinstance(f, FilterOptions):
                _filters.append(_f)
            else:
                _filters.append(f"({_f})")

        return f" {self.logical_operator._to_string()} ".join(_filters)


@dataclass
class ListOptions:
    sort: Optional[Union[SortOptions, List[SortOptions]]] = None
    filter_expression: Optional[FilterExpression] = None

    def _to_raw_info_args(self, field_name_mapping: Dict[str, str]) -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        if s := self.sort:
            if isinstance(s, SortOptions):
                args["order_by"] = s._to_string(field_name_mapping)
            else:
                args["order_by"] = ", ".join(
                    [e._to_string(field_name_mapping) for e in s]
                )
        if f := self.filter_expression:
            args["filter"] = f._to_string(
                field_name_mapping=field_name_mapping,
            )
        return args
