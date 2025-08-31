import json
import os
import re
import sys
from typing import Dict, List, Optional, Union

import mlflow
from mlflow.entities.model_registry.model_version import ModelVersion
from mlflow.tracking import MlflowClient
from pyspark import TaskContext
from pyspark.sql import SparkSession

import databricks.ml_features.local_models as local_models
from databricks.ml_features._databricks_client._databricks_client import (
    DatabricksClient,
)
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.entities.feature_serving_endpoint import (
    EndpointCoreConfig,
    FeatureServingEndpoint,
)
from databricks.ml_features.utils import request_context, training_scoring_utils
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.rest_utils import http_request, verify_rest_response
from databricks.ml_features_common.entities.on_demand_column_info import (
    OnDemandColumnInfo,
)

BASE_API_PATH = "/api/2.0/serving-endpoints"
MODEL_NAME_PREFIX = "feature-serving-model-"

# Must be one or more characters including alphanumeric, dash and underscore. The first and
# last characters can only be alphanumeric. Maximal length is 63 characters.
ENDPOINT_NAME_REGEX = "^(([a-zA-Z0-9][a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])|[a-zA-Z0-9])$"


class FeatureServingEndpointClient:
    def __init__(self, get_host_creds, fs_client):
        self._get_host_creds = get_host_creds
        self._endpoint_name_matcher = re.compile(ENDPOINT_NAME_REGEX)
        self._model_registry_uri = fs_client._model_registry_uri

        # TaskContext.get() is None on Spark drivers. This is the same check performed by
        # SparkContext._assert_on_driver(), which is called by SparkSession.getOrCreate().
        self._on_spark_driver = TaskContext.get() is None

        # Initialize a SparkSession only if on the driver.
        # _internal_spark should not be accessed directly, but through the _spark property.
        # TODO [ML-40496]: Add back appName to spark initialization once spark connect team gives a proper long term solution
        self._internal_spark = (
            SparkSession.builder.getOrCreate() if self._on_spark_driver else None
        )
        self._mlflow_client = MlflowClient()
        self._databricks_client = DatabricksClient(self._get_host_creds)

    @property
    def _spark(self):
        """
        Property method to return the initialized SparkSession.
        Throws outside of the Spark driver as the SparkSession is not initialized.
        """
        if not self._on_spark_driver:
            raise ValueError(
                "Spark operations are not enabled outside of the driver node."
            )
        return self._internal_spark

    def create_feature_serving_endpoint(
        self,
        name: str,
        config: EndpointCoreConfig,
        client_name: str,
        route_optimized: Optional[bool] = None,
    ) -> FeatureServingEndpoint:
        self._validate_endpoint_name(name)
        self._verify_endpoint_not_exists(name)
        self._validate_feature_spec_exists(config.served_entities.feature_spec_name)
        request_body = self._get_create_endpoint_request_body_with_feature_spec(
            endpoint_name=name,
            config=config,
            route_optimized=route_optimized,
        )
        result = self._call_api(path="", method="POST", json_body=request_body)
        return self._convert_to_feature_serving_endpoint(result)

    def get_feature_serving_endpoint(self, name) -> FeatureServingEndpoint:
        self._validate_endpoint_name(name)
        result = self._call_api(f"/{name}", method="GET", json_body={})
        return self._convert_to_feature_serving_endpoint(result)

    def delete_feature_serving_endpoint(self, name) -> None:
        self._validate_endpoint_name(name)
        endpoint = self._call_api(f"/{name}", method="GET", json_body={})
        legacy_model_name = self._get_model_name(name)
        need_delete_model = self._has_served_entity_of_name(endpoint, legacy_model_name)
        self._call_api(f"/{name}", "DELETE", {})
        if need_delete_model:
            self._mlflow_client.delete_registered_model(legacy_model_name)

    def _list_endpoints(self):
        listresult = self._call_api(path="", method="GET", json_body=None)
        if "endpoints" in listresult:
            return listresult["endpoints"]
        else:
            # when the result is empty the key "endpoints" is missing.
            return []

    def _validate_endpoint_name(self, name):
        if not self._endpoint_name_matcher.match(name):
            raise ValueError(
                "Endpoint name must only contain alphanumeric and dashes."
                " The first or last character cannot be dash"
            )

    def _verify_endpoint_not_exists(self, endpoint_name) -> None:
        existing_endpoints = self._list_endpoints()
        if endpoint_name in {endpoint["name"] for endpoint in existing_endpoints}:
            raise ValueError(f"Endpoint {endpoint_name} already exists")

    def _get_model_name(self, endpoint_name) -> str:
        return MODEL_NAME_PREFIX + endpoint_name

    def _get_create_endpoint_request_body_with_feature_spec(
        self,
        endpoint_name: str,
        config: EndpointCoreConfig,
        route_optimized: Optional[bool] = None,
    ) -> Dict:
        served_entities = [
            {
                "name": config.served_entities.name,
                "entity_name": config.served_entities.feature_spec_name,
                "workload_size": config.served_entities.workload_size,
                "scale_to_zero_enabled": config.served_entities.scale_to_zero_enabled,
                "instance_profile_arn": config.served_entities.instance_profile_arn,
            }
        ]
        auto_capture_dict = (
            config.auto_capture_config.to_dict() if config.auto_capture_config else None
        )
        result = {
            "name": endpoint_name,
            "config": {
                "served_entities": served_entities,
                "auto_capture_config": auto_capture_dict,
            },
            "is_feature_serving": True,
        }
        if route_optimized is not None:
            result["route_optimized"] = route_optimized

        return result

    # path starts with '/'
    # method can be GET/POST/etc
    def _call_api(self, path, method, json_body) -> Dict:
        api = BASE_API_PATH + path
        host_creds = self._get_host_creds()
        if method in ["GET", "DELETE"]:
            response = http_request(
                host_creds=host_creds,
                endpoint=api,
                method=method,
            )
        else:
            response = http_request(
                host_creds=host_creds,
                endpoint=api,
                method=method,
                json=json_body,
            )
        verify_rest_response(response=response, endpoint=api)
        return json.loads(response.text)

    def _convert_to_feature_serving_endpoint(
        self, json_result
    ) -> FeatureServingEndpoint:
        return FeatureServingEndpoint(
            json_result["name"],
            json_result["creator"],
            json_result["creation_timestamp"],
            json_result["state"],
        )

    def _has_served_entity_of_name(self, json_result, served_entity_name) -> bool:
        if "config" not in json_result and "pending_config" not in json_result:
            return False
        # gets configs from field config or pending_config
        config = json_result.get("config", None) or json_result["pending_config"]
        # gets served_entities from field served_entities or served_models
        served_entities = config.get("served_entities", None) or config.get(
            "served_models", []
        )
        for served_entity in served_entities:
            # gets entity name from field entity_name or model_name
            entity_name = served_entity.get("entity_name", None) or served_entity.get(
                "model_name", None
            )
            if entity_name == served_entity_name:
                return True
        return False

    def _validate_feature_spec_exists(self, feature_spec_name):
        self._databricks_client.verify_feature_spec_in_uc(feature_spec_name)
