"""
Usage:
import kv
kv.put("hello", "text/plain", "1h")
kv.get("1BuVbP")
"""
from typing import Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import requests
import time
import base64

BASE_URL = "https://curl.lgnat.com"
API_KV_ENDPOINT = f"{BASE_URL}/api/kv"

# Preferred: an Enum for editor/autocomplete friendliness. Keep a list for compatibility checks.
class ContentType(str, Enum):
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    JSON = "application/json"
    OCTET_STREAM = "application/octet-stream"
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"

# Backwards-compatible list of values (used for membership checks)
CONTENT_TYPES = [ct.value for ct in ContentType]

# Allowed expiration tokens (worker maps these to TTL seconds)
EXPIRATION_OPTIONS = ["1h", "1d", "1w", "1m"]

# Mapping for seconds -> token (useful when user supplies seconds)
_EXPIRATION_SECONDS_MAP = {
    3600: "1h",
    86400: "1d",
    604800: "1w",
    2592000: "1m",
}


def _normalize_expiration(expiration: Optional[Any]) -> Optional[str]:
    """
    Accepts None, an expiration token (e.g. '1h'), or an integer number of seconds that matches a known token.
    Returns a token string (e.g. '1h') or None.
    Raises ValueError for invalid values.
    """
    if expiration is None:
        return None
    if isinstance(expiration, str):
        if expiration in EXPIRATION_OPTIONS:
            return expiration
        raise ValueError(f"Unsupported expiration string: {expiration!r}. Allowed: {EXPIRATION_OPTIONS}")
    if isinstance(expiration, int):
        token = _EXPIRATION_SECONDS_MAP.get(expiration)
        if token:
            return token
        raise ValueError(f"Unsupported expiration seconds: {expiration}. Allowed seconds: {list(_EXPIRATION_SECONDS_MAP.keys())}")
    raise ValueError("expiration must be None, a supported string token, or an int number of seconds")


# New helper: build payload for both put and update
def _build_payload(*, value: Any, content_type: str, expiration: Optional[Any] = None, hash_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Constructs the JSON payload expected by the worker.
    - Accepts str or bytes for value. Bytes will be base64-encoded and a flag added in the payload.
    - Adds 'hash' when updating.
    """
    payload: Dict[str, Any] = {}
    # Normalize value: if bytes, base64-encode and mark it so caller may know
    if isinstance(value, (bytes, bytearray)):
        payload["value"] = base64.b64encode(bytes(value)).decode("ascii")
        # add a convention key so consumer could decide to decode — worker will store the string as-is.
        payload["_is_base64"] = True
    else:
        payload["value"] = value

    payload["contentType"] = content_type

    token = _normalize_expiration(expiration)
    if token is not None:
        payload["expiration"] = token

    if hash_key:
        payload["hash"] = hash_key

    return payload


# New helper: centralized POST logic with retries, backoff and consistent JSON parsing/errors
def _post_to_kv(payload: Dict[str, Any], timeout: int = 10, retries: int = 2, backoff: float = 0.5) -> Dict[str, Any]:
    """
    POST payload to API_KV_ENDPOINT, retrying on network errors or 5xx responses.
    Returns parsed JSON on success, raises requests.HTTPError on HTTP error.
    """
    attempt = 0
    last_exc: Optional[Exception] = None
    while attempt <= retries:
        try:
            resp = requests.post(API_KV_ENDPOINT, json=payload, timeout=timeout)
            # Try to parse json response where available
            try:
                data = resp.json()
            except ValueError:
                # If body isn't JSON, let requests raise for non-2xx, otherwise return empty dict
                if not resp.ok:
                    resp.raise_for_status()
                data = {}

            if resp.ok:
                return data
            # For 5xx, retry; for 4xx, raise immediately with parsed body
            if 500 <= resp.status_code < 600 and attempt < retries:
                last_exc = requests.HTTPError(f"Server error {resp.status_code} - {data}")
            else:
                # client error or exhausted retries
                raise requests.HTTPError(f"KV POST failed: {resp.status_code} - {data}")
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
        # backoff before next attempt
        attempt += 1
        time.sleep(backoff * (2 ** (attempt - 1)))
    # if we exit loop with no successful response, raise last exception
    if last_exc:
        raise last_exc
    raise requests.HTTPError("Unknown error posting to KV")


def put(value: Any, content_type: Union[ContentType, str] = ContentType.JSON, expiration: Optional[Any] = "1w", timeout: int = 10, retries: int = 2) -> Dict[str, Any]:
    """
    Store `value` in remote KV. Returns the parsed JSON response (e.g. {"hash":"1BuVbP","url":"/1BuVbP"}).
    Defaults: content_type is application/json and expiration is 1 week ("1w").
    - value: string or bytes (bytes are base64-encoded transparently)
    - retries: number of retry attempts for transient errors
    """
    # Accept either the ContentType enum or a raw string for backward compatibility
    ct_value = content_type.value if isinstance(content_type, ContentType) else content_type
    if ct_value not in CONTENT_TYPES:
        raise ValueError(f"Unsupported content_type {ct_value!r}. Allowed: {CONTENT_TYPES}")

    payload = _build_payload(value=value, content_type=ct_value, expiration=expiration)
    return _post_to_kv(payload, timeout=timeout, retries=retries)


def get(hash_key: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Retrieve content stored under the short hash.
    Returns text
    The function returns resp
    """
    if not hash_key:
        raise ValueError("hash_key is required")

    url = f"{BASE_URL.rstrip('/')}/{hash_key}"
    resp = requests.get(url, timeout=timeout)
    return resp


def update(hash_key: str, value: Any, content_type: Union[ContentType, str] = ContentType.JSON, expiration: Optional[Any] = "1w", timeout: int = 10, retries: int = 2) -> Dict[str, Any]:
    """
    Update an existing entry by its short hash.
    Defaults: content_type is application/json and expiration is 1 week ("1w").
    Returns the parsed JSON response (e.g. {"message":"Entry updated successfully.","hash":"1BuVbP"}).
    """
    if not hash_key:
        raise ValueError("hash_key is required")
    ct_value = content_type.value if isinstance(content_type, ContentType) else content_type
    if ct_value not in CONTENT_TYPES:
        raise ValueError(f"Unsupported content_type {ct_value!r}. Allowed: {CONTENT_TYPES}")

    payload = _build_payload(value=value, content_type=ct_value, expiration=expiration, hash_key=hash_key)
    return _post_to_kv(payload, timeout=timeout, retries=retries)


__all__ = ["put", "get", "update", "CONTENT_TYPES", "EXPIRATION_OPTIONS", "ContentType"]
