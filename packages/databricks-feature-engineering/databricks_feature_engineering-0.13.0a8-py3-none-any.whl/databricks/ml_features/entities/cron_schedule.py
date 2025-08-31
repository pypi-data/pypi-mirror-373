from typing import Optional

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class CronSchedule(_FeatureStoreObject):
    """
    Defines a cron schedule.

    :param quartz_cron_expression: The cron expression to use. See http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
    :param timezone_id: A Java timezone ID. The schedule for a job is resolved with respect to this timezone. If not provided, UTC will be used. See https://docs.oracle.com/javase/7/docs/api/java/util/TimeZone.html
    """

    def __init__(self, *, quartz_cron_expression: str, timezone_id: Optional[str]):
        """Initialize a CronSchedule object. See class documentation."""
        self._quartz_cron_expression = quartz_cron_expression
        self._timezone_id = timezone_id if timezone_id is not None else "UTC"

    @property
    def quartz_cron_expression(self) -> str:
        """The cron expression to use."""
        return self._quartz_cron_expression

    @property
    def timezone_id(self) -> str:
        """A Java timezone ID. The schedule for a job is resolved with respect to this timezone. See Java TimeZone for details."""
        return self._timezone_id
