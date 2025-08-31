import json
import re

from pyspark.sql.types import ArrayType, DataType, DecimalType, MapType, StructType

from databricks.ml_features_common.entities.data_type import DataType as _DataType


class DataType(_DataType):
    """Inherits from DataType in feature_store_common to add support for Spark DataType."""

    _FIXED_DECIMAL = re.compile("decimal\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)")

    @classmethod
    def from_spark_type(cls, spark_type):
        return cls.from_string(spark_type.typeName())

    @classmethod
    def spark_type_to_string(cls, spark_type):
        return DataType.to_string(DataType.from_spark_type(spark_type))

    @classmethod
    def top_level_type_supported(cls, spark_type: DataType) -> bool:
        """
        Checks whether the provided Spark data type is supported by Feature Store, only considering
        the top-level type for nested data types.

        Details on nested types:
          ArrayType: The elementType is not checked. Will return True.
          MapType: The keyType and valueType are not checked. Will return True.
          StructType: The struct fieds are not checked. Will return True.
        """
        cls.init()
        return spark_type.typeName().upper() in cls._STRING_TO_ENUM

    @classmethod
    def to_complex_spark_type(cls, json_value):
        """
        Constructs a complex Spark DataType from its compact JSON representation.

        Examples:
            - Input: '"decimal(1,2)"'
              Output: DecimalType(1,2)
            - Input: '{"containsNull":false,"elementType":"integer","type":"array"}'
              Output: ArrayType(IntegerType,false)
            - Input: '{"keyType":"integer","type":"map","valueContainsNull":True,"valueType":"integer"}'
              Output: MapType(IntegerType,IntegerType,true)
        """
        if not json_value:
            raise ValueError("Empty JSON value cannot be converted to Spark DataType")

        json_data = json.loads(json_value)
        if not isinstance(json_data, dict):
            # DecimalType does not have fromJson() method
            if json_value == "decimal":
                return DecimalType()
            if cls._FIXED_DECIMAL.match(json_data):
                m = cls._FIXED_DECIMAL.match(json_data)
                return DecimalType(int(m.group(1)), int(m.group(2)))

        if json_data["type"].upper() == cls.to_string(cls.ARRAY):
            return ArrayType.fromJson(json_data)

        if json_data["type"].upper() == cls.to_string(cls.MAP):
            return MapType.fromJson(json_data)

        if json_data["type"].upper() == cls.to_string(cls.STRUCT):
            return StructType.fromJson(json_data)

        else:
            raise ValueError(
                f"Spark type {json_data['type']} cannot be converted to a complex Spark DataType"
            )

    @classmethod
    def from_spark_simple_name(cls, spark_simple_name: str) -> "DataType":
        """
        Converts a Spark simple name to a DataType enum value.

        :param spark_simple_name: The simple name of the Spark data type.
        :return: The corresponding DataType enum value.
        """
        if not spark_simple_name:
            raise ValueError("Spark simple name is empty")
        spark_type_name = spark_simple_name

        # some spark types have overrided simple names
        if spark_type_name == "int":
            spark_type_name = "integer"
        elif spark_type_name == "bigint":
            spark_type_name = "long"
        elif spark_type_name == "smallint":
            spark_type_name = "short"
        elif spark_type_name.startswith("decimal"):
            # decimal(10, 2) -> decimal
            spark_type_name = "decimal"

        return DataType.from_string(spark_type_name)
