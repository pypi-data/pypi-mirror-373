from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features.entities.feature_serving_endpoint import EndpointCoreConfig
from databricks.ml_features.utils.feature_utils import (
    format_feature_lookups_and_functions,
)
from databricks.ml_features_common.utils import uc_utils


def validate_endpoint_name_specified(name, legacy_name):
    if name is None and legacy_name is None:
        raise ValueError("name must be specified")
    if name is not None and legacy_name is not None:
        raise ValueError("endpoint_name must not be specified if name is specified")


def format_endpoint_core_config(config: EndpointCoreConfig, _spark_client: SparkClient):
    if config.served_entities is not None:
        full_spec_name = uc_utils.get_full_udf_name(
            config.served_entities.feature_spec_name,
            _spark_client.get_current_catalog(),
            _spark_client.get_current_database(),
        )
        config.served_entities.feature_spec_name = full_spec_name
    else:
        # The following code is processing the deprecated config.servables field.
        config.servables.features = format_feature_lookups_and_functions(
            _spark_client, config.servables.features
        )
    return config


def format_feature_serving_endpoint_name(name, legacy_endpoint_name, _logger):
    validate_endpoint_name_specified(name, legacy_endpoint_name)
    if legacy_endpoint_name is not None:
        _logger.warning("endpoint_name is deprecated in favor of name")
        name = legacy_endpoint_name
    return name
