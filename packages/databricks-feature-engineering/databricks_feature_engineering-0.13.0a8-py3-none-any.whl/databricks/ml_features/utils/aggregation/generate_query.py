from datetime import datetime
from typing import List, Tuple

from pyspark.sql import DataFrame
from pyspark.sql.types import *

from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features.entities.aggregation import Aggregation
from databricks.ml_features.entities.feature_aggregations import FeatureAggregations
from databricks.ml_features.utils.aggregation.aggregation_query import (
    AGG_JOIN_CONDITIONS_TEMPLATE,
    AGG_TABLES_TEMPLATE,
    AGGREGATED_TABLE_ALIAS,
    QUERY_TEMPLATE,
    SOURCE_TABLE_ALIAS,
    TIME_BUCKET_ALIAS,
)
from databricks.ml_features.utils.aggregation.aggregation_utils import (
    get_lookup_key_list,
    timedelta_to_sql,
)
from databricks.ml_features.utils.utils import (
    sanitize_identifier,
    sanitize_multi_level_name,
)
from databricks.ml_features_common.utils import uc_utils

AGGREGATED_VIEW_SPARK_TYPE_TO_SQL = {
    BooleanType: "BOOLEAN",
    ByteType: "BYTE",
    ShortType: "SHORT",
    IntegerType: "INT",
    LongType: "LONG",
    FloatType: "FLOAT",
    DoubleType: "DOUBLE",
    StringType: "STRING",
    BinaryType: "BINARY",
    DecimalType: "DECIMAL",
    DateType: "DATE",
    TimestampType: "TIMESTAMP",
    TimestampNTZType: "TIMESTAMP_NTZ",
    YearMonthIntervalType: "INTERVAL YEAR TO MONTH",
    DayTimeIntervalType: "INTERVAL DAY TO SECOND",
}


def _get_sql_type_or_throw(dataType, col_name) -> str:
    sql_data_type = AGGREGATED_VIEW_SPARK_TYPE_TO_SQL.get(type(dataType), None)
    if sql_data_type is None:
        raise ValueError(
            f"Unsupported aggregated data type {type(dataType)} for column {col_name}"
        )
    return sql_data_type


def _generate_agg_tables(
    features: FeatureAggregations,
    tb_lookup_key_expr: str,
    full_table_name: str,
) -> str:
    def generate_agg_table(i: int, aggregation: Aggregation) -> str:
        return AGG_TABLES_TEMPLATE.format(
            i=i,
            tb_lookup_key_expr=tb_lookup_key_expr,
            timestamp_key=sanitize_identifier(features.timestamp_key),
            agg_function=aggregation.function.to_sql(
                f"{SOURCE_TABLE_ALIAS}.{sanitize_identifier(aggregation.column)}",
                timestamp_key=f"{SOURCE_TABLE_ALIAS}.{sanitize_identifier(features.timestamp_key)}",
            ),
            output_column_name=sanitize_identifier(aggregation.output_column),
            table_name=full_table_name,
            offset=timedelta_to_sql(abs(aggregation.window.offset)),
            window=timedelta_to_sql(aggregation.window.duration),
            agg_tables_lookup_key_expr=" AND ".join(
                [
                    f"{TIME_BUCKET_ALIAS}.{sanitize_identifier(key)} = {SOURCE_TABLE_ALIAS}.{sanitize_identifier(key)}"
                    for key in get_lookup_key_list(features)
                ]
            ),
            TIME_BUCKET_ALIAS=TIME_BUCKET_ALIAS,
            SOURCE_TABLE_ALIAS=SOURCE_TABLE_ALIAS,
        )

    return ",".join(
        [
            generate_agg_table(i, aggregation)
            for i, aggregation in enumerate(features.aggregations)
        ]
    )


def _generate_agg_join_conditions(features: FeatureAggregations) -> str:
    def generate_join_condition(i: int) -> str:
        return AGG_JOIN_CONDITIONS_TEMPLATE.format(
            i=i,
            AGGREGATED_TABLE_ALIAS=AGGREGATED_TABLE_ALIAS,
            TIME_BUCKET_ALIAS=TIME_BUCKET_ALIAS,
            agg_join_lookup_expr=" AND ".join(
                [
                    f"{TIME_BUCKET_ALIAS}.{sanitize_identifier(key)} = {AGGREGATED_TABLE_ALIAS}_{i}.{sanitize_identifier(key)}"
                    for key in get_lookup_key_list(features)
                ]
            ),
            timestamp_key=sanitize_identifier(features.timestamp_key),
        )

    return "\n".join(
        [generate_join_condition(i) for i in range(len(features.aggregations))]
    )


def generate_aggregation_query(
    features: FeatureAggregations, _spark_client: SparkClient
) -> str:
    lookup_key = ",".join(
        sanitize_identifier(key) for key in get_lookup_key_list(features)
    )
    output_columns = ",".join(
        [
            sanitize_identifier(aggregation.output_column)
            for aggregation in features.aggregations
        ]
    )
    tb_lookup_key_expr = ",".join(
        [
            f"{TIME_BUCKET_ALIAS}.{sanitize_identifier(key)}"
            for key in get_lookup_key_list(features)
        ]
    )

    full_source_table_name = sanitize_multi_level_name(
        uc_utils.get_full_table_name(
            features.source_table,
            _spark_client.get_current_catalog(),
            _spark_client.get_current_database(),
        )
    )
    end_time = (
        f"TIMESTAMP '{features.end_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        if features.end_time
        else f"current_timestamp()"
    )
    start_time = f"TIMESTAMP '{features.start_time.strftime('%Y-%m-%d %H:%M:%S')}'"

    return QUERY_TEMPLATE.format(
        lookup_key=lookup_key,
        start_time=start_time,
        end_time=end_time,
        table_name=full_source_table_name,
        agg_tables=_generate_agg_tables(
            features, tb_lookup_key_expr, full_source_table_name
        ),
        agg_join_conditions=_generate_agg_join_conditions(features),
        granularity=timedelta_to_sql(features.granularity),
        tb_lookup_key_expr=tb_lookup_key_expr,
        timestamp_key=sanitize_identifier(features.timestamp_key),
        output_columns=output_columns,
        TIME_BUCKET_ALIAS=TIME_BUCKET_ALIAS,
    )


def _get_complex_sql_data_type(data_type, col_name) -> str:
    if isinstance(data_type, ArrayType):
        element_type = _get_sql_type_or_throw(data_type.elementType, col_name)
        return f"ARRAY<{element_type}>"
    elif isinstance(data_type, MapType):
        key_type = _get_sql_type_or_throw(data_type.keyType, col_name)
        value_type = _get_sql_type_or_throw(data_type.valueType, col_name)
        return f"MAP<{key_type}, {value_type}>"
    elif isinstance(data_type, StructType):
        struct_fields = ", ".join(
            f"{sanitize_identifier(field.name)}: {_get_sql_type_or_throw(field.dataType, col_name)}{' NOT NULL' if not field.nullable else ''}"
            for field in data_type.fields
        )
        return f"STRUCT<{struct_fields}>"


def get_aggregated_view_schema(
    features: FeatureAggregations, aggregated_view_df: DataFrame
) -> List[str]:
    columns_sql = []
    for field in aggregated_view_df.schema.fields:
        col_name = field.name
        if isinstance(field.dataType, DecimalType):
            sql_data_type = (
                f"DECIMAL({field.dataType.precision}, {field.dataType.scale})"
            )
        elif (
            isinstance(field.dataType, StructType)
            or isinstance(field.dataType, ArrayType)
            or isinstance(field.dataType, MapType)
        ):
            sql_data_type = _get_complex_sql_data_type(field.dataType, col_name)
        else:
            sql_data_type = _get_sql_type_or_throw(field.dataType, col_name)
        col_def = f"{sanitize_identifier(col_name)} {sql_data_type}"
        if (
            not field.nullable
            or col_name in get_lookup_key_list(features)
            or col_name == features.timestamp_key
        ):
            col_def += " NOT NULL"

        columns_sql.append(col_def)

    return columns_sql


def generate_dlt_notebook(
    features: FeatureAggregations,
    output_table_name: str,  # This is only the table name, not the full UC name
    aggregated_view_schema: List[str],
    _spark_client: SparkClient,
) -> str:
    query = generate_aggregation_query(features, _spark_client)

    # Construct PRIMARY KEY constraint
    pk_columns = ", ".join(
        [f"{sanitize_identifier(pk)}" for pk in get_lookup_key_list(features)]
    )
    primary_key_sql = f", PRIMARY KEY ({pk_columns}, {sanitize_identifier(features.timestamp_key)} TIMESERIES)"

    # Combine all column definitions
    columns_sql_str = ",\n ".join(aggregated_view_schema)

    # Final CREATE TABLE statement
    create_table_sql = f"CREATE OR REFRESH MATERIALIZED VIEW {sanitize_identifier(output_table_name)} (\n  {columns_sql_str}{primary_key_sql})"

    return f"{create_table_sql} \n AS {query}"
