from collections import defaultdict
from typing import List, Optional

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import isnull, when
from pyspark.sql.types import StringType, StructField, StructType

from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class FunctionParameterInfo(_FeatureStoreObject):
    def __init__(self, name: str, type_text: str):
        self._name = name
        self._type_text = type_text

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_text(self) -> str:
        return self._type_text

    @classmethod
    def from_dict(cls, function_parameter_info_json):
        return FunctionParameterInfo(
            function_parameter_info_json["name"],
            function_parameter_info_json["type_text"],
        )


class FunctionInfo(_FeatureStoreObject):
    """
    Helper entity class that exposes properties in GetFunction's response JSON as attributes.
    https://docs.databricks.com/api-explorer/workspace/functions/get

    Note: empty fields (e.g. when 0 input parameters) are not included in the response JSON.
    """

    # Python UDFs have external_language = "Python"
    PYTHON = "Python"

    def __init__(
        self,
        full_name: str,
        input_params: List[FunctionParameterInfo],
        routine_definition: Optional[str],
        external_language: Optional[str],
    ):
        self._full_name = full_name
        self._input_params = input_params
        self._routine_definition = routine_definition
        self._external_language = external_language

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def input_params(self) -> List[FunctionParameterInfo]:
        return self._input_params

    @property
    def routine_definition(self) -> Optional[str]:
        return self._routine_definition

    @property
    def external_language(self) -> Optional[str]:
        """
        Field is None if language is SQL (not an external language).
        """
        return self._external_language

    @classmethod
    def from_dict(cls, function_info_json):
        input_params = function_info_json.get("input_params", {}).get("parameters", [])
        return FunctionInfo(
            full_name=function_info_json["full_name"],
            input_params=[FunctionParameterInfo.from_dict(p) for p in input_params],
            routine_definition=function_info_json.get("routine_definition", None),
            external_language=function_info_json.get("external_language", None),
        )


class InformationSchemaSparkClient:
    """
    Internal client to retrieve Unity Catalog metadata from system.information_schema.
    https://docs.databricks.com/sql/language-manual/sql-ref-information-schema.html
    """

    def __init__(self, spark_client: SparkClient):
        self._spark_client = spark_client

    def _get_routines_with_parameters(self, full_routine_names: List[str]) -> DataFrame:
        """
        Retrieve the routines with their parameters from information_schema.routines, information_schema.parameters.
        Return DataFrame only contains routines that 1. exist and 2. the caller has GetFunction permission on.

        Note: The returned DataFrame contains the cartesian product of routines and parameters.
        For efficiency, routines table columns are only present in the first row for each routine.
        """
        routine_name_schema = StructType(
            [
                StructField("specific_catalog", StringType(), False),
                StructField("specific_schema", StringType(), False),
                StructField("specific_name", StringType(), False),
            ]
        )
        routine_names_df = self._spark_client.createDataFrame(
            [full_routine_name.split(".") for full_routine_name in full_routine_names],
            routine_name_schema,
        )
        routines_table = self._spark_client.read_table(
            "system.information_schema.routines"
        )
        parameters_table = self._spark_client.read_table(
            "system.information_schema.parameters"
        )

        # Inner join routines table to filter out non-existent routines.
        # Left join parameters as routines may have no parameters.
        full_routines_with_parameters_df = routine_names_df.join(
            routines_table, on=routine_names_df.columns, how="inner"
        ).join(parameters_table, on=routine_names_df.columns, how="left")

        # Return only relevant metadata from information_schema, sorted by routine name + parameter order.
        # For efficiency, only preserve routine column values in the first of each routine's result rows.
        # The first row will have parameter.ordinal_value is None (no parameters) or equals 0 (first parameter).
        def select_if_first_row(col: Column) -> Column:
            return when(
                isnull(parameters_table.ordinal_position)
                | (parameters_table.ordinal_position == 0),
                col,
            ).otherwise(None)

        return full_routines_with_parameters_df.select(
            routine_names_df.columns
            + [
                select_if_first_row(routines_table.routine_definition).alias(
                    "routine_definition"
                ),
                select_if_first_row(routines_table.external_language).alias(
                    "external_language"
                ),
                parameters_table.ordinal_position,
                parameters_table.parameter_name,
                parameters_table.full_data_type,
            ]
        ).sort(routine_names_df.columns + [parameters_table.ordinal_position])

    def get_functions(self, full_function_names: List[str]) -> List[FunctionInfo]:
        """
        Retrieves and maps Unity Catalog functions' metadata as FunctionInfos.
        """
        # Avoid unnecessary Spark calls and return if empty.
        if not full_function_names:
            return []

        # Collect dict of routine name -> DataFrame rows describing the routine.
        routines_with_parameters_df = self._get_routines_with_parameters(
            full_routine_names=full_function_names
        )
        routine_infos = defaultdict(list)
        for r in routines_with_parameters_df.collect():
            routine_name = f"{r.specific_catalog}.{r.specific_schema}.{r.specific_name}"
            routine_infos[routine_name].append(r)

        # Mock GetFunction DNE error, since information_schema does not throw.
        for function_name in full_function_names:
            if not function_name in routine_infos:
                raise ValueError(f"Function '{function_name}' does not exist.")

        # Map routine_infos into FunctionInfos.
        function_infos = []
        for function_name in full_function_names:
            routine_info = routine_infos[function_name][0]
            input_params = [
                FunctionParameterInfo(name=p.parameter_name, type_text=p.full_data_type)
                for p in routine_infos[function_name]
                if p.ordinal_position is not None
            ]
            function_infos.append(
                FunctionInfo(
                    full_name=function_name,
                    input_params=input_params,
                    routine_definition=routine_info.routine_definition,
                    external_language=routine_info.external_language,
                )
            )
        return function_infos
