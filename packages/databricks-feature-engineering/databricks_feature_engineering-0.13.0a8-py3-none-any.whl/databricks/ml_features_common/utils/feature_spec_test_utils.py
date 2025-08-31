from typing import List

from databricks.ml_features_common.entities.column_info import ColumnInfo
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.entities.feature_table_info import FeatureTableInfo
from databricks.ml_features_common.entities.function_info import FunctionInfo
from databricks.ml_features_common.entities.on_demand_column_info import (
    OnDemandColumnInfo,
)

# TODO (ML-30526): Move this file to the tests module.

TEST_WORKSPACE_ID = 123


def get_test_table_infos_from_column_infos(column_infos: List[ColumnInfo]):
    table_infos = []
    unique_table_names = set(
        [
            column_info.info.table_name
            for column_info in column_infos
            if isinstance(column_info, ColumnInfo)
            and isinstance(column_info.info, FeatureColumnInfo)
        ]
    )
    for table_name in unique_table_names:
        table_id = table_name + "123456"
        table_infos.append(FeatureTableInfo(table_name=table_name, table_id=table_id))
    return table_infos


def get_test_function_infos_from_column_infos(column_infos: List[ColumnInfo]):
    function_infos = []
    unique_udf_names = set(
        [
            column_info.info.udf_name
            for column_info in column_infos
            if isinstance(column_info, ColumnInfo)
            and isinstance(column_info.info, OnDemandColumnInfo)
        ]
    )
    for udf_name in unique_udf_names:
        function_infos.append(FunctionInfo(udf_name=udf_name))
    return function_infos


def create_test_feature_spec(
    column_infos: List[ColumnInfo],
    table_infos: List[FeatureTableInfo] = None,
    function_infos: List[FunctionInfo] = None,
    workspace_id: int = TEST_WORKSPACE_ID,
):
    if table_infos is None:
        table_infos = get_test_table_infos_from_column_infos(column_infos)
    if function_infos is None:
        function_infos = get_test_function_infos_from_column_infos(column_infos)
    return FeatureSpec(
        column_infos=column_infos,
        table_infos=table_infos,
        function_infos=function_infos,
        workspace_id=workspace_id,
        feature_store_client_version="test0",
        serialization_version=FeatureSpec.SERIALIZATION_VERSION_NUMBER,
    )
