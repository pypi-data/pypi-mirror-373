from typing import Dict, Optional

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class FeatureFunction(_FeatureStoreObject):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.entities.feature_function.FeatureFunction`, `!databricks.feature_store.entities.feature_function.FeatureFunction`

    Value class used to specify a Python user-defined function (UDF) in Unity Catalog to use in a
    :class:`TrainingSet <databricks.ml_features.training_set.TrainingSet>`.

    :param udf_name: The Python UDF name.
    :param input_bindings: Mapping of UDF inputs to features in the
        :class:`TrainingSet <databricks.ml_features.training_set.TrainingSet>`.
    :param output_name: Output feature name of this FeatureFunction.
        If empty, defaults to the fully qualified `udf_name` when evaluated.
    """

    def __init__(
        self,
        *,
        udf_name: str,
        input_bindings: Optional[Dict[str, str]] = None,
        output_name: Optional[str] = None,
    ):
        """Initialize a FeatureFunction object. See class documentation."""
        # UC function names are always lowercase.
        self._udf_name = udf_name.lower()
        self._input_bindings = input_bindings if input_bindings else {}
        self._output_name = output_name

    @property
    def udf_name(self) -> str:
        """
        The name of the Python UDF called by this FeatureFunction.
        """
        return self._udf_name

    @property
    def input_bindings(self) -> Dict[str, str]:
        """
        The input to use for each argument of the Python UDF.

        For example:

        `{"x": "feature1", "y": "input1"}`
        """
        return self._input_bindings

    @property
    def output_name(self) -> Optional[str]:
        """
        The output name to use for the results of this FeatureFunction.
        If empty, defaults to the fully qualified `udf_name` when evaluated.
        """
        return self._output_name
