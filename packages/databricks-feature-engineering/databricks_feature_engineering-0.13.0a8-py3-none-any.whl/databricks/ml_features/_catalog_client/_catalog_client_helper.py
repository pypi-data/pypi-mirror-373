import logging
from typing import Set

from mlflow.protos.databricks_pb2 import RESOURCE_DOES_NOT_EXIST, ErrorCode
from mlflow.utils import databricks_utils

from databricks.ml_features._catalog_client._catalog_client import CatalogClient
from databricks.ml_features._databricks_client._databricks_client import (
    DatabricksClient,
)
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.utils import utils
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.rest_utils import get_error_code

_logger = logging.getLogger(__name__)


class CatalogClientHelper:
    """
    Helper functions that wrap calls to the catalog client with additional business logic, possibly invoking
    other clients as well (eg, DatabricksClient).
    """

    def __init__(
        self, catalog_client: CatalogClient, databricks_client: DatabricksClient
    ):
        self._catalog_client = catalog_client
        self._databricks_client = databricks_client

    def add_job_or_notebook_producer(
        self, feature_table_name, producer_action, req_context: RequestContext
    ):
        try:
            if utils.is_in_databricks_job():
                job_id = databricks_utils.get_job_id()
                if job_id:
                    job_id = int(job_id)
                    job_run_id = databricks_utils.get_job_run_id()
                    job_run_id = int(job_run_id) if job_run_id else None
                    self._catalog_client.add_job_producer(
                        feature_table_name,
                        job_id,
                        job_run_id,
                        producer_action,
                        req_context,
                    )
                else:
                    _logger.warning(
                        f"Failed to record producer in the catalog. Missing job_id ({job_id})"
                    )
            elif databricks_utils.is_in_databricks_notebook():
                notebook_path = databricks_utils.get_notebook_path()
                notebook_id = databricks_utils.get_notebook_id()
                if notebook_id:
                    notebook_id = int(notebook_id)
                    revision_id = self._databricks_client.take_notebook_snapshot(
                        notebook_path
                    )
                    revision_id = int(revision_id) if revision_id else None
                    self._catalog_client.add_notebook_producer(
                        feature_table_name,
                        notebook_id,
                        revision_id,
                        producer_action,
                        req_context,
                    )
                else:
                    _logger.warning(
                        f"Failed to record producer in the catalog. "
                        f"Missing notebook_id ({notebook_id})."
                    )
        except Exception as e:
            if get_error_code(e) == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST):
                _logger.warning(
                    f"Failed to record producer in the catalog. Notebook may have been renamed. Exception: {e}",
                )
            else:
                _logger.warning(
                    f"Failed to record producer in the catalog. Exception: {e}",
                    exc_info=True,
                )

    def add_consumer(self, feature_table_map, req_context: RequestContext):
        try:
            if utils.is_in_databricks_job():
                job_id = databricks_utils.get_job_id()
                job_run_id = databricks_utils.get_job_run_id()
                if job_id:
                    job_id = int(job_id)
                    job_run_id = int(job_run_id) if job_run_id else None
                    self._catalog_client.add_job_consumer(
                        feature_table_map, job_id, job_run_id, req_context
                    )
                else:
                    _logger.warning(
                        f"Failed to record consumer in the catalog. Missing job_run_id ({job_id})."
                    )
            elif databricks_utils.is_in_databricks_notebook():
                notebook_path = databricks_utils.get_notebook_path()
                notebook_id = databricks_utils.get_notebook_id()
                if notebook_id:
                    notebook_id = int(notebook_id)
                    revision_id = self._databricks_client.take_notebook_snapshot(
                        notebook_path
                    )
                    revision_id = int(revision_id) if revision_id else None
                    self._catalog_client.add_notebook_consumer(
                        feature_table_map, notebook_id, revision_id, req_context
                    )
                else:
                    _logger.warning(
                        f"Failed to record consumer in the catalog. "
                        f"Missing notebook_id ({notebook_id})."
                    )
        except Exception as e:
            _logger.warning(
                f"Failed to record consumer in the catalog. Exception: {e}",
                exc_info=True,
            )

    def add_data_sources(
        self,
        name: str,
        tables: Set[str],
        paths: Set[str],
        custom_sources: Set[str],
        req_context: RequestContext,
    ):
        try:
            self._catalog_client.add_data_sources(
                name,
                tables=list(tables),
                paths=list(paths),
                custom_sources=list(custom_sources),
                req_context=req_context,
            )
        except Exception as e:
            _logger.warning(
                f"Failed to record data sources in the catalog. Exception: {e}",
                exc_info=True,
            )

    def get_feature_table_from_uc_and_online_store_from_fs(
        self,
        table_name: str,
        req_context: RequestContext,
        include_producers: bool = False,
    ):
        uc_response = self._databricks_client.get_uc_table(table_name)
        feature_table_from_uc = FeatureTable.from_uc_get_table_response(uc_response)

        if "table_type" in uc_response and uc_response["table_type"] == "VIEW":
            feature_table_from_fs = self._catalog_client.get_feature_table(
                table_name, req_context, include_producers=include_producers
            )
            feature_table_from_uc.primary_keys = feature_table_from_fs.primary_keys
            feature_table_from_uc.timestamp_keys = feature_table_from_fs.timestamp_keys
            feature_table_from_uc.features = feature_table_from_fs.features
        else:
            online_stores_from_fs = self._catalog_client.get_online_stores(
                [table_name], req_context
            )[table_name]
            feature_table_from_uc.online_stores = online_stores_from_fs
        return feature_table_from_uc
