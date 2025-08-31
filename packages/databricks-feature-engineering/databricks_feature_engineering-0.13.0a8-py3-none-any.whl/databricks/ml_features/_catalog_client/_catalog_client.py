import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

from mlflow.protos.databricks_pb2 import (
    ENDPOINT_NOT_FOUND,
    RESOURCE_DOES_NOT_EXIST,
    ErrorCode,
)
from mlflow.utils import databricks_utils

from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    AddConsumer,
    AddDataSources,
    AddProducer,
    ConsumedFeatures,
    CreateFeatures,
    CreateFeatureSpec,
    CreateFeatureTable,
    DefaultValue,
    DeleteDataSources,
    DeleteFeatureSpec,
    DeleteFeatureTable,
    DeleteOnlineStore,
    DeleteTags,
    EnableDeclarativeFeatures,
)
from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    FeatureFunction as FeatureFunctionProto,
)
from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    FeatureLookup as FeatureLookupProto,
)
from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    Features,
    FeatureStoreService,
    FeatureTableFeatures,
    GenerateFeatureSpecYaml,
    GetConsumers,
    GetFeatures,
    GetFeatureTable,
    GetModelServingMetadata,
    GetOnlineStore,
    GetOnlineStores,
    GetTags,
    InputBinding,
    Job,
    KeySpec,
    LogClientEvent,
    Notebook,
    ProducerAction,
    PublishFeatureTable,
    RenameOutput,
    SetTags,
)
from databricks.ml_features.api.proto.feature_catalog_pb2 import Tag as ProtoTag
from databricks.ml_features.api.proto.feature_catalog_pb2 import (
    UpdateFeature,
    UpdateFeatureSpec,
    UpgradeToUc,
)
from databricks.ml_features.entities._permission_level import _PermissionLevel
from databricks.ml_features.entities.consumer import Consumer
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.entities.feature_spec_info import FeatureSpecInfo
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.entities.materialized_feature import MaterializedFeature
from databricks.ml_features.entities.online_store_detailed import OnlineStoreDetailed
from databricks.ml_features.entities.online_store_metadata import OnlineStoreMetadata
from databricks.ml_features.entities.tag import Tag
from databricks.ml_features.utils import utils
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.rest_utils import (
    _REST_API_PATH_PREFIX,
    call_endpoint,
    extract_api_info_for_service,
    get_error_code,
    proto_to_json,
)
from databricks.ml_features_common.entities.online_feature_table import (
    OnlineFeatureTable,
)
from databricks.ml_features_common.entities.store_type import StoreType
from databricks.ml_features_common.utils.data_type_utils import serialize_default_value
from databricks.ml_features_common.utils.uc_utils import reformat_full_table_name

_METHOD_TO_INFO = extract_api_info_for_service(
    FeatureStoreService, _REST_API_PATH_PREFIX
)

_logger = logging.getLogger(__name__)


class CatalogClient:
    """
    This provides the client interface to the backend feature catalog service running in the Databricks Control Plane.

    The catalog client should be reserved for low-level catalog operations and not contain any business logic
    that is unrelated to the catalog itself (for example, calling other Databricks backend services).  If you need
    additional business logic, consider using the CatalogClientHelper instead.
    """

    # !!!IMPORTANT!!!
    # Please use reformat_full_table_name() on feature table name field for all proto entities.

    def __init__(self, get_host_creds, feature_store_uri: Optional[str] = None):
        """
        Catalog client for the Feature Store client. Takes in an optional parameter to identify the remote workspace
        for multi-workspace Feature Store.
        :param feature_store_uri: An URI of the form ``databricks://<scope>.<prefix>`` that identifies the credentials
          of the intended Feature Store workspace. Throws an error if specified but credentials were not found.
        """
        self._get_host_creds = lambda: get_host_creds(feature_store_uri)
        self._local_host, self._local_workspace_id = self._get_local_workspace_info()
        (
            self._feature_store_workspace_host,
            self._feature_store_workspace_id,
        ) = self._get_feature_store_workspace_info(feature_store_uri)

    @property
    def feature_store_workspace_id(self) -> int:
        return self._feature_store_workspace_id

    def _get_local_workspace_info(self) -> (str, int):
        # Failure to initialize workspace info should not throw an error
        # since that will cause the client initialization to fail in FS <> autoML scenarios.
        # See https://databricks.atlassian.net/browse/ES-964436 for more details.
        try:
            local_host = utils.get_workspace_url()
            workspace_id = databricks_utils.get_workspace_id()
        except Exception:
            local_host = None
            workspace_id = None
        return local_host, self._parse_workspace_id(workspace_id)

    def _get_feature_store_workspace_info(
        self, feature_store_uri: Optional[str] = None
    ) -> (str, int):
        if feature_store_uri:
            # Retrieve the remote hostname and workspace ID stored in the secret scope by the user.
            (
                remote_hostname,
                remote_workspace_id,
            ) = databricks_utils.get_workspace_info_from_databricks_secrets(
                feature_store_uri
            )
            if not remote_workspace_id:
                raise ValueError(
                    f"'FeatureStoreClient' was initialized with 'feature_store_uri' argument "
                    f"for multi-workspace usage, but the remote Feature Store workspace ID was not "
                    f"found at URI {feature_store_uri}."
                )

            if not remote_hostname:
                raise ValueError(
                    f"'FeatureStoreClient' was initialized with 'feature_store_uri' argument "
                    f"for multi-workspace usage, but the remote Feature Store hostname was not "
                    f"found at URI {feature_store_uri}."
                )

            return remote_hostname, self._parse_workspace_id(remote_workspace_id)
        else:
            return self._local_host, self._local_workspace_id

    @staticmethod
    def _parse_workspace_id(workspace_id) -> int:
        if workspace_id:
            try:
                workspace_id = int(workspace_id)
            except (ValueError, TypeError):
                raise ValueError("Internal Error: Workspace ID was not found.")
        return workspace_id

    @staticmethod
    def _resolve_url_params(endpoint, json_str) -> str:
        param_pattern = re.compile(r"{(\w+)}")
        params = param_pattern.findall(endpoint)
        request_dict = json.loads(json_str)
        for param in params:
            if param not in request_dict:
                raise ValueError(f"Missing required parameter {param} in request body.")
            endpoint = endpoint.replace(f"{{{param}}}", request_dict[param])
        return endpoint

    def _call_endpoint(self, api, proto, req_context: RequestContext):
        endpoint, method = _METHOD_TO_INFO[api]
        request_dict = proto_to_json(proto)
        resolved_endpoint = self._resolve_url_params(endpoint, request_dict)
        response_proto = api.Response()
        return call_endpoint(
            self._get_host_creds(),
            resolved_endpoint,
            method,
            request_dict,
            response_proto,
            req_context,
        )

    def _get_feature_table(
        self, feature_table: str, include_producers: bool, req_context: RequestContext
    ):
        req_body = GetFeatureTable(
            name=reformat_full_table_name(feature_table),
            include_producers=include_producers,
            exclude_online_stores=True,
        )
        return self._call_endpoint(GetFeatureTable, req_body, req_context)

    # CRUD API to call Feature Catalog
    def create_feature_table(
        self,
        feature_table: str,
        partition_key_spec,
        primary_key_spec,
        timestamp_key_spec,
        description: str,
        is_imported: str,
        req_context: RequestContext,
    ):
        req_body = CreateFeatureTable(
            name=reformat_full_table_name(feature_table),
            primary_keys=([key_spec.to_proto() for key_spec in primary_key_spec]),
            partition_keys=([key_spec.to_proto() for key_spec in partition_key_spec]),
            timestamp_keys=([key_spec.to_proto() for key_spec in timestamp_key_spec]),
            description=description,
            is_imported=is_imported,
        )
        response_proto = self._call_endpoint(CreateFeatureTable, req_body, req_context)
        return FeatureTable.from_proto(response_proto.feature_table)

    def get_feature_table(
        self,
        feature_table: str,
        req_context: RequestContext,
        include_producers: bool = False,
    ):
        response_proto = self._get_feature_table(
            feature_table, include_producers, req_context
        )
        return FeatureTable.from_proto(response_proto.feature_table)

    def feature_table_exists(self, name: str, req_context: RequestContext):
        """
        Checks whether the feature table exists.

        This CatalogClient method is built on top of the feature-tables/get endpoint. There is no
        dedicated endpoint for feature_table_exists.
        """
        try:
            self.get_feature_table(name, req_context)
        except Exception as e:
            if get_error_code(e) == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST):
                return False
            raise e
        return True

    def can_write_to_catalog(
        self, feature_table_name: str, req_context: RequestContext
    ):
        """
        Checks whether the user has write permission to feature catalog.

        This CatalogClient method is built on top of the feature-tables/get endpoint. There is no
        dedicated endpoint for can_write_to_catalog.
        """
        response_proto = self._get_feature_table(
            feature_table=feature_table_name,
            include_producers=False,
            req_context=req_context,
        )
        return _PermissionLevel.can_write_to_catalog(
            response_proto.feature_table.permission_level
        )

    def publish_feature_table(
        self,
        feature_table: str,
        online_store_metadata: OnlineStoreMetadata,
        features: List[str],
        req_context: RequestContext,
    ):
        req_body = PublishFeatureTable(
            feature_table=reformat_full_table_name(feature_table),
            online_table=online_store_metadata.online_table,
            cloud=online_store_metadata.cloud,
            store_type=online_store_metadata.store_type,
            read_secret_prefix=online_store_metadata.read_secret_prefix,
            write_secret_prefix=online_store_metadata.write_secret_prefix,
            features=features,
        )
        if online_store_metadata.store_type == StoreType.MYSQL:
            req_body.mysql_metadata.CopyFrom(
                online_store_metadata.additional_metadata.to_proto()
            )
        elif online_store_metadata.store_type == StoreType.SQL_SERVER:
            req_body.sql_server_metadata.CopyFrom(
                online_store_metadata.additional_metadata.to_proto()
            )
        elif online_store_metadata.store_type == StoreType.DYNAMODB:
            req_body.dynamodb_metadata.CopyFrom(
                online_store_metadata.additional_metadata.to_proto()
            )
        elif online_store_metadata.store_type == StoreType.COSMOSDB:
            req_body.cosmosdb_metadata.CopyFrom(
                online_store_metadata.additional_metadata.to_proto()
            )
        else:
            raise TypeError(
                f"Unsupported online store metadata type {online_store_metadata.additional_metadata}"
            )

        response_proto = self._call_endpoint(PublishFeatureTable, req_body, req_context)
        return OnlineStoreDetailed.from_proto(response_proto.online_store)

    def delete_online_store(
        self,
        feature_table: str,
        online_store_metadata: OnlineStoreMetadata,
        req_context: RequestContext,
    ):
        req_body = DeleteOnlineStore(
            feature_table=reformat_full_table_name(feature_table),
            online_table=online_store_metadata.online_table,
            cloud=online_store_metadata.cloud,
            store_type=online_store_metadata.store_type,
        )
        if online_store_metadata.store_type == StoreType.DYNAMODB:
            req_body.table_arn = online_store_metadata.additional_metadata.table_arn
        elif online_store_metadata.store_type == StoreType.COSMOSDB:
            req_body.container_uri = (
                online_store_metadata.additional_metadata.container_uri
            )
        self._call_endpoint(DeleteOnlineStore, req_body, req_context)

    def create_features(
        self, feature_table: str, feature_specs, req_context: RequestContext
    ):
        req_body = CreateFeatures(
            feature_table=reformat_full_table_name(feature_table),
            features=[key_spec.to_proto() for key_spec in feature_specs],
        )
        self._call_endpoint(CreateFeatures, req_body, req_context)

    def upgrade_to_uc(
        self,
        source_table_name: str,
        target_table_name: str,
        req_context: RequestContext,
    ):
        req_body = UpgradeToUc(
            source_table_name=reformat_full_table_name(source_table_name),
            target_table_name=reformat_full_table_name(target_table_name),
        )
        self._call_endpoint(UpgradeToUc, req_body, req_context)

    def get_feature_tags(
        self, feature_id: str, req_context: RequestContext
    ) -> List[Tag]:
        req_body = GetTags(feature_id=feature_id)
        response_proto = self._call_endpoint(GetTags, req_body, req_context)
        return [Tag.from_proto(tag_proto) for tag_proto in response_proto.tags]

    def get_features(self, feature_table: str, req_context: RequestContext):
        all_features = []
        page_token = None
        while True:
            # Use default max_results
            req_body = GetFeatures(
                feature_table=reformat_full_table_name(feature_table),
                page_token=page_token,
            )
            response_proto = self._call_endpoint(GetFeatures, req_body, req_context)
            all_features.extend(
                [
                    MaterializedFeature.from_proto(feature)
                    for feature in response_proto.features
                ]
            )
            page_token = response_proto.next_page_token
            if not page_token:
                break
        return all_features

    def update_feature(
        self,
        feature_table: str,
        feature: str,
        data_type: str,
        req_context: RequestContext,
    ):
        req_body = UpdateFeature(
            feature_table=reformat_full_table_name(feature_table),
            name=feature,
            data_type=data_type.upper(),
        )
        response_body = self._call_endpoint(UpdateFeature, req_body, req_context)
        return MaterializedFeature.from_proto(response_body.feature)

    def delete_feature_table(
        self, feature_table: str, req_context: RequestContext, dry_run=False
    ):
        req_body = DeleteFeatureTable(
            name=reformat_full_table_name(feature_table), dry_run=dry_run
        )
        self._call_endpoint(DeleteFeatureTable, req_body, req_context)

    def add_data_sources(
        self,
        feature_table: str,
        tables: List[str],
        paths: List[str],
        custom_sources: List[str],
        req_context: RequestContext,
    ):
        req_body = AddDataSources(
            feature_table=reformat_full_table_name(feature_table),
            tables=tables,
            paths=paths,
            custom_sources=custom_sources,
        )
        self._call_endpoint(AddDataSources, req_body, req_context)

    def delete_data_sources(
        self,
        feature_table: str,
        source_names: List[str],
        req_context: RequestContext,
    ):
        req_body = DeleteDataSources(
            feature_table=reformat_full_table_name(feature_table), sources=source_names
        )
        self._call_endpoint(DeleteDataSources, req_body, req_context)

    def add_notebook_producer(
        self,
        feature_table: str,
        notebook_id: int,
        revision_id: int,
        producer_action: ProducerAction,
        req_context: RequestContext,
    ):
        notebook = Notebook(
            notebook_id=notebook_id,
            revision_id=revision_id,
            notebook_workspace_id=self._local_workspace_id,
            notebook_workspace_url=self._local_host,
        )
        req_body = AddProducer(
            feature_table=reformat_full_table_name(feature_table),
            notebook=notebook,
            producer_action=producer_action,
        )
        self._call_endpoint(AddProducer, req_body, req_context)

    def add_job_producer(
        self,
        feature_table: str,
        job_id: int,
        run_id: int,
        producer_action: ProducerAction,
        req_context: RequestContext,
    ):
        job = Job(
            job_id=job_id,
            run_id=run_id,
            job_workspace_id=self._local_workspace_id,
            job_workspace_url=self._local_host,
        )
        req_body = AddProducer(
            feature_table=reformat_full_table_name(feature_table),
            job_run=job,
            producer_action=producer_action,
        )
        self._call_endpoint(AddProducer, req_body, req_context)

    def add_notebook_consumer(
        self,
        feature_table_map: Dict[str, List[str]],
        notebook_id: int,
        revision_id: int,
        req_context: RequestContext,
    ):
        features = [
            ConsumedFeatures(
                table=reformat_full_table_name(feature_table),
                names=features,
            )
            for feature_table, features in feature_table_map.items()
        ]
        notebook = Notebook(
            notebook_id=notebook_id,
            revision_id=revision_id,
            notebook_workspace_id=self._local_workspace_id,
            notebook_workspace_url=self._local_host,
        )
        req_body = AddConsumer(
            features=features,
            notebook=notebook,
        )
        self._call_endpoint(AddConsumer, req_body, req_context)

    def add_job_consumer(
        self,
        feature_table_map: Dict[str, List[str]],
        job_id: int,
        run_id: int,
        req_context: RequestContext,
    ):
        features = [
            ConsumedFeatures(
                table=reformat_full_table_name(feature_table),
                names=features,
            )
            for feature_table, features in feature_table_map.items()
        ]
        job = Job(
            job_id=job_id,
            run_id=run_id,
            job_workspace_id=self._local_workspace_id,
            job_workspace_url=self._local_host,
        )
        req_body = AddConsumer(
            features=features,
            job_run=job,
        )
        self._call_endpoint(AddConsumer, req_body, req_context)

    def get_consumers(self, feature_table: str, req_context: RequestContext):
        req_body = GetConsumers(feature_table=reformat_full_table_name(feature_table))
        response_proto = self._call_endpoint(GetConsumers, req_body, req_context)
        return [Consumer.from_proto(consumer) for consumer in response_proto.consumers]

    def get_model_serving_metadata(
        self,
        feature_table_to_features: Dict[str, List[str]],
        req_context: RequestContext,
    ):
        req_body = GetModelServingMetadata(
            feature_table_features=[
                FeatureTableFeatures(
                    feature_table_name=reformat_full_table_name(ft_name),
                    features=features,
                )
                for (ft_name, features) in feature_table_to_features.items()
            ]
        )
        response_proto = self._call_endpoint(
            GetModelServingMetadata, req_body, req_context
        )
        return [
            OnlineFeatureTable.from_proto(online_ft)
            for online_ft in response_proto.online_feature_tables
        ]

    def set_feature_table_tags(
        self, feature_table_id: str, tags: Dict[str, str], req_context: RequestContext
    ) -> None:
        proto_tags = [ProtoTag(key=key, value=value) for key, value in tags.items()]
        req_body = SetTags(feature_table_id=feature_table_id, tags=proto_tags)
        self._call_endpoint(SetTags, req_body, req_context)

    def delete_feature_table_tags(
        self, feature_table_id: str, tags: List[str], req_context: RequestContext
    ) -> None:
        req_body = DeleteTags(feature_table_id=feature_table_id, keys=tags)
        self._call_endpoint(DeleteTags, req_body, req_context)

    def get_feature_table_tags(
        self, feature_table_id: str, req_context: RequestContext
    ) -> List[Tag]:
        req_body = GetTags(feature_table_id=feature_table_id)
        response_proto = self._call_endpoint(GetTags, req_body, req_context)
        return [Tag.from_proto(tag_proto) for tag_proto in response_proto.tags]

    def get_online_store(
        self,
        feature_table: str,
        online_store_metadata: OnlineStoreMetadata,
        req_context: RequestContext,
    ):
        req_body = GetOnlineStore(
            feature_table=reformat_full_table_name(feature_table),
            online_table=online_store_metadata.online_table,
            cloud=online_store_metadata.cloud,
            store_type=online_store_metadata.store_type,
        )
        if online_store_metadata.store_type == StoreType.DYNAMODB:
            req_body.table_arn = online_store_metadata.additional_metadata.table_arn
        elif online_store_metadata.store_type == StoreType.COSMOSDB:
            req_body.container_uri = (
                online_store_metadata.additional_metadata.container_uri
            )
        response_proto = self._call_endpoint(GetOnlineStore, req_body, req_context)
        return OnlineStoreDetailed.from_proto(response_proto.online_store)

    def get_online_stores(
        self,
        feature_tables: List[str],
        req_context: RequestContext,
    ):
        req_body = GetOnlineStores(
            feature_tables=list(map(reformat_full_table_name, feature_tables)),
        )
        response_proto = self._call_endpoint(GetOnlineStores, req_body, req_context)
        reformat_table_name_to_table_name = {
            reformat_full_table_name(feature_table): feature_table
            for feature_table in feature_tables
        }
        return {
            reformat_table_name_to_table_name[
                feature_table_online_stores.feature_table
            ]: feature_table_online_stores.online_stores
            for feature_table_online_stores in response_proto.feature_table_online_stores
        }

    @staticmethod
    def _resolve_string_or_list(
        string_or_list: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        if string_or_list is None:
            return None
        return string_or_list if isinstance(string_or_list, List) else [string_or_list]

    def _convert_feature_lookup_to_proto(
        self, feature: FeatureLookup
    ) -> FeatureLookupProto:
        rename_outputs = (
            None
            if feature._rename_outputs is None
            else [
                RenameOutput(feature_name=k, output_name=v)
                for k, v in feature._rename_outputs.items()
            ]
        )
        lookback_window_seconds = (
            None
            if feature.lookback_window is None
            else feature.lookback_window.total_seconds()
        )
        default_values = [
            DefaultValue(feature_name=k, default_value=serialize_default_value(v))
            for k, v in feature.default_values.items()
        ]
        return FeatureLookupProto(
            table_name=feature.table_name,
            lookup_keys=self._resolve_string_or_list(feature.lookup_key),
            feature_names=self._resolve_string_or_list(feature.feature_names),
            rename_outputs=rename_outputs,
            timestamp_lookup_keys=self._resolve_string_or_list(
                feature.timestamp_lookup_key
            ),
            lookback_window_seconds=lookback_window_seconds,
            default_values=default_values,
        )

    @staticmethod
    def _convert_feature_function_to_proto(
        feature: FeatureFunction,
    ) -> FeatureFunctionProto:
        input_bindings = (
            None
            if feature.input_bindings is None
            else [
                InputBinding(parameter_name=k, bound_feature_name=v)
                for k, v in feature.input_bindings.items()
            ]
        )

        return FeatureFunctionProto(
            udf_name=feature.udf_name,
            input_bindings=input_bindings,
            output_name=(
                feature.output_name if feature.output_name else feature.udf_name
            ),
        )

    def _convert_features_to_proto(
        self, features: List[Union[FeatureLookup, FeatureFunction]]
    ) -> List[Features]:
        features_proto = []
        for feature in features:
            if isinstance(feature, FeatureLookup):
                features_proto.append(
                    Features(
                        feature_lookup=self._convert_feature_lookup_to_proto(feature)
                    )
                )
            elif isinstance(feature, FeatureFunction):
                features_proto.append(
                    Features(
                        feature_function=self._convert_feature_function_to_proto(
                            feature
                        )
                    )
                )
        return features_proto

    def create_feature_spec(
        self,
        name: str,
        feature_spec_yaml: str,
        features: List[Union[FeatureLookup, FeatureFunction]],
        exclude_columns: List[str],
        req_context: RequestContext,
    ):
        features_proto = self._convert_features_to_proto(features)
        req_body = CreateFeatureSpec(
            name=name,
            feature_spec_yaml=feature_spec_yaml,
            features=features_proto,
            exclude_columns=exclude_columns,
        )
        response_proto = self._call_endpoint(CreateFeatureSpec, req_body, req_context)
        return FeatureSpecInfo.from_proto(response_proto.feature_spec_info)

    def generate_feature_spec_yaml(
        self,
        features: List[Union[FeatureLookup, FeatureFunction]],
        exclude_columns: List[str],
        input_columns: List[str],
        req_context: RequestContext,
    ):
        req_body = GenerateFeatureSpecYaml(
            features=self._convert_features_to_proto(features),
            exclude_columns=self._resolve_string_or_list(exclude_columns),
            input_columns=input_columns,
        )
        response_proto = self._call_endpoint(
            GenerateFeatureSpecYaml, req_body, req_context
        )
        return response_proto.feature_spec_yaml

    def update_feature_spec(
        self,
        name: str,
        owner: str,
        req_context: RequestContext,
    ) -> None:
        req_body = UpdateFeatureSpec(
            name=name,
            owner=owner,
        )
        self._call_endpoint(UpdateFeatureSpec, req_body, req_context)

    def delete_feature_spec(
        self,
        name: str,
        req_context: RequestContext,
    ) -> None:
        req_body = DeleteFeatureSpec(
            name=name,
        )
        self._call_endpoint(DeleteFeatureSpec, req_body, req_context)

    def log_client_event(
        self, event: str, payload: Any, req_context: RequestContext
    ) -> None:
        """
        Logs a client event to the backend service.
        """
        req_body = LogClientEvent(**{event: payload})
        self._call_endpoint(LogClientEvent, req_body, req_context)

    def validate_declarative_features_enabled(
        self, feature_spec_yaml: Optional[str], req_context: RequestContext
    ) -> None:
        """
        Validates that declarative features are enabled.
        """
        req_body = (
            EnableDeclarativeFeatures()
            if feature_spec_yaml is None
            else EnableDeclarativeFeatures(feature_spec_yaml=feature_spec_yaml)
        )

        try:
            self._call_endpoint(EnableDeclarativeFeatures, req_body, req_context)
        except Exception as e:
            if get_error_code(e) == ErrorCode.Name(ENDPOINT_NOT_FOUND):
                # swallow the error thrown if this RPC is not found
                return
            raise e
