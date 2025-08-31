import abc
import os
from typing import List

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.entities.online_feature_table import (
    OnlineFeatureTable,
)
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    FeatureTablesForServing as ProtoFeatureTablesForServing,
)


class FeatureTablesForServing(_FeatureStoreObject):
    DATA_FILE = "feature_tables_for_serving.dat"

    def __init__(self, online_feature_tables: List[OnlineFeatureTable]):
        self._online_feature_tables = online_feature_tables

    @property
    def online_feature_tables(self):
        return self._online_feature_tables

    @classmethod
    def from_proto(cls, the_proto: ProtoFeatureTablesForServing):
        online_fts = [
            OnlineFeatureTable.from_proto(online_table)
            for online_table in the_proto.online_tables
        ]
        return cls(online_feature_tables=online_fts)

    @classmethod
    def load(cls, path: str):
        """
        Loads a binary serialized ProtoFeatureTablesForServing protocol buffer.

        :param path: Root path to the binary file.
        :return: :py:class:`~databricks.ml_features_common.entities.feature_tables_for_serving.FeatureTablesForServing`
        """
        proto = ProtoFeatureTablesForServing()
        # The load path may be None when the model is packaged by Feature Store, but did not use any
        # feature tables (eg just feature functions)
        if not path:
            return cls.from_proto(proto)
        with open(os.path.join(path, cls.DATA_FILE), "rb") as f:
            proto.ParseFromString(f.read())
        return cls.from_proto(proto)
