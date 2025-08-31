from dataclasses import dataclass
from enum import Enum
from typing import Optional

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.sdk.service.ml import OnlineStore


@dataclass
class DatabricksOnlineStore(_FeatureStoreObject):
    """
    A DatabricksOnlineStore is a database instance that stores and serves features online.
    :ivar name: The name of the online store.
    :ivar capacity: The capacity of the online store. Valid values are "CU_1", "CU_2", "CU_4", "CU_8".
    :ivar read_replica_count: The number of read replicas for the online store. Defaults to 0.
    :ivar creator: The email of the creator of the online store.
    :ivar creation_time: The timestamp when the online store was created in the RFC 3339 format (i.e., "YYYY-MM-DDTHH:MM:SSZ").
    :ivar state: The current state of the online store.
    """

    name: str
    capacity: str
    read_replica_count: Optional[int] = 0

    creator: Optional[str] = None
    creation_time: Optional[str] = None
    state: Optional["DatabricksOnlineStore.State"] = None

    class State(Enum):
        """
        The state of a DatabricksOnlineStore.
        """

        STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
        STARTING = "STARTING"
        AVAILABLE = "AVAILABLE"
        DELETING = "DELETING"
        STOPPED = "STOPPED"
        UPDATING = "UPDATING"
        FAILING_OVER = "FAILING_OVER"

    @classmethod
    def _from_online_store(cls, online_store: OnlineStore):
        """
        Create a DatabricksOnlineStore from an OnlineStore.
        """
        return cls(
            name=online_store.name,
            capacity=online_store.capacity,
            read_replica_count=online_store.read_replica_count,
            creator=online_store.creator,
            creation_time=online_store.creation_time,
            state=(
                cls.State(online_store.state.value)
                if online_store.state is not None
                else None
            ),
        )

    def _to_sdk_online_store(self) -> OnlineStore:
        """
        Create an OnlineStore from a DatabricksOnlineStore. Only fields that can be accepted as input are included.
        """
        return OnlineStore(
            name=self.name,
            capacity=self.capacity,
            read_replica_count=self.read_replica_count,
        )
