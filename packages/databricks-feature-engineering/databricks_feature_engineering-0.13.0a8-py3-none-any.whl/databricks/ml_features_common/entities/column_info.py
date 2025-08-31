import copy
from typing import Optional, Union

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec_constants import (
    FEATURE_COLUMN_INFO,
    ON_DEMAND_COLUMN_INFO,
    SOURCE_DATA_COLUMN_INFO,
)
from databricks.ml_features_common.entities.on_demand_column_info import (
    OnDemandColumnInfo,
)
from databricks.ml_features_common.entities.source_data_column_info import (
    SourceDataColumnInfo,
)
from databricks.ml_features_common.protos.feature_spec_pb2 import (
    ColumnInfo as ProtoColumnInfo,
)


class ColumnInfo(_FeatureStoreObject):
    """
    ColumnInfo's structure and properties are mapped 1:1 to the ColumnInfo proto message, unless specified otherwise.
    """

    def __init__(
        self,
        info: Union[SourceDataColumnInfo, FeatureColumnInfo, OnDemandColumnInfo],
        include: bool,
        data_type: Optional[str] = None,
        topological_ordering: Optional[int] = None,
    ):
        if not isinstance(
            info, (SourceDataColumnInfo, FeatureColumnInfo, OnDemandColumnInfo)
        ):
            raise ValueError(
                "info must be one of SourceDataColumnInfo, FeatureColumnInfo, OnDemandColumnInfo."
            )
        self._info = info
        self._include = include
        self._data_type = data_type
        self._topological_ordering = topological_ordering

    @property
    def info(
        self,
    ) -> Union[SourceDataColumnInfo, FeatureColumnInfo, OnDemandColumnInfo]:
        return self._info

    @property
    def include(self) -> bool:
        return self._include

    @property
    def data_type(self) -> Optional[str]:
        """
        FeatureSpecs before v7 are not required to have data types.
        """
        return self._data_type

    @property
    def topological_ordering(self) -> Optional[int]:
        """
        FeatureSpecs before v8 are not required to have topological ordering.
        """
        return self._topological_ordering

    @property
    def output_name(self) -> str:
        """
        This field does not exist in the proto, and is provided for convenience.
        """
        return self.info.output_name

    def with_topological_ordering(self, ordering: int):
        new_column_info = copy.copy(self)
        new_column_info._topological_ordering = ordering
        return new_column_info

    @classmethod
    def from_proto(cls, column_info_proto):
        if column_info_proto.HasField(SOURCE_DATA_COLUMN_INFO):
            info = SourceDataColumnInfo.from_proto(
                column_info_proto.source_data_column_info
            )
        elif column_info_proto.HasField(FEATURE_COLUMN_INFO):
            info = FeatureColumnInfo.from_proto(column_info_proto.feature_column_info)
        elif column_info_proto.HasField(ON_DEMAND_COLUMN_INFO):
            info = OnDemandColumnInfo.from_proto(
                column_info_proto.on_demand_column_info
            )
        else:
            raise ValueError("Unsupported info type: " + str(column_info_proto))

        data_type = (
            column_info_proto.data_type
            if column_info_proto.HasField("data_type")
            else None
        )
        topological_ordering = (
            column_info_proto.topological_ordering
            if column_info_proto.HasField("topological_ordering")
            else None
        )
        return ColumnInfo(
            info=info,
            include=column_info_proto.include,
            data_type=data_type,
            topological_ordering=topological_ordering,
        )

    def to_proto(self):
        column_info = ProtoColumnInfo(
            include=self.include,
            data_type=self.data_type,
            topological_ordering=self.topological_ordering,
        )
        if isinstance(self.info, SourceDataColumnInfo):
            column_info.source_data_column_info.CopyFrom(self.info.to_proto())
        elif isinstance(self.info, FeatureColumnInfo):
            column_info.feature_column_info.CopyFrom(self.info.to_proto())
        elif isinstance(self.info, OnDemandColumnInfo):
            column_info.on_demand_column_info.CopyFrom(self.info.to_proto())
        else:
            raise ValueError("Unsupported info type: " + str(self.info))

        return column_info
