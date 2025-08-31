import base64
import json
import logging
import os
import time
from typing import Dict

import requests
from google.protobuf.json_format import MessageToJson, ParseDict
from mlflow.protos import databricks_pb2

from databricks.ml_features.utils import request_context
from databricks.ml_features.version import VERSION

_ENV_FEATURE_STORE_LITESWAP_ID = "FEATURE_STORE_LITESWAP_ID"
_LITESWAP_ROUTING_HEADER = "x-databricks-traffic-id"
_REST_API_PATH_PREFIX = "/api/2.0"
_DEFAULT_HEADERS = {"User-Agent": "feature-store-python-client/%s" % VERSION}

# The feature store service has a header size limit of 96 kb (API proxy allows 128kb).
# We limit our headers to be within 88kb so together with API proxy added headers (reserving 8kb for them)
# the total header size is within the limit.
_HEADER_SIZE_LIMIT = 88 * 1024

# Default client-side timeout to tell the client stop waiting for a response after a given number of seconds.
# A Timeout exception is raised if the server has not issued a response for timeout seconds.
# Timeout exception is a subclass of RequestException. So timeout will be caught and retried.
_DEFAULT_TIMEOUT_SECONDS = 60 * 2

_logger = logging.getLogger(__name__)


def http_request(
    host_creds,
    endpoint,
    retries=3,
    retry_interval=3,
    max_rate_limit_interval=60,
    extra_headers=None,
    timeout=_DEFAULT_TIMEOUT_SECONDS,
    **kwargs
):
    """
    Makes an HTTP request with the specified method to the specified hostname/endpoint. Ratelimit
    error code (429) will be retried with an exponential back off (1, 2, 4, ... seconds) for at most
    `max_rate_limit_interval` seconds.  Internal errors (500s) will be retried up to `retries` times
    , waiting `retry_interval` seconds between successive retries. Parses the API response
    (assumed to be JSON) into a Python object and returns it.

    :param extra_headers: a dictionary of extra headers to add to request. Headers with None value
      are not sent to server as this class uses the requests lib that ignores them.
    :param host_creds: Databricks creds containing hostname and optional authentication.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :return: Parsed API response
    """
    hostname = host_creds.host
    auth_str = None
    if host_creds.username and host_creds.password:
        basic_auth_str = ("%s:%s" % (host_creds.username, host_creds.password)).encode(
            "utf-8"
        )
        auth_str = "Basic " + base64.standard_b64encode(basic_auth_str).decode("utf-8")
    elif host_creds.token:
        auth_str = "Bearer %s" % host_creds.token

    headers = dict(_DEFAULT_HEADERS)

    # Inject any extra headers
    if extra_headers is not None:
        # This size calc assumes each char takes 1 byte (no unicode etc.), since header names and values should
        # all be ASCII chars as defined by RFC7230. The 2 is for ": " in each header when they are transmitted.
        extra_header_size = 0
        for k, v in extra_headers.items():
            # Only add count if header value is not None, since headers with None values will be
            # dropped when transmitted.
            if v is not None:
                extra_header_size += len(k) + len(v) + 2
        if extra_header_size <= _HEADER_SIZE_LIMIT:
            headers.update(extra_headers)
        else:
            headers[request_context.HEADER_SIZE_EXCEEDED_LIMIT] = "true"

    if auth_str:
        headers["Authorization"] = auth_str

    if host_creds.server_cert_path is None:
        verify = not host_creds.ignore_tls_verification
    else:
        verify = host_creds.server_cert_path

    if host_creds.client_cert_path is not None:
        kwargs["cert"] = host_creds.client_cert_path

    if timeout:
        kwargs["timeout"] = timeout

    def request_with_ratelimit_retries(max_rate_limit_interval, **kwargs):
        response = requests.request(**kwargs)
        time_left = max_rate_limit_interval
        sleep = 1
        while response.status_code == 429 and time_left > 0:
            _logger.warning(
                "API request to %s returned status code 429 (Rate limit exceeded). "
                "Retrying in %d seconds. "
                "Will continue to retry 429s for up to %d seconds.",
                kwargs.get("url", endpoint),
                sleep,
                time_left,
            )
            time.sleep(sleep)
            time_left -= sleep
            response = requests.request(**kwargs)
            sleep = min(time_left, sleep * 2)  # sleep for 1, 2, 4, ... seconds;
        return response

    cleaned_hostname = hostname[:-1] if hostname.endswith("/") else hostname
    url = "%s%s" % (cleaned_hostname, endpoint)
    for i in range(retries):
        try:
            response = request_with_ratelimit_retries(
                max_rate_limit_interval,
                url=url,
                headers=headers,
                verify=verify,
                **kwargs
            )
            if response.status_code < 500:
                return response
            else:
                _logger.error(
                    "API request to %s failed with code %s, retrying up to %s more times. "
                    "API response body: %s",
                    url,
                    response.status_code,
                    retries - i - 1,
                    response.text,
                )
        # All exceptions that Requests explicitly raises inherit from requests.exceptions.RequestException.
        # See https://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        # for more details.
        except requests.exceptions.RequestException as e:
            _logger.error(
                "API request encountered unexpected error: %s. "
                "Requested service might be temporarily unavailable, "
                "retrying up to %s more times.",
                str(e),
                retries - i - 1,
            )
        time.sleep(retry_interval)
    raise Exception("API request to %s failed after %s tries" % (url, retries))


def _can_parse_as_json(string):
    try:
        json.loads(string)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def verify_rest_response(response, endpoint):
    """Verify the return code and format, raise exception if the request was not successful."""
    if response.status_code != 200:
        if _can_parse_as_json(response.text):
            # ToDo(ML-20622): return cleaner error to client, eg: mlflow.exceptions.RestException
            raise Exception(json.loads(response.text))
        else:
            base_msg = (
                "API request to endpoint %s failed with error code "
                "%s != 200"
                % (
                    endpoint,
                    response.status_code,
                )
            )
            raise Exception("%s. Response body: '%s'" % (base_msg, response.text))

    # Skip validation for endpoints (e.g. DBFS file-download API) which may return a non-JSON
    # response
    if endpoint.startswith(_REST_API_PATH_PREFIX) and not _can_parse_as_json(
        response.text
    ):
        base_msg = (
            "API request to endpoint was successful but the response body was not "
            "in a valid JSON format"
        )
        raise Exception("%s. Response body: '%s'" % (base_msg, response.text))

    return response


def get_error_code(e: Exception):
    if hasattr(e, "args") and len(e.args) > 0 and "error_code" in e.args[0]:
        return e.args[0]["error_code"]
    return None


def get_path(path_prefix, endpoint_path):
    return "{}{}".format(path_prefix, endpoint_path)


def extract_api_info_for_service(service, path_prefix):
    """Return a dictionary mapping each API method to a tuple (path, HTTP method)"""
    service_methods = service.DESCRIPTOR.methods
    res = {}
    for service_method in service_methods:
        endpoints = service_method.GetOptions().Extensions[databricks_pb2.rpc].endpoints
        endpoint = endpoints[0]
        endpoint_path = get_path(path_prefix, endpoint.path)
        res[service().GetRequestClass(service_method)] = (
            endpoint_path,
            endpoint.method,
        )
    return res


def json_to_proto(js_dict, message):
    """Parses a JSON dictionary into a message proto, ignoring unknown fields in the JSON."""
    ParseDict(js_dict=js_dict, message=message, ignore_unknown_fields=True)


def proto_to_json(message):
    """Converts a message to JSON, using snake_case for field names."""
    return MessageToJson(message, preserving_proto_field_name=True)


# GET requests encode all parameters as part of the URL string, e.g. endpoint?param1=str&param2=0&param3=true
# However, Python's requests library does not properly lowercase boolean parameters for GET requests,
# e.g. it sends "endpoint?param=True" instead of "endpoint?param=true" for parameters {"param": True}.
#
# We convert booleans to lowercase strings as this aligns with industry standards and is expected by the backend.
# Per Google documentation, we must support primitives, repeated primitives, and non-repeated nested messages.
# https://github.com/googleapis/googleapis/blob/73da6697f598f1ba30618924936a59f8e457ec89/google/api/http.proto#L117
def lowercase_bools_for_get_request_params(json_body: Dict[str, any]) -> Dict[str, any]:
    def convert_value(value: any):
        # support repeated primitives
        if isinstance(value, list):
            return [convert_value(e) for e in value]
        # support nested messages
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        # convert value to lowercase string if it's a boolean
        else:
            return "true" if value is True else "false" if value is False else value

    return {k: convert_value(v) for k, v in json_body.items()}


def call_endpoint(
    host_creds,
    endpoint,
    method,
    json_body,
    response_proto,
    req_context,
    timeout=_DEFAULT_TIMEOUT_SECONDS,
):
    # Convert json string to json dictionary, to pass to requests
    if json_body:
        json_body = json.loads(json_body)

    headers = req_context.get_headers()
    # Route request to LiteSwap unit if configured in environment variable
    assert _LITESWAP_ROUTING_HEADER not in headers
    if _ENV_FEATURE_STORE_LITESWAP_ID in os.environ:
        headers[_LITESWAP_ROUTING_HEADER] = os.environ[_ENV_FEATURE_STORE_LITESWAP_ID]

    if method == "GET":
        params = lowercase_bools_for_get_request_params(json_body)
        response = http_request(
            host_creds=host_creds,
            endpoint=endpoint,
            method=method,
            params=params,
            extra_headers=headers,
            timeout=timeout,
        )
    else:
        response = http_request(
            host_creds=host_creds,
            endpoint=endpoint,
            method=method,
            json=json_body,
            extra_headers=headers,
            timeout=timeout,
        )
    response = verify_rest_response(response, endpoint)
    js_dict = json.loads(response.text)
    json_to_proto(js_dict=js_dict, message=response_proto)
    return response_proto
