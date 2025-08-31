from databricks.ml_features_common.entities._proto_enum_entity import _ProtoEnumEntity


class PublishMode(_ProtoEnumEntity):
    """Publish modes for online store."""

    # TODO: Change string values to enum values from the proto once the proto is updated.

    PUBLISH_MODE_UNSPECIFIED = "PUBLISH_MODE_UNSPECIFIED"
    TRIGGERED = "TRIGGERED"
    CONTINUOUS = "CONTINUOUS"

    @classmethod
    def _enum_type(cls):
        return str
