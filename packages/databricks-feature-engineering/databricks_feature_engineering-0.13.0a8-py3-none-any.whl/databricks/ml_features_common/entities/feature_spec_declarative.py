from typing import List

from typing_extensions import override

# Currently the following classes are defined in the fe-client folder. It can only be used in the fe-client.
# Meaning this file cannot be imported in the LookupClient.
from databricks.ml_features.entities.data_source import DataSource
from databricks.ml_features.entities.feature import Feature
from databricks.ml_features_common.entities._feature_spec_base import _FeatureSpecBase
from databricks.ml_features_common.entities.column_info import ColumnInfo
from databricks.ml_features_common.entities.feature_spec_constants import (
    DATA_TYPE,
    INCLUDE,
    INPUT_COLUMNS,
    SOURCE,
    TRAINING_DATA,
)
from databricks.ml_features_common.entities.source_data_column_info import (
    SourceDataColumnInfo,
)


class FeatureSpecDeclarative(_FeatureSpecBase):
    """
    FeatureSpecDeclarative contains a group of declarative features.
    """

    # Field names used in the YAML serialization
    FEATURES_FIELD_NAME = "features"
    DATA_SOURCES_FIELD_NAME = "data_sources"

    def __init__(
        self,
        *,  # Force all arguments to be keyword-only
        features: List[Feature],
        column_infos: List[ColumnInfo],
        workspace_id: int,
        feature_store_client_version: str,
        serialization_version: int
    ):
        super().__init__(serialization_version)
        self._features = features
        self._column_infos = column_infos
        self._workspace_id = workspace_id
        self._feature_store_client_version = feature_store_client_version

    @property
    def column_infos(self):
        return self._column_infos

    @property
    def features(self):
        return self._features

    def _get_data_sources(self):
        return [feature.source for feature in self._features]

    @override
    def _to_dict(self):
        yaml_dict = {}
        if self._column_infos:
            yaml_dict[INPUT_COLUMNS] = [
                {
                    column_info.info.name: {
                        SOURCE: TRAINING_DATA,
                        INCLUDE: column_info.include,
                        DATA_TYPE: column_info.data_type,
                    }
                }
                for column_info in self._column_infos
                if column_info.info is not None
            ]
        yaml_dict[self.FEATURES_FIELD_NAME] = {
            feature.name: feature._to_yaml_dict() for feature in self._features
        }
        yaml_dict[self.DATA_SOURCES_FIELD_NAME] = {
            data_source.full_name(): data_source._to_yaml_dict()
            for data_source in self._get_data_sources()
        }
        # For readability, place SERIALIZATION_VERSION_NUMBER last in the dictionary.
        yaml_dict[self.SERIALIZATION_VERSION_FIELD_NAME] = self.serialization_version
        yaml_dict[self.WORKSPACE_ID_FIELD_NAME] = self._workspace_id
        yaml_dict[
            self.FEATURE_STORE_CLIENT_VERSION_FIELD_NAME
        ] = self._feature_store_client_version
        return yaml_dict

    @classmethod
    def _from_dict(cls, spec_dict):
        """Create a FeatureSpecDeclarative from a dictionary."""
        # Parse data sources first
        data_sources = {}
        for data_source_name, data_source_dict in spec_dict[
            cls.DATA_SOURCES_FIELD_NAME
        ].items():
            data_sources[data_source_name] = DataSource._from_yaml_dict(
                data_source_dict
            )

        # Parse features, referencing the data sources by name
        features = []
        for feature_name, feature_dict in spec_dict[cls.FEATURES_FIELD_NAME].items():
            feature = Feature._from_yaml_dict(
                feature_name,
                feature_dict,
                data_sources[feature_dict[Feature.DATA_SOURCE_FIELD_NAME]],
            )
            features.append(feature)

        # Get serialization version
        serialization_version = spec_dict[cls.SERIALIZATION_VERSION_FIELD_NAME]

        # Parse column_infos if present
        column_infos = []
        if INPUT_COLUMNS in spec_dict:
            for column_dict in spec_dict[INPUT_COLUMNS]:
                for column_name, column_spec in column_dict.items():
                    if column_spec.get(SOURCE) == TRAINING_DATA:
                        column_info = ColumnInfo(
                            info=SourceDataColumnInfo(column_name),
                            include=column_spec.get(INCLUDE, True),
                            data_type=column_spec.get(DATA_TYPE),
                        )
                        column_infos.append(column_info)

        # Get workspace_id and feature_store_client_version if present
        workspace_id = spec_dict.get(cls.WORKSPACE_ID_FIELD_NAME)
        feature_store_client_version = spec_dict.get(
            cls.FEATURE_STORE_CLIENT_VERSION_FIELD_NAME
        )

        return cls(
            column_infos=column_infos,
            features=features,
            serialization_version=serialization_version,
            workspace_id=workspace_id,
            feature_store_client_version=feature_store_client_version,
        )
