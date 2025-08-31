from typing import Dict

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.protos.feature_spec_pb2 import (
    InputBinding as ProtoInputBinding,
)
from databricks.ml_features_common.protos.feature_spec_pb2 import (
    OnDemandColumnInfo as ProtoOnDemandColumnInfo,
)


class OnDemandColumnInfo(_FeatureStoreObject):
    def __init__(
        self,
        udf_name: str,
        input_bindings: Dict[str, str],
        output_name: str,
    ):
        if not udf_name:
            raise ValueError("udf_name must be non-empty.")
        if not output_name:
            raise ValueError("output_name must be non-empty.")

        self._udf_name = udf_name
        self._input_bindings = input_bindings
        self._output_name = output_name

    @property
    def udf_name(self) -> str:
        return self._udf_name

    @property
    def input_bindings(self) -> Dict[str, str]:
        """
        input_bindings is serialized as the InputBindings proto message.
        """
        return self._input_bindings

    @property
    def output_name(self) -> str:
        return self._output_name

    @classmethod
    def from_proto(cls, on_demand_column_info_proto):
        input_bindings_dict = {
            input_binding.parameter: input_binding.bound_to
            for input_binding in on_demand_column_info_proto.input_bindings
        }
        return OnDemandColumnInfo(
            udf_name=on_demand_column_info_proto.udf_name,
            input_bindings=input_bindings_dict,
            output_name=on_demand_column_info_proto.output_name,
        )

    def to_proto(self):
        input_bindings_list = [
            ProtoInputBinding(parameter=k, bound_to=v)
            for k, v in self.input_bindings.items()
        ]
        return ProtoOnDemandColumnInfo(
            udf_name=self.udf_name,
            input_bindings=input_bindings_list,
            output_name=self.output_name,
        )
