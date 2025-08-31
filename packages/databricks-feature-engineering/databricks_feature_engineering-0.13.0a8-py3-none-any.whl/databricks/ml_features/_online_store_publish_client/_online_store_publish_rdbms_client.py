import logging
import random
import string
import time
from datetime import timedelta
from typing import List, Optional

from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession

from databricks.ml_features._online_store_publish_client._online_store_publish_client import (
    OnlineStorePublishClient,
    OnlineTable,
    is_rdbms_spec,
)
from databricks.ml_features.online_store_spec import (
    AmazonRdsMySqlSpec,
    AzureMySqlSpec,
    AzureSqlServerSpec,
    OnlineStoreSpec,
)
from databricks.ml_features.publish_engine import (
    PublishMySqlEngine,
    PublishSqlEngine,
    PublishSqlServerEngine,
)
from databricks.ml_features.utils.publish_utils import get_latest_snapshot
from databricks.ml_features.utils.spark_utils import serialize_complex_data_types

_logger = logging.getLogger(__name__)


def temp_table_name():
    rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"databricks_tmp_{rand_suffix}"


def is_datatype_compatible(new_type, old_type):
    # longtext is compatible with both text and longtext.
    # More details at
    # https://docs.google.com/document/d/1AYnGCgxe7dYJ0efdQTbU8oms15EN_B2uHVHFx_1hXBQ/edit#
    LONGTEXT = "longtext"
    TEXT = "text"
    if new_type == LONGTEXT and old_type in (TEXT, LONGTEXT):
        return True
    return new_type == old_type


def needs_datatype_upgrade(new_type, old_type):
    if not is_datatype_compatible(new_type, old_type):
        raise TypeError(
            f"Trying to perform incompatible upgrade of type {old_type} to {new_type}."
        )
    return new_type != old_type


def generate_sql_engine(online_store_spec, spark_session):
    if isinstance(online_store_spec, AzureSqlServerSpec):
        return PublishSqlServerEngine(online_store_spec, spark_session)
    return PublishMySqlEngine(online_store_spec, spark_session)


class OnlineStorePublishRdbmsClient(OnlineStorePublishClient):
    def __init__(self, online_store):
        if not is_rdbms_spec(online_store):
            raise ValueError(f"Unexpected online store type {type(online_store)}")
        self.database = online_store.database_name
        self.table_name = online_store.table_name
        self.online_store = online_store
        # TODO [ML-40496]: Add back appName to spark initialization once spark connect team gives a proper long term solution
        self.spark_session = SparkSession.builder.getOrCreate()
        self.sql_engine = generate_sql_engine(self.online_store, self.spark_session)

    def _online_table_exists(self, table_name):
        # TODO: Check if this works for a user without read access to table_name.
        result_set = self.sql_engine.get_online_tables(table_names=[table_name])
        return result_set.next()  # Returns false if there are no rows in the result set

    def _get_column_types(self, table_name):
        result_set = self.sql_engine.get_column_types(table_name)

        col_to_type = {}

        while result_set.next():
            data_type = result_set.getString(PublishSqlEngine.DATA_TYPE)
            # JDBC writes string columns in Spark dataframes to MSSQL as NVARCHAR(max) columns
            # because TEXT is deprecated in MSSQL. Therefore, we append the string size when
            # returning the NVARCHAR column type.
            if data_type == "nvarchar":
                data_type += "(max)"
            # JDBC writes binary columns in Spark dataframes to MSSQL as VARBINARY columns
            # because the maximum limit for BLOB is 50 in MSSQL. Therefore, we append the max
            # size when returning the NVARCHAR column type.
            elif data_type == "varbinary":
                data_type += "(max)"
            # Decimal columns in MySQL and MSSQL require precision and scale information, which needs
            # to be fetched separately from the numeric_precision and numeric_scale columns in the
            # database's information schema table.
            elif data_type == "decimal":
                precision = result_set.getString(PublishSqlEngine.NUMERIC_PRECISION)
                scale = result_set.getString(PublishSqlEngine.NUMERIC_SCALE)
                data_type = f"decimal({precision},{scale})"
            col_to_type[result_set.getString(PublishSqlEngine.COLUMN_NAME)] = data_type

        return col_to_type

    def _extend_schema(self, base_sql_table, new_sql_table):
        base_columns_to_types = self._get_column_types(base_sql_table)
        new_columns_to_types = self._get_column_types(new_sql_table)

        add_columns = []

        for (col, type) in new_columns_to_types.items():
            if col in base_columns_to_types:
                if not is_datatype_compatible(
                    new_type=type, old_type=base_columns_to_types[col]
                ):
                    raise ValueError(
                        "Existing data in the online store is incompatible with the data "
                        f"being published : new type {type} and old type {base_columns_to_types[col]}. To resolve this error, drop the table "
                        f'"{base_sql_table}" from the online store.'
                    )

                if needs_datatype_upgrade(type, base_columns_to_types[col]):
                    _logger.warning(
                        f"The column {col} of datatype {type} will be changed to datatype "
                        f"{base_columns_to_types[col]} which might result in data truncation. "
                        f"Please use overwrite mode in publish_table for the migration. Using "
                        f"merge mode in publish_table will fail for incompatible types in the "
                        f"future."
                    )
            else:
                add_columns.append((col, type))

        self.sql_engine.add_columns(base_sql_table, add_columns)

    def _overwrite_table(self, original_sql_table, tmp_sql_table):
        """
        Overwrite the original table with a temporary one through a drop and a rename.
        Manual error handling is required for MySQL as DROP and RENAME commands cannot be rolled back.
        """
        try:
            with self.sql_engine.in_transaction():
                self.sql_engine.drop_table(original_sql_table)
                self.sql_engine.rename_table(tmp_sql_table, original_sql_table)
        except Exception as e:
            # Both the temporary and original table exist in the case of a SQL Server error
            if isinstance(self.sql_engine, PublishSqlServerEngine):
                self.sql_engine.drop_table(tmp_sql_table)
                raise ValueError(
                    f"Could not overwrite table {original_sql_table} due to error: {e}. "
                    f"No data has been modified."
                )
            # The temporary table is guaranteed to exist in the case of a MySQL error
            elif isinstance(self.sql_engine, PublishMySqlEngine):
                raise ValueError(
                    f"Could not rename table {tmp_sql_table} to {original_sql_table} due to error: {e}. "
                    f"Please execute this manually."
                )

    def _publish_overwrite(
        self,
        df,
        primary_keys: List[str],
        timestamp_keys,
        lookback_window: Optional[timedelta],
    ):
        # Lookback window and publishing a range of data is not supported for SQL stores.
        if lookback_window:
            raise ValueError(
                "Publishing with a lookback window is not supported for SQL online stores."
            )
        if timestamp_keys:
            df = get_latest_snapshot(df, primary_keys, timestamp_keys)
        if not self._online_table_exists(self.table_name):
            self._create_table(
                self.table_name,
                df,
                self.sql_engine.jdbc_url,
                self.sql_engine.jdbc_properties,
                primary_keys,
            )
        else:
            tmp_table = self._write_to_tmp_table(
                df,
                self.sql_engine.jdbc_url,
                self.sql_engine.jdbc_properties,
                primary_keys,
            )
            self._overwrite_table(self.table_name, tmp_table)

    def _extend_schema_and_merge_into(
        self, base_sql_table, source_sql_table, columns, primary_keys
    ):
        """
        Extend the base table's schema to match the source table's, then merges the source table into the base.
        On failure, the operation is retried to mitigate potential data inconsistencies.
        For example, MySQL schema extensions cannot be rolled back so a merge failure will lead to NULL data.
        """
        max_tries = 2
        for tries in range(1, max_tries + 1):
            try:
                with self.sql_engine.in_transaction():
                    self._extend_schema(base_sql_table, source_sql_table)
                    self.sql_engine.merge_table_into(
                        base_sql_table, source_sql_table, columns, primary_keys
                    )
                break
            except:
                if tries == max_tries:
                    raise
                time.sleep(2)

    def _publish_merge(
        self,
        df,
        primary_keys: List[str],
        timestamp_keys,
        lookback_window: Optional[timedelta],
    ):
        """
        DataFrameWriter.jdbc does not support the write semantics we want (described in
        `publish` docstring). Thus this function initially writes all data from df into
        a temporary SQL table. Then SQL code is run to insert this data into the
        online store.
        """
        # Lookback window and publishing a range of data is not supported for SQL stores.
        if lookback_window:
            raise ValueError(
                "Publishing with a lookback window is not supported for SQL online stores."
            )
        if timestamp_keys:
            df = get_latest_snapshot(df, primary_keys, timestamp_keys)
        if not self._online_table_exists(self.table_name):
            self._create_table(
                self.table_name,
                df,
                self.sql_engine.jdbc_url,
                self.sql_engine.jdbc_properties,
                primary_keys,
            )
        else:
            tmp_table = self._write_to_tmp_table(
                df,
                self.sql_engine.jdbc_url,
                self.sql_engine.jdbc_properties,
                primary_keys,
            )

            try:
                self._extend_schema_and_merge_into(
                    self.table_name, tmp_table, df.columns, primary_keys
                )
            finally:
                self.sql_engine.drop_table(tmp_table)

    def _create_table(
        self, name, df, jdbc_url, connection_properties, primary_keys: str
    ):
        """
        Creates and writes df to SQL table `name` defined by connection_properties, sets
        the primary key(s).
        """
        self.sql_engine.create_empty_table(
            name, df.schema, jdbc_url, connection_properties, primary_keys
        )
        try:
            df = serialize_complex_data_types(df)
            df.write.jdbc(
                url=jdbc_url,
                table=name,
                mode="append",
                properties=connection_properties,
            )
        except Py4JJavaError as e:
            error_str = str(e)
            # This write may fail if the string primary key maximum length is exceeded.
            if "java.sql.BatchUpdateException" in error_str and (
                PublishMySqlEngine.PRIMARY_KEY_STRING_ERROR in error_str
                or PublishSqlServerEngine.PRIMARY_KEY_STRING_ERROR in error_str
            ):
                raise ValueError(
                    "Unable to publish features because a primary key string is too long. "
                    "Check the online store spec documentation for maximum primary key string lengths."
                )
            else:
                raise

    def _drop_online_table(
        self,
        online_table_name: str,
    ):
        self.sql_engine.drop_table(online_table_name)

    def _write_to_tmp_table(
        self, df, jdbc_url, connection_properties, primary_keys: str
    ):
        """
        Writes df to a temporary SQL table defined by connection_properties, sets
        the primary key(s).
        """
        name = temp_table_name()
        self._create_table(name, df, jdbc_url, connection_properties, primary_keys)
        return name

    # Parameters needed to override parent method
    def get_or_create_online_table(self, df, primary_keys, timestamp_keys):
        # RDBMS online stores support both "overwrite" and "merge" mode for publish and
        # creating a table instance is tightly ingrained as a part of the publish logic.
        # For now this method is no-op. It does not create a new online table if one does not exist
        # and returns None for cloud provider ID.
        # Logic for creation for empty table is handled in the specific publish functions.
        # ToDo(ML-20621): Identify the need to support "overwrite" mode in future and design
        #                 how online table can be created in advance to save the cloud provider
        #                 unique ID in backend catalog.
        return self.get_online_table()

    # Get online store without additional parameters
    def get_online_table(self):
        return OnlineTable(
            name=self.table_name, cloud_provider_unique_id=None, new_table=False
        )

    def close(self):
        """
        Closes the sql engine connection.
        :return:
        """
        self.sql_engine.close()
