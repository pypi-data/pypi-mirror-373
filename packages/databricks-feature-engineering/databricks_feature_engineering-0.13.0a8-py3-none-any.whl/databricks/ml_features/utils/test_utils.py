import inspect
import uuid
from typing import Dict, List, Optional

from databricks.ml_features._information_schema_spark_client._information_schema_spark_client import (
    FunctionInfo as UCFunctionInfo,
)
from databricks.ml_features._information_schema_spark_client._information_schema_spark_client import (
    FunctionParameterInfo,
)
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.utils import request_context
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.version import VERSION

# TODO (ML-30526): Move this file to the tests module.

ILLEGAL_TABLE_NAMES = [
    ".table",
    "database.",
    "catalog.database.table.col",
    "table.",
    "a.b.c.d",
    "a.b.",
    ".a.b.c",
    "a.b.c.",
    "..",
    ".a.",
    "..a",
    "",
    "inv/alid",
    "a b.c",
    "\x00.a",
    None,
]
ILLEGAL_1L_NAMES = ["..", "", None, "db.", ".db"]
VALID_UC_CATALOGS = ["prod_catalog", "dev_catalog", "test", "__catalog123__"]
VALID_DEFAULT_HMS_CATALOGS = ["hive_metastore", "spark_catalog"]

VALID_FEATURE_STORE_1L_TABLE_NAMES = [
    "some_table",
    "___table___",
    "table123",
    "_test_table_123_",
]
VALID_FEATURE_STORE_2L_TABLE_NAMES = [
    "db.table",
    "schema.table",
    "_._",
    "a123_def.123_ddd_fff",
    "d@tabase.table",
    "`database.table`",
    "main$database.table",
    "database.tablename@*&!",
]
VALID_FEATURE_STORE_3L_TABLE_NAMES = [
    "dev.schema.table",
    "prod.database.table",
    "hive_metastore.db.table",
    "spark_catalog.schema.table_1",
    "123_abc.456_def.789_ghi",
    "_._._",
    "oltp.main$database.table",
]
DEFAULT_DF_SIZE_IN_BYTES = 123456789


def create_test_feature_table(
    name,
    description,
    primary_keys,
    partition_cols,
    features,
    table_id=str(uuid.uuid4()),
    creation_timestamp=0,
    notebook_producers=None,
    job_producers=None,
    timestamp_keys=None,
    path_data_sources=None,
    table_data_sources=None,
    custom_data_sources=None,
):
    return FeatureTable(
        name=name,
        table_id=table_id,
        description=description,
        primary_keys=primary_keys,
        partition_columns=partition_cols,
        timestamp_keys=timestamp_keys if timestamp_keys is not None else [],
        features=features,
        creation_timestamp=creation_timestamp,
        online_stores=[],
        notebook_producers=notebook_producers if notebook_producers is not None else [],
        job_producers=job_producers if job_producers is not None else [],
        table_data_sources=table_data_sources if table_data_sources is not None else [],
        path_data_sources=path_data_sources if path_data_sources is not None else [],
        custom_data_sources=(
            custom_data_sources if custom_data_sources is not None else []
        ),
    )


def create_test_uc_function_info(
    full_name: str,
    input_params: List[Dict[str, str]],
    routine_definition: Optional[str] = None,
    external_language: Optional[str] = "PYTHON",
):
    """
    input_params using format [{"name": ___, "type_text": ___}, ...]
    """
    return UCFunctionInfo(
        full_name=full_name,
        input_params=map(lambda x: FunctionParameterInfo.from_dict(x), input_params),
        routine_definition=routine_definition,
        external_language=external_language,
    )


def assert_request_context(
    method_calls,
    expected_feature_store_method_name,
    expected_feature_store_python_client_name,
):
    """
    Assert that every method call in the list of mock.method_call objects that is called
    with a RequestContext parameter is the expected feature_client_method_name, the expected
    feature_store_python_client_name, and the current python client version.

    :param method_calls: a list of method calls captured by a mock.
    :param expected_feature_store_method_name: the expected feature store method name in the
    the RequestContext parameter of the captured method calls.
    :param expected_feature_store_python_client_name: the expected name of the client that
    triggers the method call.
    """
    for method_call in method_calls:
        _, positional_args, keyword_args = method_call
        keyword_args_vals = list(keyword_args.values())
        method_params = keyword_args_vals + list(positional_args)
        for method_param in method_params:
            if method_param.__class__ == RequestContext:
                feature_store_method_name = method_param.get_header(
                    request_context.FEATURE_STORE_METHOD_NAME
                )
                assert feature_store_method_name == expected_feature_store_method_name
                feature_store_python_client_name = method_param.get_header(
                    request_context.FEATURE_STORE_PYTHON_CLIENT_NAME
                )
                assert (
                    feature_store_python_client_name
                    == expected_feature_store_python_client_name
                )
                feature_store_version = method_param.get_header(
                    request_context.FEATURE_STORE_PYTHON_CLIENT_VERSION
                )
                assert feature_store_version == VERSION


def create_streaming_req_context_headers(
    is_streaming: bool,
    is_streaming_checkpoint_specified: Optional[bool],
    streaming_trigger: Optional[str],
):
    return {
        request_context.IS_STREAMING: str(is_streaming).lower(),
        request_context.STREAMING_TRIGGER: streaming_trigger,
        request_context.IS_STREAMING_CHECKPOINT_SPECIFIED: (
            None
            if is_streaming_checkpoint_specified is None
            else str(is_streaming_checkpoint_specified).lower()
        ),
    }


def create_publish_table_request_context(
    dataframe_size_in_bytes: Optional[int] = DEFAULT_DF_SIZE_IN_BYTES,
    is_publish_filter_condition_specified: bool = False,
    is_streaming: bool = False,
    is_streaming_checkpoint_specified: Optional[bool] = None,
    num_features: int = 0,
    num_rows: Optional[int] = 10,
    publish_auth_type: str = "role",
    streaming_trigger: Optional[str] = None,
    total_num_features_in_table: int = 0,
    write_mode: str = "merge",
    client_name="FeatureEngineeringClient",
):
    return RequestContext(
        request_context.PUBLISH_TABLE,
        client_name,
        {
            request_context.DATAFRAME_SIZE_IN_BYTES: (
                str(dataframe_size_in_bytes)
                if dataframe_size_in_bytes is not None
                else None
            ),
            request_context.IS_PUBLISH_FILTER_CONDITION_SPECIFIED: str(
                is_publish_filter_condition_specified
            ).lower(),
            request_context.NUM_FEATURES: str(num_features),
            request_context.NUM_ROWS: str(num_rows) if num_rows is not None else None,
            request_context.PUBLISH_AUTH_TYPE: publish_auth_type,
            request_context.TOTAL_NUM_FEATURES_IN_TABLE: str(
                total_num_features_in_table
            ),
            request_context.WRITE_MODE: write_mode,
            **create_streaming_req_context_headers(
                is_streaming, is_streaming_checkpoint_specified, streaming_trigger
            ),
        },
    )


def create_write_table_request_context(
    is_streaming: bool = False,
    is_streaming_checkpoint_specified: Optional[bool] = None,
    num_features: int = 0,
    streaming_trigger: Optional[str] = None,
    total_num_features_in_table: int = 0,
    write_mode: str = "merge",
    client_name: str = "FeatureEngineeringClient",
):
    return RequestContext(
        request_context.WRITE_TABLE,
        client_name,
        {
            request_context.NUM_FEATURES: str(num_features),
            request_context.TOTAL_NUM_FEATURES_IN_TABLE: str(
                total_num_features_in_table
            ),
            request_context.WRITE_MODE: write_mode,
            **create_streaming_req_context_headers(
                is_streaming, is_streaming_checkpoint_specified, streaming_trigger
            ),
        },
    )


def get_all_public_methods(obj, white_list: Optional[List[str]] = None):
    if white_list is None:
        white_list = []
    return map(
        lambda f: f[1],
        filter(
            lambda f: callable(f[1])
            and not f[0].startswith("_")
            and not f[0] in white_list,
            inspect.getmembers(obj),
        ),
    )
