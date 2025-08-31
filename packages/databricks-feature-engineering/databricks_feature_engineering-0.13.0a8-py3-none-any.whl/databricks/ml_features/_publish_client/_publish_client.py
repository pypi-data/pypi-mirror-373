import logging
import uuid
from typing import Any, Dict, List, Optional, Union

from mlflow.protos.databricks_pb2 import RESOURCE_DOES_NOT_EXIST, ErrorCode
from pyspark.sql.streaming import StreamingQuery

import databricks.ml_features.utils.validation_utils
from databricks.ml_features._catalog_client._catalog_client import CatalogClient
from databricks.ml_features._catalog_client._catalog_client_helper import (
    CatalogClientHelper,
)
from databricks.ml_features._online_store_publish_client._online_store_publish_client import (
    is_ttl_spec,
)
from databricks.ml_features._online_store_publish_client._online_store_publish_client_factory import (
    get_online_store_publish_client,
)
from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features._spark_client._spark_client_helper import SparkClientHelper
from databricks.ml_features.constants import MERGE, OVERWRITE
from databricks.ml_features.entities.online_store import DatabricksOnlineStore
from databricks.ml_features.entities.online_store_metadata import OnlineStoreMetadata
from databricks.ml_features.entities.published_table import PublishedTable
from databricks.ml_features.online_store_spec.online_store_spec import OnlineStoreSpec
from databricks.ml_features.utils import request_context, schema_utils, utils
from databricks.ml_features.utils.exceptions import ConflictError
from databricks.ml_features.utils.publish_utils import (
    update_online_store_spec_sticky_ttl,
)
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.rest_utils import get_error_code
from databricks.ml_features_common.utils import uc_utils
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors.platform import BadRequest, NotFound
from databricks.sdk.service.database import (
    SyncedDatabaseTable,
    SyncedTableSchedulingPolicy,
    SyncedTableSpec,
)
from databricks.sdk.service.ml import PublishSpec, PublishSpecPublishMode
from databricks.sdk.service.pipelines import PipelineState

_logger = logging.getLogger(__name__)


class PublishClient:
    _PUBLISH_MODES = [OVERWRITE, MERGE]

    def __init__(
        self,
        catalog_client: CatalogClient,
        catalog_client_helper: CatalogClientHelper,
        spark_client: SparkClient,
        spark_client_helper: SparkClientHelper,
        workspace_client: WorkspaceClient,
    ):
        self._catalog_client = catalog_client
        self._catalog_client_helper = catalog_client_helper
        self._spark_client = spark_client
        self._spark_client_helper = spark_client_helper
        self._workspace_client = workspace_client

    def _publish_table(
        self,
        name: str,
        online_store: OnlineStoreSpec,
        *,
        filter_condition: Optional[str],
        mode: str,
        streaming: bool,
        checkpoint_location: Optional[str],
        trigger: Dict[str, Any],
        features: Union[str, List[str], None],
        client_name: str,
    ) -> Optional[StreamingQuery]:
        is_uc_table = uc_utils.is_uc_entity(name)
        req_context = RequestContext(request_context.PUBLISH_TABLE, client_name)

        # Check: valid mode used
        mode_string = mode.strip().lower()
        if mode_string not in self._PUBLISH_MODES:
            supported_modes_list = ", ".join([f"'{m}'" for m in self._PUBLISH_MODES])
            raise ValueError(
                f"Unsupported mode '{mode}'. Use one of ({supported_modes_list})"
            )

        # Check: arguments and combination of arguments
        if streaming and mode == OVERWRITE:
            raise ValueError(
                f'Streaming publish_table does not support mode="{OVERWRITE}"'
            )

        # Empty input_features means the default behavior of publishing the entire table.
        input_features = utils.as_list(features, [])
        if input_features and mode == OVERWRITE:
            raise ValueError(
                f'publish_table for selected columns does not support mode="{OVERWRITE}"'
            )

        checkpoint_location = databricks.ml_features.utils.validation_utils.standardize_checkpoint_location(
            checkpoint_location
        )
        if checkpoint_location is not None and not streaming:
            _logger.warning("Ignoring checkpoint_location, since df is not streaming.")
            checkpoint_location = None

        self._verify_table_exists_in_delta_and_catalog(name, req_context)

        if is_uc_table:
            catalog_feature_table = self._catalog_client_helper.get_feature_table_from_uc_and_online_store_from_fs(
                name, req_context
            )
        else:
            catalog_feature_table = self._catalog_client.get_feature_table(
                name, req_context
            )
            # The below is only here to ensure that migration from get_feature_table to get_online_stores goes smoothly.
            # Can be removed if determined to be unnecessary.
            catalog_feature_table.online_stores = (
                self._catalog_client.get_online_stores([name], req_context)[name]
            )

        # Check: schema between delta table and in catalog
        hive_feature_table_df = self._spark_client.read_table(name, None)
        catalog_features = self._catalog_client.get_features(name, req_context) or []

        # ToDo(mparkhe): DRY this code with schema comparison in write_tables
        # Check: Primary keys
        if not schema_utils.catalog_matches_delta_schema(
            catalog_features,
            hive_feature_table_df.schema,
            column_filter=catalog_feature_table.primary_keys or [],
        ):
            primary_keys = [
                pk
                for pk in catalog_features
                if pk.name in catalog_feature_table.primary_keys
            ]
            raise ValueError(
                f"Mismatched primary keys. Primary keys in the catalog, '{primary_keys}' do not "
                f"match keys in the data table schema {hive_feature_table_df.schema}."
            )

        # Check: Partition columns
        if (
            catalog_feature_table.partition_columns
            and not schema_utils.catalog_matches_delta_schema(
                catalog_features,
                hive_feature_table_df.schema,
                column_filter=catalog_feature_table.partition_columns or [],
            )
        ):
            partition_columns = [
                pk
                for pk in catalog_features
                if pk.name in catalog_feature_table.partition_columns
            ]
            raise ValueError(
                f"Mismatched partition columns. Partition columns  in the catalog, "
                f"'{partition_columns}' do not match keys in the data table "
                f"schema {hive_feature_table_df.schema}."
            )

        catalog_feature_names = {feature.name for feature in catalog_features}

        features_to_publish = None
        if input_features:
            input_features_names_lower_case = [
                feature_name.lower() for feature_name in input_features
            ]
            catalog_feature_names_lower_case = [
                feature_name.lower() for feature_name in catalog_feature_names
            ]
            input_features_not_in_catalog = [
                feature_name
                for feature_name in input_features_names_lower_case
                if feature_name not in catalog_feature_names_lower_case
            ]

            if len(input_features_not_in_catalog) > 0:
                raise ValueError(
                    f"Unknown feature column names. Input features, "
                    f"'{input_features_not_in_catalog}' not found in Feature Store."
                )
            input_features_correct_case = [
                feature_name
                for feature_name in catalog_feature_names
                if feature_name.lower() in input_features_names_lower_case
            ]
            # Add required primary key and timestamp key columns to user input features if they are not already included.
            features_to_publish = list(
                set(input_features_correct_case).union(
                    set(catalog_feature_table.primary_keys),
                    set(catalog_feature_table.timestamp_keys),
                )
            )

        # Check: features listed in the catalog for publish are also available in the delta table
        catalog_feature_names_for_publish = (
            features_to_publish if features_to_publish else catalog_feature_names
        )
        features_for_publish_not_in_hive = [
            feature_name
            for feature_name in catalog_feature_names_for_publish
            if feature_name not in hive_feature_table_df.columns
        ]
        if len(features_for_publish_not_in_hive) > 0:
            raise RuntimeError(
                f"Schema mismatch. The following features being published were found in Feature Store, "
                f"but not in the data table: {sorted(features_for_publish_not_in_hive)}."
            )

        # check: features listed in the catalog not in the delta table and warn.
        # It warns when the selected columns we publish pass the previous check but there is a
        # mismatch for the unpublished columns.
        features_not_in_hive = [
            feature_name
            for feature_name in catalog_feature_names
            if feature_name not in hive_feature_table_df.columns
        ]
        if len(features_not_in_hive) > 0:
            _logger.warning(
                f"Schema mismatch. {features_not_in_hive} found in the feature catalog, "
                f"but were not found in the data table."
            )

        # Check: features not found catalog and warn.
        features_not_in_catalog = [
            feature_name
            for feature_name in hive_feature_table_df.columns
            if feature_name not in catalog_feature_names
        ]
        if len(features_not_in_catalog) > 0:
            if features_to_publish:
                _logger.warning(
                    f"Schema mismatch. {features_not_in_catalog} not found in the catalog. "
                )
            else:
                _logger.warning(
                    f"Schema mismatch. {features_not_in_catalog} not found in the catalog. "
                    f"Extra features in data table will not be published to the online store."
                )

        # Check: Time series publish attributes can only be used with time series feature tables.
        # This only needs to be checked prior to the first publish, as timestamp keys and ttl are immutable.
        # TTL is allowed to be None for both regular and time series (snapshot publish) feature tables.
        if is_ttl_spec(online_store) and online_store.ttl is not None:
            if len(catalog_feature_table.timestamp_keys) == 0:
                raise ValueError(
                    "Time to live can only be used with time series feature tables."
                )

        # Prepare DataFrame for publish
        publish_df = self._spark_client.read_table(
            name, as_of_delta_timestamp=None, streaming=streaming
        )

        # Filter rows
        if filter_condition:
            # force filtering before proceeding with other operations.
            # e.g. computing latest snapshot
            publish_df = publish_df.filter(filter_condition)
            # [ML-49081] caching the filtered dataframe does not work if it is streaming
            if not streaming:
                publish_df = publish_df.cache()

        # Only publish features that exist in the catalog.
        if len(features_not_in_catalog) > 0:
            selected_columns = [
                c for c in publish_df.columns if c not in features_not_in_catalog
            ]
            publish_df = publish_df.select(*selected_columns)

        # Only publish features that are selected by user.
        if features_to_publish:
            user_selected_columns = [
                c for c in publish_df.columns if c in features_to_publish
            ]
            _logger.info(
                f"The following features will be published to the online store: [{user_selected_columns}]."
            )
            publish_df = publish_df.select(*user_selected_columns)

        # Augment the online store spec (e.g. resolve and store implicit values as part of the spec)
        online_store = online_store._augment_online_store_spec(name)

        # TODO (ML-22021): validate that there is only one timestamp key prior to publishing
        os_publish_client = get_online_store_publish_client(online_store)
        online_table = os_publish_client.get_or_create_online_table(
            publish_df,
            catalog_feature_table.primary_keys,
            catalog_feature_table.timestamp_keys,
        )

        # Update catalog metadata with publish log
        try:
            # Create the online store metadata object for use in publish
            online_store_metadata = OnlineStoreMetadata(
                online_store, online_table.cloud_provider_unique_id
            )

            # Call GetOnlineStore and retrieve the OnlineStoreDetailed from the Feature Catalog.
            # Then, update the online store spec with any relevant sticky values returned (e.g. ttl).
            # If no online store is found, nothing needs to be done since this is a new store.
            try:
                online_store_detailed = self._catalog_client.get_online_store(
                    name, online_store_metadata, req_context
                )
                online_store = update_online_store_spec_sticky_ttl(
                    online_store, online_store_detailed
                )
                # Update the online store metadata object to reflect the updates for the online store spec.
                online_store_metadata = OnlineStoreMetadata(
                    online_store, online_table.cloud_provider_unique_id
                )
            except Exception as e:
                # All exceptions not caused by a non-existent online store should be re-raised.
                if get_error_code(e) != ErrorCode.Name(RESOURCE_DOES_NOT_EXIST):
                    raise e

            size_metrics = {
                request_context.NUM_ROWS: None,
                request_context.DATAFRAME_SIZE_IN_BYTES: None,
            }
            if not streaming:
                # Count number of rows in the df. This triggers df execution, which is ok because it will be
                # written to the online store which also requires execution right below anyway.
                # Delta table keeps row counts in its log, so this count just sums up all the stored counts
                # from each data file of the delta log. The speed grows linearly with the number of files and
                # should be acceptable - it is a very small percentage when compared to writing to online
                # stores.
                size_metrics[request_context.NUM_ROWS] = str(publish_df.count())
                try:
                    # https://kb.databricks.com/en_US/sql/find-size-of-table
                    # The size comes from Spark analyzer. `publish_df` originates from read_table,
                    # so Spark has the table metadata to calculate the size and `sizeInBytes` works here.
                    # Otherwise it would just return spark.sql.defaultSizeInBytes (which is Long.MaxValue).
                    dataframe_size = (
                        publish_df._jdf.queryExecution()
                        .analyzed()
                        .stats()
                        .sizeInBytes()
                    )
                    size_metrics[request_context.DATAFRAME_SIZE_IN_BYTES] = str(
                        dataframe_size
                    )
                except Exception as e:
                    # Using debug as this is only for instrumentation and doesn't affect users' operations
                    _logger.debug(
                        f"Failed to record the estimated size of dataframe. Exception: {e}",
                        exc_info=True,
                    )

            publish_req_context = RequestContext(
                request_context.PUBLISH_TABLE,
                client_name=client_name,
                # Instrumentation
                custom_headers={
                    request_context.IS_PUBLISH_FILTER_CONDITION_SPECIFIED: str(
                        filter_condition is not None
                    ).lower(),
                    request_context.IS_STREAMING: str(streaming).lower(),
                    request_context.IS_STREAMING_CHECKPOINT_SPECIFIED: (
                        str(checkpoint_location is not None).lower()
                        if streaming
                        else None
                    ),
                    request_context.NUM_FEATURES: str(len(publish_df.schema)),
                    request_context.PUBLISH_AUTH_TYPE: online_store.auth_type(),
                    request_context.STREAMING_TRIGGER: request_context.extract_streaming_trigger_header(
                        streaming, trigger
                    ),
                    request_context.TOTAL_NUM_FEATURES_IN_TABLE: str(
                        len(hive_feature_table_df.schema)
                    ),
                    request_context.WRITE_MODE: mode,
                    **size_metrics,
                },
            )
            # Resolve sticky values prior to calling PublishFeatureTable, as the `None` value is ambiguous.
            self._catalog_client.publish_feature_table(
                name,
                online_store_metadata,
                features_to_publish,
                publish_req_context,
            )
        except Exception as e:
            if online_table.is_new_empty_table:
                additional_msg = (
                    f"You may need to manually clean up the empty table '{online_table.name}' "
                    f"at the specified online store location. "
                )
            else:
                additional_msg = ""
            _logger.error(
                f"Failed to record online store in the catalog. {additional_msg}Exception: {e}",
                exc_info=True,
            )
            raise e

        # The lookback_window defaults to the online store TTL
        lookback_window = online_store.ttl if is_ttl_spec(online_store) else None

        # Create a new publish client, since the online store spec may have been updated.
        os_publish_client = get_online_store_publish_client(online_store)
        return os_publish_client.publish(
            publish_df,
            catalog_feature_table.primary_keys,
            catalog_feature_table.timestamp_keys,
            streaming,
            mode_string,
            trigger,
            checkpoint_location,
            lookback_window=lookback_window,
        )

    def _drop_online_table(
        self, feature_table_name: str, online_store: OnlineStoreSpec, client_name: str
    ) -> None:
        req_context = RequestContext(request_context.DROP_ONLINE_TABLE, client_name)

        # We want to add these checks to fail early and do not attempt to delete from
        # online store provider if user does not have access to feature table
        self._verify_table_exists_in_delta_and_catalog(
            feature_table_name,
            req_context,
        )

        # augment feature table name for default database/table name
        online_store = online_store._augment_online_store_spec(feature_table_name)
        os_publish_client = get_online_store_publish_client(online_store)
        # will throw here if online table does not exist in provider
        online_table = os_publish_client.get_online_table()
        # Create the online store metadata object for use in publish
        online_store_metadata = OnlineStoreMetadata(
            online_store, online_table.cloud_provider_unique_id
        )

        # call get online store to verify that the online store exists in databricks
        self._catalog_client.get_online_store(
            feature_table_name, online_store_metadata, req_context
        )

        _logger.warning(
            "Deleting an online published table can lead to unexpected failures in downstream "
            " dependencies. Ensure that the online table being dropped is no longer used for "
            " Model Serving feature lookup or any other use cases. "
        )

        # if table does not exist or user has inadequate permissions,
        # drop_online_table will raise an error and skip metadata deletion
        os_publish_client._drop_online_table(online_table.name)

        # delete online store metadata if online table dropped succesfully
        self._catalog_client.delete_online_store(
            feature_table_name, online_store_metadata, req_context
        )

        _logger.info(
            f"Published table {online_table.name} dropped from online store "
            "and removed from Databricks. "
        )

    def _verify_table_exists_in_delta_and_catalog(
        self, feature_table_name, req_context
    ):
        is_uc_table = uc_utils.is_uc_entity(feature_table_name)
        # Check: feature table exists as a delta table
        self._spark_client_helper.check_feature_table_exists(feature_table_name)

        # Check: feature tables exists in the catalog and user contains READ permissions
        if not is_uc_table and not self._catalog_client.feature_table_exists(
            feature_table_name, req_context
        ):
            raise ValueError(
                f"Feature table '{feature_table_name}' does not exist in the catalog."
            )

    def _publish_databricks_table(
        self,
        source_table_name: str,
        online_table_name: str,
        online_store: DatabricksOnlineStore,
        streaming: bool,
    ) -> PublishedTable:
        # TODO: switch to use feature store APIs when available

        source_table_info = self._workspace_client.tables.get(source_table_name)

        if source_table_info.properties.get("delta.enableChangeDataFeed") != "true":
            raise ValueError(
                f"Publishing to Online Feature Store requires change data feed enabled on the table '{source_table_name}'."
            )

        # Check if the online table already exists as a synced database table
        existing_online_table = self._try_get_existing_online_table(online_table_name)

        if existing_online_table is not None:
            return self._publish_to_existing_databricks_online_table(
                existing_online_table=existing_online_table,
                source_table_name=source_table_name,
                online_table_name=online_table_name,
                online_store=online_store,
            )

        # Publish to a new online table
        publish_mode = (
            PublishSpecPublishMode.CONTINUOUS
            if streaming
            else PublishSpecPublishMode.TRIGGERED
        )
        publish_table_response = self._workspace_client.feature_store.publish_table(
            source_table_name=source_table_name,
            publish_spec=PublishSpec(
                online_store=online_store.name,
                online_table_name=online_table_name,
                publish_mode=publish_mode,
            ),
        )

        return PublishedTable(
            online_table_name=publish_table_response.online_table_name,
            pipeline_id=publish_table_response.pipeline_id,
        )

    def _publish_to_existing_databricks_online_table(
        self,
        existing_online_table: SyncedDatabaseTable,
        source_table_name: str,
        online_table_name: str,
        online_store: DatabricksOnlineStore,
    ) -> PublishedTable:
        """
        Attempts to publish to an existing online table.
        """
        # Verify the source table that corresponds to the online table is the same as the provided source table
        if (
            existing_online_table.spec.source_table_full_name.lower()
            != source_table_name.lower()
        ):
            raise ValueError(
                f"Online table '{existing_online_table.name}' already exists with a different source table."
            )

        # verify the online table has a pipeline_id
        if not existing_online_table.data_synchronization_status.pipeline_id:
            raise ValueError(
                f"Cannot publish to online table '{existing_online_table.name}' because it is not linked to source table '{source_table_name}'."
            )

        scheduling_policy = existing_online_table.spec.scheduling_policy
        # Verify that the online table scheduling policy is not already set to continuously sync
        if scheduling_policy == SyncedTableSchedulingPolicy.CONTINUOUS:
            _logger.warning(
                f"Online table '{existing_online_table.name}' is already configured to continuously sync from source table '{source_table_name}'."
            )
        elif scheduling_policy == SyncedTableSchedulingPolicy.SNAPSHOT:
            raise ValueError(
                f"Cannot publish to online table '{existing_online_table.name}' because it is configured to snapshot sync from source table '{source_table_name}'."
            )
        else:
            pipeline = self._workspace_client.pipelines.get(
                existing_online_table.data_synchronization_status.pipeline_id
            )

            # Verify pipeline state
            if (
                pipeline.state == PipelineState.IDLE
                or pipeline.state == PipelineState.FAILED
            ):
                # TO-DO [ML-56408]: While the Feature Store SDK is not ready, rely on the call to the Pipelines SDK
                # to publish the existing online table and expect a no-op from the call to the Feature Store SDK.
                # When the Feature Store SDK is ready, remove the call to the Pipelines SDK and rely on the call
                # to the Feature Store SDK.
                self._workspace_client.pipelines.start_update(pipeline.pipeline_id)
                self._workspace_client.feature_store.publish_table(
                    source_table_name=source_table_name,
                    publish_spec=PublishSpec(
                        online_store=online_store.name,
                        online_table_name=online_table_name,
                        publish_mode=PublishSpecPublishMode.TRIGGERED,
                    ),
                )
            elif pipeline.state != PipelineState.RUNNING:
                # TODO: investigate and handle other pipeline states correctly
                raise ConflictError(
                    f"Cannot publish to online table '{existing_online_table.name}' because feature sync is in an unexpected state: {pipeline.state}."
                )

        return PublishedTable(
            online_table_name=existing_online_table.name,
            pipeline_id=existing_online_table.data_synchronization_status.pipeline_id,
        )

    def _try_get_existing_online_table(
        self, online_table_name: str
    ) -> Optional[SyncedDatabaseTable]:
        """
        Attempts to get an existing online table. Returns None if it doesn't exist.
        """
        try:
            return self._workspace_client.database.get_synced_database_table(
                online_table_name
            )
        except NotFound:
            # thrown if no table with the given name exists
            return None
        except BadRequest as e:
            if any(
                msg in str(e)
                for msg in (
                    "is not a synced database table",
                    "is a legacy synced database table",
                    "No workspace id from entity.",
                )
            ):
                # thrown if the table with the given name is not a Lakebase synced database table
                raise ValueError(
                    f"Cannot publish to existing table '{online_table_name}' because it is not an online feature table."
                )
            if "cannot handle API requests" in str(e):
                # thrown if the table with the given name is a Lakebase synced database table but is not ready for publish
                raise ValueError(
                    f"Cannot publish to existing online table '{online_table_name}' because it is not ready for publish."
                )
            raise ValueError(f"Cannot publish to '{online_table_name}': {e}")
