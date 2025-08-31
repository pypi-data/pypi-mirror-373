def detect_coinstalled_clients():
    """
    Co-installation detection. The lookup client has nearly identical code in its version of
    databricks/feature_store/__init__.py.
    """

    # Detect if core client installed
    try:
        from databricks._feature_store_pkg_metadata import _core_client_pkg_metadata

        core_client_installed = True
    except ImportError:
        core_client_installed = False
    except Exception as e:
        print(
            f"Internal Warning: unexpected exception trying to import core client pkg_metadata: {e}"
        )
        core_client_installed = False

    # Detect if lookup client installed
    try:
        from databricks._feature_store_pkg_metadata import _lookup_client_pkg_metadata

        lookup_client_installed = True
    except ImportError:
        lookup_client_installed = False
    except Exception as e:
        print(
            f"Internal Warning: unexpected exception trying to import lookup client pkg_metadata: {e}"
        )
        lookup_client_installed = False

    # If neither client is installed, log a warning because we should never get into this situation.
    if not core_client_installed and not lookup_client_installed:
        print("Internal Warning: no feature store clients detected")

    # If both clients are installed, throw an exception because the earlier installed client will be in a broken
    # state due to having some of its files clobbered by the later installed client.  Note the order
    # of which clients are mentioned is different between clients to indicate which __init__.py emitted this error.
    if core_client_installed and lookup_client_installed:
        raise Exception(
            "The Databricks Feature Store client from databricks-feature-engineering and Databricks Lookup client from databricks-feature-lookup cannot be installed in the "
            "same python environment. Use pip to uninstall both packages, then pip install the package "
            "you intend to use."
        )


detect_coinstalled_clients()

# Support sugar-syntax `from databricks.feature_store import FeatureStoreClient`, etc.
from databricks.feature_store.client import FeatureStoreClient
from databricks.feature_store.decorators import feature_table
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.utils.logging_utils import _configure_feature_store_loggers

_configure_feature_store_loggers(root_module_name=__name__)

__all__ = ["FeatureStoreClient", "feature_table", "FeatureLookup", "FeatureFunction"]
