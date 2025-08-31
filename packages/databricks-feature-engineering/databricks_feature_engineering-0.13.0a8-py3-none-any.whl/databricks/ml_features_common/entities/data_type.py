from typing import Any

from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    DataType as ProtoDataType,
)


class DataType(_ProtoEnumEntity):
    """Online store data types."""

    INTEGER = ProtoDataType.Value("INTEGER")
    FLOAT = ProtoDataType.Value("FLOAT")
    BOOLEAN = ProtoDataType.Value("BOOLEAN")
    STRING = ProtoDataType.Value("STRING")
    DOUBLE = ProtoDataType.Value("DOUBLE")
    LONG = ProtoDataType.Value("LONG")
    TIMESTAMP = ProtoDataType.Value("TIMESTAMP")
    DATE = ProtoDataType.Value("DATE")
    SHORT = ProtoDataType.Value("SHORT")
    ARRAY = ProtoDataType.Value("ARRAY")
    MAP = ProtoDataType.Value("MAP")
    BINARY = ProtoDataType.Value("BINARY")
    DECIMAL = ProtoDataType.Value("DECIMAL")
    STRUCT = ProtoDataType.Value("STRUCT")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoDataType
