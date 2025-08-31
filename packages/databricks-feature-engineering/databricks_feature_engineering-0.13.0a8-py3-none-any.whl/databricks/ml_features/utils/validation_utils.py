import logging
from typing import List, Union

from pyspark.sql import DataFrame

from databricks.ml_features.utils import utils

_logger = logging.getLogger(__name__)


def standardize_checkpoint_location(checkpoint_location):
    if checkpoint_location is None:
        return checkpoint_location
    checkpoint_location = checkpoint_location.strip()
    if checkpoint_location == "":
        checkpoint_location = None
    return checkpoint_location


def _is_spark_connect_data_frame(df):
    # We cannot directly pyspark.sql.connect.dataframe.DataFrame as it requires Spark 3.4, which
    # is not installed on DBR 12.2 and earlier. Instead, we string match on the type.
    return (
        type(df).__name__ == "DataFrame"
        and type(df).__module__ == "pyspark.sql.connect.dataframe"
    )


def check_dataframe_type(df):
    """
    Check if df is a PySpark DataFrame, otherwise raise an error.
    """
    if not (isinstance(df, DataFrame) or _is_spark_connect_data_frame(df)):
        raise ValueError(
            f"Unsupported DataFrame type: {type(df)}. DataFrame must be a PySpark DataFrame."
        )


def check_kwargs_empty(the_kwargs, method_name):
    if len(the_kwargs) != 0:
        raise TypeError(
            f"{method_name}() got unexpected keyword argument(s): {list(the_kwargs.keys())}"
        )


def check_duplicate_keys(keys: Union[str, List[str]], key_name: str) -> None:
    """
    Check if there are duplicate keys. Raise an error if there is duplicates.
    """
    if keys and isinstance(keys, list):
        seen = set()
        for k in keys:
            if k in seen:
                raise ValueError(
                    f"Found duplicated key '{k}' in {key_name}. {key_name} must be unique."
                )
            seen.add(k)


def check_and_extract_timestamp_keys_in_primary_keys(
    primary_keys: Union[str, List[str]], timestamp_keys: Union[str, List[str], None]
) -> (List[str], List[str]):
    """
    Check and extract timestamp keys in primary keys.

    This function checks and warns if not all the timestamp keys are in primary keys.
    It also extracts timestamp keys from primary keys and return two disjoint list of keys representing
    primary keys only and timestamp keys.

    This is for aligning the definition of primary keys with UC.

    Before, users are not expected to include timestamp keys in "primary keys" when using feature store API.
    After this change, we allow(and expect) users to include timestamp keys as part of the primary keys.
    And will log a warning message if not all timestamp keys are in primary keys.

    Since the FS system(client and service) has not been updated to accommodate TK in PK, we do a simple hack
    here to move the TK from PK in the returned two lists of keys.

    It returns two list, with:
    - the first one being list of PK columns with TK removed; and
    - the second one being list of TK columns.
    """
    if not primary_keys:
        raise ValueError("primary_keys can not be empty.")
    primary_keys_as_list = utils.as_list(primary_keys)
    timestamp_keys_as_list = utils.as_list(timestamp_keys, default=[])
    for tk in timestamp_keys_as_list:
        if tk not in primary_keys_as_list:
            _logger.warning(
                f"Timestamp key '{tk}' is not included in primary keys. "
                f"Timestamp keys are also primary keys. "
                f"Please include timestamp keys in the future."
            )
    pk_without_tk = [
        pk for pk in primary_keys_as_list if pk not in timestamp_keys_as_list
    ]
    if not pk_without_tk:
        raise ValueError(
            "A feature table must have at least one primary key that is not also a timeseries key."
        )
    return pk_without_tk, timestamp_keys_as_list
