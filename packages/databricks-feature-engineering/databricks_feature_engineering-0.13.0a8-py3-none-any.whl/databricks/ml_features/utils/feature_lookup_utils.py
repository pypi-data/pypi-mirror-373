import copy
import datetime
import logging
import re
from collections import defaultdict
from functools import reduce
from typing import Dict, List, Optional, Tuple

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.functions import sum, unix_timestamp

from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features.entities.data_source import DataSource
from databricks.ml_features.entities.data_type import DataType
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.environment_variables import BROADCAST_JOIN_THRESHOLD
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.utils import uc_utils

_logger = logging.getLogger(__name__)


def _spark_asof_join_features(
    df: DataFrame,
    df_lookup_keys: List[str],
    df_timestamp_lookup_key: str,
    feature_table_data: DataFrame,
    feature_table_keys: List[str],
    feature_table_timestamp_key: str,
    feature_to_output_name: Dict[str, str],
    lookback_window_seconds: Optional[float] = None,
    use_spark_native_join: Optional[bool] = False,
) -> DataFrame:
    # Alias feature table's keys to DataFrame lookup keys
    ft_key_aliases = [
        feature_table_data[ft_key].alias(df_key)
        for (ft_key, df_key) in zip(feature_table_keys, df_lookup_keys)
    ]
    # Alias features to corresponding output names
    ft_features = [
        (feature_name, output_name)
        for feature_name, output_name in feature_to_output_name.items()
        # Skip join if feature it is already in DataFrame and therefore overridden
        if output_name not in df.columns
    ]
    ft_feature_aliases = [
        feature_table_data[feature_name].alias(output_name)
        for feature_name, output_name in ft_features
    ]
    # Alias feature table's timestamp key to DataFrame timestamp lookup keys
    ft_timestamp_key_aliases = [
        feature_table_data[feature_table_timestamp_key].alias(df_timestamp_lookup_key)
    ]
    # Select key, timestamp key, and feature columns from feature table
    feature_and_keys = feature_table_data.select(
        ft_key_aliases + ft_timestamp_key_aliases + ft_feature_aliases
    )

    _logger.debug(
        "Using native spark for point in time join"
        if use_spark_native_join
        else "Using tempo for point in time join"
    )

    if use_spark_native_join:
        joined_df = _spark_asof_join_features_native(
            labels_df=df,
            features_df=feature_and_keys,
            primary_keys=df_lookup_keys,
            timestamp_key=df_timestamp_lookup_key,
            lookback_window_seconds=lookback_window_seconds,
        )
    else:
        joined_df = _spark_asof_join_features_tempo(
            df=df,
            df_lookup_keys=df_lookup_keys,
            df_timestamp_lookup_key=df_timestamp_lookup_key,
            feature_and_keys=feature_and_keys,
            ft_features=ft_features,
            lookback_window_seconds=lookback_window_seconds,
        )
    return joined_df


def _spark_asof_join_features_tempo(
    df: DataFrame,
    df_lookup_keys: List[str],
    df_timestamp_lookup_key: str,
    feature_and_keys: DataFrame,
    ft_features: List[Tuple[str, str]],
    lookback_window_seconds: Optional[float] = None,
) -> DataFrame:
    # [ML-19825] Import TSDF only at as-of join time to avoid DynamoDB publish issue
    from tempo.tsdf import TSDF

    # Initialize Tempo TSDFs for df and feature table.
    # Feature table timestamp keys and primary keys are aliased to
    # DataFrame's timestamp lookup keys and lookup keys respectively
    # because ts_col and partition_cols must match.
    df_tsdf = TSDF(df, ts_col=df_timestamp_lookup_key, partition_cols=df_lookup_keys)
    ft_tsdf = TSDF(
        feature_and_keys,
        ts_col=df_timestamp_lookup_key,
        partition_cols=df_lookup_keys,
    )
    # Perform as-of join
    joined_df = df_tsdf.asofJoin(
        ft_tsdf,
        left_prefix="left",
        right_prefix="right",
        skipNulls=False,
        tolerance=lookback_window_seconds
        if lookback_window_seconds is not None
        else None,
    ).df
    # Remove prefixes from joined df to restore column names
    left_aliases = [
        joined_df[f"left_{column_name}"].alias(column_name)
        for column_name in df.columns
        if column_name not in df_lookup_keys
    ]
    right_aliases = [
        joined_df[f"right_{output_name}"].alias(output_name)
        for (_, output_name) in ft_features
    ]
    return joined_df.select(df_lookup_keys + left_aliases + right_aliases)


def _spark_asof_join_features_native(
    labels_df: DataFrame,
    features_df: DataFrame,
    primary_keys: List[str],
    timestamp_key: str,
    lookback_window_seconds: Optional[float] = None,
):
    """
    Performs an as-of join operation between two dataframes using native Spark operations.
    Uses broadcast join for label dataset when within a size threshold to improve
    efficiency of join operation with the assumption that size(labels_df) << size(features_df).
    TODO(ML-40580): automatically switch labels_df and features_df based on size
    The join operation is performed as follows:
        1. Drop non-join key (primary and timestamp keys) columns from labels and features DataFrames
        2. Broadcast join labels onto features DataFrame if within broadcast threshold.
        3. Select maximum timestamp for each primary key
        4. Rejoin non-primary key columns from features DataFrame to get features data
        5. Rejoin non-primary key columns from labels DataFrame to get joint data

    Parameters:
    labels_df (DataFrame): The labels dataframe to join.
    features_df (DataFrame): The features dataframe to join.
    primary_keys (List[str]): The primary keys used for joining.
    timestamp_key (str): The timestamp key used for joining.
    lookback_window_seconds (Optional[float]): The lookback window in seconds.
        If provided, the join operation will only consider records within this window.

    Returns:
    DataFrame: The result of the as-of join operation.
    """
    labels_df_keys_only = labels_df.select(
        [F.col(key) for key in primary_keys] + [F.col(timestamp_key)]
    )

    # Broadcast labels DataFrame if within the broadcast threshold
    if _df_in_size_threshold(labels_df_keys_only, BROADCAST_JOIN_THRESHOLD.get()):
        labels_df_keys_only = F.broadcast(labels_df_keys_only)

    # Drop non-primary key columns from features DataFrame
    features_df_keys_only = features_df.select(
        [F.col(key).alias(f"__features_pk_{key}") for key in primary_keys]
        + [F.col(timestamp_key).alias("__features_tk")]
    )

    # Create join conditions
    join_conditions = [
        labels_df_keys_only[key] == features_df_keys_only[f"__features_pk_{key}"]
        for key in primary_keys
    ]
    join_conditions = reduce(lambda x, y: x & y, join_conditions)
    join_conditions &= (
        labels_df_keys_only[timestamp_key] >= features_df_keys_only["__features_tk"]
    )
    if lookback_window_seconds is not None:
        join_conditions &= (
            unix_timestamp(labels_df_keys_only[timestamp_key])
            - unix_timestamp(features_df_keys_only["__features_tk"])
        ) <= lookback_window_seconds

    # Join labels and features DataFrames
    labels_df_keys_with_features_keys = labels_df_keys_only.join(
        features_df_keys_only, on=join_conditions, how="left"
    )

    # Find the features max timestamps for each primary keys and timestamp key in labels
    labels_df_keys_with_features_keys = labels_df_keys_with_features_keys.groupBy(
        [labels_df_keys_only[key] for key in primary_keys] + [F.col(timestamp_key)]
    ).agg(F.max("__features_tk").alias("__max_ts"))

    if _df_in_size_threshold(
        labels_df_keys_with_features_keys, BROADCAST_JOIN_THRESHOLD.get()
    ):
        labels_df_keys_with_features_keys = F.broadcast(
            labels_df_keys_with_features_keys
        )

    # Rejoin features DataFrame to get the features data
    join_conditions = [
        features_df[key] == labels_df_keys_with_features_keys[key]
        for key in primary_keys
    ]
    join_conditions = reduce(lambda x, y: x & y, join_conditions)
    join_conditions &= (
        features_df[timestamp_key] == labels_df_keys_with_features_keys["__max_ts"]
    )

    features = features_df.join(
        labels_df_keys_with_features_keys,
        on=join_conditions,
        how="inner",
    )

    pk_columns_to_drop = [
        labels_df_keys_with_features_keys[key] for key in primary_keys
    ]
    features = features.drop(*pk_columns_to_drop).drop(
        features_df[timestamp_key], labels_df_keys_with_features_keys["__max_ts"]
    )
    features = features.dropDuplicates(primary_keys + [timestamp_key])
    # Rejoin labels DataFrame if columns were dropped
    joint_df = labels_df.join(features, on=primary_keys + [timestamp_key], how="left")
    return joint_df


def _df_in_size_threshold(df, threshold) -> float:
    # Default to within threshold if can not find
    try:
        num_bytes = _get_df_size_from_spark_plan(df)
    except Exception as e:
        num_bytes = 0
    return num_bytes <= threshold


def _get_df_size_from_spark_plan(df: DataFrame) -> float:
    spark_client = SparkClient()
    spark = spark_client._spark
    df.createOrReplaceTempView("view")

    plan = spark.sql("explain cost select * from view").collect()[0][0]
    search_result = re.search(r"sizeInBytes=.*(['\)])", plan, re.MULTILINE)
    if search_result is not None:
        result = search_result.group(0).replace(")", "")
    else:
        raise ValueError("Unable to obtain sizeInBytes from Spark plan")

    units_map = {"TiB": 1024**4, "GiB": 1024**3, "MiB": 1024**2, "KiB": 1024}
    size, units = result.split("=")[1].split()
    return float(size) * units_map.get(units.rstrip(","), 1)


def _spark_join_features(
    df: DataFrame,
    df_keys: List[str],
    feature_table_data: DataFrame,
    feature_table_keys: List[str],
    feature_to_output_name: Dict[str, str],
) -> DataFrame:
    """
    Helper to join `feature_name` from `feature_table_data` into `df`.

    This join uses a temporary table that contains only the keys and feature
    from the feature table. The temporary table aliases the keys to match
    the lookup keys and the feature to match the output_name.

    Aliasing the keys allows us to join on name instead of by column,
    which prevents duplicate column names after the join.
    (see: https://kb.databricks.com/data/join-two-dataframes-duplicated-columns.html)

    The joined-in feature is guaranteed to be unique because FeatureSpec
    columns must be unique and the join is skipped if the feature
    already exists in the DataFrame.
    """

    # Alias feature table's keys to DataFrame lookup keys
    ft_key_aliases = [
        feature_table_data[ft_key].alias(df_key)
        for (ft_key, df_key) in zip(feature_table_keys, df_keys)
    ]
    # Alias features to corresponding output names
    ft_feature_aliases = [
        feature_table_data[feature_name].alias(output_name)
        for feature_name, output_name in feature_to_output_name.items()
        # Skip join if feature it is already in DataFrame and therefore overridden
        if output_name not in df.columns
    ]
    # Select key and feature columns from feature table
    feature_and_keys = feature_table_data.select(ft_key_aliases + ft_feature_aliases)
    # Join feature to feature table
    return df.join(feature_and_keys, df_keys, how="left")


def _validate_join_keys(
    feature_column_info: FeatureColumnInfo,
    df: DataFrame,
    feature_table_metadata: FeatureTable,
    feature_table_data: DataFrame,
    is_timestamp_key: bool = False,
):
    join_error_phrase = (
        f"Unable to join feature table '{feature_column_info.table_name}'"
    )
    feature_column_info_keys = (
        feature_column_info.timestamp_lookup_key
        if is_timestamp_key
        else feature_column_info.lookup_key
    )
    feature_table_keys = (
        feature_table_metadata.timestamp_keys
        if is_timestamp_key
        else feature_table_metadata.primary_keys
    )

    lookup_key_kind = "timestamp lookup key" if is_timestamp_key else "lookup key"
    feature_table_key_kind = "timestamp key" if is_timestamp_key else "primary key"

    # Validate df has necessary keys
    missing_df_keys = list(
        filter(lambda df_key: df_key not in df.columns, feature_column_info_keys)
    )
    if missing_df_keys:
        missing_keys = ", ".join([f"'{key}'" for key in missing_df_keys])
        raise ValueError(
            f"{join_error_phrase} because {lookup_key_kind} {missing_keys} not found in DataFrame."
        )
    # Validate feature table has necessary keys
    missing_ft_keys = list(
        filter(
            lambda ft_key: ft_key not in feature_table_data.columns, feature_table_keys
        )
    )
    if missing_ft_keys:
        missing_keys = ", ".join([f"'{key}'" for key in missing_ft_keys])
        raise ValueError(
            f"{join_error_phrase} because {feature_table_key_kind} {missing_keys} not found in feature table."
        )

    # Validate number of feature table keys matches number of df lookup keys
    if len(feature_column_info_keys) != len(feature_table_keys):
        raise ValueError(
            f"{join_error_phrase} because "
            f"number of {feature_table_key_kind}s ({feature_table_keys}) "
            f"does not match "
            f"number of {lookup_key_kind}s ({feature_column_info_keys})."
        )

    # Validate feature table keys match types of df keys. The number of keys is expected to be the same.
    for (df_key, ft_key) in zip(feature_column_info_keys, feature_table_keys):
        df_key_type = DataType.from_spark_type(df.schema[df_key].dataType)
        ft_key_type = DataType.from_spark_type(
            feature_table_data.schema[ft_key].dataType
        )
        if df_key_type != ft_key_type:
            raise ValueError(
                f"{join_error_phrase} because {feature_table_key_kind} '{ft_key}' has type '{DataType.to_string(ft_key_type)}' "
                f"but corresponding {lookup_key_kind} '{df_key}' has type '{DataType.to_string(df_key_type)}' in DataFrame."
            )


def _validate_join_feature_data(
    df: DataFrame,
    features_to_join: List[FeatureColumnInfo],
    feature_table_metadata_map: Dict[str, FeatureTable],
    feature_table_data_map: Dict[str, DataFrame],
):
    for feature_info in features_to_join:
        feature_table_metadata = feature_table_metadata_map[feature_info.table_name]
        feature_table_data = feature_table_data_map[feature_info.table_name]
        # Validate feature table primary keys match length/type of df lookup keys
        _validate_join_keys(
            feature_info,
            df,
            feature_table_metadata,
            feature_table_data,
            is_timestamp_key=False,
        )
        # Validate feature table timestamp keys match length/type of df timestamp lookup keys
        _validate_join_keys(
            feature_info,
            df,
            feature_table_metadata,
            feature_table_data,
            is_timestamp_key=True,
        )


def join_feature_data_if_not_overridden(
    feature_spec: FeatureSpec,
    df: DataFrame,
    features_to_join: List[FeatureColumnInfo],
    feature_table_metadata_map: Dict[str, FeatureTable],
    feature_table_data_map: Dict[str, DataFrame],
    use_spark_native_join: Optional[bool] = False,
) -> DataFrame:
    """
    Joins `df` with features specified by `feature_spec.feature_column_infos` if they do not already exist.

    Return column order is df.columns + newly joined features. The newly joined feature order is not guaranteed to
    match `feature_spec.feature_column_infos` as feature lookups are first grouped by table for efficiency.

    Before joining, it checks that:
    1. Feature table keys match length and types of `df` lookup keys specified by FeatureSpec
    2. `df` contains lookup keys specified by FeatureSpec
    3. Feature table timestamp lookup keys match length and types of `df` timestamp lookup keys if specified by FeatureSpec
    4. `df` contains timestamp lookup keys if specified by FeatureSpec
    """
    _validate_join_feature_data(
        df=df,
        features_to_join=features_to_join,
        feature_table_metadata_map=feature_table_metadata_map,
        feature_table_data_map=feature_table_data_map,
    )

    # Helper class to group all unique combinations of feature table names and lookup keys.
    # All features in each of these groups will be JOINed with the training df using a single JOIN.
    class JoinDataKey:
        def __init__(
            self,
            feature_table: str,
            lookup_key: List[str],
            timestamp_lookup_key: List[str],
            lookback_window: Optional[datetime.timedelta] = None,
        ):
            self.feature_table = feature_table
            self.lookup_key = lookup_key
            self.timestamp_lookup_key = timestamp_lookup_key
            self.lookback_window = lookback_window

        def __hash__(self):
            return (
                hash(self.feature_table)
                + hash(tuple(self.lookup_key))
                + hash(tuple(self.timestamp_lookup_key))
                + hash(self.lookback_window)
            )

        def __eq__(self, other):
            return (
                self.feature_table == other.feature_table
                and self.lookup_key == other.lookup_key
                and self.timestamp_lookup_key == other.timestamp_lookup_key
                and self.lookback_window == other.lookback_window
            )

    # Iterate through the list of FeatureColumnInfo and group features by name of the
    # feature table and lookup key(s) and timestamp lookup key(s)
    table_join_data = defaultdict(dict)
    lookback_windows = {
        t.table_name: t.lookback_window for t in feature_spec.table_infos
    }
    for feature_info in features_to_join:
        join_data_key = JoinDataKey(
            feature_info.table_name,
            feature_info.lookup_key,
            feature_info.timestamp_lookup_key,
            lookback_windows[feature_info.table_name],
        )
        table_join_data[join_data_key][
            feature_info.feature_name
        ] = feature_info.output_name

    for join_data_key, feature_to_output_name in table_join_data.items():

        feature_table_metadata = feature_table_metadata_map[join_data_key.feature_table]
        feature_table_data = feature_table_data_map[join_data_key.feature_table]

        if join_data_key.timestamp_lookup_key:
            # If lookback window is set to 0, then perform exact join instead of asof join to get perf benefits.
            if (
                join_data_key.lookback_window is not None
                and join_data_key.lookback_window == 0
            ):
                df = _spark_join_features(
                    df=df,
                    df_keys=join_data_key.lookup_key
                    + join_data_key.timestamp_lookup_key,
                    feature_table_data=feature_table_data,
                    feature_table_keys=feature_table_metadata.primary_keys
                    + feature_table_metadata.timestamp_keys,
                    feature_to_output_name=feature_to_output_name,
                )
            else:
                df = _spark_asof_join_features(
                    df=df,
                    df_lookup_keys=join_data_key.lookup_key,
                    df_timestamp_lookup_key=join_data_key.timestamp_lookup_key[0],
                    feature_table_data=feature_table_data,
                    feature_table_keys=feature_table_metadata.primary_keys,
                    feature_table_timestamp_key=feature_table_metadata.timestamp_keys[
                        0
                    ],
                    feature_to_output_name=feature_to_output_name,
                    lookback_window_seconds=join_data_key.lookback_window,
                    use_spark_native_join=use_spark_native_join,
                )
        else:
            df = _spark_join_features(
                df=df,
                df_keys=join_data_key.lookup_key,
                feature_table_data=feature_table_data,
                feature_table_keys=feature_table_metadata.primary_keys,
                feature_to_output_name=feature_to_output_name,
            )
    return df


def get_feature_lookups_with_full_table_names(
    feature_lookups: List[FeatureLookup], current_catalog: str, current_schema: str
) -> List[FeatureLookup]:
    """
    Takes in a list of FeatureLookups, and returns copies with reformatted table names.
    """
    table_names = {fl.table_name for fl in feature_lookups}
    uc_utils._check_qualified_table_names(table_names)
    uc_utils._verify_all_tables_are_either_in_uc_or_in_hms(
        table_names, current_catalog, current_schema
    )
    standardized_feature_lookups = []
    for fl in feature_lookups:
        fl_copy = copy.deepcopy(fl)
        fl_copy._table_name = uc_utils.get_full_table_name(
            fl_copy.table_name, current_catalog, current_schema
        )
        standardized_feature_lookups.append(fl_copy)
    return standardized_feature_lookups


def augment_training_df_with_computed_features(
    df: DataFrame, computed_features_df: Dict[DataSource, DataFrame]
) -> DataFrame:
    """
    Annotate a training DataFrame with computed features using as-of joins.

    Args:
        df: The training DataFrame to annotate
        computed_features_df: Dictionary mapping DataSource to computed features DataFrame

    Returns:
        DataFrame: The annotated DataFrame with computed features joined
    """
    result_df = df
    for data_source, features_df in computed_features_df.items():
        result_df = _spark_asof_join_features_native(
            labels_df=result_df,
            features_df=features_df,
            primary_keys=data_source.entity_columns,
            timestamp_key=data_source.timeseries_column,
        )
    return result_df
