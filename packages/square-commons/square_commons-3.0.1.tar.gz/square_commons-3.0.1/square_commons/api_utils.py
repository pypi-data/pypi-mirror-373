from datetime import datetime
from typing import Any, Literal, overload, Optional

import requests
from deprecated import deprecated


def get_api_output_in_standard_format(
    data: Any = None,
    message: str = None,
    log: Any = None,
):
    return {"data": data, "message": message, "log": log}


@deprecated(
    "make_request_json_output has been deprecated, use make_request with return_type='json' instead."
)
def make_request_json_output(
    method,
    base_url,
    endpoint,
    data=None,
    json=None,
    params=None,
    headers=None,
    files=None,
    auth=None,
) -> Any:
    return make_request(
        method=method,
        url=base_url,
        endpoint=endpoint,
        data=data,
        json=json,
        params=params,
        headers=headers,
        files=files,
        auth=auth,
        timeout=None,
        return_type="json",
    )


@overload
def make_request(
    method: str,
    url: str,
    *,
    endpoint: Optional[str] = ...,
    data: Optional[dict] = ...,
    json: Optional[dict] = ...,
    params: Optional[dict] = ...,
    headers: Optional[dict] = ...,
    files: Optional[dict] = ...,
    auth: Optional[Any] = ...,
    timeout: Optional[float] = ...,
    return_type: Literal["json"],
) -> Any: ...


@overload
def make_request(
    method: str,
    url: str,
    *,
    endpoint: Optional[str] = ...,
    data: Optional[dict] = ...,
    json: Optional[dict] = ...,
    params: Optional[dict] = ...,
    headers: Optional[dict] = ...,
    files: Optional[dict] = ...,
    auth: Optional[Any] = ...,
    timeout: Optional[float] = ...,
    return_type: Literal["text"],
) -> str: ...


@overload
def make_request(
    method: str,
    url: str,
    *,
    endpoint: Optional[str] = ...,
    data: Optional[dict] = ...,
    json: Optional[dict] = ...,
    params: Optional[dict] = ...,
    headers: Optional[dict] = ...,
    files: Optional[dict] = ...,
    auth: Optional[Any] = ...,
    timeout: Optional[float] = ...,
    return_type: Literal["bytes"],
) -> bytes: ...


@overload
def make_request(
    method: str,
    url: str,
    *,
    endpoint: Optional[str] = ...,
    data: Optional[dict] = ...,
    json: Optional[dict] = ...,
    params: Optional[dict] = ...,
    headers: Optional[dict] = ...,
    files: Optional[dict] = ...,
    auth: Optional[Any] = ...,
    timeout: Optional[float] = ...,
    return_type: Literal["response"],
) -> requests.Response: ...


def make_request(
    method: str,
    url: str,
    *,
    endpoint: Optional[str] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    files: Optional[dict] = None,
    auth: Optional[Any] = None,
    timeout: Optional[float] = None,
    return_type: Literal["json", "text", "bytes", "response"] = "text",
) -> Any:

    if headers:
        headers = {key.replace("_", "-"): value for key, value in headers.items()}

    if endpoint:
        url = f"{url.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        response = requests.request(
            method,
            url,
            json=json,
            data=data,
            params=params,
            headers=headers,
            files=files,
            auth=auth,
            timeout=timeout,
        )
        response.raise_for_status()

        if return_type == "json":
            return response.json()
        elif return_type == "bytes":
            return response.content
        elif return_type == "response":
            return response
        else:
            return response.text
    except Exception:
        raise


def create_cookie(
    key: str,
    value: str,
    domain: str = None,
    expires: datetime = None,
    path: str = "/",
    same_site: str = "Strict",  # "Strict", "Lax", or "None"
    secure: bool = False,
    http_only: bool = True,
) -> dict:
    if not key or not value:
        raise ValueError("Cookie key and value are required.")

    cookie_options = {
        "httponly": http_only,
        "path": path,
        "secure": secure,
        "samesite": same_site,
        "value": value,
        "key": key,
    }

    if expires:
        if not isinstance(expires, datetime):
            raise ValueError("Expires must be a datetime object.")
        cookie_options["expires"] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    if domain:
        cookie_options["domain"] = domain
    return cookie_options
