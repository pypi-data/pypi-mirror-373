from databricks.ml_features._online_store_publish_client._online_store_publish_client import (
    OnlineStorePublishClient,
    is_nosql_spec,
    is_rdbms_spec,
)
from databricks.ml_features._online_store_publish_client._online_store_publish_nosql_client import (
    OnlineStorePublishNoSqlClient,
)
from databricks.ml_features._online_store_publish_client._online_store_publish_rdbms_client import (
    OnlineStorePublishRdbmsClient,
)
from databricks.ml_features.online_store_spec import OnlineStoreSpec


def get_online_store_publish_client(
    online_store_spec: OnlineStoreSpec,
) -> OnlineStorePublishClient:
    if is_rdbms_spec(online_store_spec):
        return OnlineStorePublishRdbmsClient(online_store_spec)
    elif is_nosql_spec(online_store_spec):
        return OnlineStorePublishNoSqlClient(online_store_spec)
    raise ValueError(f"Unexpected online store type {type(online_store_spec)}")
