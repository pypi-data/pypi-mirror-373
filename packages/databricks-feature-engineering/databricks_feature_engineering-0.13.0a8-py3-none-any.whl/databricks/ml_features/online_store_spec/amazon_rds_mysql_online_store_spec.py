from typing import Union

from databricks.ml_features.online_store_spec.online_store_properties import (
    AWS_AURORA,
    AWS_MYSQL,
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


class AmazonRdsMySqlSpec(OnlineStoreSpec):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.online_store_spec.AmazonRdsMySqlSpec`, `!databricks.feature_store.online_store_spec.AmazonRdsMySqlSpec`

    Class that defines and creates :class:`AmazonRdsMySqlSpec` objects.

    This :class:`OnlineStoreSpec` implementation is intended for publishing
    features to Amazon RDS MySQL and Aurora (MySQL-compatible edition).

    See :class:`OnlineStoreSpec` documentation for more usage information,
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

    .. todo::

       [ML-15546]: Identify clear mechanism to inherit constructor
       pydocs from base class and
       remove ``See xxx documentation for more usage information`` section.
    """

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
        """Initialize AmazonRdsMySqlSpec objects."""
        super().__init__(
            AWS_MYSQL,
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
        """Define the cloud propert for the data store."""
        return Cloud.AWS

    @property
    def store_type(self):
        """Define the data store type property.

        .. todo::

           (mparkhe): Get the right ``_type``
        """
        if self.type == AWS_MYSQL:
            return StoreType.MYSQL
        elif self.type == AWS_AURORA:
            return StoreType.AURORA_MYSQL

    @property
    def _jdbc_parameters(self) -> str:
        """
        usePipelineAuth and useBatchMultiSend are not supported by Aurora.
        While they are supported by RDS MySQL Community Edition, we do not distinguish between
        RDS MySQL Community Edition and Aurora, so disable for both.
        """
        return "?usePipelineAuth=false&useBatchMultiSend=false"

    def auth_type(self):
        """Publish Auth type."""
        return SECRETS

    def _augment_online_store_spec(self, full_feature_table_name):
        """
        Apply default database and table name for Amazon RDS MySQL.
        Local workspace hive metastore: database = <database>, table = <table>
        UC: database = <catalog>-<database>, table = <table>
        """
        return self._augment_sql_online_store_spec_helper(
            full_feature_table_name, self.database_name, self.table_name
        )

    def _get_online_store_name(self):
        """
        Online store name for Amazon RDS MySQL
        """
        return f"{self.database_name}.{self.table_name}"
