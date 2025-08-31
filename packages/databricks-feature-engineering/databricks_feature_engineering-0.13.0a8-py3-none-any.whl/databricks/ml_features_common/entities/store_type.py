from typing import Any

from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    StoreType as ProtoStoreType,
)


class StoreType(_ProtoEnumEntity):
    """Online store types."""

    AURORA_MYSQL = ProtoStoreType.Value("AURORA_MYSQL")
    SQL_SERVER = ProtoStoreType.Value("SQL_SERVER")
    MYSQL = ProtoStoreType.Value("MYSQL")
    DYNAMODB = ProtoStoreType.Value("DYNAMODB")
    COSMOSDB = ProtoStoreType.Value("COSMOSDB")
    BRICKSTORE = ProtoStoreType.Value("BRICKSTORE")
    DATABRICKS_ONLINE_STORE = ProtoStoreType.Value("DATABRICKS_ONLINE_STORE")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoStoreType
