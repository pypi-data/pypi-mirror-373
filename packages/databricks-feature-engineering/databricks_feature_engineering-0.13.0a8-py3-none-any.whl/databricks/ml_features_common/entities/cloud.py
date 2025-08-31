from typing import Any

from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    Cloud as ProtoCloud,
)


class Cloud(_ProtoEnumEntity):
    """Cloud types."""

    AWS = ProtoCloud.Value("AWS")
    AZURE = ProtoCloud.Value("AZURE")
    GCP = ProtoCloud.Value("GCP")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoCloud
