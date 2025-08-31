import logging
import re
from typing import Any, Dict, List, Optional, Union

from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import StructType
from pyspark.sql.utils import AnalysisException

from databricks.ml_features._catalog_client._catalog_client import CatalogClient
from databricks.ml_features._catalog_client._catalog_client_helper import (
    CatalogClientHelper,
)
from databricks.ml_features._databricks_client._databricks_client import (
    DatabricksClient,
)
from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features._spark_client._spark_client_helper import SparkClientHelper
from databricks.ml_features.api.proto.feature_catalog_pb2 import ProducerAction
from databricks.ml_features.constants import (
    _DEFAULT_WRITE_STREAM_TRIGGER,
    _ERROR,
    _SOURCE_FORMAT_DELTA,
    _WARN,
    DATA_TYPES_REQUIRES_DETAILS,
    MERGE,
    OVERWRITE,
)
from databricks.ml_features.entities.data_type import DataType
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.entities.key_spec import KeySpec
from databricks.ml_features.entities.materialized_feature import MaterializedFeature
from databricks.ml_features.entities.online_store_metadata import (
    CosmosDbMetadata,
    DynamoDbMetadata,
    MySqlMetadata,
    SqlServerMetadata,
)
from databricks.ml_features.utils import (
    request_context,
    schema_utils,
    utils,
    validation_utils,
)
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.spark_listener import SparkSourceListener
from databricks.ml_features_common.entities.store_type import StoreType
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    OnlineStore as ProtoOnlineStore,
)
from databricks.ml_features_common.utils import uc_utils

_logger = logging.getLogger(__name__)


class ComputeClient:
    """
    The compute client manages metadata about feature tables, eg:

    - Creating/registering feature tables
    - Reading feature table metadata
    - Dropping feature tables from the catalog
    - Managing attributes of feature tables such as tags
    """

    _WRITE_MODES = [OVERWRITE, MERGE]

    def __init__(
        self,
        catalog_client: CatalogClient,
        catalog_client_helper: CatalogClientHelper,
        spark_client: SparkClient,
        spark_client_helper: SparkClientHelper,
        databricks_client: DatabricksClient,
    ):
        self._catalog_client = catalog_client
        self._catalog_client_helper = catalog_client_helper
        self._spark_client = spark_client
        self._spark_client_helper = spark_client_helper
        self._databricks_client = databricks_client

    def create_table(
        self,
        name: str,
        primary_keys: Union[str, List[str]],
        df: Optional[DataFrame],
        *,
        timestamp_keys: Union[str, List[str], None],
        partition_columns: Union[str, List[str], None],
        schema: Optional[StructType],
        description: Optional[str],
        tags: Optional[Dict[str, str]],
        client_name: str,
        **kwargs,
    ) -> FeatureTable:
        features_df = kwargs.pop("features_df", None)
        if features_df is not None and df is not None:
            raise ValueError("Either features_df or df can be provided, but not both.")
        if features_df is not None:
            _logger.warning(
                'The "features_df" parameter is deprecated. Use "df" instead.'
            )
            df = features_df
        path = kwargs.pop("path", None)
        if path is not None and uc_utils.is_uc_entity(name):
            raise ValueError("Path argument is not supported for Unity Catalog tables.")
        validation_utils.check_kwargs_empty(kwargs, "create_table")

        return self._create_table(
            name,
            primary_keys,
            df,
            timestamp_keys=timestamp_keys,
            partition_columns=partition_columns,
            schema=schema,
            description=description,
            path=path,
            tags=tags,
            req_context=RequestContext(
                request_context.CREATE_TABLE, client_name=client_name
            ),
        )

    def _create_table(
        self,
        name: str,
        primary_keys: Union[str, List[str]],
        df: DataFrame,
        *,
        timestamp_keys: Union[str, List[str]],
        partition_columns: Union[str, List[str]],
        schema: StructType,
        description: str,
        path: Optional[str],
        tags: Optional[Dict[str, str]],
        req_context: Optional[RequestContext],
    ) -> FeatureTable:
        is_uc_table = uc_utils.is_uc_entity(name)

        # Validate no duplicated keys for primary_keys and timestamp_keys
        validation_utils.check_duplicate_keys(primary_keys, "primary_keys")
        validation_utils.check_duplicate_keys(timestamp_keys, "timestamp_keys")

        # Allow TK in PK, warn if not all TKs are in PKs; and
        # Extract TK from PK for service compatibility.
        (
            primary_keys,
            timestamp_keys,
        ) = validation_utils.check_and_extract_timestamp_keys_in_primary_keys(
            primary_keys, timestamp_keys
        )

        if schema is None and df is None:
            raise ValueError("Either schema or df must be provided")

        if schema and df and not ComputeClient._schema_eq(schema, df.schema):
            raise ValueError(
                "Provide either 'schema' or 'df' arguments. If both arguments "
                "are provided, their schemas must match."
            )

        if df is not None:
            validation_utils.check_dataframe_type(df)
        self._spark_client_helper.check_catalog_database_exists(name)

        table_schema = schema or df.schema
        ComputeClient._check_schema_top_level_types_supported(table_schema)

        partition_cols_as_list = utils.as_list(partition_columns, default=[])
        if partition_columns:
            ComputeClient._check_schema_has_columns(
                table_schema, partition_cols_as_list, "partition columns"
            )

        primary_keys_as_list = utils.as_list(primary_keys)
        ComputeClient._check_schema_has_columns(
            table_schema, primary_keys_as_list, "primary keys"
        )

        timestamp_keys_as_list = utils.as_list(timestamp_keys, default=[])
        if timestamp_keys:
            ComputeClient._check_schema_has_columns(
                table_schema, timestamp_keys_as_list, "timestamp keys"
            )

        # 1. Handle cases where the table exists in either Hive or the Catalog
        delta_table_exists = self._spark_client.table_exists(name)
        catalog_table_exists = (
            delta_table_exists
            if is_uc_table
            else self._catalog_client.feature_table_exists(name, req_context)
        )

        if delta_table_exists and not catalog_table_exists:
            raise ValueError(f"Data table {name} already exists. Use a different name.")

        if catalog_table_exists and not delta_table_exists:
            raise ValueError(
                f"Feature table {name} already exists, but data table not accessible in Spark. "
                f"Consider deleting the feature table to resolve this error."
            )

        if catalog_table_exists and delta_table_exists:
            if not is_uc_table:
                self._check_catalog_matches_delta_metadata(
                    name,
                    table_schema,
                    primary_keys_as_list,
                    partition_cols_as_list,
                    timestamp_keys_as_list,
                    req_context,
                )
            return self.get_table(name, req_context)

        # At this point, neither the Delta table nor the Catalog table exist.

        # 2. Create empty Delta table. If this fails for some reason, the Feature Table will not be
        # added to the Feature Catalog.
        # If the table is in UC, use the description as table comment
        table_comment = description if is_uc_table else None
        self._spark_client.create_table(
            name, table_schema, partition_cols_as_list, path, table_comment
        )

        if is_uc_table:
            try:
                # Set PK/TK constraint on the Delta table if there is not existing PK/TK constraint
                self._set_pk_tk_if_not_exist(
                    full_table_name=name,
                    primary_keys=primary_keys_as_list,
                    timestamp_keys=timestamp_keys_as_list,
                )
            except Exception as e:
                # Delete empty Delta table.
                self._spark_client.delete_empty_table(name)
                raise e

        # 3. Add feature table and features to the Feature Catalog.
        # Features (other than primary keys and partition keys) are added in a separate call.
        delta_schema = {
            feature.name: feature.dataType
            for feature in self._spark_client.get_feature_table_schema(name)
        }

        partition_key_specs = []
        for k in partition_cols_as_list:
            spark_data_type = delta_schema[k]
            partition_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        primary_key_specs = []
        for k in primary_keys_as_list:
            spark_data_type = delta_schema[k]
            primary_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        timestamp_key_specs = []
        for k in timestamp_keys_as_list:
            spark_data_type = delta_schema[k]
            timestamp_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        feature_key_specs = self._get_feature_key_specs(
            delta_schema,
            primary_keys_as_list,
            timestamp_keys_as_list,
            partition_cols_as_list,
        )

        try:
            self._create_feature_table_with_features_and_tags(
                name=name,
                partition_key_specs=partition_key_specs,
                primary_key_specs=primary_key_specs,
                timestamp_key_specs=timestamp_key_specs,
                description=None if is_uc_table else description,
                is_imported=False,
                feature_key_specs=feature_key_specs,
                tags=tags,
                req_context=req_context,
            )
        except Exception as e:
            # Delete empty Delta table.  The feature table will have already been cleaned up from the catalog.
            self._spark_client.delete_empty_table(name)
            raise e

        # 4. Write to Delta table
        if df is not None:
            try:
                # Use mode OVERWRITE since this a new feature table.
                self.write_table(
                    name,
                    df,
                    mode=OVERWRITE,
                    checkpoint_location=None,
                    trigger=_DEFAULT_WRITE_STREAM_TRIGGER,
                    producer_action=ProducerAction.CREATE,
                    req_context=req_context,
                )
            except Exception as e:
                # Delete the entire delta table if fatal exception occurs.
                # This may happen after partial data was written and an unknown exception is thrown.
                # It is OK to delete the feature table here because we are certain this is the
                # feature table we just created. We should NOT delete any existing feature table
                # created by user
                self._spark_client.delete_table(name)
                self._catalog_client.delete_feature_table(name, req_context)
                raise e

        _logger.info(f"Created feature table '{name}'.")
        return self.get_table(name, req_context)

    def register_table(
        self,
        *,
        delta_table: str,
        primary_keys: Union[str, List[str]],
        timestamp_keys: Union[str, List[str], None],
        description: Optional[str],
        tags: Optional[Dict[str, str]],
        client_name: str,
    ) -> FeatureTable:
        is_uc_table = uc_utils.is_uc_entity(delta_table)

        # Validate no duplicated keys for primary_keys and timestamp_keys
        validation_utils.check_duplicate_keys(primary_keys, "primary_keys")
        validation_utils.check_duplicate_keys(timestamp_keys, "timestamp_keys")

        # Allow TK in PK, warn if not all TKs are in PKs; and
        # Extract TK from PK for service compatibility.
        (
            primary_keys,
            timestamp_keys,
        ) = validation_utils.check_and_extract_timestamp_keys_in_primary_keys(
            primary_keys, timestamp_keys
        )

        # Validate if the provided table exists.
        req_context = RequestContext(request_context.REGISTER_TABLE, client_name)
        self._spark_client_helper.check_catalog_database_exists(delta_table)
        if not self._spark_client.table_exists(delta_table):
            raise ValueError(
                f"The provided Delta table '{delta_table}' could not be found."
            )

        # Only Delta tables can be registered
        if not self._spark_client.is_delta_table(delta_table):
            raise ValueError(
                f"The provided table '{delta_table}' is not a Delta table. "
                f"Use 'DESCRIBE TABLE EXTENDED' SQL command to verify table type."
            )

        df = self._spark_client.read_table(delta_table)

        # Validate if the provided Delta table is feature store compliant
        # 1. Check if the Delta table contains valid types and the specified primary key and
        #    timestamp key columns.
        table_schema = df.schema
        ComputeClient._check_schema_top_level_types_supported(table_schema)

        primary_keys_as_list = utils.as_list(primary_keys)
        ComputeClient._check_schema_has_columns(
            table_schema, primary_keys_as_list, "primary keys"
        )

        timestamp_keys_as_list = utils.as_list(timestamp_keys, default=[])
        if timestamp_keys:
            ComputeClient._check_schema_has_columns(
                table_schema, timestamp_keys_as_list, "timestamp keys"
            )

        # 2. Check that the Delta table does not contain generated columns.
        #    More details: go/import_delta_table
        if self._spark_client.has_generated_columns(delta_table):
            raise ValueError(
                f"Provided Delta table must not contain generated column(s)."
            )
        # 3. Handle the case where the Delta table is already a feature table.
        if self._catalog_client.feature_table_exists(delta_table, req_context):
            self._check_catalog_matches_delta_metadata(
                delta_table,
                table_schema,
                primary_keys_as_list,
                utils.as_list(
                    self._spark_client.get_partition_columns_for_delta_table(
                        delta_table
                    ),
                    default=[],
                ),
                timestamp_keys_as_list,
                req_context,
            )
            return self.get_table(delta_table, req_context)

        # 4. Check no two rows have the same primary keys.
        if self._spark_client.df_violates_pk_constraint(
            df, primary_keys_as_list + timestamp_keys_as_list
        ):
            raise ValueError(
                f"Non-unique rows detected in input dataframe for key combination"
                f"{primary_keys_as_list + timestamp_keys_as_list}."
            )

        # Register the table with feature store
        delta_schema = {feature.name: feature.dataType for feature in table_schema}
        primary_key_specs = []
        for k in primary_keys_as_list:
            spark_data_type = delta_schema[k]
            primary_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        timestamp_key_specs = []
        for k in timestamp_keys_as_list:
            spark_data_type = delta_schema[k]
            timestamp_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        partition_columns_as_list = utils.as_list(
            self._spark_client.get_partition_columns_for_delta_table(delta_table),
            default=[],
        )
        partition_key_specs = []
        for k in partition_columns_as_list:
            spark_data_type = delta_schema[k]
            partition_key_specs.append(KeySpec(k, spark_data_type.typeName()))

        feature_key_specs = self._get_feature_key_specs(
            delta_schema,
            primary_keys_as_list,
            timestamp_keys_as_list,
            partition_columns_as_list,
        )

        self._create_feature_table_with_features_and_tags(
            name=delta_table,
            partition_key_specs=partition_key_specs,
            primary_key_specs=primary_key_specs,
            timestamp_key_specs=timestamp_key_specs,
            description=None if is_uc_table else description,
            is_imported=True,
            feature_key_specs=feature_key_specs,
            tags=tags,
            req_context=req_context,
        )

        self._catalog_client_helper.add_job_or_notebook_producer(
            delta_table, ProducerAction.REGISTER, req_context
        )

        # Update table comment if it is UC table
        # Note that we do not unset the table's comment when desciption is None, as it might surprise users.
        if is_uc_table and description is not None:
            self._spark_client.set_table_comment(delta_table, description)

        return self.get_table(delta_table, req_context)

    def write_table(
        self,
        name: str,
        df: DataFrame,
        mode: str,
        checkpoint_location: Union[str, None],
        trigger: Dict[str, Any],
        producer_action: ProducerAction,
        req_context: RequestContext,
    ) -> Union[StreamingQuery, None]:
        """
        Write to a feature table.

        If the input :class:`DataFrame <pyspark.sql.DataFrame>` is streaming, will create a write stream.

        :param name: A feature table name of the form ``<database_name>.<table_name>``,
          for example ``dev.user_features``. Raises an exception if this feature table does not
          exist.
        :param df: Spark :class:`DataFrame <pyspark.sql.DataFrame>` with feature data. Raises an exception if the schema does not
          match that of the feature table.
        :param mode: Two supported write modes:

          * ``"overwrite"`` updates the whole table.

          * ``"merge"`` will upsert the rows in ``df`` into the feature table. If ``df`` contains
            columns not present in the feature table, these columns will be added as new features.

        :param checkpoint_location: Sets the Structured Streaming ``checkpointLocation`` option.
          By setting a ``checkpoint_location``, Spark Structured Streaming will store
          progress information and intermediate state, enabling recovery after failures.
          This parameter is only supported when the argument ``df`` is a streaming :class:`DataFrame <pyspark.sql.DataFrame>`.
        :param trigger: If ``df.isStreaming``, ``trigger`` defines the timing of stream data
          processing, the dictionary will be unpacked and passed to :meth:`DataStreamWriter.trigger <pyspark.sql.streaming.DataStreamWriter.trigger>`
          as arguments. For example, ``trigger={'once': True}`` will result in a call to
          ``DataStreamWriter.trigger(once=True)``.
        :return: If ``df.isStreaming``, returns a PySpark :class:`StreaminQuery <pyspark.sql.streaming.StreamingQuery>`, :obj:`None` otherwise.
        """
        is_uc_table = uc_utils.is_uc_entity(name)

        validation_utils.check_dataframe_type(df)
        mode_string = mode.strip().lower()
        if mode_string not in self._WRITE_MODES:
            supported_modes_list = ", ".join([f"'{m}'" for m in self._WRITE_MODES])
            raise ValueError(
                f"Unsupported mode '{mode}'. Use one of {supported_modes_list}"
            )

        checkpoint_location = validation_utils.standardize_checkpoint_location(
            checkpoint_location
        )
        if checkpoint_location is not None and not df.isStreaming:
            _logger.warning("Ignoring checkpoint_location, since df is not streaming.")
            checkpoint_location = None

        ComputeClient._check_schema_top_level_types_supported(df.schema)
        self._spark_client_helper.check_feature_table_exists(name)
        if is_uc_table:
            feature_table = self._catalog_client_helper.get_feature_table_from_uc_and_online_store_from_fs(
                name, req_context
            )
        else:
            feature_table = self._catalog_client.get_feature_table(name, req_context)
            # The below is only here to ensure that migration from get_feature_table to get_online_stores goes smoothly.
            # Can be removed if determined to be unnecessary.
            feature_table.online_stores = self._catalog_client.get_online_stores(
                [name], req_context
            )[name]

        if not is_uc_table:
            # We know from the successful `get_feature_table call` above that the user has
            # at least read permission. Otherwise backend will throw RESOURCE_DOES_NOT_EXIST exception.
            # Since this is a write operation, we want to check whether the user has write permission
            # on the feature table prior to other operations.
            # We don't need this check for tables in UC as UC manages the permissions.
            if not self._catalog_client.can_write_to_catalog(name, req_context):
                raise PermissionError(
                    f"You do not have permission to write to feature table {name}."
                )

        # Validate: Internal state is consistent. Existing Delta schema should match Catalog schema.
        features = self._catalog_client.get_features(name, req_context)
        existing_schema = self._spark_client.get_feature_table_schema(name)
        if not schema_utils.catalog_matches_delta_schema(features, existing_schema):
            # If the existing Delta table does not match the Feature Catalog, the state is invalid
            # and we cannot write to the feature table. Error out.
            schema_utils.log_catalog_schema_not_match_delta_schema(
                features, existing_schema, level=_ERROR
            )

        # Validate: Provided DataFrame has key and partition columns
        if not schema_utils.catalog_matches_delta_schema(
            features, df.schema, column_filter=feature_table.primary_keys
        ):
            raise ValueError(
                f"The provided DataFrame must contain all specified primary key columns and have "
                f"the same type. Could not find key(s) '{feature_table.primary_keys}' with "
                f"correct types in schema {df.schema}."
            )
        if not schema_utils.catalog_matches_delta_schema(
            features, df.schema, column_filter=feature_table.partition_columns
        ):
            raise ValueError(
                f"The provided DataFrame must contain all specified partition columns and have "
                f"the same type. Could not find partition column(s) "
                f"'{feature_table.partition_columns}' with correct types in schema {df.schema}."
            )
        if not schema_utils.catalog_matches_delta_schema(
            features, df.schema, column_filter=feature_table.timestamp_keys
        ):
            raise ValueError(
                f"The provided DataFrame must contain the specified timestamp key column "
                f"and have the same type. Could not find key '{feature_table.timestamp_keys[0]}' "
                f"with correct types in schema {df.schema}."
            )

        # Invariant: We know from a validation check above that the Delta table schema matches the
        # Catalog schema.

        # Check for schema differences between the Catalog feature table and df's schema.
        if not schema_utils.catalog_matches_delta_schema(features, df.schema):
            # If this is a feature table with point-in-time lookup timestamp keys.
            # Validate: all existing table columns are present in the df.
            if feature_table.timestamp_keys:
                feature_names = [feature.name for feature in features]
                df_column_names = [c.name for c in df.schema]
                missing_column_names = list(set(feature_names) - set(df_column_names))
                if missing_column_names:
                    raise ValueError(
                        f"Feature table has a timestamp column. When calling write_table "
                        f"the provided DataFrame must contain all the feature columns. "
                        f"Could not find column(s) '{missing_column_names}'."
                    )
            # Attempt to update both the Delta table and Catalog schemas.
            # New columns will be added, column type mismatch will raise an error.
            ComputeClient._check_unique_case_insensitive_schema(features, df.schema)
            # First update the Delta schema. Spark will handle any type changes, and throw on
            # incompatible types.
            self._update_delta_features(name, df.schema)
            # Now update the Catalog using *the types in the Delta table*. We do not use the types
            # in `df` here so we can defer schema merging logic to Spark.
            delta_schema = self._spark_client.get_feature_table_schema(name)
            if not is_uc_table:
                self._update_catalog_features_with_delta_schema(
                    name, feature_table, features, delta_schema, req_context
                )
        else:
            delta_schema = df.schema

        # Write data to Delta table
        return_value = (
            self._spark_client.write_table(
                name,
                utils.sanitize_identifiers(feature_table.primary_keys),
                utils.sanitize_identifiers(feature_table.timestamp_keys),
                df,
                mode_string,
                checkpoint_location,
                trigger,
            )
            if is_uc_table
            else self._write_table_with_spark_listener(
                name=name,
                feature_table=feature_table,
                df=df,
                mode_string=mode_string,
                checkpoint_location=checkpoint_location,
                trigger=trigger,
                req_context=req_context,
            )
        )

        # record producer to feature catalog, with additional instrumentation headers if the method name is write_table
        if (
            req_context.get_header(request_context.FEATURE_STORE_METHOD_NAME)
            == request_context.WRITE_TABLE
        ):
            add_producer_custom_headers = {
                request_context.IS_STREAMING: str(df.isStreaming).lower(),
                request_context.IS_STREAMING_CHECKPOINT_SPECIFIED: (
                    str(checkpoint_location is not None).lower()
                    if df.isStreaming
                    else None
                ),
                request_context.NUM_FEATURES: str(len(df.schema)),
                request_context.STREAMING_TRIGGER: request_context.extract_streaming_trigger_header(
                    df.isStreaming, trigger
                ),
                request_context.TOTAL_NUM_FEATURES_IN_TABLE: str(len(delta_schema)),
                request_context.WRITE_MODE: mode_string,
            }
            add_producer_req_context = RequestContext.with_additional_custom_headers(
                req_context, add_producer_custom_headers
            )
        else:
            add_producer_req_context = req_context

        self._catalog_client_helper.add_job_or_notebook_producer(
            name, producer_action, add_producer_req_context
        )

        return return_value

    def _write_table_with_spark_listener(
        self,
        name: str,
        feature_table: FeatureTable,
        df: DataFrame,
        mode_string: str,
        checkpoint_location: Union[str, None],
        trigger: Dict[str, Any],
        req_context: RequestContext,
    ):
        with SparkSourceListener() as spark_source_listener:
            return_value = self._spark_client.write_table(
                name,
                utils.sanitize_identifiers(feature_table.primary_keys),
                utils.sanitize_identifiers(feature_table.timestamp_keys),
                df,
                mode_string,
                checkpoint_location,
                trigger,
            )
            subscribed_data_sources = spark_source_listener.get_data_sources()

        # Exclude self-referential data sources. Feature table should exist.
        feature_table_data_source = self._spark_client.get_delta_table_path(name)
        # set(None) can produce exception, set default to empty list
        excluded_paths = set(utils.as_list(feature_table_data_source, default=[]))
        # filter the delta checkpoint file.
        # regexp refer: delta-standalone/src/main/scala/io/delta/standalone/internal/util/FileNames.scala?L27
        checkpoint_file_pattern = r"\d+\.checkpoint(\.\d+\.\d+)?\.parquet"

        tables = set()
        paths = set()
        for fmt, sources in subscribed_data_sources.items():
            # filter out source that are an exact match to the excluded paths.
            # ToDo(mparkhe): Currently Spark listener will not return subdirs as data sources,
            #                but in future investigate a clean mechanism to deduplicate,
            #                and eliminate redundant subdirs reported as (Delta) data sources.
            #                eg: ["dbfs:/X.db/Y", "dbfs:/X.db/Y/_delta_log/checkpoint..."]
            valid_sources = list(
                filter(
                    lambda source: all(
                        [
                            source not in excluded_paths,
                            not re.match(
                                checkpoint_file_pattern, source.split("/")[-1]
                            ),
                        ]
                    ),
                    sources,
                )
            )
            if len(valid_sources) > 0:
                # We rely on the spark listener to determine whether a data source is a delta table
                # for now. However, spark listener categorize delta table by looking up the
                # leaf node in spark query plan whereas we categorize delta table by whether or not
                # it would show up in the `Data` tab. Inconsistency could happen if user reads a
                # delta directory as delta table through `spark.read.format("delta")`,
                # we should store such data source as a path rather than a delta table.
                if fmt == _SOURCE_FORMAT_DELTA:
                    for path in valid_sources:
                        # Convert table-paths to "db_name.table_name".
                        # Note: If a table-path does not match the top level DBFS path
                        #       it is preserved as is.
                        converted_table = self._spark_client.convert_to_table_format(
                            path
                        )
                        if converted_table == path:
                            # Failed to convert table-path to "db_name.table_name",
                            # record data source as a path
                            paths.add(path)
                        else:
                            tables.add(converted_table)
                            # Exclude DBFS paths for all the table data sources
                            excluded_paths.add(path)
                else:
                    paths.update(valid_sources)

        # filter out paths match or are subdirectory (or files) under excluded paths
        # Example: if excluded_paths = ["dbfs:/path/to/database.db/table]
        #          also exclude sub-paths like "dbfs:/path/to/database.db/table/subpath"
        #          but do not exclude "dbfs:/path/to/database.db/tablesubdir"
        # ToDo(mparkhe): In future investigate a clean mechanism to eliminate subdirs
        #                of path sources, if returned by Spark listener.
        #                eg: ["dbfs:/X/Y", "dbfs:/X/Y/subdir"] => ["dbfs:/X/Y"]
        valid_paths = list(
            filter(
                lambda source: all(
                    [
                        source != excluded_path
                        and not source.startswith(utils.as_directory(excluded_path))
                        for excluded_path in excluded_paths
                    ]
                ),
                paths,
            )
        )

        # record data sources to feature catalog
        if len(tables) > 0 or len(valid_paths) > 0:
            self._catalog_client_helper.add_data_sources(
                name=name,
                tables=tables,
                paths=valid_paths,
                custom_sources=set(),  # No custom_sources in auto tracked data sources
                req_context=req_context,
            )
        return return_value

    def get_table(
        self, name: str, req_context: RequestContext, include_producers=True
    ) -> FeatureTable:
        """
        Returns a full FeatureTable entity with tags attached.
         - include_producers has default True to avoid changing existing client behavior.
         - Includes the timestamp key a part of the primary key in the returned FeatureTable

        Warns if the catalog schema does not match the delta table schema.
        Avoid using this method when simpler metadata access (e.g. directly calling GetFeatureTable) will suffice.
        """
        is_uc_table = uc_utils.is_uc_entity(name)

        self._spark_client_helper.check_feature_table_exists(name)
        if is_uc_table:
            feature_table = self._catalog_client_helper.get_feature_table_from_uc_and_online_store_from_fs(
                name, req_context, include_producers=include_producers
            )
        else:
            feature_table = self._catalog_client.get_feature_table(
                name, req_context, include_producers=include_producers
            )
            # The below is only here to ensure that migration from get_feature_table to get_online_stores goes smoothly.
            # Can be removed if determined to be unnecessary.
            feature_table.online_stores = self._catalog_client.get_online_stores(
                [name], req_context
            )[name]
        features = self._catalog_client.get_features(name, req_context)
        feature_table.online_stores = self._catalog_client.get_online_stores(
            [name], req_context
        )[name]
        df = self._spark_client.read_table(name)
        if not schema_utils.catalog_matches_delta_schema(features, df.schema):
            schema_utils.log_catalog_schema_not_match_delta_schema(
                features, df.schema, level=_WARN
            )
        if is_uc_table:
            tags = self._databricks_client.get_uc_table_tags(name)
            feature_table._tags = tags
        else:
            tag_entities = self._catalog_client.get_feature_table_tags(
                feature_table.table_id, req_context
            )
            tag_entities_dict = {
                tag_entity.key: tag_entity.value for tag_entity in tag_entities
            }
            feature_table._tags = tag_entities_dict

        # Make TK part of PK
        original_pk = feature_table.primary_keys
        feature_table.primary_keys = original_pk + [
            tk for tk in feature_table.timestamp_keys if tk not in original_pk
        ]
        return feature_table

    def drop_table(self, name: str, client_name: str) -> None:
        is_uc_table = uc_utils.is_uc_entity(name)
        req_context = RequestContext(request_context.DROP_TABLE, client_name)

        delta_table_exists = self._spark_client.table_exists(name)
        feature_table_exists = (
            delta_table_exists
            if is_uc_table
            else self._catalog_client.feature_table_exists(name, req_context)
        )

        # Handle cases where catalog data does not exist.
        if not feature_table_exists and delta_table_exists:
            raise ValueError(
                f"Delta table '{name}' is not a feature table. Use spark API to drop the delta table. "
                f"For more information on Spark API, "
                f"see https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-drop-table.html."
            )
        if not feature_table_exists and not delta_table_exists:
            raise ValueError(f"Feature table '{name}' does not exist.")

        if is_uc_table:
            feature_table = self._catalog_client_helper.get_feature_table_from_uc_and_online_store_from_fs(
                name, req_context
            )
        else:
            feature_table = self._catalog_client.get_feature_table(name, req_context)
            feature_table.online_stores = self._catalog_client.get_online_stores(
                [name], req_context
            )[name]

        # Delete the feature table and underlying delta table.
        # First perform a dry-run deletion of catalog data as the backend validates the API call.
        try:
            self._catalog_client.delete_feature_table(name, req_context, dry_run=True)
        except Exception as e:
            _logger.error(f"Unable to delete the feature table due to {e}.")
            raise e
        if (
            is_uc_table
            and self._databricks_client.get_uc_table(name)["table_type"] == "VIEW"
        ):
            self._spark_client.delete_view(name)
        else:
            self._spark_client.delete_table(name)
        try:
            self._catalog_client.delete_feature_table(name, req_context)
        except Exception as e:
            _logger.error(
                f"Failed to delete the feature table from Feature Catalog due to {e}."
                f" To fix this, re-run the 'drop_table' method."
            )
            raise e
        _logger.warning(
            "Deleting a feature table can lead to unexpected failures in upstream "
            "producers and downstream consumers (models, endpoints, and scheduled jobs)."
        )
        if feature_table.online_stores:
            ComputeClient._log_online_store_info(feature_table.online_stores)

    def read_table(self, name: str, client_name: str, **kwargs) -> DataFrame:
        as_of_delta_timestamp = kwargs.pop("as_of_delta_timestamp", None)
        validation_utils.check_kwargs_empty(kwargs, "read_table")

        req_context = RequestContext(request_context.READ_TABLE, client_name)
        self._spark_client_helper.check_feature_table_exists(name)
        df = self._spark_client.read_table(name, as_of_delta_timestamp)
        features = self._catalog_client.get_features(name, req_context)
        if not schema_utils.catalog_matches_delta_schema(features, df.schema):
            schema_utils.log_catalog_schema_not_match_delta_schema(
                features, df.schema, level=_WARN
            )
        # Add consumer of each feature as final step
        consumer_feature_table_map = {name: [feature.name for feature in features]}
        self._catalog_client_helper.add_consumer(
            consumer_feature_table_map, req_context
        )
        return df

    def set_feature_table_tag(
        self, *, table_name: str, key: str, value: str, client_name: str
    ) -> None:
        is_uc_table = uc_utils.is_uc_entity(table_name)
        # Tags for UC tables can be key-only so don't validate 'value'
        if is_uc_table:
            utils.validate_params_non_empty(locals(), ["table_name", "key"])
        else:
            utils.validate_params_non_empty(locals(), ["table_name", "key", "value"])
        req_context = RequestContext(request_context.SET_FEATURE_TABLE_TAG, client_name)
        ft = self.get_table(table_name, req_context, include_producers=False)

        if is_uc_table:
            self._spark_client.set_table_tags(table_name, {key: value})
        else:
            self._catalog_client.set_feature_table_tags(
                ft.table_id, {key: value}, req_context
            )

    def delete_feature_table_tag(
        self, *, table_name: str, key: str, client_name: str
    ) -> None:
        is_uc_table = uc_utils.is_uc_entity(table_name)
        utils.validate_params_non_empty(locals(), ["table_name", "key"])
        req_context = RequestContext(
            request_context.DELETE_FEATURE_TABLE_TAG, client_name
        )
        ft = self.get_table(table_name, req_context, include_producers=False)
        if key not in ft.tags:
            _logger.warning(
                f'The tag "{key}" for feature table "{table_name}" was not found, so the delete operation has been skipped.'
            )
        else:
            if is_uc_table:
                self._spark_client.unset_table_tags(table_name, [key])
            else:
                self._catalog_client.delete_feature_table_tags(
                    ft.table_id, [key], req_context
                )

    def _check_catalog_matches_delta_metadata(
        self,
        name,
        table_schema,
        primary_keys_as_list,
        partition_cols_as_list,
        timestamp_keys_as_list,
        req_context,
    ) -> None:
        """
        Checks if existing feature table catalog metadata with {name} matches the data table
        metadata including the table_schema, primary keys, timestamp keys and partition columns.
        Raise an error if there is mismatch.
        """
        ft = self._catalog_client.get_feature_table(name, req_context)
        # The below is only here to ensure that migration from get_feature_table to get_online_stores goes smoothly.
        # Can be removed if determined to be unnecessary.
        ft.online_stores = self._catalog_client.get_online_stores([name], req_context)[
            name
        ]
        existing_features = self._catalog_client.get_features(name, req_context)
        schemas_match = schema_utils.catalog_matches_delta_schema(
            existing_features, table_schema
        )
        primary_keys_match = primary_keys_as_list == ft.primary_keys
        partition_keys_match = partition_cols_as_list == ft.partition_columns
        timestamp_keys_match = timestamp_keys_as_list == ft.timestamp_keys
        if (
            schemas_match
            and primary_keys_match
            and partition_keys_match
            and timestamp_keys_match
        ):
            _logger.warning(
                f'The feature table "{name}" already exists. Use "FeatureStoreClient.write_table"'
                f" API to write to the feature table."
            )
        else:
            error_msg = (
                f"The feature table '{name}' already exists with a different schema.:\n"
            )
            if not schemas_match:
                error_msg += (
                    f"Existing schema: {existing_features}\n"
                    f"New schema:{table_schema}\n\n"
                )
            if not primary_keys_match:
                error_msg += (
                    f"Existing primary keys: {ft.primary_keys}\n"
                    f"New primary keys: {primary_keys_as_list}\n\n"
                )
            if not partition_keys_match:
                error_msg += (
                    f"Existing partition keys: {ft.partition_columns}\n"
                    f"New partition keys: {partition_cols_as_list}\n\n"
                )
            if not timestamp_keys_match:
                error_msg += (
                    f"Existing timestamp keys: {ft.timestamp_keys}\n"
                    f"New timestamp keys: {timestamp_keys_as_list}\n\n"
                )

            raise ValueError(error_msg)

    @staticmethod
    def _schema_eq(schema1, schema2):
        return set(schema1.fields) == set(schema2.fields)

    @staticmethod
    def _check_schema_top_level_types_supported(schema: StructType) -> None:
        """
        Checks whether the provided schema is supported by Feature Store, only considering the
        top-level type for nested data types.
        """
        unsupported_name_type = [
            (field.name, field.dataType)
            for field in schema.fields
            if not DataType.top_level_type_supported(field.dataType)
        ]
        if unsupported_name_type:
            plural = len(unsupported_name_type) > 1
            missing_cols_str = ", ".join(
                [
                    f"\n\t- {feat_name} (type: {feat_type})"
                    for (feat_name, feat_type) in unsupported_name_type
                ]
            )
            raise ValueError(
                f"Unsupported data type for column{'s' if plural else ''}: {missing_cols_str}"
            )

    @staticmethod
    def _check_schema_has_columns(schema, columns, col_type):
        schema_cols = [field.name for field in schema.fields]
        for col in columns:
            if col not in schema_cols:
                raise ValueError(
                    f"The provided DataFrame or schema must contain all specified {col_type}. "
                    f"Schema {schema} is missing column '{col}'"
                )

    @staticmethod
    def _get_feature_key_specs(
        delta_schema: StructType,
        primary_keys_as_list: List[str],
        timestamp_keys_as_list: List[str],
        partition_cols_as_list: List[str],
    ) -> List[KeySpec]:
        """
        Returns the KeySpec for only features in the delta_schema. KeySpecs are not created for
        primary keys, partition keys, and timestamp keys.
        """
        feature_key_specs = []
        for k in delta_schema:
            if (
                k not in partition_cols_as_list
                and k not in primary_keys_as_list
                and k not in timestamp_keys_as_list
            ):
                spark_data_type = delta_schema[k]
                # If the feature is a complex Spark DataType, convert the Spark DataType to its
                # JSON representation to be updated in the Feature Catalog.
                data_type_details = (
                    spark_data_type.json()
                    if DataType.from_spark_type(spark_data_type)
                    in DATA_TYPES_REQUIRES_DETAILS
                    else None
                )
                feature_key_specs.append(
                    KeySpec(k, spark_data_type.typeName(), data_type_details)
                )
        return feature_key_specs

    def _create_feature_table_with_features_and_tags(
        self,
        *,
        name: str,
        partition_key_specs: List[KeySpec],
        primary_key_specs: List[KeySpec],
        timestamp_key_specs: List[KeySpec],
        feature_key_specs: List[KeySpec],
        is_imported: bool,
        tags: Optional[Dict[str, str]],
        description: str,
        req_context: Optional[RequestContext],
    ) -> FeatureTable:
        """
        Create the feature_table, features and tags.

        If any step fails, the exception handler cleans up the feature table from the feature catalog
        and propagates the exception to the caller for further handling.
        """
        is_uc_table = uc_utils.is_uc_entity(name)
        feature_table = None

        try:
            # Additional instrumentation headers for create_feature_table
            req_context_method_name = req_context.get_header(
                request_context.FEATURE_STORE_METHOD_NAME
            )
            if req_context_method_name in (
                request_context.CREATE_TABLE,
                request_context.CREATE_FEATURE_TABLE,
                request_context.REGISTER_TABLE,
            ):
                create_feature_table_req_context = RequestContext.with_additional_custom_headers(
                    req_context,
                    {
                        # all keys are counted as features here, so that NUM_FEATURES matches len(FeatureTable.features)
                        request_context.NUM_FEATURES: str(
                            len(
                                {
                                    key_spec.name
                                    for key_spec in (
                                        partition_key_specs
                                        + primary_key_specs
                                        + timestamp_key_specs
                                        + feature_key_specs
                                    )
                                }
                            )
                        ),
                        request_context.NUM_TAGS: (
                            "0" if tags is None else str(len(tags))
                        ),
                    },
                )
            else:
                create_feature_table_req_context = req_context

            feature_table = self._catalog_client.create_feature_table(
                name,
                partition_key_spec=partition_key_specs,
                primary_key_spec=primary_key_specs,
                timestamp_key_spec=timestamp_key_specs,
                description=description,
                is_imported=is_imported,
                req_context=create_feature_table_req_context,
            )
            if len(feature_key_specs) > 0 and not is_uc_table:
                self._catalog_client.create_features(
                    name, feature_key_specs, req_context
                )
            if tags:
                if is_uc_table:
                    self._spark_client.set_table_tags(name, tags)
                else:
                    table_id = feature_table.table_id
                    self._catalog_client.set_feature_table_tags(
                        table_id, tags, req_context
                    )
            return feature_table
        except Exception as e:
            # Delete the newly created feature table in the catalog
            if feature_table:
                self._catalog_client.delete_feature_table(name, req_context)
            raise e

    @staticmethod
    def _log_online_store_info(online_stores: ProtoOnlineStore):
        message = "You must delete the following published online stores: \n"
        for online_store in online_stores:
            canonical_name = utils.get_canonical_online_store_name(online_store)
            message += f"\t - '{online_store.name}'{f' ({canonical_name})' if canonical_name else ''} \n"
            if online_store.WhichOneof("additional_metadata") is None:
                continue
            metadata = getattr(
                online_store, online_store.WhichOneof("additional_metadata")
            )
            if online_store.WhichOneof("additional_metadata") == "dynamodb_metadata":
                message += DynamoDbMetadata.from_proto(metadata).description
            elif online_store.WhichOneof("additional_metadata") == "mysql_metadata":
                message += MySqlMetadata.from_proto(metadata).description
            elif (
                online_store.WhichOneof("additional_metadata") == "sql_server_metadata"
            ):
                message += SqlServerMetadata.from_proto(metadata).description
            elif online_store.WhichOneof("additional_metadata") == "cosmosdb_metadata":
                message += CosmosDbMetadata.from_proto(metadata).description
            else:
                message += f"\t\t - Unknown online store. \n"
        _logger.warning(message)

    @staticmethod
    def _check_unique_case_insensitive_schema(
        catalog_features: List[MaterializedFeature], df_schema: DataFrame
    ) -> None:
        """
        Verify schema is unique and case sensitive.

        Confirm that column names in Feature Catalog and user's input
        DataFrame do not have duplicate
        case insensitive columns when writing data to the feature table.

        Prevents the following cases:
        1. User input DataFrame's schema is '{'feat1': 'FLOAT', 'FEAT1': 'FLOAT'}'
        2. User input DataFrame's schema is '{'FEAT1': 'FLOAT'}', and Feature Catalog's schema is
        '{'feat1': 'FLOAT'}'
        """
        df_cols = {}
        for df_column in df_schema:
            if df_column.name.lower() in df_cols:
                raise ValueError(
                    f"The provided DataFrame cannot contain duplicate column names. Column names are case insensitive. "
                    f"The DataFrame contains duplicate columns: {df_cols[df_column.name.lower()]}, {df_column.name}"
                )
            df_cols[df_column.name.lower()] = df_column.name

        for feature in catalog_features:
            if (
                feature.name.lower() in df_cols
                and feature.name != df_cols[feature.name.lower()]
            ):
                raise ValueError(
                    f"Feature names cannot differ by only case. The provided DataFrame has column "
                    f"{df_cols[feature.name.lower()]}, which duplicates the Feature Catalog column {feature.name}. "
                    f"Please rename the column"
                )

    def _update_delta_features(self, name, schema):
        """
        Update the Delta table with name `name`.

        This update happens by merging in `schema`. Will throw if the schema
        is incompatible with the existing Delta table schema.

        .. note::

           Validate: Delta table schemas are compatible. Because SparkClient.write_table enables
           the "mergeSchema" option, differences in schema will be reconciled by Spark. We will
           later write this schema to the Feature Catalog. In this way, we defer the schema
           merging logic to Spark.
        """
        try:
            self._spark_client.attempt_to_update_delta_table_schema(name, schema)
        except AnalysisException as e:
            raise ValueError(
                "FeatureStoreClient uses Delta APIs. The schema of the new DataFrame is "
                f"incompatible with existing Delta table. Saw AnalysisException: {str(e)}"
            )

    def _update_catalog_features_with_delta_schema(
        self, name, ft, features, delta_schema, req_context: RequestContext
    ):
        """
        Update the catalog to include all columns of the provided Delta table schema.

        :param name: Feature table name
        :param ft: FeatureTable
        :param features: [Features]
        :param delta_schema: Schema of the data table.
        :param req_context: The RequestContext
        """
        catalog_features_to_fs_types = {
            f.name: DataType.from_string(f.data_type) for f in features
        }
        delta_features_to_fs_types = {
            feature.name: DataType.from_spark_type(feature.dataType)
            for feature in delta_schema
        }
        complex_catalog_features_to_spark_types = (
            schema_utils.get_complex_catalog_schema(
                features, catalog_features_to_fs_types
            )
        )
        complex_delta_features_to_spark_types = schema_utils.get_complex_delta_schema(
            delta_schema, delta_features_to_fs_types
        )

        feaures_and_data_types_to_add = []
        features_and_data_types_to_update = []
        for feat, fs_data_type in delta_features_to_fs_types.items():
            simple_types_mismatch = (feat in catalog_features_to_fs_types) and (
                fs_data_type != catalog_features_to_fs_types[feat]
            )
            complex_types_mismatch = (
                feat in complex_catalog_features_to_spark_types
            ) and (
                complex_catalog_features_to_spark_types[feat]
                != complex_delta_features_to_spark_types[feat]
            )
            if simple_types_mismatch or complex_types_mismatch:
                # If the feature is a complex Spark DataType, convert the Spark DataType to its
                # JSON representation to be updated in the Feature Catalog.
                data_type_details = complex_delta_features_to_spark_types.get(feat)
                if data_type_details:
                    data_type_details = data_type_details.json()
                features_and_data_types_to_update.append(
                    (feat, fs_data_type, data_type_details)
                )
            if feat not in ft.primary_keys and feat not in catalog_features_to_fs_types:
                # If the feature is a complex Spark DataType, convert the Spark DataType to its
                # JSON representation to be updated in the Feature Catalog.
                data_type_details = complex_delta_features_to_spark_types.get(feat)
                if data_type_details:
                    data_type_details = data_type_details.json()
                feaures_and_data_types_to_add.append(
                    (feat, fs_data_type, data_type_details)
                )
        if feaures_and_data_types_to_add:
            key_specs = [
                KeySpec(
                    feat,
                    DataType.to_string(data_type),
                    data_type_details,
                )
                for (
                    feat,
                    data_type,
                    data_type_details,
                ) in feaures_and_data_types_to_add
            ]
            self._catalog_client.create_features(name, key_specs, req_context)
        # There is no need to update types of existing columns because mergeSchema does not support
        # column type changes.

    def _set_pk_tk_if_not_exist(
        self,
        full_table_name: str,
        primary_keys: List[str],
        timestamp_keys: List[str],
    ):
        """
        Idempotent operation to set NOT NULL on PK/TK, and declare them as table constraint if no PK constraint exists.
        Ignore when there exists PK constraint on the table.
        """
        tk_col = None
        if timestamp_keys:
            if len(timestamp_keys) == 1:
                tk_col = timestamp_keys[0]
            else:
                raise ValueError("Setting multiple timeseries keys is not supported.")
        # timestamp_keys may or may not be included in primary_keys. To handle both cases, separate out the two and re-combine them.
        pk_without_tk = [pk for pk in primary_keys if pk not in timestamp_keys]
        # Expected delta PKs are equivalent to FS PKs + TKs in order
        expected_pk = pk_without_tk + timestamp_keys
        # Get existing PK of the table from SHOW CREATE TABLE
        existing_pk = self._spark_client.get_pk_from_table_create_stmt(full_table_name)
        if not existing_pk and expected_pk:
            _logger.info(
                f"Setting columns {expected_pk} of table '{full_table_name}' to NOT NULL."
            )
            # Set all delta primary keys to NOT NULL
            self._spark_client.set_cols_not_null(
                full_table_name=full_table_name, cols=expected_pk
            )
            _logger.info(
                f"Setting Primary Keys constraint {expected_pk} on table '{full_table_name}'."
            )
            # Set PK/TK constraint to all delta primary keys
            self._spark_client.set_cols_pk_tk(
                full_table_name=full_table_name,
                pk_cols=expected_pk,
                tk_col=tk_col,
            )
