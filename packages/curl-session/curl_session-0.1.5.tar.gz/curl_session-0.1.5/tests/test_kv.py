import base64
import sys
from pathlib import Path
import pytest

# Add src to path so we can import curl_session when running directly
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from curl_session import kv


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text="", headers=None, ok=True):
        self.status_code = status_code
        self._json = json_data
        self.text = text
        self.headers = headers or {}
        self.ok = ok

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json


def test_put_returns_parsed_json(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return DummyResponse(status_code=200, json_data={"hash": "1BuVbP", "url": "/1BuVbP"}, ok=True)

    monkeypatch.setattr("requests.post", fake_post)
    res = kv.put("hello", content_type="text/plain")
    assert res.get("hash") == "1BuVbP"
    assert captured["json"]["contentType"] == "text/plain"
    assert captured["json"]["value"] == "hello"


def test_put_with_bytes_sets_base64_and_encodes(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["json"] = json
        return DummyResponse(status_code=200, json_data={"hash": "abc"})

    monkeypatch.setattr("requests.post", fake_post)
    data = b"\x00\x01\x02"
    res = kv.put(data, content_type="application/octet-stream")
    assert captured["json"]["_is_base64"] is True
    assert captured["json"]["value"] == base64.b64encode(data).decode("ascii")


def test_update_includes_hash(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["json"] = json
        return DummyResponse(status_code=200, json_data={"message": "ok"})

    monkeypatch.setattr("requests.post", fake_post)
    res = kv.update("1BuVbP", "new", content_type="text/plain")
    assert captured["json"]["hash"] == "1BuVbP"
    assert captured["json"]["value"] == "new"


def test_get_returns_text_and_content_type(monkeypatch):
    def fake_get(url, timeout=None):
        return DummyResponse(status_code=200, text="hello", headers={"Content-Type": "text/plain"})

    monkeypatch.setattr("requests.get", fake_get)
    res = kv.get("1BuVbP")
    assert res["status_code"] == 200
    assert res["content_type"] == "text/plain"
    assert res["text"] == "hello"


def test_post_retries_on_5xx_then_succeeds(monkeypatch):
    calls = []
    responses = [
        DummyResponse(status_code=500, json_data={"error": "boom"}, ok=False),
        DummyResponse(status_code=200, json_data={"hash": "retryok"}, ok=True),
    ]

    def fake_post(url, json=None, timeout=None):
        calls.append(1)
        return responses[len(calls) - 1]

    monkeypatch.setattr("requests.post", fake_post)
    res = kv.put("hello", content_type="text/plain", retries=2)
    assert res.get("hash") == "retryok"
    assert len(calls) == 2


def test_invalid_content_type_raises():
    with pytest.raises(ValueError):
        kv.put("x", content_type="bad")
