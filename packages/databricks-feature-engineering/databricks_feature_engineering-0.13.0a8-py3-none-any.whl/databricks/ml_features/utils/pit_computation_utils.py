"""
Point-in-Time Feature Computation Utilities
===========================================

This module provides utilities for computing time-windowed features with point-in-time correctness
using an enhanced bitmask approach. It's designed for use with declarative Feature objects
that define computations over DataSource objects.

The implementation handles:
- Multiple data sources with different schemas
- Multiple time windows per source (including offset windows)
- Microsecond-precision timestamp handling
- All aggregation function types with correct null handling
- Efficient batching and optimization strategies

Key Innovation: Enhanced bitmask approach that uses conditional aggregation to handle
empty time windows correctly, eliminating the need for dummy records or complex joins.
"""

import random
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Tuple

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from databricks.ml_features.constants import _FEATURE_ENGINEERING_COMPUTATION_PRECISION
from databricks.ml_features.entities.data_source import DataSource
from databricks.ml_features.entities.feature import Feature


def _get_default_value_for_function(function_name: str) -> F.Column:
    """
    Get the appropriate default value when no records exist in time window.

    Different aggregation functions have different semantics for empty windows:
    - Count functions (count, approx_count_distinct) return 0
    - All other functions (sum, avg, min, max, etc.) return null

    Args:
        function_name: Name of the aggregation function (e.g., "count", "sum", "avg")

    Returns:
        PySpark literal column with appropriate default value
    """
    COUNT_FUNCTIONS = {"count", "approx_count_distinct"}

    if function_name.lower() in COUNT_FUNCTIONS:
        return F.lit(0)
    else:
        return F.lit(None)


def _cast_timestamp_to_long_with_precision(col_name, precision_factor):
    """Helper function to cast a timestamp column to long with precision."""
    # ToDo: refactor this to use timestamp_micros() or unix_micros() instead
    return F.col(col_name).cast("timestamp").cast("long") * precision_factor + (
        F.col(col_name).cast("timestamp").cast("double")
        * precision_factor
        % precision_factor
    ).cast("long")


def _create_microsecond_precision_time_condition(
    source_ts_col: str,
    train_ts_col: str,
    duration: timedelta,
    offset: timedelta = timedelta(0),
) -> F.Column:
    """
    Create time window condition with microsecond precision.

    This function creates a condition that determines whether a source timestamp
    falls within the specified time window relative to a training timestamp.
    It maintains microsecond precision using the same approach as the existing
    compute_features() implementation.

    Args:
        source_ts_col: Source timestamp column name
        train_ts_col: Training timestamp column name
        duration: Window duration (how far back to look from train_ts)
        offset: Window offset (shift backward from train_ts), defaults to 0

    Returns:
        PySpark condition column for time window membership with microsecond precision

    Example:
        # Standard 7-day window: source_ts in [train_ts - 7 days, train_ts)
        condition = _create_microsecond_precision_time_condition(
            "source_ts", "train_ts", timedelta(days=7)
        )

        # Offset window: source_ts in [train_ts - 7 days - 1 day, train_ts - 1 day)
        condition = _create_microsecond_precision_time_condition(
            "source_ts", "train_ts", timedelta(days=7), timedelta(days=-1)
        )
    """
    # Calculate precision factor for microsecond handling
    # This matches the precision used in existing compute_features() implementation
    precision_factor = (
        int(1 / _FEATURE_ENGINEERING_COMPUTATION_PRECISION)
        if _FEATURE_ENGINEERING_COMPUTATION_PRECISION != 0
        else 1
    )

    # Convert timedeltas to microseconds for precise arithmetic
    duration_microseconds = int(duration.total_seconds() * precision_factor)
    offset_microseconds = int(offset.total_seconds() * precision_factor)

    # Convert timestamps to microsecond precision long values
    # This preserves full timestamp precision including microseconds
    source_ts_long = _cast_timestamp_to_long_with_precision(
        source_ts_col, precision_factor
    )
    train_ts_long = _cast_timestamp_to_long_with_precision(
        train_ts_col, precision_factor
    )

    # Create time window bounds in microsecond precision
    # Window is [train_ts - duration + offset, train_ts + offset)
    window_start = (
        train_ts_long - F.lit(duration_microseconds) + F.lit(offset_microseconds)
    )
    window_end = train_ts_long + F.lit(offset_microseconds)

    return (source_ts_long >= window_start) & (source_ts_long < window_end)


def _group_features_by_source_and_window(
    features: List[Feature],
) -> Dict[DataSource, Dict[Tuple[timedelta, timedelta], List[Feature]]]:
    """
    Group features by data source and time window for efficient batch processing.

    This optimization reduces redundant computations by:
    1. Processing each data source only once
    2. Minimizing the number of window specifications created

    Args:
        features: List of Feature objects to group

    Returns:
        Nested dictionary mapping:
        {data_source: {(duration, offset): [features_with_same_window]}}

    Example:
        features = [
            Feature(source=bookings, time_window=TimeWindow(days=7)),      # Group 1
            Feature(source=bookings, time_window=TimeWindow(days=7)),      # Group 1
            Feature(source=bookings, time_window=TimeWindow(days=3)),      # Group 2
            Feature(source=transactions, time_window=TimeWindow(days=7)),  # Group 3
        ]

        Result: {
            bookings_source: {
                (7_days, 0_offset): [feature1, feature2],
                (3_days, 0_offset): [feature3]
            },
            transactions_source: {
                (7_days, 0_offset): [feature4]
            }
        }
    """
    grouped = defaultdict(lambda: defaultdict(list))

    for feature in features:
        source = feature.source
        duration = feature.time_window.duration
        offset = feature.time_window.offset
        window_key = (duration, offset)

        grouped[source][window_key].append(feature)

    return grouped


def _extract_train_timestamp_column(train_df: DataFrame, source: DataSource) -> str:
    """
    Extract the training timestamp column name from the training DataFrame.

    The training DataFrame should contain a timestamp column that corresponds to
    the source's timeseries_column. This function identifies that column.

    Args:
        train_df: Training DataFrame
        source: DataSource object with timeseries_column property

    Returns:
        Name of the timestamp column in train_df

    Raises:
        ValueError: If the expected timestamp column is not found
    """
    # The training DataFrame should have the same timeseries column as the source
    expected_ts_col = source.timeseries_column

    if expected_ts_col not in train_df.columns:
        raise ValueError(
            f"Expected timestamp column '{expected_ts_col}' not found in training DataFrame. "
            f"Available columns: {train_df.columns}"
        )

    return expected_ts_col


def augment_df_with_pit_computed_features(
    train_df: DataFrame,
    features: List[Feature],
    sources: Dict[DataSource, DataFrame],
) -> DataFrame:
    """
    Augment training DataFrame with point-in-time computed features using enhanced bitmask approach.

    This function implements the production-ready solution for computing time-windowed features
    with point-in-time correctness. It processes multiple data sources and features efficiently
    while maintaining microsecond precision and handling all edge cases correctly.

    Key Features:
    - Groups features by data source and time window for optimal performance
    - Uses conditional bitmask aggregation to handle empty windows correctly
    - Maintains microsecond timestamp precision
    - Supports offset time windows for advanced use cases
    - Handles all aggregation function types with appropriate null semantics

    Args:
        train_df: Training DataFrame containing entity columns, timestamps, and labels
        features: List of Feature objects defining the computations to perform
        sources: Dictionary mapping DataSource objects to their loaded DataFrames

    Returns:
        DataFrame with original training data plus all computed feature columns

    Raises:
        ValueError: If features reference DataSources not present in sources dict
        ValueError: If required columns are missing from DataFrames

    Example:
        # Training data
        train_df = spark.createDataFrame([
            (1, datetime(2025, 5, 2), 'a'),
            (1, datetime(2025, 5, 4), 'b')
        ], ["customer_id", "ts", "label"])

        # Source data
        bookings_df = spark.createDataFrame([
            (1, datetime(2025, 5, 1), 123),
            (1, datetime(2025, 5, 3), 456)
        ], ["customer_id", "ts", "booking_id"])

        # Features
        features = [
            Feature(source=bookings_source, inputs=["booking_id"], function=Count(),
                   time_window=TimeWindow(duration=timedelta(days=7))),
            Feature(source=bookings_source, inputs=["booking_id"], function=Sum(),
                   time_window=TimeWindow(duration=timedelta(days=3)))
        ]

        # Sources mapping
        sources = {bookings_source: bookings_df}

        # Compute features
        result = augment_df_with_pit_computed_features(train_df, features, sources)

        # Result will have original columns plus computed features:
        # [customer_id, ts, label, booking_id_count_7d, booking_id_sum_3d]
    """
    if not features:
        return train_df

    # Validate that all feature sources are available in sources dict
    feature_sources = {feature.source for feature in features}
    available_sources = set(sources.keys())
    missing_sources = feature_sources - available_sources
    if missing_sources:
        raise ValueError(
            f"Features reference DataSources not found in sources dict: "
            f"{[source.full_name() for source in missing_sources]}"
        )

    # Group features by data source and time window for efficient batch processing
    features_by_source_and_window = _group_features_by_source_and_window(features)

    # Process each data source independently and collect results
    all_source_results = []

    for source, windows_to_features in features_by_source_and_window.items():
        # Get the pre-loaded source DataFrame
        source_df = sources[source]

        # Extract the training timestamp column name
        train_ts_col = _extract_train_timestamp_column(train_df, source)

        # Generate a unique column name for the source timestamp
        source_ts_col = f"source_ts_{random.randint(1, 1_000_000)}"

        # Handle column name collisions by temporarily renaming source columns
        train_columns = set(train_df.columns)
        source_columns = set(source_df.columns)
        collision_columns = (
            train_columns.intersection(source_columns)
            - set(source.entity_columns)
            - {source.timeseries_column}
        )

        # Create mapping for collision resolution specific to this source
        source_collision_renames = {}
        source_df_renamed = source_df

        # Generate source identity for unique aliases and collision resolution
        source_id = abs(hash(str(source)))
        source_alias = f"source_{source_id}"

        if collision_columns:
            # Temporarily rename colliding columns in source DataFrame
            # Include source identity to avoid cross-source conflicts
            for col_name in collision_columns:
                temp_name = f"__temp_source_{source_id}_{col_name}_{random.randint(1, 1_000_000)}"
                source_collision_renames[
                    col_name
                ] = temp_name  # Map original name to temp name
                source_df_renamed = source_df_renamed.withColumnRenamed(
                    col_name, temp_name
                )

        # Perform point-in-time join: training data with source data
        # Only include source records that occurred before the training timestamp
        joined = (
            train_df.alias("train")
            .join(
                source_df_renamed.alias(source_alias),
                # Join on all entity columns
                [
                    F.col(f"train.{col}") == F.col(f"{source_alias}.{col}")
                    for col in source.entity_columns
                ],
                "inner",
            )
            .filter(
                # Point-in-time correctness: source timestamp < training timestamp
                F.col(f"{source_alias}.{source.timeseries_column}")
                < F.col(f"train.{train_ts_col}")
            )
            .select(
                # Select all training columns with original names
                *[F.col(f"train.{col}").alias(col) for col in train_df.columns],
                # Add source timestamp for window calculations
                F.col(f"{source_alias}.{source.timeseries_column}").alias(
                    source_ts_col
                ),
                # Add source columns needed for feature inputs (excluding join keys and timestamp)
                *[
                    F.col(f"{source_alias}.{col_name}").alias(col_name)
                    for col_name in source_df_renamed.columns
                    if col_name
                    not in (source.entity_columns + [source.timeseries_column])
                ],
            )
        )

        # Create an inverse bitmasks for each unique time window
        # This allows multiple features to share the same bitmask calculation
        current_df = joined
        window_specs = {}

        for (duration, offset), window_features in windows_to_features.items():
            # Create unique identifier for this time window
            window_key = (duration, offset)
            inverse_bitmask_col = f"inv_bitmask_{abs(hash((duration, offset)))}__{random.randint(1, 1_000_000)}"

            # Create time window condition with microsecond precision
            time_condition = _create_microsecond_precision_time_condition(
                source_ts_col, train_ts_col, duration, offset
            )

            # Add inverse bitmask column: 0 if in window, 1 if outside window
            current_df = current_df.withColumn(
                inverse_bitmask_col, F.when(time_condition, 0).otherwise(1)
            )

            # Create window specification for this time window
            # Partition by entity columns + training timestamp to ensure each training
            # record gets its own independent feature calculation
            partition_cols = source.entity_columns + [train_ts_col]
            window_spec = (
                Window.partitionBy(*partition_cols)
                .orderBy(inverse_bitmask_col)
                .rangeBetween(0, 0)  # Only aggregate records allowed by inverse bitmask
            )
            window_specs[window_key] = (window_spec, inverse_bitmask_col)

        # Apply feature computations for all features in this source
        for (duration, offset), window_features in windows_to_features.items():
            window_key = (duration, offset)
            window_spec, inverse_bitmask_col = window_specs[window_key]

            for feature in window_features:
                # Map feature inputs to current DataFrame column names (handle renames)
                # Only apply renames for features from this specific source
                mapped_inputs = []
                for input_col in feature.inputs:
                    # Check if this input was renamed due to collision
                    if input_col in source_collision_renames:
                        actual_col_name = source_collision_renames[input_col]
                    else:
                        actual_col_name = input_col
                    mapped_inputs.append(actual_col_name)

                # Get the Spark aggregation function for this feature using mapped column names
                spark_function = feature.function.spark_function(mapped_inputs)

                # Get appropriate default value for this function type
                default_value = _get_default_value_for_function(feature.function.name)

                # Apply conditional aggregation using inverse bitmask for inclusion check
                # Only aggregate when inverse bitmask = 0 (records in time window allowed by inverse bitmask)
                # Use default value when inverse bitmask = 1 (no records in window)
                current_df = current_df.withColumn(
                    feature.name,
                    F.when(
                        F.col(inverse_bitmask_col) == F.lit(0),
                        spark_function.over(window_spec),
                    ).otherwise(default_value),
                )

        # Clean up intermediate columns and prepare for aggregation
        feature_columns = [
            feature.name
            for window_features in windows_to_features.values()
            for feature in window_features
        ]
        columns_to_keep = train_df.columns + feature_columns

        # Group by training record and aggregate features using first()
        # This handles any duplicates created by the point-in-time join
        source_result = (
            current_df.groupBy(*train_df.columns)
            .agg(*[F.first(col).alias(col) for col in feature_columns])
            .select(*columns_to_keep)
        )

        all_source_results.append(source_result)

    # Combine results from all data sources
    if len(all_source_results) == 1:
        # Single source - return result directly
        final_result = all_source_results[0]
    else:
        # Multiple sources - join results together
        final_result = train_df

        for source_result in all_source_results:
            # Extract only the new feature columns from this source
            source_feature_cols = [
                col for col in source_result.columns if col not in train_df.columns
            ]

            # Select training columns + new features from this source
            source_features_only = source_result.select(
                *train_df.columns, *source_feature_cols
            )

            # Left join to preserve all training records
            final_result = final_result.join(
                source_features_only,
                train_df.columns,  # Join on all original training columns
                "left",
            )

    return final_result
