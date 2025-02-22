"""
Contains useful wrappers for HTTPS requests.
"""
import json
import base64
import requests
from dateutil import parser
from termcolor import cprint

from e2etest.config import TestCfg


def get_server_interface(test_cfg: TestCfg, interface: str):
    """
    Wrapper for a GET request for the server returning the specified interface data.
    """
    request_body = (
        test_cfg.api_url
        + "/appengine/v1/"
        + test_cfg.realm
        + "/devices/"
        + test_cfg.device_id
        + "/interfaces/"
        + interface
    )
    headers = {"Authorization": "Bearer " + test_cfg.appengine_token}
    print(f"Sending HTTP GET request: {request_body}", flush=True)
    res = requests.get(request_body, headers=headers, timeout=1)
    if res.status_code != 200:
        cprint(res.text, "red", flush=True)
        raise requests.HTTPError("GET request failed.")

    return res.json()


def post_server_interface(test_cfg: TestCfg, interface: str, endpoint: str, data: dict):
    """
    Wrapper for a POST request for the server, uploading new values to an interface.
    """
    request_body = (
        test_cfg.api_url
        + "/appengine/v1/"
        + test_cfg.realm
        + "/devices/"
        + test_cfg.device_id
        + "/interfaces/"
        + interface
        + endpoint
    )
    json_data = json.dumps({"data": data}, default=str)
    headers = {
        "Authorization": "Bearer " + test_cfg.appengine_token,
        "Content-Type": "application/json",
    }
    print(f"Sending HTTP POST request: {request_body} {json_data}", flush=True)
    res = requests.post(url=request_body, data=json_data, headers=headers, timeout=1)
    if res.status_code != 200:
        cprint(res.text, "red", flush=True)
        raise requests.HTTPError("POST request failed.")


def delete_server_interface(test_cfg: TestCfg, interface: str, endpoint: str):
    """
    Wrapper for a DELETE request for the server, deleting an endpoint.
    """
    request_body = (
        test_cfg.api_url
        + "/appengine/v1/"
        + test_cfg.realm
        + "/devices/"
        + test_cfg.device_id
        + "/interfaces/"
        + interface
        + endpoint
    )
    headers = {
        "Authorization": "Bearer " + test_cfg.appengine_token,
        "Content-Type": "application/json",
    }
    print(f"Sending HTTP DELETE request: {request_body}", flush=True)
    res = requests.delete(request_body, headers=headers, timeout=1)
    if res.status_code != 204:
        cprint(res.text, "red", flush=True)
        raise requests.HTTPError("DELETE request failed.")


def prepare_transmit_data(key, value):
    """
    Some data to be transmitted should be encoded to an appropriate type.
    """
    if key == "binaryblob_endpoint":
        return base64.b64encode(value).decode("utf-8")
    if key == "binaryblobarray_endpoint":
        return [base64.b64encode(v).decode("utf-8") for v in value]
    return value


def parse_received_data(data):
    """
    Some of the received data is not automatically parsed as python types.
    Specifically, datetime and binaryblob should be converted manually from strings.
    """
    # Parse datetime from string to datetime
    data["datetime_endpoint"] = parser.parse(data["datetime_endpoint"])
    data["datetimearray_endpoint"] = [parser.parse(dt) for dt in data["datetimearray_endpoint"]]

    # Decode binary blob from base64
    data["binaryblob_endpoint"] = base64.b64decode(data["binaryblob_endpoint"])
    data["binaryblobarray_endpoint"] = [
        base64.b64decode(dt) for dt in data["binaryblobarray_endpoint"]
    ]
