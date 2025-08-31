from typing import Any

from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    QueryMode as ProtoQueryMode,
)


class QueryMode(_ProtoEnumEntity):
    """Online store query modes."""

    PRIMARY_KEY_LOOKUP = ProtoQueryMode.Value("PRIMARY_KEY_LOOKUP")
    RANGE_QUERY = ProtoQueryMode.Value("RANGE_QUERY")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoQueryMode
