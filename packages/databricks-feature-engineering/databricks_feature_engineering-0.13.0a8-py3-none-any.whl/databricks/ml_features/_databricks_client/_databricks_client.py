from typing import Dict
from urllib.parse import quote

from databricks.ml_features.utils.rest_utils import http_request, verify_rest_response

_GET_JOB_ENDPOINT = "/api/2.0/jobs/get"


class DatabricksClient:
    """
    This client issues requests to services other than Feature Store.

    If the number of APIs accessed grows too large, we should split this up into per-service APIs
    and import the request/repsonse protos for validation.
    """

    def __init__(self, get_host_creds):
        self._get_host_creds = get_host_creds

    def take_notebook_snapshot(self, notebook_path: str):
        """
        Sends a request to WebApp to take a notebook snapshot, and returns the revision timestamp
        of the snapshot.

        This method should be updated to route the call through the Feature Store service, as
        mlflow does.
        """
        response = http_request(
            self._get_host_creds(),
            "/api/2.0/workspace/take-notebook-snapshot",  # Inlined because this is not a public API
            method="POST",
            json={"hidden": True, "path": notebook_path},
        )
        response = verify_rest_response(
            response, "/api/2.0/workspace/take-notebook-snapshot"
        )
        # It would be better to deserialize the response as a proto, but the Feature Store python
        # wheel should not leak other internal WebApp APIs.
        return response.json()["revision"]["revision_timestamp"]

    def delete_uc_function(self, full_function_name: str):
        """
        Sends a request to UnityCatalog to delete a feature spec.
        """
        url = f"/api/2.0/unity-catalog/functions/{full_function_name}"
        response = http_request(
            self._get_host_creds(),
            url,
            method="DELETE",
        )
        verify_rest_response(response, url)

    def verify_feature_spec_in_uc(self, full_feature_spec_name: str):
        """
        Verify a FeatureSpec exists in UnityCatalog and verify the securable kind is FeatureSpec.
        """
        url = f"/api/2.0/unity-catalog/functions/{full_feature_spec_name}"
        response = http_request(
            self._get_host_creds(),
            url,
            method="GET",
        )
        verify_rest_response(response, url)
        if response.json()["securable_kind"] != "FUNCTION_FEATURE_SPEC":
            raise ValueError(f"{full_feature_spec_name} is not a FeatureSpec.")

    def get_uc_table(self, table_name: str) -> Dict[str, str]:
        """
        Get a UC table.
        """
        url = f"/api/2.1/unity-catalog/tables/{quote(table_name)}"
        response = http_request(
            self._get_host_creds(),
            url,
            method="GET",
        )
        verify_rest_response(response, url)
        resp_json = response.json()
        return resp_json

    def get_uc_table_tags(self, table_name: str) -> Dict[str, str]:
        """
        Get the tags for a UC table.
        """
        url = f"/api/2.0/unity-catalog/securable-tags/TABLE/{quote(table_name)}"
        response = http_request(
            self._get_host_creds(),
            url,
            method="GET",
        )
        verify_rest_response(response, url)
        resp_json = response.json()
        if "tag_assignments" in resp_json:
            tag_assignments = resp_json["tag_assignments"]
            if len(tag_assignments) > 0 and "tag_key_value_pairs" in tag_assignments[0]:
                key_value_pairs = tag_assignments[0]["tag_key_value_pairs"]
                tags = {tag["key"]: tag["value"] for tag in key_value_pairs}
                return tags
        return {}

    def get_uc_function(self, function_name: str) -> Dict[str, str]:
        """
        Get a UC function.
        """
        url = f"/api/2.0/unity-catalog/functions/{function_name}"
        response = http_request(
            self._get_host_creds(),
            url,
            method="GET",
        )
        verify_rest_response(response, url)
        resp_json = response.json()
        return resp_json
