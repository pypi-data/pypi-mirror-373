# Backward compatibility module - imports from function.py
# This module maintains backward compatibility for existing code that imports from aggregation_function.py

from databricks.ml_features.entities.function import (
    AGGREGATION_FUNCTION_BY_SHORTHAND,
    ApproxCountDistinct,
    Avg,
    Count,
    First,
    Function,
    Last,
    Max,
    Min,
    PercentileApprox,
    StddevPop,
    StddevSamp,
    Sum,
    VarPop,
    VarSamp,
)

# Backward compatibility alias
AggregationFunction = Function

# Re-export all classes and constants for backward compatibility
__all__ = [
    "AggregationFunction",  # Backward compatibility alias
    "Function",  # New name
    "Avg",
    "Count",
    "ApproxCountDistinct",
    "PercentileApprox",
    "First",
    "Last",
    "Max",
    "Min",
    "StddevPop",
    "StddevSamp",
    "Sum",
    "VarPop",
    "VarSamp",
    "AGGREGATION_FUNCTION_BY_SHORTHAND",
]
