from typing import Union

from databricks.ml_features.online_store_spec.online_store_properties import (
    AZURE_MYSQL,
    DATABASE_NAME,
    HOSTNAME,
    PORT,
    SECRETS,
    TABLE_NAME,
    USER,
)
from databricks.ml_features.online_store_spec.online_store_spec import OnlineStoreSpec
from databricks.ml_features_common.entities.cloud import Cloud
from databricks.ml_features_common.entities.store_type import StoreType
from databricks.ml_features_common.utils.uc_utils import LOCAL_METASTORE_NAMES


class AzureMySqlSpec(OnlineStoreSpec):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.online_store_spec.AzureMySqlSpec`, `!databricks.feature_store.online_store_spec.AzureMySqlSpec`

    Define the `AzureMySqlSpec` class.

    This :class:`OnlineStoreSpec <databricks.ml_features.online_store_spec.OnlineStoreSpec>`
    implementation is intended for publishing
    features to Azure Database for MySQL.

    See :class:`OnlineStoreSpec <databricks.ml_features.online_store_spec.OnlineStoreSpec>`
    documentation for more usage information,
    including parameter descriptions.

    :param hostname: Hostname to access online store.
    :param port: Port number to access online store.
    :param user: Username that has access to the online store. **Deprecated**.
      Use ``write_secret_prefix`` instead.
    :param password: Password to access the online store. **Deprecated**.
      Use ``write_secret_prefix`` instead.
    :param database_name: Database name.
    :param table_name: Table name.
    :param driver_name: Name of custom JDBC driver to access the online store.
    :param read_secret_prefix: Prefix for read secret.
    :param write_secret_prefix: Prefix for write secret.
    """

    # TODO [ML-15546]: Identify clear mechanism to inherit constructor pydocs from base class and
    #   remove `See xxx documentation for more usage information` section.
    # TODO (ML-23105): Remove explicit parameters for MLR 12.0.
    def __init__(
        self,
        hostname: str,
        port: int,
        user: Union[str, None] = None,
        password: Union[str, None] = None,
        database_name: Union[str, None] = None,
        table_name: Union[str, None] = None,
        driver_name: Union[str, None] = None,
        read_secret_prefix: Union[str, None] = None,
        write_secret_prefix: Union[str, None] = None,
    ):
        """Initialize AzureMySqlSpec objects."""
        super().__init__(
            AZURE_MYSQL,
            hostname,
            port,
            user,
            password,
            database_name=database_name,
            table_name=table_name,
            driver_name=driver_name,
            read_secret_prefix=read_secret_prefix,
            write_secret_prefix=write_secret_prefix,
        )

    @property
    def hostname(self):
        """Hostname to access the online store."""
        return self._properties[HOSTNAME]

    @property
    def port(self):
        """Port number to access the online store."""
        return self._properties[PORT]

    @property
    def database_name(self):
        """Database name."""
        return self._properties[DATABASE_NAME]

    @property
    def cloud(self):
        """Define the cloud the fature store runs."""
        return Cloud.AZURE

    @property
    def store_type(self):
        """Define the data store type."""
        return StoreType.MYSQL

    def auth_type(self):
        """Publish Auth type."""
        return SECRETS

    def _lookup_jdbc_auth_user_with_write_permissions(self):
        """
        Generate the user authentication string used in the JDBC URL.

        On AzureMysql it requires the format: "user@server"
        """
        # https://docs.microsoft.com/en-us/azure/mysql/howto-connection-string
        # servername is extracted from hostname (<servername>.mysql.database.azure.com)
        server_name = self._properties[HOSTNAME].split(".")[0]

        return f"{self._lookup_user_with_write_permissions()}@{server_name}"

    def _augment_online_store_spec(self, full_feature_table_name):
        """
        Apply default database and table name for Azure MySQL.
        Local workspace hive metastore: database = <database>, table = <table>
        UC: database = <catalog>-<database>, table = <table>
        """
        return self._augment_sql_online_store_spec_helper(
            full_feature_table_name, self.database_name, self.table_name
        )

    def _get_online_store_name(self):
        """
        Online store name for Azure MySQL
        """
        return f"{self.database_name}.{self.table_name}"
