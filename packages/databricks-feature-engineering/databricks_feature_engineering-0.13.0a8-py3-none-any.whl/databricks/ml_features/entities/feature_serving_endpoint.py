import logging
from typing import Dict, List, Optional, Union

from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.utils import utils
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)

FEATURE_SERVING_ENDPOINT_PREFIX = "serving-endpoints"

_logger = logging.getLogger(__name__)


class AutoCaptureConfig(_FeatureStoreObject):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.entities.feature_serving_endpoint.AutoCaptureConfig`, `!databricks.feature_store.entities.feature_serving_endpoint.AutoCaptureConfig`
    """

    def __init__(
        self,
        *,
        catalog_name: str,
        schema_name: str,
        table_name_prefix: str,
        enabled: bool = True,
    ):
        """
        :param catalog_name: The catalog name of the auto-capturing tables
        :param schema_name: The schema name of the auto-capturing tables
        :param table_name_prefix: The prefix of the table names
        """
        self.catalog_name = catalog_name
        self.schema_name = schema_name
        self.table_name_prefix = table_name_prefix
        self.enabled = enabled

    def to_dict(self):
        return {
            "catalog_name": self.catalog_name,
            "schema_name": self.schema_name,
            "table_name_prefix": self.table_name_prefix,
            "enabled": self.enabled,
        }


class ServedEntity(_FeatureStoreObject):
    """
    .. note::

       Aliases: `databricks.feature_engineering.entities.feature_serving_endpoint.ServedEntity`, `databricks.feature_store.entities.feature_serving_endpoint.ServedEntity`
    """

    def __init__(
        self,
        *,
        feature_spec_name: str,
        name: str = "",
        workload_size: str = "Small",
        scale_to_zero_enabled: bool = True,
        instance_profile_arn: str = None,
    ):
        """
        A ServedEntity represents a FeatureSpec to be served and related configurations.
        :param feature_spec_name: The name of a FeatureSpec in UC.
        :param workload_size: Allowed values are Small, Medium, Large.
        :param scale_to_zero_enabled: If enabled, the cluster size will scale to 0 when there is no traffic for certain amount of time.
        :param instance_profile_arn: The ARN of the IAM instance profile to use for the cluster.
        """
        self.feature_spec_name = feature_spec_name
        self.name = name
        self.workload_size = workload_size
        self.scale_to_zero_enabled = scale_to_zero_enabled
        self.instance_profile_arn = instance_profile_arn


class Servable(_FeatureStoreObject):
    """
    .. note::

       Aliases: `databricks.feature_engineering.entities.feature_serving_endpoint.Servable`, `databricks.feature_store.entities.feature_serving_endpoint.Servable`
    """

    def __init__(
        self,
        features: List[Union[FeatureLookup, FeatureFunction]],
        workload_size: str = "Small",
        scale_to_zero_enabled: bool = True,
        extra_pip_requirements: Optional[List[str]] = None,
    ):
        """
        A Servable is a group of features to be served and related configurations.
        :param features: A list of FeatureLookups and FeatureFunctions.
        :param workload_size: Allowed values are Small, Medium, Large.
        :param scale_to_zero_enabled: If enabled, the cluster size will scale to 0 when there is no traffic for certain amount of time.
        :param extra_pip_requirements: The requirements needed by FeatureFunctions.
        """
        self.features = features
        self.workload_size = workload_size
        self.scale_to_zero_enabled = scale_to_zero_enabled
        self.extra_pip_requirements = extra_pip_requirements


class EndpointCoreConfig(_FeatureStoreObject):
    """
    .. note::

       Aliases: `databricks.feature_engineering.entities.feature_serving_endpoint.EndpointCoreConfig`, `databricks.feature_store.entities.feature_serving_endpoint.EndpointCoreConfig`
    """

    def __init__(
        self,
        servables: Servable = None,
        *,
        served_entities: ServedEntity = None,
        auto_capture_config: AutoCaptureConfig = None,
    ):
        """
        :param servables: Deprecated. Please use served_entities instead.
        :param served_entities: A ServedEntity specified in this config.
        :param auto_capture_config: The config for auto-capturing.
        """
        if isinstance(servables, ServedEntity):
            raise ValueError(
                "served_entities should be specified as named argument, e.g. "
                "EndpointCoreConfig(served_entities=ServedEntity(...))"
            )
        if servables is None and served_entities is None:
            raise ValueError(
                "served_entities should be specified in EndpointCoreConfig."
            )
        if servables is not None and served_entities is not None:
            raise ValueError(
                "Only one of servables and served_entities should be specified in "
                "EndpointCoreConfig."
            )
        if servables is not None:
            _logger.warning(
                "servables in EndpointCoreConfig is deprecated. "
                "Please use served_entities instead."
            )
        self.servables = servables
        self.served_entities = served_entities
        self.auto_capture_config = auto_capture_config


class FeatureServingEndpoint(_FeatureStoreObject):
    """
    .. note::

       Aliases: `databricks.feature_engineering.entities.feature_serving_endpoint.FeatureServingEndpoint`, `databricks.feature_store.entities.feature_serving_endpoint.FeatureServingEndpoint`
    """

    def __init__(
        self,
        name: str,
        creator: str,
        creation_time_millis: int,
        state: Dict[str, str],
    ):
        self._name = name
        self._creator = creator
        self._creation_time_millis = creation_time_millis
        self._state = state

    @property
    def name(self) -> str:
        return self._name

    @property
    def creator(self) -> str:
        return self._creator

    @property
    def creation_time_millis(self) -> int:
        return self._creation_time_millis

    @property
    def state(self) -> Dict[str, str]:
        """The state of the endpoint. Value could be READY, FAILED or IN_PROGRESS."""
        return self._state

    @property
    def url(self) -> str:
        return "/".join(
            [
                utils.get_workspace_url(),
                FEATURE_SERVING_ENDPOINT_PREFIX,
                self.name,
                "invocations",
            ]
        )
