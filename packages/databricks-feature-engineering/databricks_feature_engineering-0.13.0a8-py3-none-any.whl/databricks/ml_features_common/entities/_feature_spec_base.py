from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.utils.yaml_utils import write_yaml


class _FeatureSpecBase(_FeatureStoreObject):

    FEATURE_ARTIFACT_FILE = "feature_spec.yaml"
    WORKSPACE_ID_FIELD_NAME = "workspace_id"
    FEATURE_STORE_CLIENT_VERSION_FIELD_NAME = "feature_store_client_version"
    SERIALIZATION_VERSION_FIELD_NAME = "serialization_version"
    SERIALIZATION_VERSION_NUMBER = 10

    def __init__(self, serialization_version: int):
        self._serialization_version = serialization_version

    @property
    def serialization_version(self) -> int:
        return self._serialization_version

    def _to_dict(self):
        raise NotImplementedError("Derived classes must implement this method")

    def save(self, path: str):
        """
        Convert spec to a YAML artifact and store at given `path` location.
        :param path: Root path to where YAML artifact is expected to be stored.
        :return: None
        """
        write_yaml(
            path=path,
            file_name=self.FEATURE_ARTIFACT_FILE,
            data_dict=self._to_dict(),
        )
