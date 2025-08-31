from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.protos.feature_spec_pb2 import (
    FunctionInfo as ProtoFunctionInfo,
)


class FunctionInfo(_FeatureStoreObject):
    def __init__(self, udf_name: str):
        if not udf_name:
            raise ValueError("udf_name must be non-empty.")
        self._udf_name = udf_name

    @property
    def udf_name(self) -> str:
        return self._udf_name

    @classmethod
    def from_proto(cls, function_info_proto):
        return cls(udf_name=function_info_proto.udf_name)

    def to_proto(self):
        return ProtoFunctionInfo(udf_name=self.udf_name)
