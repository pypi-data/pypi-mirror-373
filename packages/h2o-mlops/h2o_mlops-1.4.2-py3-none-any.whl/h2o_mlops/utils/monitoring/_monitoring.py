import enum
import functools
import warnings
from copy import copy
from typing import Any, Callable, Dict, List, Optional

from h2o_mlops._experiments import MLOpsExperiment
from h2o_mlops.options import (
    BaselineData,
    CategoricalAggregate,
    Column,
    MissingValues,
    MonitoringOptions,
    NumericalAggregate,
)
from h2o_mlops.types import ColumnLogicalType

try:
    import numpy
    import pyspark as _pyspark
    import pyspark.sql as _pyspark_sql
    import pyspark.sql.functions as fun

    spark_available = True
except ImportError:
    spark_available = False


def spark_required(func: Callable) -> Callable:
    @functools.wraps(func)
    def check_spark(*args: Any, **kwargs: Any) -> Any:
        if not spark_available:
            raise RuntimeError("PySpark is required to use this function.")
        return func(*args, **kwargs)

    return check_spark


class Format(enum.Enum):
    """Data formats for source/sink."""

    BIGQUERY = "Google BigQuery table"
    CSV = "CSV file"
    JDBC_QUERY = "SQL query through JDBC connection"
    JDBC_TABLE = "SQL table through JDBC connection"
    ORC = "ORC file"
    PARQUET = "Parquet file"
    SNOWFLAKE_QUERY = "Snowflake query"
    SNOWFLAKE_TABLE = "Snowflake table"


format_map: Dict[Format, Dict[str, str]] = {
    Format.BIGQUERY: {"format": "bigquery"},
    Format.CSV: {"format": "csv", "header": "true", "inferschema": "true"},
    Format.JDBC_QUERY: {"format": "jdbc"},
    Format.JDBC_TABLE: {"format": "jdbc"},
    Format.ORC: {"format": "orc"},
    Format.PARQUET: {"format": "parquet"},
    Format.SNOWFLAKE_QUERY: {"format": "net.snowflake.spark.snowflake"},
    Format.SNOWFLAKE_TABLE: {"format": "net.snowflake.spark.snowflake"},
}


@spark_required
def read_source(
    spark: _pyspark_sql.SparkSession,
    source_data: str,
    source_format: Format,
    source_config: Optional[Dict[str, str]] = None,
) -> _pyspark_sql.DataFrame:
    _source_config = copy(format_map[source_format])
    if source_config:
        _source_config.update(source_config)
    if source_format in [Format.JDBC_QUERY, Format.SNOWFLAKE_QUERY]:
        _source_config["query"] = source_data
    if source_format in [Format.JDBC_TABLE, Format.SNOWFLAKE_TABLE]:
        _source_config["dbtable"] = source_data
    if source_format in [
        Format.JDBC_QUERY,
        Format.JDBC_TABLE,
    ] and not _source_config.get("url"):
        raise RuntimeError("JDBC connection URL required for source.")
    if source_format in [
        Format.SNOWFLAKE_QUERY,
        Format.SNOWFLAKE_TABLE,
    ]:
        required_sf_options = {
            "sfDatabase",
            "sfURL",
            "sfUser",
        }
        missing_sf_options = required_sf_options.difference(_source_config.keys())
        if missing_sf_options:
            raise RuntimeError(
                f"Snowflake option(s) {missing_sf_options} required for source."
            )

    if source_format in [
        Format.JDBC_QUERY,
        Format.JDBC_TABLE,
        Format.SNOWFLAKE_QUERY,
        Format.SNOWFLAKE_TABLE,
    ]:
        return spark.read.load(**_source_config)
    else:
        return spark.read.load(source_data, **_source_config)


@spark_required
def get_spark_master() -> str:
    active_session = _pyspark_sql.SparkSession.getActiveSession()
    if active_session:
        return active_session.conf.get("spark.master")

    if hasattr(_pyspark.SparkContext, "_active_spark_context"):
        active_context = _pyspark.SparkContext._active_spark_context
        if hasattr(active_context, "master") and active_context.master:
            return active_context.master

    return "local[*]"


@spark_required
def get_spark_session(
    app_name: str = "mlops_spark_scorer_job",
    mini_batch_size: int = 1000,
    master: Optional[str] = None,
    spark_config: Optional[Dict[str, Any]] = None,
) -> _pyspark_sql.SparkSession:
    if not spark_config:
        spark_config = {}
    conf = _pyspark.SparkConf()
    conf.setAppName(app_name)
    if master:
        conf.setMaster(master)
    if master and master.startswith("local"):
        driver_memory = conf.get("spark.driver.memory", "5g")
        conf.set("spark.driver.memory", driver_memory)
    conf.get("spark.sql.caseSensitive", "true")
    conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", str(mini_batch_size))
    conf.setAll([(k, str(v)) for k, v in spark_config.items()])
    spark = _pyspark_sql.SparkSession.builder.config(conf=conf).getOrCreate()
    return spark


@spark_required
def prepare_monitoring_options_from_data_frame(
    data_frame: _pyspark_sql.DataFrame,
    logical_type_overrides: Optional[Dict[str, ColumnLogicalType]] = None,
    input_columns: Optional[List[Column]] = None,
    output_columns: Optional[List[Column]] = None,
    experiment: Optional[MLOpsExperiment] = None,
    timestamp_column: Optional[str] = "__timestamp__",
) -> MonitoringOptions:
    data_frame.cache()
    data_frame = data_frame.withColumn(
        timestamp_column,
        col=fun.lit(0).cast(_pyspark_sql.types.TimestampType()),
    )

    input_dic = {}
    output_dic = {}
    if experiment:
        input_dic = {col["name"]: col["type"] for col in experiment.input_schema}
        output_dic = {col["name"]: col["type"] for col in experiment.output_schema}

    logical_types_input = _infer_logical_type(
        data_frame,
        logical_type_overrides=logical_type_overrides,
        timestamp_column=timestamp_column,
        monitored_columns=input_columns,
    )

    logical_types_output = _infer_logical_type(
        data_frame,
        logical_type_overrides=logical_type_overrides,
        timestamp_column=timestamp_column,
        monitored_columns=output_columns,
    )

    logical_types = {}

    for key, value in logical_types_input.items():
        if value == ColumnLogicalType.UNKNOWN and input_dic:
            logical_types[key] = _map_column_type(input_dic[key])
        else:
            logical_types[key] = value

    for key, value in logical_types_output.items():
        if value == ColumnLogicalType.UNKNOWN and output_dic:
            # Find all matching output columns with suffixes for this base column
            for output_col_name, output_col_type in output_dic.items():
                if (
                    _extract_base_column_name(output_col_name) == key
                    or output_col_name == key
                ):
                    logical_types[output_col_name] = _map_column_type(output_col_type)
        else:
            # Find all matching output columns with suffixes for this base column
            if output_dic:
                for output_col_name in output_dic.keys():
                    if (
                        _extract_base_column_name(output_col_name) == key
                        or output_col_name == key
                    ):
                        logical_types[output_col_name] = value
            else:
                logical_types[key] = value

    if experiment and not input_columns:
        input_columns = [
            Column(
                name=key,
                logical_type=value,
            )
            for key, value in logical_types.items()
            if key in input_dic.keys()
        ]

    if experiment and not output_columns:
        output_columns = []
        for output_col_name in output_dic.keys():
            if output_col_name in logical_types:
                output_columns.append(
                    Column(
                        name=output_col_name,  # Use the experiment schema column
                        logical_type=logical_types[output_col_name],
                        is_model_output=True,
                    )
                )

    for col_name in input_dic.keys():
        column_names = [c.name for c in input_columns]
        if col_name not in column_names:
            warnings.warn(
                (
                    f"Input schema column '{col_name}' not found "
                    f"in baseline columns: {column_names}"
                ),
                stacklevel=2,
            )

    for col_name in output_dic.keys():
        column_names = [c.name for c in output_columns]
        if col_name not in column_names:
            warnings.warn(
                (
                    f"Output schema column '{col_name}' not found"
                    f" in baseline columns: {column_names}"
                ),
                stacklevel=2,
            )

    baseline = _get_categorical_aggs(
        data_frame,
        logical_types=logical_types,
        timestamp_column=timestamp_column,
    )

    baseline_numerical_edges = _get_numerical_edges(
        data_frame,
        logical_types=logical_types,
    )

    baseline_numerical_aggs = _get_numerical_aggs(
        data_frame,
        baseline_numerical_edges=baseline_numerical_edges,
        timestamp_column=timestamp_column,
    )

    baseline.extend(baseline_numerical_aggs)

    if not experiment and not input_columns:
        output_column_names = [c.name for c in output_columns] if output_columns else []
        input_columns = [
            Column(
                name=base.column_name,
                logical_type=base.logical_type,
            )
            for base in baseline
            if base.column_name not in output_column_names
        ]

    if output_columns:
        output_column_names = [c.name for c in output_columns]
        for base in baseline:
            if base.column_name in output_column_names:
                base.is_model_output = True

    return MonitoringOptions(
        timestamp_column=timestamp_column,
        input_columns=input_columns,
        output_columns=output_columns,
        baseline_data=baseline,
    )


def _extract_base_column_name(column_name: str) -> str:
    """Extract column name by removing common suffixes like .0, .1, .lower, .upper."""
    import re

    # Remove suffixes like .0, .1, .2, etc.
    base_name = re.sub(r"\.\d+$", "", column_name)
    # Remove suffixes like .lower, .upper
    base_name = re.sub(r"\.(lower|upper)$", "", base_name)
    # Remove suffixes like .offset.lower, .offset.upper
    base_name = re.sub(r"\.offset\.(lower|upper)$", "", base_name)
    return base_name


def _infer_logical_type(
    sdf: _pyspark_sql.DataFrame,
    logical_type_overrides: Optional[Dict[str, ColumnLogicalType]] = None,
    timestamp_column: str = "__timestamp__",
    monitored_columns: Optional[List[Column]] = None,
) -> Dict[str, ColumnLogicalType]:
    logical_types = {}
    for field in sdf.schema.fields:
        matching_monitored_columns = (
            list(
                filter(
                    lambda c: _extract_base_column_name(c.name) == field.name
                    or c.name == field.name,
                    monitored_columns,
                )
            )
            if monitored_columns
            else []
        )

        if not monitored_columns or matching_monitored_columns:
            if isinstance(field.dataType, _pyspark_sql.types.StringType):
                if sdf.select(fun.count_distinct(field.name)).first()[0] < 10000:
                    field_logical_type = ColumnLogicalType.CATEGORICAL
                else:
                    field_logical_type = ColumnLogicalType.UNKNOWN
            elif isinstance(field.dataType, _pyspark_sql.types.DateType):
                if sdf.select(fun.count_distinct(field.name)).first()[0] < 10000:
                    field_logical_type = ColumnLogicalType.DATETIME
                else:
                    field_logical_type = ColumnLogicalType.UNKNOWN
            else:
                field_logical_type = ColumnLogicalType.NUMERICAL

            if matching_monitored_columns:
                # Use the monitored column names instead of the DataFrame field name
                for monitored_col in matching_monitored_columns:
                    logical_types[monitored_col.name] = field_logical_type
            else:
                # No monitored columns specified, use DataFrame field name
                logical_types[field.name] = field_logical_type

    if logical_type_overrides:
        logical_types.update(logical_type_overrides)
    logical_types[timestamp_column] = ColumnLogicalType.TIMESTAMP
    return logical_types


def _map_column_type(column_type: str) -> ColumnLogicalType:
    categorical_types = ["str", "string", "bool", "boolean"]
    datetime_types = ["datetime64", "datetime", "time64"]
    numerical_types = ["int", "float", "double", "int32", "int64", "float32", "float64"]

    type_lower = column_type.lower()

    if type_lower in categorical_types:
        return ColumnLogicalType.CATEGORICAL
    elif type_lower in datetime_types:
        return ColumnLogicalType.DATETIME
    elif type_lower in numerical_types:
        return ColumnLogicalType.NUMERICAL
    else:
        return ColumnLogicalType.UNKNOWN


def _get_categorical_aggs(
    sdf: _pyspark_sql.DataFrame,
    logical_types: Dict[str, ColumnLogicalType],
    timestamp_column: str,
) -> List[BaselineData]:
    aggregates: List[BaselineData] = []
    categorical_columns = [
        k for k, v in logical_types.items() if v == ColumnLogicalType.CATEGORICAL
    ]

    # Create mapping of DataFrame column names for queries
    df_column_names = [field.name for field in sdf.schema.fields]

    for monitored_column_name in categorical_columns:
        # Find the corresponding DataFrame column name
        df_column_name = None
        if monitored_column_name in df_column_names:
            df_column_name = monitored_column_name
        else:
            # Try to find matching column by base name
            base_col = _extract_base_column_name(monitored_column_name)
            for df_col in df_column_names:
                if _extract_base_column_name(df_col) == base_col or df_col == base_col:
                    df_column_name = df_col
                    break

        if not df_column_name:
            continue  # Skip if no matching column found

        missing_count = sdf.filter(
            f"{df_column_name} IS NULL OR {df_column_name} = ''"
        ).count()
        counts = (
            sdf.select(timestamp_column, df_column_name)
            .dropna()
            .filter(f"{df_column_name} != ''")
            .groupby(timestamp_column, df_column_name)
            .count()
        )
        counts = (
            counts.groupby(timestamp_column)
            .pivot(df_column_name)
            .sum()
            .fillna(0)
            .drop(timestamp_column)
        )
        value_counts_dict = counts.toPandas().iloc[0].to_dict()  # type: ignore
        data = BaselineData(
            column_name=monitored_column_name,  # Use the monitored column name
            logical_type=ColumnLogicalType.CATEGORICAL,
            categorical_aggregate=CategoricalAggregate(
                value_counts=value_counts_dict,
            ),
            missing_values=MissingValues(
                row_count=missing_count,
            ),
        )
        aggregates.append(data)
    return aggregates


def _get_numerical_edges(
    sdf: _pyspark_sql.DataFrame, logical_types: Dict[str, ColumnLogicalType]
) -> Dict[str, List[float]]:
    monitored_numerical_columns = [
        k for k, v in logical_types.items() if v == ColumnLogicalType.NUMERICAL
    ]

    # Create mapping of DataFrame column names for queries
    df_column_names = [field.name for field in sdf.schema.fields]
    base_columns_map = {}
    for monitored_col in monitored_numerical_columns:
        # Check if monitored column exists directly in DataFrame
        if monitored_col in df_column_names:
            base_columns_map[monitored_col] = monitored_col
        else:
            # Try to find matching column by base name
            base_col = _extract_base_column_name(monitored_col)
            matching_df_col = None
            for df_col in df_column_names:
                if _extract_base_column_name(df_col) == base_col or df_col == base_col:
                    matching_df_col = df_col
                    break
            if matching_df_col:
                base_columns_map[monitored_col] = matching_df_col

    # Get unique DataFrame column names for the query
    unique_base_columns = list(set(base_columns_map.values()))

    numerical_edges = {}
    if unique_base_columns:
        edges = (
            sdf.select(*unique_base_columns)
            .dropna()
            .dropDuplicates()
            .approxQuantile(
                col=unique_base_columns,
                probabilities=[x / 10 for x in range(0, 11)],
                relativeError=1e-6,
            )
        )

        # Create a mapping from base column name to edges
        base_to_edges = dict(zip(unique_base_columns, edges))

        # Map monitored column names to their edges
        for monitored_col, base_col in base_columns_map.items():
            numerical_edges[monitored_col] = (
                [float("-inf")]
                + list(dict.fromkeys(base_to_edges[base_col]))
                + [float("inf")]
            )

    return numerical_edges


def _get_numerical_aggs(
    sdf: _pyspark_sql.DataFrame,
    baseline_numerical_edges: Dict[str, List[float]],
    timestamp_column: str,
) -> List[BaselineData]:
    aggregates: List[BaselineData] = []
    grouped_sdf = sdf.groupby(timestamp_column)

    # Create mapping of DataFrame column names for queries
    df_column_names = [field.name for field in sdf.schema.fields]

    for monitored_column_name, edges in baseline_numerical_edges.items():
        # Find the corresponding DataFrame column name
        df_column_name = None
        if monitored_column_name in df_column_names:
            df_column_name = monitored_column_name
        else:
            # Try to find matching column by base name
            base_col = _extract_base_column_name(monitored_column_name)
            for df_col in df_column_names:
                if _extract_base_column_name(df_col) == base_col or df_col == base_col:
                    df_column_name = df_col
                    break

        if not df_column_name:
            continue  # Skip if no matching column found

        col = sdf[df_column_name]
        native_aggs = grouped_sdf.agg(
            fun.count(fun.when(fun.isnull(col), timestamp_column)).alias(
                f"missing_count({df_column_name})"
            ),
            fun.count(col),  # This already excludes nulls
            fun.sum(col),  # This already excludes nulls
            fun.min(col),  # This already excludes nulls
            fun.max(col),  # This already excludes nulls
            fun.mean(col),  # This already excludes nulls
            fun.stddev(col),  # This already excludes nulls
        )
        rdd = sdf.select(timestamp_column, df_column_name).dropna().rdd
        num_bins = len(edges) - 1
        rdd_aggs = (
            rdd.aggregateByKey(  # type: ignore
                zeroValue=numpy.zeros(num_bins, dtype=int),
                seqFunc=lambda x, y: x
                + numpy.histogram(y, bins=edges)[0],  # noqa: B023
                combFunc=lambda x, y: x + y,
            )
            .map(lambda x: (x[0], x[1].tolist()))
            .toDF(
                _pyspark_sql.types.StructType(
                    [
                        _pyspark_sql.types.StructField(
                            timestamp_column,
                            _pyspark_sql.types.TimestampType(),
                            True,
                        ),
                        _pyspark_sql.types.StructField(
                            "histogram_counts",
                            _pyspark_sql.types.ArrayType(
                                _pyspark_sql.types.LongType(), True
                            ),
                            True,
                        ),
                    ]
                )
            )
        )
        result_df = native_aggs.join(rdd_aggs, on=timestamp_column).cache()

        rows = result_df.collect()
        for row in rows:

            baseline_data = BaselineData(
                column_name=monitored_column_name,  # Use the monitored column name
                logical_type=ColumnLogicalType.NUMERICAL,
                numerical_aggregate=NumericalAggregate(
                    bin_edges=edges,
                    bin_count=row["histogram_counts"],
                    mean_value=row[f"avg({df_column_name})"],
                    standard_deviation=row[f"stddev({df_column_name})"],
                    min_value=row[f"min({df_column_name})"],
                    max_value=row[f"max({df_column_name})"],
                    sum_value=row[f"sum({df_column_name})"],
                ),
                missing_values=MissingValues(
                    row_count=row[f"missing_count({df_column_name})"],
                ),
            )
            aggregates.append(baseline_data)

        result_df.unpersist()

    return aggregates
