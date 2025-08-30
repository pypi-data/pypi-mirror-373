from datetime import datetime

import pytest
import requests

from square_commons.api_utils import (
    get_api_output_in_standard_format,
    make_request_json_output,
    create_cookie,
    make_request,
)


def test_get_api_output_in_standard_format():
    result = get_api_output_in_standard_format(
        data={"key": "value"}, message="Success", log={"time_taken": 25}
    )
    assert result == {
        "data": {"key": "value"},
        "message": "Success",
        "log": {"time_taken": 25},
    }


def test_make_request_json_output_success(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"message": "Success"}
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.request", return_value=mock_response)

    result = make_request_json_output(
        method="GET", base_url="https://httpbin.org", endpoint="get"
    )
    assert result == {"message": "Success"}


def test_make_request_json_output_failure(mocker):
    mocker.patch("requests.request", side_effect=requests.RequestException)

    with pytest.raises(Exception):
        make_request_json_output(
            method="GET", base_url="https://httpbin.org", endpoint="get"
        )


def test_create_cookie():
    expires = datetime(2025, 12, 31, 23, 59, 59)
    cookie = create_cookie(
        key="sessionid",
        value="abc123",
        domain="example.com",
        expires=expires,
        same_site="Lax",
        secure=True,
        http_only=True,
    )
    assert cookie == {
        "key": "sessionid",
        "value": "abc123",
        "domain": "example.com",
        "expires": "Wed, 31-Dec-2025 23:59:59 GMT",
        "path": "/",
        "samesite": "Lax",
        "secure": True,
        "httponly": True,
    }


def test_create_cookie_invalid_expires():
    with pytest.raises(ValueError, match="Expires must be a datetime object."):
        create_cookie("key", "value", expires="invalid")


def test_make_request_output_success(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"message": "Success"}
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.request", return_value=mock_response)

    result = make_request(
        method="GET",
        url="https://httpbin.org",
        endpoint="get",
        return_type="json",
    )
    assert result == {"message": "Success"}


def test_make_request_output_failure(mocker):
    mocker.patch("requests.request", side_effect=requests.RequestException)

    with pytest.raises(Exception):
        make_request(
            method="GET",
            url="https://httpbin.org",
            endpoint="get",
            return_type="json",
        )


def test_make_request_text_output_success(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html><body>ok</body></html>"
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.request", return_value=mock_response)

    result = make_request(
        method="GET",
        url="https://httpbin.org",
        endpoint="get",
        return_type="text",
    )
    assert result == "<html><body>ok</body></html>"


def test_make_request_bytes_output_success(mocker):
    mock_response = mocker.Mock()
    mock_response.content = b"binary-data"
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.request", return_value=mock_response)

    result = make_request(
        method="GET",
        url="https://httpbin.org",
        endpoint="get",
        return_type="bytes",
    )
    assert result == b"binary-data"


def test_make_request_response_output_success(mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.request", return_value=mock_response)

    result = make_request(
        method="GET",
        url="https://httpbin.org",
        endpoint="get",
        return_type="response",
    )
    assert result is mock_response


def test_make_request_passes_timeout(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "ok"
    mock_response.raise_for_status = mocker.Mock()

    mock_request = mocker.patch("requests.request", return_value=mock_response)

    result = make_request(
        method="GET",
        url="https://httpbin.org",
        endpoint="get",
        return_type="text",
        timeout=5,
    )
    mock_request.assert_called_once()
    _, kwargs = mock_request.call_args
    assert kwargs["timeout"] == 5
    assert result == "ok"
