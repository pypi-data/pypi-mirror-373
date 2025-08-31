from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class PublishedTable(_FeatureStoreObject):
    def __init__(self, online_table_name: str, pipeline_id: str):
        self.online_table_name = online_table_name
        self.pipeline_id = pipeline_id
