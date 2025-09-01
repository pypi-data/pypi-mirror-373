"""
CurlSession: Initialize with a curl command string, parse it, and expose
both a requests.Session and an httpx.Client configured with equivalent
headers, cookies, proxies, TLS options, and other reusable settings.

Also provides a run() method to execute the original curl command using
the system curl binary.
"""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import requests

try:
    import httpx
except ImportError:  # pragma: no cover - httpx is declared in requirements
    httpx = None  # type: ignore

if TYPE_CHECKING:  # for typing only
    import httpx as _httpx


@dataclass
class ParsedCurl:
    method: Optional[str] = None
    url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    data: Optional[Union[str, bytes]] = None
    verify: Union[bool, str] = True
    cert: Optional[Union[str, Tuple[str, str]]] = None
    proxies: Dict[str, str] = field(default_factory=dict)
    http2: bool = False
    follow_redirects: bool = False
    auth: Optional[Tuple[str, str]] = None


class CurlSession:
    """Create reusable HTTP clients from a curl command string.

    Contract:
    - Input: a shell-style curl command string.
    - Outputs:
        - get_requests_session() -> requests.Session (headers/cookies/etc preloaded)
        - get_httpx_client() -> httpx.Client (same settings)
        - run() -> subprocess.CompletedProcess[str]
        - get_curl_string() -> str
    - Success: Sessions include same headers, cookies, and core settings.
    - Error modes: ValueError for malformed curl; RuntimeError if curl not found on run().
    """

    def __init__(self, curl_string: str) -> None:
        if not isinstance(curl_string, str) or not curl_string.strip():
            raise ValueError("curl_string must be a non-empty string")
        self._curl_string = curl_string.strip()
        self._parsed = self._parse_curl(self._curl_string)
        # Lazy-initialized client/session objects
        self._requests_session = None
        self._httpx_client = None

    # ----------------------------- Public API ----------------------------- #
    def get_curl_string(self) -> str:
        return self._curl_string

    def get_requests_session(self) -> requests.Session:
        if self._requests_session is None:
            self._requests_session = self._build_requests_session(self._parsed)
        return self._requests_session

    def get_httpx_client(self) -> "_httpx.Client":
        if httpx is None:  # pragma: no cover
            raise RuntimeError("httpx is not installed; install httpx to use this feature")
        if self._httpx_client is None:
            self._httpx_client = self._build_httpx_client(self._parsed)
        return self._httpx_client

    def run(self, check: bool = False, timeout: Optional[float] = None) -> subprocess.CompletedProcess[str]:
        """Execute the original curl command using the system curl binary.

        Returns subprocess.CompletedProcess with text output. Raises if curl is missing.
        """
        argv = self._to_argv(self._curl_string)
        if not argv or argv[0] != "curl":
            # Prepend curl if the user omitted it for convenience
            argv = ["curl"] + argv
        try:
            return subprocess.run(
                argv,
                check=check,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError as e:  # curl not available
            raise RuntimeError("System 'curl' not found in PATH") from e

    # ----------------------------- Internals ------------------------------ #
    @staticmethod
    def _to_argv(curl_string: str) -> List[str]:
        # shlex supports POSIX shell splitting with quotes preserved
        return shlex.split(curl_string, posix=True)

    @staticmethod
    def _parse_curl(curl_string: str) -> ParsedCurl:
        argv = CurlSession._to_argv(curl_string)
        # Allow the command to omit the leading 'curl'
        if argv and argv[0] == "curl":
            argv = argv[1:]
        if not argv:
            raise ValueError("No arguments found in curl string")

        pc = ParsedCurl()
        def get(i: int) -> str:
            try:
                return argv[i]
            except IndexError as exc:
                raise ValueError("Unexpected end of curl arguments") from exc

        i = 0
        while i < len(argv):
            token = argv[i]
            if token in ("-H", "--header"):
                i += 1
                header = get(i)
                name, _, value = header.partition(":")
                if not _:
                    raise ValueError(f"Invalid header: {header}")
                name = name.strip()
                value = value.strip()
                # Merge duplicate headers by comma per RFC where sensible
                if name.lower() == "cookie":
                    # If Cookie header provided explicitly, merge into cookies
                    pc.cookies.update(_parse_cookie_header(value))
                else:
                    if name in pc.headers:
                        pc.headers[name] = f"{pc.headers[name]}, {value}"
                    else:
                        pc.headers[name] = value
            elif token in ("-A", "--user-agent"):
                i += 1
                pc.headers["User-Agent"] = get(i)
            elif token in ("-e", "--referer"):
                i += 1
                pc.headers["Referer"] = get(i)
            elif token in ("-b", "--cookie"):
                i += 1
                pc.cookies.update(_parse_cookie_header(get(i)))
            elif token in ("-X", "--request"):
                i += 1
                pc.method = get(i).upper()
            elif token in ("-d", "--data", "--data-raw", "--data-binary"):
                i += 1
                pc.data = get(i)
                if pc.method is None:
                    pc.method = "POST"
            elif token == "--data-urlencode":
                i += 1
                val = get(i)
                if pc.data:
                    pc.data = f"{pc.data}&{val}"
                else:
                    pc.data = val
                if pc.method is None:
                    pc.method = "POST"
            elif token in ("-k", "--insecure"):
                pc.verify = False
            elif token == "--cacert":
                i += 1
                pc.verify = get(i)
            elif token == "--cert":
                i += 1
                pc.cert = get(i)
            elif token == "--key":
                i += 1
                key_path = get(i)
                # Combine cert and key if cert already present
                if isinstance(pc.cert, str):
                    pc.cert = (pc.cert, key_path)
                else:
                    pc.cert = ("", key_path)  # incomplete but maintains tuple type
            elif token in ("-u", "--user"):
                i += 1
                cred = get(i)
                if ":" in cred:
                    u, p = cred.split(":", 1)
                else:
                    u, p = cred, ""
                pc.auth = (u, p)
            elif token in ("--http2", "--http2-prior-knowledge"):
                pc.http2 = True
            elif token in ("-L", "--location"):
                pc.follow_redirects = True
            elif token == "--proxy":
                i += 1
                proxy = get(i)
                # Proxy may specify scheme or not; apply to all schemes if missing
                if "://" in proxy:
                    scheme = proxy.split(":", 1)[0]
                    pc.proxies[scheme] = proxy
                else:
                    pc.proxies.update({"http": proxy, "https": proxy})
            elif token.startswith("-"):
                # Unhandled flag: skip its value if it expects one is hard; best-effort ignore.
                # Try to detect combined short flags like -sSL; expand known ones.
                # We'll specifically look for -I (HEAD); -m or --max-time accept an argument.
                if token == "-I" or token == "--head":
                    pc.method = "HEAD"
                elif token in ("-m", "--max-time"):
                    # We don't persist default timeout in sessions; ignore but parse argument.
                    i += 1  # consume seconds
                # else: ignore other flags
            else:
                # Positional: likely the URL. Per curl, the last positional is the URL.
                pc.url = token
            i += 1

        return pc

    @staticmethod
    def _build_requests_session(pc: ParsedCurl) -> requests.Session:
        s = requests.Session()
        # headers
        if pc.headers:
            s.headers.update(pc.headers)
        # cookies
        if pc.cookies:
            jar = requests.cookies.cookiejar_from_dict(pc.cookies)
            s.cookies.update(jar)
        # TLS
        s.verify = pc.verify
        if pc.cert:
            s.cert = pc.cert
        # proxies
        if pc.proxies:
            s.proxies.update(pc.proxies)
        # auth
        if pc.auth:
            from requests.auth import HTTPBasicAuth

            s.auth = HTTPBasicAuth(*pc.auth)
        # trust env off to avoid env proxies interfering with explicit ones
        s.trust_env = False
        return s

    @staticmethod
    def _build_httpx_client(pc: ParsedCurl) -> "_httpx.Client":
        assert httpx is not None
        # httpx Client supports default headers, cookies, proxies, verify, cert, http2, follow_redirects
        kwargs = {
            "headers": pc.headers or None,
            "cookies": pc.cookies or None,
            "verify": pc.verify,
            "cert": pc.cert,
            "http2": pc.http2,
            "follow_redirects": pc.follow_redirects,
            "trust_env": False,
        }
        # Setup proxy for httpx>=0.28 via transport
        transport = None
        proxy_url = pc.proxies.get("https") or pc.proxies.get("http")
        if proxy_url:
            transport = httpx.HTTPTransport(proxy=proxy_url)
        # Remove None to avoid overriding defaults
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if transport is not None:
            clean_kwargs["transport"] = transport
        client = httpx.Client(**clean_kwargs)
        if pc.auth:
            client.auth = httpx.BasicAuth(*pc.auth)
        return client


def _parse_cookie_header(value: str) -> Dict[str, str]:
    """Parse Cookie header or -b value into dict.

    Supports formats like "a=1; b=2" or "name=value" or cookie-file path (ignored).
    If a path is provided (contains '=' absent and looks like a file), we ignore
    loading from file for safety and portability.
    """
    if not value:
        return {}
    if "=" not in value and ";" not in value and "/" in value:
        # Looks like a filename; ignore silently.
        return {}
    parts = [p.strip() for p in value.split(";") if p.strip()]
    cookies: Dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


__all__ = ["CurlSession"]

__version__ = "0.1.0"
