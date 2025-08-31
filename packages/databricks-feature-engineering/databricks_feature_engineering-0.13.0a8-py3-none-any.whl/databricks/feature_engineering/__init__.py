import importlib.metadata


def is_package_installed(package_name):
    try:
        # Attempt to get the distribution of the specified package
        importlib.metadata.version(package_name)
        return True
    except Exception:
        return False


# When one of the proto files (e.g feature_catalog_pb2) is imported from both databricks-feature-store and databricks-feature-engineering
# there will be a type error since the proto file names are the same but contents are slightly different.
# This function is a best effort to catch and surface a better error message.
def duplicate_proto_detection():
    try:
        from databricks.ml_features.api.proto import feature_catalog_pb2
    except TypeError as e:
        if "duplicate file name" in str(e) and is_package_installed(
            "databricks-feature-store"
        ):
            print(
                "An error can occur when importing from both databricks-feature-store "
                "and databricks-feature-engineering. Run '%pip uninstall databricks-feature-store' to uninstall databricks-feature-store, then "
                "run 'dbutils.library.restartPython()' to restart the Python interpreter, and try again. If you would like to use the specific databricks-feature-store version, "
                "use the corresponding Databricks Runtime for Machine Learning version (see https://docs.databricks.com/release-notes/runtime/index.html#feature-engineering-compatibility-matrix) instead."
            )
        raise e


duplicate_proto_detection()

# Inject FeatureEngineeringClient specific things
from databricks.ml_features.utils.logging_utils import _configure_feature_store_loggers

_configure_feature_store_loggers(root_module_name=__name__)

# Support sugar-syntax `from databricks.feature_engineering import FeatureEngineeringClient`, etc.
from databricks.feature_engineering.client import UNSET, FeatureEngineeringClient
from databricks.feature_engineering.entities.aggregation import Aggregation, Window
from databricks.feature_engineering.entities.cron_schedule import CronSchedule
from databricks.feature_engineering.entities.feature_aggregations import (
    FeatureAggregations,
)
from databricks.feature_engineering.entities.feature_function import FeatureFunction
from databricks.feature_engineering.entities.feature_lookup import FeatureLookup
from databricks.feature_engineering.upgrade_client import UpgradeClient
from databricks.ml_features.entities.online_store import DatabricksOnlineStore

__all__ = [
    "FeatureEngineeringClient",
    "Aggregation",
    "Window",
    "CronSchedule",
    "FeatureAggregations",
    "FeatureLookup",
    "FeatureFunction",
    "UpgradeClient",
    "UNSET",
    "DatabricksOnlineStore",
]
