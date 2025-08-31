from typing import List, Union

from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.utils.feature_lookup_utils import (
    get_feature_lookups_with_full_table_names,
)
from databricks.ml_features.utils.on_demand_utils import (
    get_feature_functions_with_full_udf_names,
)


def format_feature_lookups_and_functions(
    _spark_client: SparkClient, features: List[Union[FeatureLookup, FeatureFunction]]
):
    fl_idx = []
    ff_idx = []
    feature_lookups = []
    feature_functions = []
    for idx, feature in enumerate(features):
        if isinstance(feature, FeatureLookup):
            fl_idx.append(idx)
            feature_lookups.append(feature)
        elif isinstance(feature, FeatureFunction):
            ff_idx.append(idx)
            feature_functions.append(feature)
        else:
            raise ValueError(
                f"Expected a list of FeatureLookups for 'feature_lookups', but received type '{type(feature)}'."
            )

    # FeatureLookups and FeatureFunctions must have fully qualified table, UDF names
    feature_lookups = get_feature_lookups_with_full_table_names(
        feature_lookups,
        _spark_client.get_current_catalog(),
        _spark_client.get_current_database(),
    )
    feature_functions = get_feature_functions_with_full_udf_names(
        feature_functions,
        _spark_client.get_current_catalog(),
        _spark_client.get_current_database(),
    )

    # Restore original order of FeatureLookups, FeatureFunctions. Copy to avoid mutating original list.
    features = features.copy()
    for idx, feature in zip(fl_idx + ff_idx, feature_lookups + feature_functions):
        features[idx] = feature

    return features
