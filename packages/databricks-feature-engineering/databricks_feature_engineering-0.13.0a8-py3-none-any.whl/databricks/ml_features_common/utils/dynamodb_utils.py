import json
from typing import Any, Dict, List, Optional

import boto3
import numpy as np
from botocore.config import Config

DYNAMODB = "dynamodb"
TABLE = "Table"
ATTRIBUTE_NAME = "AttributeName"
ATTRIBUTE_TYPE = "AttributeType"
KEY_TYPE = "KeyType"
KEY_SCHEMA = "KeySchema"
KEYS = "Keys"
ITEM = "Item"
ITEMS = "Items"
DYNAMODB_STRING_TYPE = "S"
DYNAMODB_NUMBER_TYPE = "N"
HASH = "HASH"
RANGE = "RANGE"
BATCH_GET_ITEM_LIMIT = 100
ATTRIBUTES_TO_GET = "AttributesToGet"

PRIMARY_KEY_ATTRIBUTE_NAME_VALUE = "_feature_store_internal__primary_keys"
PRIMARY_KEY_SCHEMA = {ATTRIBUTE_NAME: PRIMARY_KEY_ATTRIBUTE_NAME_VALUE, KEY_TYPE: HASH}
TTL_KEY_ATTRIBUTE_NAME_VALUE = "_feature_store_internal__ttl_column"

DEFAULT_CONFIG = Config(
    retries={"max_attempts": 3, "mode": "standard"}, read_timeout=30
)


def to_dynamodb_primary_key(primary_key_values: List[Any]):
    return {PRIMARY_KEY_ATTRIBUTE_NAME_VALUE: json.dumps(primary_key_values)}


def to_range_schema(timestamp_key: str):
    return {ATTRIBUTE_NAME: timestamp_key, KEY_TYPE: RANGE}


def key_schema_to_tuple(key_schema_element: Dict[str, str]):
    return (key_schema_element[ATTRIBUTE_NAME], key_schema_element[KEY_TYPE])


def key_schemas_equal(key_schema1: List[Dict], key_schema2: List[Dict]):
    # Compare two KeySchemas, ignoring order of items.
    key_schema_tuples1 = set(key_schema_to_tuple(ks) for ks in key_schema1)
    key_schema_tuples2 = set(key_schema_to_tuple(ks) for ks in key_schema2)
    return key_schema_tuples1 == key_schema_tuples2


def to_safe_select_expression(feature_names: List[str]):
    """
    Helper to create the args for safe feature selection in DynamoDB. DynamoDB projection expressions (which define the
    attributes to retrieve), cannot be used with reserved keywords or special characters (including spaces).
    e.g. "feat 1", "_feat_1", "comment" are all invalid projection expressions.

    See the Amazon documentation for more details:
    https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Query.html#DDB-Query-request-ExpressionAttributeNames

    To be safe, we alias all features with [#f0, #f1...]. Selecting ["feat 1", "_feat_1", "comment"] yields:
        - ProjectionExpression="#f0, #f1, #f2"
        - ExpressionAttributeNames={"#f0": "feat 1", "#f1": "_feat_1", "#f2": "comment}

    :param feature_names: List of feature names to select.
    :return: Safe DynamoDB expression args for selecting the given features.
    """
    safe_aliases = [f"#f{i}" for i in range(len(feature_names))]
    return {
        "ProjectionExpression": ", ".join(safe_aliases),
        "ExpressionAttributeNames": dict(zip(safe_aliases, feature_names)),
    }


def get_dynamodb_resource(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    session_token: Optional[str] = None,
    endpoint_url: Optional[str] = None,
):
    return boto3.resource(
        DYNAMODB,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
        aws_session_token=session_token,
        endpoint_url=endpoint_url,
        config=DEFAULT_CONFIG,
    )


def paginate_keys(
    batch_keys: Dict[str, List[Any]],
    batch_size_limit: int,
) -> List[Dict[str, List[Any]]]:
    """
    :param batch_keys: A large dictionary from key to list of items.
    :param batch_size_limit:  item size limit for each dictionary
    :return a list of smaller dictionaries with item size not exceeed the limit
    """
    result = []
    count = 0
    for table in batch_keys.keys():
        # if count is 0 (using new mini batch) create a new dictionary
        if count == 0:
            result.append({table: []})
        # otherwise continue filling up most recent dictionary with table key until batch limit hit
        else:
            result[-1][table] = []

        num_items = len(batch_keys[table])
        # if current count + num_items is less than batch limit, append keys for table to current dictionary
        if count + num_items <= batch_size_limit:
            result[-1][table].extend(batch_keys[table])
        # otherwise append until limit reached and create new dictionaries for remaining items in table
        else:
            batch_remaining = batch_size_limit - count
            result[-1][table].extend(batch_keys[table][:batch_remaining])
            for i in range(batch_remaining, num_items, batch_size_limit):
                result.append(
                    {table: batch_keys[table][i : min(num_items, i + batch_size_limit)]}
                )

        # update count within dictionary, mod by batch_size_limit to reset on each new dictionary
        count = (count + num_items) % batch_size_limit

    return result


def merge_batched_results(
    batched_result: List[Dict[str, List[Any]]]
) -> Dict[str, List[Any]]:
    """
    :param batched_result: A list of small dictionaries.
    :return One single dictionary that combines the small dictionaries.
    """
    result = {}
    for batch in batched_result:
        for table in batch.keys():
            if table not in result:
                result[table] = []
            result[table].extend(batch[table])

    return result
