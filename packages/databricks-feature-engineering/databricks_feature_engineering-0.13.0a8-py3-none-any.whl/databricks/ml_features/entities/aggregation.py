import datetime
from typing import Optional, Union

from databricks.ml_features.entities.function import (
    AGGREGATION_FUNCTION_BY_SHORTHAND,
    Function,
)
from databricks.ml_features.entities.time_window import TimeWindow, Window
from databricks.ml_features.utils.time_utils import format_duration
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class Aggregation(_FeatureStoreObject):
    """
    Defines a single aggregated feature.

    :param column: The source column to aggregate. The column must exist in the parent FeatureAggregation source_table.
    :param output_column: The output column name. If not provided, a default name will be generated.
    :param function: The function to use. If a string is given, it will be interpreted as short-hand (e.g., "sum", "avg", "count").
    :param time_window: The time window to aggregate data with.
    """

    def __init__(
        self,
        *,
        function: Union[str, Function],
        time_window: Optional[TimeWindow] = None,
        column: Optional[str] = None,
        output_column: Optional[str] = None,
        **kwargs,
    ):
        """Initialize an Aggregation object. See class documentation."""
        self._column = column
        if isinstance(function, str):
            if function.lower() not in AGGREGATION_FUNCTION_BY_SHORTHAND:
                raise ValueError(f"Invalid aggregation function: {function}.")

            self._function = AGGREGATION_FUNCTION_BY_SHORTHAND[function.lower()]

        else:
            self._function = function

        # backward compatibility for existing code
        self._time_window = time_window or kwargs.get("window")

        # If output_column is not provided, generate a default output column name.
        self._output_column = (
            output_column
            if output_column
            else self._generate_default_output_column_name()
        )

    @property
    def column(self) -> str | None:
        """The source column to aggregate."""
        return self._column

    @property
    def output_column(self) -> str:
        """The output column name."""
        return self._output_column

    @property
    def function(self) -> Function:
        """The aggregation function to use."""
        return self._function

    @property
    def time_window(self) -> TimeWindow:
        """The time window to aggregate data with."""
        return self._time_window

    @property
    def window(self) -> Window:
        """The time window to aggregate data with."""
        return self.time_window

    def _generate_default_output_column_name(self) -> str:
        """
        Generates a default output column name.

        :return: A string representing the default output column name.
        """
        duration_str = format_duration(self._time_window.duration)
        offset_str = (
            format_duration(-self._time_window.offset)
            if self._time_window.offset != datetime.timedelta(0)
            else ""
        )
        if duration_str is None or offset_str is None:
            raise ValueError(
                f"Cannot auto-generate output column name for input column {self._column} with duration {self._time_window.duration} and offset {-self._time_window.offset} because the duration or offset contains fractional hours. Please specify output_column explicitly."
            )

        if offset_str:
            offset_str = f"_offset_{offset_str}"

        return f"{self._column or ''}_{self._function.name}_{duration_str}{offset_str}"
