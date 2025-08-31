import logging
from collections import defaultdict
from typing import Dict, List, Optional, Set

from pyspark.sql import DataFrame

from databricks.ml_features._information_schema_spark_client._information_schema_spark_client import (
    FunctionInfo as UCFunctionInfo,
)
from databricks.ml_features.constants import _WARN
from databricks.ml_features.entities.data_type import DataType
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.entities.materialized_feature import MaterializedFeature
from databricks.ml_features.utils import schema_utils, utils, validation_utils
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.version import VERSION
from databricks.ml_features_common.entities.column_info import ColumnInfo
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.entities.feature_table_info import FeatureTableInfo
from databricks.ml_features_common.entities.function_info import FunctionInfo
from databricks.ml_features_common.entities.on_demand_column_info import (
    OnDemandColumnInfo,
)
from databricks.ml_features_common.entities.source_data_column_info import (
    SourceDataColumnInfo,
)
from databricks.ml_features_common.utils import uc_utils, utils_common
from databricks.ml_features_common.utils.feature_spec_utils import (
    assign_topological_ordering,
)

_logger = logging.getLogger(__name__)

MAX_FEATURE_FUNCTIONS = 100


def get_features_for_tables(
    catalog_client, req_context: RequestContext, table_names: Set[str]
) -> Dict[str, List[MaterializedFeature]]:
    """
    Lookup features from the feature catalog for all table_names, return a dictionary of tablename -> list of features.
    """
    return {
        table_name: catalog_client.get_features(table_name, req_context)
        for table_name in table_names
    }


def get_feature_table_metadata_for_tables(
    catalog_client,
    catalog_client_helper,
    req_context: RequestContext,
    table_names: Set[str],
) -> Dict[str, FeatureTable]:
    """
    Lookup FeatureTable metadata from the feature catalog for all table_names, return a dictionary of tablename -> FeatureTable.
    """
    feature_table_metadata = {}
    non_uc_online_stores = catalog_client.get_online_stores(
        [
            table_name
            for table_name in table_names
            if not uc_utils.is_uc_entity(table_name)
        ],
        req_context,
    )
    for table_name in table_names:
        if uc_utils.is_uc_entity(table_name):
            feature_table_metadata[
                table_name
            ] = catalog_client_helper.get_feature_table_from_uc_and_online_store_from_fs(
                table_name, req_context
            )
        else:
            feature_table_metadata[table_name] = catalog_client.get_feature_table(
                table_name, req_context
            )
            feature_table_metadata[table_name].online_stores = non_uc_online_stores[
                table_name
            ]
    return feature_table_metadata


def explode_feature_lookups(
    feature_lookups: List[FeatureLookup],
    feature_table_features_map: Dict[str, List[MaterializedFeature]],
    feature_table_metadata_map: Dict[str, FeatureTable],
) -> List[FeatureColumnInfo]:
    """
    Explode FeatureLookups and collect into FeatureColumnInfos. A FeatureLookup may explode into either:
    1. A single FeatureColumnInfo, in the case where only a single feature name is specified.
    2. Multiple FeatureColumnInfos, in the cases where either multiple or all feature names are specified.

    When all features are specified in a FeatureLookup (feature_names is None),
    FeatureColumnInfos will be created for all features except primary and timestamp keys.
    The order of FeatureColumnInfos returned will be the same as the order returned by GetFeatures:
    1. All partition keys that are not primary keys, in the partition key order.
    2. All other non-key features in alphabetical order.
    """
    feature_column_infos = []
    for feature_lookup in feature_lookups:
        feature_column_infos_for_feature_lookup = _explode_feature_lookup(
            feature_lookup=feature_lookup,
            features=feature_table_features_map[feature_lookup.table_name],
            feature_table=feature_table_metadata_map[feature_lookup.table_name],
        )
        feature_column_infos += feature_column_infos_for_feature_lookup
    return feature_column_infos


def _explode_feature_lookup(
    feature_lookup: FeatureLookup,
    features: List[MaterializedFeature],
    feature_table: FeatureTable,
) -> List[FeatureColumnInfo]:
    feature_names = []
    if feature_lookup._get_feature_names():
        # If the user explicitly passed in a feature name or list of feature names, use that
        feature_names.extend(feature_lookup._get_feature_names())
    else:
        # Otherwise assume the user wants all columns in the feature table
        keys = {*feature_table.primary_keys, *feature_table.timestamp_keys}
        feature_names.extend(
            [feature.name for feature in features if feature.name not in keys]
        )

    return [
        FeatureColumnInfo(
            table_name=feature_lookup.table_name,
            feature_name=feature_name,
            lookup_key=utils.as_list(feature_lookup.lookup_key),
            output_name=(feature_lookup._get_output_name(feature_name)),
            timestamp_lookup_key=utils.as_list(
                feature_lookup.timestamp_lookup_key, default=[]
            ),
        )
        for feature_name in feature_names
    ]


def load_feature_data_for_tables(
    spark_client, table_names: Set[str]
) -> Dict[str, DataFrame]:
    """
    Load feature DataFrame objects for all table_names, return a dictionary of tablename -> DataFrame.
    """
    return {
        table_name: spark_client.read_table(table_name) for table_name in table_names
    }


def _validate_and_convert_lookback_windows(
    feature_lookups: List[FeatureLookup],
) -> Dict[str, Optional[float]]:
    """
    Gets lookback_window values from all feature_lookups, validates that lookback_window values are consistent per feature table,
    converts the lookback window into total seconds, and returns a dictionary of tablename -> lookback_window values. In the
    case where lookback_window is not defined, the key value mapping will be "feature_table_name" -> None.
    """
    table_lookback_windows_map = defaultdict(set)
    for fl in feature_lookups:
        table_lookback_windows_map[fl.table_name].add(fl.lookback_window)

    for table_name, lookback_windows in table_lookback_windows_map.items():
        if len(set(lookback_windows)) > 1:
            if None in lookback_windows:
                raise ValueError(
                    f"lookback_window values must be consistently defined per feature table. '{table_name}' has "
                    f"missing lookback_window values: {lookback_windows}."
                )
            else:
                raise ValueError(
                    f"Only one value for lookback_window can be defined per feature table. '{table_name}' has "
                    f"conflicting lookback_window values: {lookback_windows}."
                )

    # convert lookback windows to seconds
    for table_name, lookback_windows in table_lookback_windows_map.items():
        # Get the only element from a single member set
        window = next(iter(lookback_windows))
        table_lookback_windows_map[table_name] = (
            window.total_seconds() if window is not None else None
        )

    return table_lookback_windows_map


def validate_feature_column_infos_data(
    spark_client_helper,
    feature_column_infos: List[FeatureColumnInfo],
    features_by_table: Dict[str, List[MaterializedFeature]],
    feature_table_data_map: Dict[str, DataFrame],
):
    """
    Validates required FeatureLookup data. Checks:
    1. Feature tables exist in Delta.
    2. Feature data types match in Delta and Feature Catalog.
    """
    table_to_features = defaultdict(list)
    for fci in feature_column_infos:
        table_to_features[fci.table_name].append(fci.feature_name)

    for table_name, features_in_spec in table_to_features.items():
        spark_client_helper.check_feature_table_exists(table_name)

        catalog_features = features_by_table[table_name]
        feature_table_data = feature_table_data_map[table_name]
        catalog_schema = {
            feature.name: feature.data_type for feature in catalog_features
        }
        delta_schema = {
            feature.name: DataType.spark_type_to_string(feature.dataType)
            for feature in feature_table_data.schema
        }

        for feature_name in features_in_spec:
            if feature_name not in catalog_schema:
                raise ValueError(
                    f"Unable to find feature '{feature_name}' from feature table '{table_name}' in Feature Catalog."
                )
            if feature_name not in delta_schema:
                raise ValueError(
                    f"Unable to find feature '{feature_name}' from feature table '{table_name}' in Delta."
                )
            if catalog_schema[feature_name] != delta_schema[feature_name]:
                raise ValueError(
                    f"Expected type of feature '{feature_name}' from feature table '{table_name}' "
                    f"to be equivalent in Feature Catalog and Delta. "
                    f"Feature has type '{catalog_schema[feature_name]}' in Feature Catalog and "
                    f"'{delta_schema[feature_name]}' in Delta."
                )

        # Warn if mismatch in other features in feature table
        if not schema_utils.catalog_matches_delta_schema(
            catalog_features, feature_table_data.schema
        ):
            schema_utils.log_catalog_schema_not_match_delta_schema(
                catalog_features,
                feature_table_data.schema,
                level=_WARN,
            )


def verify_df_and_labels(
    df: DataFrame,
    label_names: List[str],
    exclude_columns: List[str],
):
    # Verify DataFrame type and column uniqueness
    validation_utils.check_dataframe_type(df)
    utils_common.validate_strings_unique(
        df.columns, "Found duplicate DataFrame column names {}."
    )

    # Validate label_names, exclude_columns are unique
    utils_common.validate_strings_unique(label_names, "Found duplicate label names {}.")
    # Verify that label_names is in DataFrame and not in exclude_columns
    for label_name in label_names:
        if label_name not in df.columns:
            raise ValueError(f"Label column '{label_name}' was not found in DataFrame")
        if label_name in exclude_columns:
            raise ValueError(f"Label column '{label_name}' cannot be excluded")


def get_uc_function_infos(
    information_schema_spark_client, udf_names: Set[str]
) -> Dict[str, UCFunctionInfo]:
    # Note: Only GetFunction ACLs are required here. ExecuteFunction ACL will be checked at SQL execution.
    function_infos = information_schema_spark_client.get_functions(list(udf_names))
    return {function_info.full_name: function_info for function_info in function_infos}


def _validate_on_demand_column_info_udfs(
    on_demand_column_infos: List[OnDemandColumnInfo],
    uc_function_infos: Dict[str, UCFunctionInfo],
):
    """
    Validates OnDemandColumnInfo UDFs can be applied as on-demand features. Checks:
    1. UDF is defined in Python.
    2. UDF input parameters are consistent with its input bindings.

    Note: Provided UC FunctionInfos not required by OnDemandColumnInfos are not validated.
    """
    for odci in on_demand_column_infos:
        function_info = uc_function_infos[odci.udf_name]
        if function_info.external_language != UCFunctionInfo.PYTHON:
            raise ValueError(
                f"FeatureFunction UDF '{odci.udf_name}' is not a Python UDF. Only Python UDFs are supported."
            )

        udf_input_params = [p.name for p in function_info.input_params]
        if odci.input_bindings.keys() != set(udf_input_params):
            raise ValueError(
                f"FeatureFunction UDF '{odci.udf_name}' input parameters {udf_input_params} "
                f"do not match input bindings {odci.input_bindings}."
            )


class _FeatureTableMetadata:
    def __init__(
        self,
        feature_table_features_map: Dict[str, List[MaterializedFeature]],
        feature_table_metadata_map: Dict[str, FeatureTable],
        feature_table_data_map: Dict[str, DataFrame],
    ):
        self.feature_table_features_map = feature_table_features_map
        self.feature_table_metadata_map = feature_table_metadata_map
        self.feature_table_data_map = feature_table_data_map


def warn_if_non_photon_for_native_spark(use_native_spark, spark_client):
    if use_native_spark and not spark_client.is_photon_cluster():
        _logger.warning(
            "Native spark join is significantly more performant on Photon-enabled clusters. Consider "
            "switching to a Photon-enabled cluster if performance is an issue."
        )


def get_table_metadata(
    catalog_client, catalog_client_helper, spark_client, table_names, req_context
):
    # Retrieve feature table metadata and Delta table
    feature_table_features_map: Dict[
        str, List[MaterializedFeature]
    ] = get_features_for_tables(catalog_client, req_context, table_names=table_names)
    feature_table_metadata_map: Dict[
        str, FeatureTable
    ] = get_feature_table_metadata_for_tables(
        catalog_client, catalog_client_helper, req_context, table_names=table_names
    )
    feature_table_data_map: Dict[str, DataFrame] = load_feature_data_for_tables(
        spark_client, table_names=table_names
    )

    return _FeatureTableMetadata(
        feature_table_features_map,
        feature_table_metadata_map,
        feature_table_data_map,
    )


class _ColumnInfos:
    def __init__(
        self,
        source_data_column_infos: List[SourceDataColumnInfo],
        feature_column_infos: List[FeatureColumnInfo],
        on_demand_column_infos: List[OnDemandColumnInfo],
    ):
        self.source_data_column_infos = source_data_column_infos
        self.feature_column_infos = feature_column_infos
        self.on_demand_column_infos = on_demand_column_infos


def get_column_infos(
    feature_lookups: List[FeatureLookup],
    feature_functions: List[FeatureFunction],
    ft_metadata: _FeatureTableMetadata,
    df_columns: List[str] = [],
    label_names: List[str] = [],
) -> _ColumnInfos:
    # Collect `List[SourceDataColumnInfo]`
    source_data_column_infos: List[SourceDataColumnInfo] = [
        SourceDataColumnInfo(col) for col in df_columns if col not in label_names
    ]

    # Collect `List[FeatureColumnInfo]`
    feature_column_infos: List[FeatureColumnInfo] = (
        explode_feature_lookups(
            feature_lookups,
            ft_metadata.feature_table_features_map,
            ft_metadata.feature_table_metadata_map,
        )
        if feature_lookups
        else []
    )

    # Collect `List[OnDemandColumnInfo]`
    on_demand_column_infos = (
        [
            OnDemandColumnInfo(
                udf_name=feature_function.udf_name,
                input_bindings=feature_function.input_bindings,
                output_name=feature_function.output_name,
            )
            for feature_function in feature_functions
        ]
        if feature_functions
        else []
    )
    return _ColumnInfos(
        source_data_column_infos, feature_column_infos, on_demand_column_infos
    )


def validate_column_infos(
    spark_client_helper,
    information_schema_spark_client,
    ft_metadata,
    source_column_infos,
    feature_column_infos,
    on_demand_column_infos,
    label_names=[],
):
    source_data_names = [sdci.name for sdci in source_column_infos]

    # Verify features have unique output names
    feature_output_names = [fci.output_name for fci in feature_column_infos]
    utils_common.validate_strings_unique(
        feature_output_names, "Found duplicate feature output names {}."
    )

    # Verify labels do not collide with feature output names
    for label_name in label_names:
        if label_name in feature_output_names:
            raise ValueError(
                f"Feature cannot have same output name as label '{label_name}'."
            )

    # Verify that FeatureLookup output names do not conflict with source data names
    feature_conflicts = [
        name for name in feature_output_names if name in source_data_names
    ]
    if len(feature_conflicts) > 0:
        feature_conflicts_str = ", ".join([f"'{name}'" for name in feature_conflicts])
        raise ValueError(
            f"DataFrame contains column names that match feature output names specified"
            f" in FeatureLookups: {feature_conflicts_str}. Either remove these columns"
            f" from the DataFrame or FeatureLookups."
        )

    # Validate FeatureLookup data exists (including for columns that will be excluded).
    validate_feature_column_infos_data(
        spark_client_helper,
        feature_column_infos,
        ft_metadata.feature_table_features_map,
        ft_metadata.feature_table_data_map,
    )

    on_demand_input_names = utils_common.get_unique_list_order(
        [
            input_name
            for odci in on_demand_column_infos
            for input_name in odci.input_bindings.values()
        ]
    )
    on_demand_output_names = [odci.output_name for odci in on_demand_column_infos]

    # Verify on-demand features have unique output names
    utils_common.validate_strings_unique(
        on_demand_output_names, "Found duplicate on-demand feature output names {}."
    )

    # Verify labels do not collide with on-demand output names
    for label_name in label_names:
        if label_name in on_demand_output_names:
            raise ValueError(
                f"On-demand feature cannot have same output name as label '{label_name}'."
            )

    # Verify on-demand feature output names do not conflict with source data or feature output names
    source_data_and_feature_output_names = set(source_data_names + feature_output_names)
    on_demand_conflicts = [
        name
        for name in on_demand_output_names
        if name in source_data_and_feature_output_names
    ]
    if len(on_demand_conflicts) > 0:
        conflicting_on_demand_feature_names = ", ".join(
            f"'{name}'" for name in on_demand_conflicts
        )
        raise ValueError(
            f"FeatureFunctions contains output names that match either DataFrame column names "
            f"or feature output names specified in FeatureLookups: {conflicting_on_demand_feature_names}. "
            f"Either remove these columns from the DataFrame, FeatureLookups, or FeatureFunctions."
        )

    # Validate on-demand and feature inputs exist in either source data or feature or function
    # outputs from previous levels
    all_output_names = source_data_and_feature_output_names.union(
        on_demand_output_names
    )
    missing_on_demand_inputs = set(on_demand_input_names).difference(all_output_names)
    if len(missing_on_demand_inputs) > 0:
        missing_on_demand_inputs_names = ", ".join(
            [f"'{name}'" for name in sorted(missing_on_demand_inputs)]
        )
        raise ValueError(
            f"Could not find input binding columns {missing_on_demand_inputs_names} required "
            "by FeatureFunctions."
        )

    feature_input_names = utils_common.get_unique_list_order(
        [input_name for fci in feature_column_infos for input_name in fci.lookup_key]
    )
    # Validate feature inputs exist in either source data or feature or function outputs
    missing_lookup_inputs = set(feature_input_names).difference(all_output_names)
    if len(missing_lookup_inputs) > 0:
        missing_input_names = ", ".join(
            [f"'{name}'" for name in sorted(missing_lookup_inputs)]
        )
        raise ValueError(
            f"Could not find lookup key columns {missing_input_names} required by "
            "FeatureLookups."
        )

    uc_function_infos = get_uc_function_infos(
        information_schema_spark_client,
        {odci.udf_name for odci in on_demand_column_infos},
    )
    # Validate FeatureFunctions UDFs (including for columns that will be excluded).
    _validate_on_demand_column_info_udfs(
        on_demand_column_infos=on_demand_column_infos,
        uc_function_infos=uc_function_infos,
    )


def build_feature_spec(
    feature_lookups,
    ft_metadata,
    all_column_infos,
    exclude_columns,
    workspace_id,
):
    # The order of ColumnInfos in feature_spec.yaml should be:
    # 1. SourceDataColumnInfos: non-label and non-excluded columns from the input DataFrame
    # 2. FeatureColumnInfos: features retrieved through FeatureLookups
    # 3. OnDemandColumnInfos: features created by FeatureFunctions
    column_infos = [
        ColumnInfo(info=info, include=info.output_name not in exclude_columns)
        for info in all_column_infos.source_data_column_infos
        + all_column_infos.feature_column_infos
        + all_column_infos.on_demand_column_infos
    ]
    # Excluded columns that are on-demand inputs or feature lookup keys
    # should still be in feature_spec.yaml with include=False.
    on_demand_input_names = utils_common.get_unique_list_order(
        [
            input_name
            for odci in all_column_infos.on_demand_column_infos
            for input_name in odci.input_bindings.values()
        ]
    )
    lookup_keys_and_on_demand_inputs = set(on_demand_input_names)
    for fci in all_column_infos.feature_column_infos:
        lookup_keys_and_on_demand_inputs.update(fci.lookup_key)

    column_infos = [
        ci
        for ci in column_infos
        if ci.include or ci.output_name in lookup_keys_and_on_demand_inputs
    ]

    # Sort table_infos by table_name, function_infos by udf_name, so they appear sorted in feature_spec.yaml
    # Exclude unnecessary table_infos, function_infos from the FeatureSpec. When a FeatureLookup or FeatureFunction
    # output feature is excluded, the underlying table or UDF is not required in the FeatureSpec.
    consumed_table_names = [
        ci.info.table_name
        for ci in column_infos
        if isinstance(ci.info, FeatureColumnInfo)
    ]
    consumed_table_names = sorted(set(consumed_table_names))
    consumed_udf_names = [
        ci.info.udf_name
        for ci in column_infos
        if isinstance(ci.info, OnDemandColumnInfo)
    ]
    consumed_udf_names = sorted(set(consumed_udf_names))

    # Collect lookback windows
    table_lookback_window_map = _validate_and_convert_lookback_windows(feature_lookups)

    table_infos = [
        FeatureTableInfo(
            table_name=table_name,
            table_id=ft_metadata.feature_table_metadata_map[table_name].table_id,
            lookback_window=table_lookback_window_map[table_name],
        )
        for table_name in consumed_table_names
    ]
    function_infos = [
        FunctionInfo(udf_name=udf_name) for udf_name in consumed_udf_names
    ]

    # Build FeatureSpec
    feature_spec = FeatureSpec(
        column_infos=assign_topological_ordering(
            column_infos=column_infos,
        ),
        table_infos=table_infos,
        function_infos=function_infos,
        workspace_id=workspace_id,
        feature_store_client_version=VERSION,
        serialization_version=FeatureSpec.SERIALIZATION_VERSION_NUMBER,
    )

    return feature_spec


def add_inferred_source_columns(column_infos: _ColumnInfos) -> _ColumnInfos:
    """
    Automatically infers and adds source columns that are required as inputs but weren't explicitly provided.

    This function identifies columns that are required as inputs for feature lookups or on-demand functions
    but don't exist in the current set of output columns. These missing columns must come from the source
    DataFrame or the input request when FeatureSpec in feaure serving endpoints.

    Example: If a feature lookup uses 'user_id' as a lookup key, but 'user_id' isn't produced by any
    feature lookup or function, the it **must** be present in the source DataFrame or online request.
    """

    # Collect all column names used as inputs for on-demand functions (UDFs)
    # These are the columns that UDFs expect as parameters
    on_demand_input_names = utils_common.get_unique_list_order(
        [
            input_name
            for odci in column_infos.on_demand_column_infos
            for input_name in odci.input_bindings.values()  # input_bindings maps UDF params to column names
        ]
    )
    # Collect all column names produced by on-demand functions
    on_demand_output_names = [
        odci.output_name for odci in column_infos.on_demand_column_infos
    ]

    # Collect all column names used as lookup keys for feature lookups
    # These are the join keys needed to fetch features from feature tables
    feature_input_names = utils_common.get_unique_list_order(
        [
            input_name
            for fci in column_infos.feature_column_infos
            for input_name in fci.lookup_key  # lookup_key is a list of column names used for joining
        ]
    )
    # Collect all feature column names produced as outputs of feature lookups (from feature tables)
    feature_output_names = [
        fci.output_name for fci in column_infos.feature_column_infos
    ]

    # Combine all output column names (features + on-demand)
    # These are columns that will be available after all transformations
    all_output_names = feature_output_names + on_demand_output_names

    # Find lookup keys that aren't produced by any feature or function
    # These must come from the source DataFrame or online request
    missing_lookup_inputs = [
        feature_input_name
        for feature_input_name in feature_input_names
        if feature_input_name not in all_output_names
    ]
    # Find on-demand function inputs that aren't produced by any feature or function
    # These also must come from the source DataFrame
    missing_on_demand_inputs = [
        on_demand_input_name
        for on_demand_input_name in on_demand_input_names
        if on_demand_input_name not in all_output_names
    ]

    # Combine all missing inputs (removing duplicates while preserving order)
    inferred_inputs = utils_common.get_unique_list_order(
        missing_lookup_inputs + missing_on_demand_inputs
    )
    # Create SourceDataColumnInfo objects for each inferred input
    source_data_column_infos = [SourceDataColumnInfo(col) for col in inferred_inputs]

    # Return updated ColumnInfos with the inferred source columns added
    return _ColumnInfos(
        source_data_column_infos=column_infos.source_data_column_infos
        + source_data_column_infos,  # Append inferred columns to existing source columns
        feature_column_infos=column_infos.feature_column_infos,
        on_demand_column_infos=column_infos.on_demand_column_infos,
    )
