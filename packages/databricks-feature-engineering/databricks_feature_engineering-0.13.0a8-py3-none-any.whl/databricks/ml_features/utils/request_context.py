from __future__ import (  # This is needed for RequestContext to refer to its own type, as postponed evaluation in py 3.7 requires opt-in
    annotations,
)

import logging
from typing import Optional

import pkg_resources
import yaml
from mlflow.utils import databricks_utils

from databricks.ml_features.constants import (
    STREAMING_TRIGGER_CONTINUOUS,
    STREAMING_TRIGGER_ONCE,
    STREAMING_TRIGGER_PROCESSING_TIME,
)
from databricks.ml_features.version import VERSION

_logger = logging.getLogger(__name__)

# Load in the list of valid default header keys from the headers.yaml bundled resource
constants_yml = pkg_resources.resource_string(__name__, "headers.yaml")
if constants_yml is None or len(constants_yml) == 0:
    raise Exception(
        "Missing headers.yaml package resource.  This indicates a packaging error."
    )
constants = yaml.safe_load(constants_yml)
valid_header_keys = {}
for key in constants.keys():
    valid_header_keys[key] = set(constants.get(key, []))

# Default header key for the feature store client API method that originated this request context
FEATURE_STORE_METHOD_NAME = "feature-store-method-name"
FEATURE_STORE_PYTHON_CLIENT_VERSION = "feature-store-python-client-version"
FEATURE_STORE_PYTHON_WHL_NAME = "feature-store-python-whl-name"
FEATURE_STORE_PYTHON_CLIENT_NAME = "feature-store-python-client-name"

# Other default header keys
CLUSTER_ID = "cluster_id"
NOTEBOOK_ID = "notebook_id"
JOB_ID = "job_id"
JOB_RUN_ID = "job_run_id"
JOB_TYPE = "job_type"

# A special header key for indicating that headers are not sent because they are too large
HEADER_SIZE_EXCEEDED_LIMIT = "header-size-exceeded-limit"

# custom header keys
DATAFRAME_SIZE_IN_BYTES = "dataframe-size-in-bytes"
FEATURE_SPEC_GRAPH_MAP = "feature-spec-graph-map"
IS_PUBLISH_FILTER_CONDITION_SPECIFIED = "is-publish-filter-condition-specified"
IS_STREAMING = "is-streaming"
IS_STREAMING_CHECKPOINT_SPECIFIED = "is-streaming-checkpoint-specified"
IS_TRAINING_SET_LABEL_SPECIFIED = "is-training-set-label-specified"
NUM_ON_DEMAND_FEATURES_LOGGED = "num-on-demand-features-logged"
NUM_LINES_PER_ON_DEMAND_FEATURE = "num-lines-per-on-demand-feature"
NUM_FEATURE_TABLES = "num-feature-tables"
NUM_FEATURES = "num-features"
NUM_FEATURES_OVERRIDDEN = "num-features-overridden"
NUM_FUNCTIONS = "num-functions"
NUM_ON_DEMAND_FEATURES_OVERRIDDEN = "num-on-demand-features-overridden"
NUM_ON_DEMAND_FEATURE_INPUTS_OVERRIDDEN = "num-on-demand-feature-inputs-overridden"
NUM_ROWS = "num-rows"
NUM_TAGS = "num-tags"
PUBLISH_AUTH_TYPE = "publish_auth_type"
STREAMING_TRIGGER = "streaming-trigger"
TOTAL_NUM_FEATURES_IN_TABLE = "total-num-features-in-table"
WRITE_MODE = "write-mode"

DEFAULT_HEADERS = "default_headers"
# Valid header keys and header values for FEATURE_STORE_METHOD_NAME header key.
GET_TABLE = "get_table"
GET_FEATURE_TABLE = "get_feature_table"
CREATE_TABLE = "create_table"
CREATE_FEATURE_SPEC = "create_feature_spec"
GENERATE_FEATURE_SPEC_YAML = "generate_feature_spec_yaml"
UPDATE_FEATURE_SPEC = "update_feature_spec"
DELETE_FEATURE_SPEC = "delete_feature_spec"
CREATE_FEATURE_TABLE = "create_feature_table"
REGISTER_TABLE = "register_table"
PUBLISH_TABLE = "publish_table"
WRITE_TABLE = "write_table"
READ_TABLE = "read_table"
DROP_TABLE = "drop_table"
DROP_ONLINE_TABLE = "drop_online_table"
LOG_CLIENT_EVENT = "log_client_event"
LOG_MODEL = "log_model"
SCORE_BATCH = "score_batch"
CREATE_TRAINING_SET = "create_training_set"
GET_MODEL_SERVING_METADATA = "get_model_serving_metadata"
SET_FEATURE_TABLE_TAG = "set_feature_table_tag"
DELETE_FEATURE_TABLE_TAG = "delete_feature_table_tag"
ADD_DATA_SOURCES = "add_data_sources"
DELETE_DATA_SOURCES = "delete_data_sources"
UPGRADE_WORKSPACE_TABLE = "upgrade_workpace_table"
CREATE_FEATURE = "create_feature"
COMPUTE_FEATURES = "compute_features"
TEST_ONLY_METHOD = "test_only_method"

# python client names
FEATURE_STORE_CLIENT = "FeatureStoreClient"
FEATURE_ENGINEERING_CLIENT = "FeatureEngineeringClient"
# Used to track adoption of mlflow.pyfunc.predict
MLFLOW_CLIENT = "MLflowClient"


def extract_streaming_trigger_header(
    is_streaming: bool, trigger: dict
) -> Optional[str]:
    """
    Extracts a trigger header value for instrumentation from the trigger dict.
    Returns None when is_streaming is False or trigger can not be recognized.

    E.g. {"processingTime": "5 seconds"} -> "processingTime"
    """
    streaming_trigger_header = None
    # only one trigger can be set in Spark
    if is_streaming and len(trigger.keys()) == 1:
        trigger_key = list(trigger.keys())[0]
        # unknown triggers (if Spark in the future adds more trigger types) are ignored here, as the backend validates the value.
        if trigger_key in (
            STREAMING_TRIGGER_CONTINUOUS,
            STREAMING_TRIGGER_ONCE,
            STREAMING_TRIGGER_PROCESSING_TIME,
        ):
            streaming_trigger_header = trigger_key
    return streaming_trigger_header


class RequestContext:

    """
    An object for instrumenting the feature store client usage patterns.  Client methods in the public
    API should create a RequestContext and pass it down the callstack to the catalog client, which will
    add all relevant context to the outgoing requests as HTTP headers.  The catalog service will read the
    headers and record in usage logs.
    """

    # The list of valid header values for the FEATURE_STORE_METHOD_NAME header key
    valid_feature_store_method_names = [
        GET_TABLE,
        GET_FEATURE_TABLE,
        CREATE_TABLE,
        CREATE_FEATURE_SPEC,
        GENERATE_FEATURE_SPEC_YAML,
        UPDATE_FEATURE_SPEC,
        DELETE_FEATURE_SPEC,
        CREATE_FEATURE_TABLE,
        PUBLISH_TABLE,
        WRITE_TABLE,
        READ_TABLE,
        REGISTER_TABLE,
        DROP_TABLE,
        DROP_ONLINE_TABLE,
        LOG_CLIENT_EVENT,
        LOG_MODEL,
        SCORE_BATCH,
        CREATE_TRAINING_SET,
        GET_MODEL_SERVING_METADATA,
        SET_FEATURE_TABLE_TAG,
        DELETE_FEATURE_TABLE_TAG,
        ADD_DATA_SOURCES,
        DELETE_DATA_SOURCES,
        UPGRADE_WORKSPACE_TABLE,
        CREATE_FEATURE,
        COMPUTE_FEATURES,
        TEST_ONLY_METHOD,
    ]

    valid_python_client_names = [
        FEATURE_STORE_CLIENT,
        FEATURE_ENGINEERING_CLIENT,
        MLFLOW_CLIENT,
    ]

    @classmethod
    def with_additional_custom_headers(
        cls, original_request_context: RequestContext, additional_custom_headers: dict
    ):
        """
        Create a copy of the given request context with additional custom headers added.
        Overwriting existing headers is not allowed and causes ValueError.
        """
        feature_store_method_name = original_request_context.get_header(
            FEATURE_STORE_METHOD_NAME
        )
        feature_store_client_name = original_request_context.get_header(
            FEATURE_STORE_PYTHON_CLIENT_NAME
        )
        original_custom_headers = original_request_context.get_custom_headers()
        for k, v in additional_custom_headers.items():
            if k in original_custom_headers and v != original_custom_headers[k]:
                raise ValueError(
                    f"Header {k} exists already and can not be overwritten."
                )

        return cls(
            feature_store_method_name,
            feature_store_client_name,
            {**original_custom_headers, **additional_custom_headers},
            default_headers=original_request_context.get_default_headers(),
        )

    def __init__(
        self,
        feature_store_method_name: str,
        client_name: str,
        custom_headers: dict = None,
        **kwargs,
    ):
        """
        Initializer

        :param feature_store_method_name: The feature store method creating this request context.
        :param custom_headers: The custom headers to be included in this request context. Note that headers
          with None value are not sent to server if using rest_utils.
        """
        if (
            feature_store_method_name
            not in RequestContext.valid_feature_store_method_names
        ):
            raise ValueError(
                f"Invalid feature store method name given: {feature_store_method_name}"
            )
        if client_name not in RequestContext.valid_python_client_names:
            raise ValueError(f"Invalid client name given: {client_name}")

        if "default_headers" in kwargs:
            # A hidden constructor param so that `with_additional_custom_headers` doesn't have to regenerate
            # default args again. Otherwise it risks getting different values for default headers that
            # potentially do not have fixed values (e.g. a potential CREATED_AT header that uses current time),
            # which breaks the "with_xxx" copy semantics.
            # Avoiding regeneration of header values also provides a small performance advantage.
            default_headers = kwargs["default_headers"]
        else:
            default_headers = self._create_default_headers(
                feature_store_method_name, client_name
            )

        if custom_headers is None:
            custom_headers = {}

        # Ensure that no header keys outside of those declared in headers.yaml have snuck into the codebase
        self._validate_headers(
            feature_store_method_name,
            default_headers,
            custom_headers,
            valid_header_keys,
        )

        self._default_headers = default_headers
        self._custom_headers = custom_headers

    def __eq__(self, other):
        """
        Override equality testing to compare the internal state rather than comparing by reference.
        Curently only needed for testing purposes.  If additional state variables are added to this
        object this method will need to be updated accordingly.
        """
        if not isinstance(other, RequestContext):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def _create_default_headers(self, feature_store_method_name, client_name):
        """
        Create the default headers that will be sent with every RPC request from the client.
        """
        default_headers = {
            FEATURE_STORE_METHOD_NAME: feature_store_method_name,
            FEATURE_STORE_PYTHON_CLIENT_VERSION: VERSION,
            # This header will only be set from databricks-feature-engineering > 0.1.3 so we can hardcode it here.
            # FeatureStoreRpcHeaderLoggingHook will resolve the whl name for older whls that don't send this value
            # using the client version.
            FEATURE_STORE_PYTHON_WHL_NAME: "databricks-feature-engineering",
            FEATURE_STORE_PYTHON_CLIENT_NAME: client_name,
        }
        try:
            if databricks_utils.is_in_cluster():
                default_headers[CLUSTER_ID] = databricks_utils.get_cluster_id()
            if databricks_utils.is_in_databricks_notebook():
                default_headers[NOTEBOOK_ID] = databricks_utils.get_notebook_id()
            if databricks_utils.is_in_databricks_job():
                default_headers[JOB_ID] = databricks_utils.get_job_id()
                default_headers[JOB_RUN_ID] = databricks_utils.get_job_run_id()
                default_headers[JOB_TYPE] = databricks_utils.get_job_type()
        except Exception as e:
            _logger.warning(
                "Exeption while adding standard headers, some headers will not be added.",
                exc_info=e,
            )
        return default_headers

    def _validate_headers(
        self,
        feature_store_method_name,
        default_headers,
        custom_headers,
        valid_header_keys,
    ):
        """
        Ensure that all headers are in the list of valid headers expected by the catalog service.
        This prevents any headers being added to the client while forgetting to add to the
        catalog service, since both share the headers.yaml file.
        """
        unknown_header_keys = []
        for key in default_headers.keys():
            if key not in valid_header_keys[DEFAULT_HEADERS]:
                unknown_header_keys.append(key)
        for key in custom_headers.keys():
            if (feature_store_method_name not in valid_header_keys) or (
                key not in valid_header_keys[feature_store_method_name]
            ):
                unknown_header_keys.append(key)
        if len(unknown_header_keys) > 0:
            raise ValueError(
                f'Unknown header key{"s" if len(unknown_header_keys) > 1 else ""}: '
                f'{", ".join(unknown_header_keys)}. Please add to headers.yaml'
            )

    def get_header(self, header_name: str):
        """
        Get the specified header, or return None if there is no corresponding header.
        """
        return self._custom_headers.get(header_name) or self._default_headers.get(
            header_name
        )

    def get_headers(self) -> dict:
        """
        Get the stored headers.
        """
        return {**self._default_headers, **self._custom_headers}

    def get_default_headers(self) -> dict:
        return dict.copy(self._default_headers)

    def get_custom_headers(self) -> dict:
        return dict.copy(self._custom_headers)
