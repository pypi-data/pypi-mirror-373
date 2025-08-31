from datetime import timedelta
from typing import List

from databricks.ml_features.entities.aggregation import Aggregation
from databricks.ml_features.entities.aggregation_function import (
    AGGREGATION_FUNCTION_BY_SHORTHAND,
    AggregationFunction,
)
from databricks.ml_features.entities.feature_aggregations import FeatureAggregations


def get_lookup_key_list(features: FeatureAggregations) -> List[str]:
    if isinstance(features.lookup_key, str):
        return [features.lookup_key]
    else:
        return features.lookup_key


def timedelta_to_sql(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    return f"{total_seconds} SECOND"
