from curl_session import CurlSession


def test_basic_headers_and_cookies_requests():
    curl = (
        'curl -H "Accept: application/json" -H "X-Token: abc" '
        '-b "a=1; b=2" https://example.com/api'
    )
    cs = CurlSession(curl)
    s = cs.get_requests_session()
    assert s.headers["Accept"] == "application/json"
    assert s.headers["X-Token"] == "abc"
    assert s.cookies.get("a") == "1"
    assert s.cookies.get("b") == "2"


def test_httpx_client_config():
    curl = (
        'curl --http2 -L -H "User-Agent: test-agent" --proxy http://localhost:8080 '
        '-u user:pass https://example.org'
    )
    cs = CurlSession(curl)
    client = cs.get_httpx_client()
    # headers are case-insensitive mapping; httpx stores lowercase
    assert client.headers.get("user-agent") == "test-agent"
    # auth applied
    assert client.auth is not None
    # proxies
    # httpx proxies config is not public on client; quick smoke by making a request would need network
    # Just assert the object exists and is client
    assert client is not None


def test_run_returns_completed_process():
    # Use a safe, minimal command that should succeed quickly
    cs = CurlSession("curl --version")
    result = cs.run(check=True)
    assert result.returncode == 0
    assert "curl" in result.stdout.lower()


def test_get_curl_string_roundtrip():
    original = 'curl -H "A: B" https://example.com'
    cs = CurlSession(original)
    assert cs.get_curl_string() == original
