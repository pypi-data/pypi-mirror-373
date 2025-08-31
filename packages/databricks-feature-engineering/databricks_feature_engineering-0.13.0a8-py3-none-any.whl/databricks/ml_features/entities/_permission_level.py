from typing import Any

from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    PermissionLevel as ProtoPermissionLevel,
)
from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity


class _PermissionLevel(_ProtoEnumEntity):
    """Permission Levels."""

    _CAN_MANAGE = ProtoPermissionLevel.Value("CAN_MANAGE")
    _CAN_EDIT_METADATA = ProtoPermissionLevel.Value("CAN_EDIT_METADATA")
    _CAN_VIEW_METADATA = ProtoPermissionLevel.Value("CAN_VIEW_METADATA")
    _MANAGED_BY_UC = ProtoPermissionLevel.Value("MANAGED_BY_UC")

    @classmethod
    def _enum_type(cls) -> Any:
        return ProtoPermissionLevel

    @staticmethod
    def can_write_to_catalog(permission_level):
        return permission_level in [
            _PermissionLevel._CAN_MANAGE,
            _PermissionLevel._CAN_EDIT_METADATA,
            _PermissionLevel._MANAGED_BY_UC,
        ]
