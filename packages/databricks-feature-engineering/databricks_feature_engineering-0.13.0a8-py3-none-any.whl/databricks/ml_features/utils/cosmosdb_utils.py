import json
import re
from enum import Enum
from typing import List, Optional

from azure.cosmos.exceptions import CosmosHttpResponseError
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, struct, udf
from pyspark.sql.types import StringType

from databricks.ml_features.utils.cosmosdb_type_utils import (
    BASIC_DATA_TYPE_IDENTITIES,
    get_data_type_converter,
)

PRIMARY_KEY_PROPERTY_NAME_VALUE = "_feature_store_internal__primary_keys"
FEATURE_STORE_SENTINEL_ID_VALUE = "_fs"

# when indexing mode is set to be `consistent`, the system properties `id` and `_ts` are automatically indexed.
# we also exclude all other columns to potentially be automatically indexed by Cosmos DB.
# https://learn.microsoft.com/en-us/azure/cosmos-db/index-policy
CONTAINER_INDEXING_POLICY = {
    "indexingMode": "consistent",
    "excludedPaths": [
        {"path": "/*"},
    ],
}
AUTO_SCALE_MAX_THROUGHPUT = 4000
THROUGHPUT_CONTROL_CONTAINER_NAME = (
    "databricks_feature_store_throughput_control_container"
)


class ThroughputType(Enum):
    SERVERLESS = "serverless"
    PROVISIONED = "provisioned"
    NONE = "none"


def generate_cosmosdb_primary_key(df: DataFrame, primary_keys: List[str]) -> DataFrame:
    """
    Generate the Feature Store internal primary key for Cosmos DB, and drop the individual primary keys.
    All DataFrame column data types are expected to be compatible with Cosmos DB.
    """
    return df.withColumn(
        PRIMARY_KEY_PROPERTY_NAME_VALUE,
        udf(json.dumps, StringType())(struct(*primary_keys)),
    ).drop(*primary_keys)


def generate_cosmosdb_id(
    df: DataFrame, column_for_id: Optional[str] = None
) -> DataFrame:
    """
    Generate the expected Cosmos DB id property. If provided, the `column_for_id` will be used as the `id` property.
    Otherwise, the Feature Store sentinel id value will be used.
    """
    id_col = (
        df[column_for_id] if column_for_id else lit(FEATURE_STORE_SENTINEL_ID_VALUE)
    )
    return df.withColumn("id", id_col)


def generate_cosmosdb_safe_data_types(df: DataFrame) -> DataFrame:
    """
    Helper function to convert a provided DataFrame for Cosmos DB publish.
    All unsupported data types, including nested ones, will converted to a Cosmos DB safe type.
    """
    # The column projections are either an existing column name or a converted column entity.
    columns = []
    for field in df.schema.fields:
        if type(field.dataType) in BASIC_DATA_TYPE_IDENTITIES:
            columns.append(field.name)
        else:
            converter = get_data_type_converter(field.dataType)
            to_cosmosdb_udf = udf(converter.to_cosmosdb, converter.online_data_type())
            columns.append(to_cosmosdb_udf(df[field.name]).alias(field.name))
    # Bulk projecting with df.select is faster than replacing columns inplace with df.withColumn.
    return df.select(*columns)


def validate_cosmosdb_name(name: str, name_type: str):
    """
    This is the same validation done in the backend. For Cosmos DB, we use Spark SQL to create the online store prior
    to any backend validation, so client-side validation is required to prevent SQL injections.
    """
    if not re.match(r"^\w+$", name):
        raise ValueError(
            f"The provided {name_type} must only contain alphanumeric or underscore characters."
        )


def is_serverless_throughput_offer_error(e: Exception) -> bool:
    """
    Determine if an exception was cause by offering a throughput to a serverless Cosmos DB account.
    TODO (ML-22040): Programmatically retrieve this info and refactor the Cosmos DB publish engine.
    """
    serverless_offer_error = "Setting offer throughput or autopilot on container is not supported for serverless accounts."
    if isinstance(e, CosmosHttpResponseError) and serverless_offer_error in str(e):
        return True
    return False
