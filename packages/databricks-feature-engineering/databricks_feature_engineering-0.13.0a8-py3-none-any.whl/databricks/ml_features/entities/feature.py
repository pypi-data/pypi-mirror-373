from typing import Any, Dict, List, Optional

from pyspark.sql import Column

from databricks.ml_features.entities.aggregation import TimeWindow
from databricks.ml_features.entities.data_source import DataSource
from databricks.ml_features.entities.function import Function
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class Feature(_FeatureStoreObject):
    """
    Represents a feature definition that combines a data source with aggregation logic.

    :param name: The name of the feature. Leading and trailing whitespace will be stripped.
                 If not provided or empty after stripping, a name will be auto-generated
                 based on the input columns, function, and time window.
    :param source: The data source for this feature
    :param inputs: List of column names from the source to use as input
    :param function: The aggregation function to apply to the input columns
    :param time_window: The time window for the aggregation
    :param description: Optional description of the feature
    """

    INPUTS_FIELD_NAME = "inputs"
    DATA_SOURCE_FIELD_NAME = "data_source"
    FUNCTION_FIELD_NAME = "function"
    TIME_WINDOW_FIELD_NAME = "time_window"

    def __init__(
        self,
        *,
        source: DataSource,
        inputs: List[str],
        function: Function,
        time_window: TimeWindow,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Initialize a Feature object. See class documentation."""
        # Strip whitespace from name if provided
        if name is not None and isinstance(name, str):
            name = name.strip()

        self._validate_parameters(name, source, inputs, function, time_window)

        # Generate name if not provided or empty
        self._name = name or self._generate_name(source, inputs, function, time_window)
        self._source = source
        self._inputs = inputs
        self._function = function
        self._time_window = time_window
        self._description = description

    @property
    def name(self) -> str:
        """The name of the feature."""
        return self._name

    @property
    def source(self) -> DataSource:
        """The data source for this feature."""
        return self._source

    @property
    def inputs(self) -> List[str]:
        """List of column names from the source to use as input."""
        return self._inputs

    @property
    def function(self) -> Function:
        """The aggregation function to apply to the input columns."""
        return self._function

    @property
    def time_window(self) -> TimeWindow:
        """The time window for the aggregation."""
        return self._time_window

    @property
    def description(self) -> Optional[str]:
        """Optional description of the feature."""
        return self._description

    @staticmethod
    def _generate_name(
        source: DataSource,
        inputs: List[str],
        function: Function,
        time_window: TimeWindow,
    ) -> str:
        # ToDo: move this to backend as a part of CreateFeature API
        """Generate a feature name from the provided parameters."""
        return f"{inputs[0]}_{function.name}_{str(time_window)}"

    def computation_function(self) -> Column:
        func = self.function.spark_function(self.inputs)
        if self.time_window:
            func = func.over(
                self.time_window.spark_window(
                    self.source.entity_columns, self.source.order_column
                )
            )
        name = self.name
        return func.alias(name)

    def _validate_parameters(
        self,
        name: Optional[str],
        source: DataSource,
        inputs: List[str],
        function: Function,
        time_window: TimeWindow,
    ):
        """Validates the parameters provided to the Feature class."""
        if name is not None and not isinstance(name, str):
            raise ValueError("The 'name' must be a string when provided.")

        if not isinstance(source, DataSource):
            raise ValueError("The 'source' must be a DataSource instance.")

        if not isinstance(inputs, list):
            raise ValueError("The 'inputs' must be a list.")

        if not inputs:
            raise ValueError("The 'inputs' must contain at least one column name.")

        for i, column in enumerate(inputs):
            if not isinstance(column, str) or not column.strip():
                raise ValueError(
                    f"All column names in 'inputs' must be non-empty strings. "
                    f"Invalid column at index {i}: {column}"
                )

        if not isinstance(function, Function):
            raise ValueError("The 'function' must be a Function instance.")

        if not isinstance(time_window, TimeWindow):
            raise ValueError("The 'time_window' must be a TimeWindow instance.")

    def _to_yaml_dict(self) -> Dict[str, Any]:
        """Convert the feature to a dictionary that can be used to generate a YAML file."""
        return {
            self.INPUTS_FIELD_NAME: self.inputs,
            self.DATA_SOURCE_FIELD_NAME: self.source.full_name(),
            self.FUNCTION_FIELD_NAME: self.function._to_yaml_dict(),
            self.TIME_WINDOW_FIELD_NAME: self.time_window._to_yaml_dict(),
        }

    @classmethod
    def _from_yaml_dict(
        cls,
        feature_name: str,
        feature_dict: Dict[str, Any],
        data_source: DataSource,
    ) -> "Feature":
        """Create a Feature from a dictionary loaded from YAML."""
        # Parse the function
        function = Function._from_yaml_dict(feature_dict[cls.FUNCTION_FIELD_NAME])

        # Parse the time window
        time_window = TimeWindow._from_yaml_dict(
            feature_dict[cls.TIME_WINDOW_FIELD_NAME]
        )

        return cls(
            name=feature_name,
            source=data_source,
            inputs=feature_dict[cls.INPUTS_FIELD_NAME],
            function=function,
            time_window=time_window,
        )
