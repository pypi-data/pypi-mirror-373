from typing import Dict

from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    FeatureTable as ProtoFeatureTable,
)
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.utils.utils_common import deprecated


class FeatureTable(_FeatureStoreObject):
    """
    .. note::

       Aliases:`!databricks.feature_engineering.entities.feature_table.FeatureTable`, `!databricks.feature_store.entities.feature_table.FeatureTable`

    Value class describing one feature table.

    This will typically not be instantiated directly, instead the
    :meth:`create_table() <databricks.feature_engineering.client.FeatureEngineeringClient.create_table>`
    will create :class:`.FeatureTable` objects.
    """

    def __init__(
        self,
        name,
        table_id,
        description,
        primary_keys,
        partition_columns,
        features,
        creation_timestamp=None,
        online_stores=None,
        notebook_producers=None,
        job_producers=None,
        table_data_sources=None,
        path_data_sources=None,
        custom_data_sources=None,
        timestamp_keys=None,
        tags=None,
    ):
        """Initialize a FeatureTable object."""
        self.name = name
        self.table_id = table_id
        self.description = description
        self.primary_keys = primary_keys
        self.partition_columns = partition_columns
        self.features = features
        self.creation_timestamp = creation_timestamp
        self.online_stores = online_stores if online_stores is not None else []
        self.notebook_producers = (
            notebook_producers if notebook_producers is not None else []
        )
        self.job_producers = job_producers if job_producers is not None else []
        self.table_data_sources = (
            table_data_sources if table_data_sources is not None else []
        )
        self.path_data_sources = (
            path_data_sources if path_data_sources is not None else []
        )
        self.custom_data_sources = (
            custom_data_sources if custom_data_sources is not None else []
        )
        self.timestamp_keys = timestamp_keys if timestamp_keys is not None else []
        self._tags = tags

    @property
    @deprecated("FeatureTable.primary_keys", since="v0.3.6")
    def keys(self):
        return self.primary_keys

    @property
    def tags(self) -> Dict[str, str]:
        """
        Get the tags associated with the feature table.

        :return a Dictionary of all tags associated with the feature table as key/value pairs
        """
        if self._tags is None:
            # If no tags are set, self._tags is expected an empty dictionary.
            raise ValueError(
                "Internal error: tags have not been fetched for this FeatureTable instance"
            )
        return self._tags

    @classmethod
    def from_proto(cls, feature_table_proto: ProtoFeatureTable):
        """Return a FeatureStore object from a proto.

        Note: `repeated` proto fields are cast from
              `google.protobuf.pyext._message.RepeatedScalarContainer`
              to list.

        :param FeatureTable feature_table_proto: Prototype for a :class:`.FeatureTable` object.
        :return FeatureTable: a FeatureStore object from a proto.
        """
        return cls(
            name=feature_table_proto.name,
            table_id=feature_table_proto.id,
            description=feature_table_proto.description,
            primary_keys=list(feature_table_proto.primary_keys),
            partition_columns=list(feature_table_proto.partition_keys),
            features=list(feature_table_proto.features),
            creation_timestamp=feature_table_proto.creation_timestamp,
            online_stores=list(feature_table_proto.online_stores),
            notebook_producers=list(feature_table_proto.notebook_producers),
            job_producers=list(feature_table_proto.job_producers),
            table_data_sources=[
                s.table for s in feature_table_proto.data_sources if s.table
            ],
            path_data_sources=[
                s.path for s in feature_table_proto.data_sources if s.path
            ],
            custom_data_sources=[
                s.custom_source
                for s in feature_table_proto.data_sources
                if s.custom_source
            ],
            timestamp_keys=list(feature_table_proto.timestamp_keys),
            tags=None,
        )

    @classmethod
    def from_uc_get_table_response(cls, uc_get_table_response: Dict[str, object]):
        """Return a FeatureStore object from a UC get_table response. Note: UC does not return online_stores or tags.

        :param dict uc_get_table_response: A dictionary representing a UC get_table response.
        :return FeatureTable: a FeatureStore object from the UC response.
        """
        table_name = uc_get_table_response["full_name"]

        if uc_get_table_response["securable_kind"] == "TABLE_ONLINE_VIEW":
            source_table = uc_get_table_response["properties_pairs"]["properties"][
                "source_table"
            ]
            raise ValueError(
                f"Table '{table_name}' is an online view. Online Views are not feature tables. Please use the source table '{source_table}' instead."
            )

        if (
            "table_type" in uc_get_table_response
            and uc_get_table_response["table_type"] == "VIEW"
        ):
            return cls(
                name=table_name,
                table_id=uc_get_table_response["table_id"],
                description=uc_get_table_response["comment"]
                if "comment" in uc_get_table_response
                else "",
                primary_keys=[],
                partition_columns=[],
                features=[],
                creation_timestamp=uc_get_table_response["created_at"],
                timestamp_keys=[],
            )

        table_constraints = (
            uc_get_table_response["table_constraints"]
            if "table_constraints" in uc_get_table_response
            else []
        )
        primary_key_constraints = [
            c for c in table_constraints if "primary_key_constraint" in c
        ]
        if len(primary_key_constraints) == 0:
            raise ValueError(
                "Table can't be used as a feature table because it has no primary key constraint defined."
                + " Use 'ALTER TABLE table_name ADD CONSTRAINT table_name_pk PRIMARY KEY( key_column [,...] )'"
                + " to add a primary key constraint on the table."
            )
        primary_key_constraint = primary_key_constraint = primary_key_constraints[0][
            "primary_key_constraint"
        ]
        timestamp_keys = (
            primary_key_constraint["timeseries_columns"]
            if "timeseries_columns" in primary_key_constraint
            else []
        )
        primary_keys = [
            c
            for c in primary_key_constraint["child_columns"]
            if c not in timestamp_keys
        ]

        columns = uc_get_table_response["columns"]
        features = [c["name"] for c in columns]
        partition_columns_unordered = [c for c in columns if "partition_index" in c]
        partition_columns = [
            c["name"]
            for c in sorted(
                partition_columns_unordered, key=lambda x: x["partition_index"]
            )
        ]

        return cls(
            name=table_name,
            table_id=uc_get_table_response["table_id"],
            description=uc_get_table_response["comment"]
            if "comment" in uc_get_table_response
            else "",
            primary_keys=primary_keys,
            partition_columns=partition_columns,
            features=features,
            creation_timestamp=uc_get_table_response["created_at"],
            timestamp_keys=timestamp_keys,
        )
