import copy
import datetime
from typing import List, Optional, Union

from databricks.ml_features.api.proto.feature_catalog_pb2 import AggregationInfo
from databricks.ml_features.entities.aggregation import Aggregation
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)

MIN_GRANULARITY = datetime.timedelta(hours=1)
MIN_GRANULARITY_UNIT = datetime.timedelta(seconds=1)


class FeatureAggregations(_FeatureStoreObject):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.entities.feature_lookup.FeatureLookup`, `!databricks.feature_store.entities.feature_lookup.FeatureLookup`

    Defines an aggregation specification.

    :param source_table: The source table to perform aggregation on. The source table can be any delta table.
    :param lookup_key: Key to use when computing aggregation. It can be a single key or a list of keys.
    :param timestamp_key: Key for timestamp. Used for determining the temporal position of data points.
    :param granularity: The temporal granularity at which to generate aggregated features.
        For example, a granularity of 1 day means the aggregation materialized view will contain one row
        per primary key and per day since start_time until now. The minimum granularity is 1 hour.
        All window durations and offsets must be divisible by the granularity.
    :param start_time: The earliest time to generate aggregated features from. For example, a start_time of 2020-01-01
        means the aggregation materialized view will not contain any rows before this time.
        This will be the start of the first granularity interval.
    :param end_time: The latest time to generate aggregated features to. If None, it means the time of materialization
        pipeline run; if a datetime object, it means to use it as the end time.
    :param aggregations: A list of aggregations to perform. Each aggregation defines an output column.
    """

    def __init__(
        self,
        *,
        source_table: str,
        lookup_key: Union[str, List[str]],
        timestamp_key: str,
        granularity: datetime.timedelta,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        aggregations: List[Aggregation],
    ):
        """Initialize a FeatureAggregations object. See class documentation."""

        self._source_table = source_table
        self._lookup_key = copy.copy(lookup_key)
        self._timestamp_key = timestamp_key
        self._granularity = granularity
        self._start_time = start_time
        self._end_time = end_time
        self._aggregations = aggregations.copy()

        self._validate_parameters()

    def _validate_parameters(self):
        if (
            not isinstance(self._granularity, datetime.timedelta)
            or self._granularity < MIN_GRANULARITY
        ):
            raise ValueError(
                f"Granularity must be a datetime.timedelta of at least 1 hour. Received: {self._granularity}."
            )

        if self._granularity % MIN_GRANULARITY_UNIT != datetime.timedelta(0):
            raise ValueError(
                f"Granularity {self._granularity} must be divisible by {MIN_GRANULARITY_UNIT}."
            )

        if self._end_time is not None and self._end_time < self._start_time:
            raise ValueError(
                f"End time {self._end_time} cannot be earlier than start time {self._start_time}."
            )

        # Check that windows are divisible by granularity.
        for agg in self._aggregations:
            if agg.window.duration % self._granularity != datetime.timedelta(0):
                raise ValueError(
                    f"Window duration {agg.window.duration} must be divisible by granularity {self._granularity}."
                )

            if agg.window.offset % self._granularity != datetime.timedelta(0):
                raise ValueError(
                    f"Window offset {agg.window.offset} must be divisible by granularity {self._granularity}."
                )

    @property
    def source_table(self) -> str:
        """Returns the source table used for aggregation."""
        return self._source_table

    @property
    def lookup_key(self) -> Union[str, List[str]]:
        """Returns the lookup key(s) used for aggregation."""
        return self._lookup_key

    @property
    def timestamp_key(self) -> str:
        """Returns the timestamp key used for aggregation."""
        return self._timestamp_key

    @property
    def granularity(self) -> datetime.timedelta:
        """Returns the granularity at which features are aggregated."""
        return self._granularity

    @property
    def start_time(self) -> datetime.datetime:
        """Returns the start time from which to generate aggregated features."""
        return self._start_time

    @property
    def end_time(self) -> Optional[datetime.datetime]:
        """Returns the end time up to which to generate aggregated features."""
        return self._end_time

    @property
    def aggregations(self) -> List[Aggregation]:
        """Returns the list of aggregations to perform."""
        return self._aggregations

    def copy(self, **kwargs):
        """
        Create a copy of the current object with the specified attributes updated.

        :param kwargs: The attributes to update.
        :return: A new FeatureAggregations object with the specified attributes updated.
        """
        for p in self._properties():
            kwargs[p] = kwargs.get(p, getattr(self, p))

        return FeatureAggregations(**kwargs)

    def to_aggregation_info(self) -> AggregationInfo:
        return AggregationInfo(
            num_aggregation_columns=len(self._aggregations),
            aggregation_largest_window_seconds=max(
                int(agg.window.duration.total_seconds()) for agg in self._aggregations
            )
            if self._aggregations
            else 0,
            aggregation_start_time=int(self._start_time.timestamp()),
            aggregation_end_time=int(self._end_time.timestamp())
            if self._end_time is not None
            else 0,
            aggregation_granularity_seconds=int(self._granularity.total_seconds()),
            aggregation_function=",".join(
                sorted(set(agg.function.name for agg in self._aggregations))
            ),
        )
