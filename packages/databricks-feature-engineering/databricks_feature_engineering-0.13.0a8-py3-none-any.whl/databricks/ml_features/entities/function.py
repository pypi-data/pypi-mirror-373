from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional

from pyspark.sql import Column
from pyspark.sql import functions as F
from typing_extensions import override

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class Function(_FeatureStoreObject):
    """Abstract base class for all aggregation functions."""

    @abstractmethod
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def spark_function(self, input_columns: List[str]) -> Column:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the aggregation function."""
        pass

    def extra_parameters(self) -> Dict[str, Any]:
        """
        Return the extra parameters of the function.
        Only applicable to a few functions that require additional parameters.
        """
        return {}

    def _to_yaml_dict(self) -> Dict[str, Any]:
        """Convert the function to a dictionary that can be used to generate a YAML file."""
        result = {"operator": self.name}
        if extra_params := self.extra_parameters():
            result["extra_parameters"] = extra_params
        return result

    @classmethod
    def _from_yaml_dict(cls, function_dict: Dict[str, Any]) -> "Function":
        """Create a Function from a dictionary loaded from YAML."""
        operator = function_dict["operator"]
        extra_params = function_dict.get("extra_parameters", {})

        # Map operator names to function classes
        if operator == "approx_count_distinct":
            relative_sd = extra_params.get("relativeSD")
            return ApproxCountDistinct(relativeSD=relative_sd)
        elif operator == "percentile_approx":
            percentile = extra_params.get("percentile")
            accuracy = extra_params.get("accuracy")
            return PercentileApprox(percentile=percentile, accuracy=accuracy)
        elif operator in AGGREGATION_FUNCTION_BY_SHORTHAND:
            # For simple functions without parameters, use the mapping
            return AGGREGATION_FUNCTION_BY_SHORTHAND[operator]
        else:
            raise ValueError(f"Unknown function operator: {operator}")

    @classmethod
    def from_string(cls, function_str: str) -> "Function":
        """
        Create a Function instance from a string representation.

        :param function_str: String name of the aggregation function
        :return: Function instance
        :raises ValueError: If the function string is not recognized
        """
        if not isinstance(function_str, str):
            raise ValueError(f"Expected string, got {type(function_str)}")

        function_str = function_str.lower().strip()
        if function_str in AGGREGATION_FUNCTION_BY_SHORTHAND:
            return AGGREGATION_FUNCTION_BY_SHORTHAND[function_str]
        else:
            raise ValueError(
                f"Unknown function '{function_str}'. "
                f"Valid functions are: {list(AGGREGATION_FUNCTION_BY_SHORTHAND.keys())}"
            )


class Avg(Function):
    """Class representing the average (avg) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"AVG({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.avg(input_columns[0])

    @property
    def name(self) -> str:
        return "avg"


class Count(Function):
    """Class representing the count aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"COUNT({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.count(input_columns[0])

    @property
    def name(self) -> str:
        return "count"


class ApproxCountDistinct(Function):
    """
    Class representing the approximate count distinct aggregation function.
    See https://docs.databricks.com/en/sql/language-manual/functions/approx_count_distinct.html

    :param relativeSD: The relative standard deviation allowed in the approximation.
    """

    # Field names used in the YAML serialization
    PARAM_RELATIVE_SD = "relativeSD"

    def __init__(self, relativeSD: Optional[float] = None):
        if relativeSD is not None and not isinstance(relativeSD, float):
            raise ValueError("relativeSD must be a float if supplied.")
        self._relativeSD = relativeSD

    @property
    def name(self) -> str:
        return "approx_count_distinct"

    @property
    def relativeSD(self) -> Optional[float]:
        return self._relativeSD

    @override
    def extra_parameters(self) -> Dict[str, Any]:
        return {
            self.PARAM_RELATIVE_SD: self._relativeSD,
        }

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if self._relativeSD:
            return f"APPROX_COUNT_DISTINCT({column_name}, {self._relativeSD})"
        return f"APPROX_COUNT_DISTINCT({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        if self._relativeSD:
            return F.approx_count_distinct(input_columns[0], self._relativeSD)
        return F.approx_count_distinct(input_columns[0])


class PercentileApprox(Function):
    """
    Class representing the percentile approximation aggregation function.
    See https://docs.databricks.com/en/sql/language-manual/functions/approx_percentile.html

    :param percentile: The percentile to approximate.
    :param accuracy: The accuracy of the approximation.
    """

    # Field names used in the YAML serialization
    PARAM_PERCENTILE = "percentile"
    PARAM_ACCURACY = "accuracy"

    def __init__(self, percentile: float, accuracy: Optional[int] = None):
        if not isinstance(percentile, float):
            raise ValueError("percentile must be a float.")
        if accuracy is not None and not isinstance(accuracy, int):
            raise ValueError("accuracy must be an integer if supplied.")
        self._percentile = percentile
        self._accuracy = accuracy

    @property
    def name(self) -> str:
        return "percentile_approx"

    @property
    def percentile(self) -> float:
        return self._percentile

    @property
    def accuracy(self) -> Optional[int]:
        return self._accuracy

    @override
    def extra_parameters(self) -> Dict[str, Any]:
        return {
            self.PARAM_PERCENTILE: self._percentile,
            self.PARAM_ACCURACY: self._accuracy,
        }

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if self._accuracy:
            return f"PERCENTILE_APPROX({column_name}, {self._percentile}, {self._accuracy})"
        return f"PERCENTILE_APPROX({column_name}, {self._percentile})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        if self._accuracy:
            return F.percentile_approx(
                input_columns[0], self._percentile, self._accuracy
            )
        return F.percentile_approx(input_columns[0], self._percentile)


class First(Function):
    """Class representing the first aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if not timestamp_key:
            raise ValueError(
                "timestamp_key must be supplied for First aggregation function."
            )
        return f"MIN_BY({column_name}, {timestamp_key})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.first(input_columns[0])

    @property
    def name(self) -> str:
        return "first"


class Last(Function):
    """Class representing the last aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if not timestamp_key:
            raise ValueError(
                "timestamp_key must be supplied for Last aggregation function."
            )
        return f"MAX_BY({column_name}, {timestamp_key})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.last(input_columns[0])

    @property
    def name(self) -> str:
        return "last"


class Max(Function):
    """Class representing the maximum (max) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"MAX({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.max(input_columns[0])

    @property
    def name(self) -> str:
        return "max"


class Min(Function):
    """Class representing the minimum (min) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"MIN({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.min(input_columns[0])

    @property
    def name(self) -> str:
        return "min"


class StddevPop(Function):
    """Class representing the population standard deviation (stddev_pop) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"STDDEV_POP({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.stddev_pop(input_columns[0])

    @property
    def name(self) -> str:
        return "stddev_pop"


class StddevSamp(Function):
    """Class representing the sample standard deviation (stddev_samp) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"STDDEV_SAMP({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.stddev_samp(input_columns[0])

    @property
    def name(self) -> str:
        return "stddev_samp"


class Sum(Function):
    """Class representing the sum aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"SUM({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.sum(input_columns[0])

    @property
    def name(self) -> str:
        return "sum"


class VarPop(Function):
    """Class representing the population variance (var_pop) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"VAR_POP({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.var_pop(input_columns[0])

    @property
    def name(self) -> str:
        return "var_pop"


class VarSamp(Function):
    """Class representing the sample variance (var_samp) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"VAR_SAMP({column_name})"

    @override
    def spark_function(self, input_columns: List[str]) -> Column:
        return F.var_samp(input_columns[0])

    @property
    def name(self) -> str:
        return "var_samp"


# Mapping from shorthand strings to instances of corresponding classes
# Only include aggregations that don't require additional arguments
AGGREGATION_FUNCTION_BY_SHORTHAND = {
    "mean": Avg(),
    "avg": Avg(),
    "count": Count(),
    "first": First(),
    "last": Last(),
    "max": Max(),
    "min": Min(),
    "stddev_pop": StddevPop(),
    "stddev_samp": StddevSamp(),
    "sum": Sum(),
    "var_pop": VarPop(),
    "var_samp": VarSamp(),
    "approx_count_distinct": ApproxCountDistinct(),
}
