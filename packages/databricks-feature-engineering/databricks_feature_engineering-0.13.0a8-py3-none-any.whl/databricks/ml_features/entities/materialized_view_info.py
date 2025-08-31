from typing import Optional

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class MaterializedViewInfo(_FeatureStoreObject):
    """
    Information about a materialized view.

    :param pipeline_id: The ID for the pipeline.
    :param pipeline_name: The name of the pipeline.
    """

    def __init__(
        self,
        *,
        pipeline_id: str,
        pipeline_name: str,
    ):
        """Initialize a MaterializedViewInfo object. See class documentation."""
        self._pipeline_id = pipeline_id
        self._pipeline_name = pipeline_name

    @property
    def pipeline_id(self) -> str:
        """The ID for the pipeline."""
        return self._pipeline_id

    @property
    def pipeline_name(self) -> str:
        """The name of the pipeline."""
        return self._pipeline_name
