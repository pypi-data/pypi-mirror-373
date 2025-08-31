from typing import Union

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)
from databricks.ml_features_common.entities.cloud import Cloud
from databricks.ml_features_common.entities.query_mode import QueryMode
from databricks.ml_features_common.entities.store_type import StoreType


class BrickstoreConf(_FeatureStoreObject):
    def __init__(self, host: str, port: int, table_serving_url: str):
        self._host = host
        self._port = port
        self._table_serving_url = table_serving_url

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def table_serving_url(self):
        return self._table_serving_url


class MySqlConf(_FeatureStoreObject):
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port


class SqlServerConf(_FeatureStoreObject):
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port


class DynamoDbConf(_FeatureStoreObject):
    def __init__(self, region: str):
        self._region = region

    @property
    def region(self):
        return self._region


class CosmosDbConf(_FeatureStoreObject):
    def __init__(self, account_uri: str):
        self._account_uri = account_uri

    @property
    def account_uri(self):
        return self._account_uri


class OnlineStoreForServing:
    def __init__(
        self,
        cloud: Cloud,
        store_type: StoreType,
        read_secret_prefix: str,
        creation_timestamp_ms: int,
        extra_configs: Union[BrickstoreConf, MySqlConf, SqlServerConf, DynamoDbConf],
        query_mode: QueryMode,
    ):
        self._cloud = cloud
        self._store_type = store_type
        self._read_secret_prefix = read_secret_prefix
        self._creation_timestamp_ms = creation_timestamp_ms
        self._extra_configs = extra_configs
        self._query_mode = query_mode

    @property
    def extra_configs(self):
        return self._extra_configs

    @property
    def creation_timestamp_ms(self):
        return self._creation_timestamp_ms

    @property
    def query_mode(self) -> QueryMode:
        return self._query_mode

    @property
    def cloud(self):
        return self._cloud

    @property
    def store_type(self):
        return self._store_type

    @property
    def read_secret_prefix(self):
        return self._read_secret_prefix

    @classmethod
    def from_proto(cls, the_proto):
        conf = None
        if the_proto.WhichOneof("extra_configs") == "mysql_conf":
            conf = MySqlConf(the_proto.mysql_conf.host, the_proto.mysql_conf.port)
        elif the_proto.WhichOneof("extra_configs") == "sql_server_conf":
            conf = SqlServerConf(
                the_proto.sql_server_conf.host, the_proto.sql_server_conf.port
            )
        elif the_proto.WhichOneof("extra_configs") == "brickstore_conf":
            conf = BrickstoreConf(
                the_proto.brickstore_conf.host,
                the_proto.brickstore_conf.port,
                the_proto.brickstore_conf.table_serving_url,
            )
        elif the_proto.WhichOneof("extra_configs") == "dynamodb_conf":
            conf = DynamoDbConf(the_proto.dynamodb_conf.region)
        elif the_proto.WhichOneof("extra_configs") == "cosmosdb_conf":
            conf = CosmosDbConf(the_proto.cosmosdb_conf.account_uri)
        else:
            raise ValueError("Unsupported Store Type: " + str(the_proto))

        # The `query_mode` should always be defined. We explicitly check this to avoid erroneously retrieving the
        # default QueryMode enum value `PRIMARY_KEY_LOOKUP` when the `query_mode` proto field is not set.
        if not the_proto.HasField("query_mode"):
            raise ValueError(f"'query_mode' should be defined: {the_proto}")
        return cls(
            cloud=the_proto.cloud,
            store_type=the_proto.store_type,
            extra_configs=conf,
            read_secret_prefix=the_proto.read_secret_prefix,
            creation_timestamp_ms=the_proto.creation_timestamp_ms,
            query_mode=the_proto.query_mode,
        )
