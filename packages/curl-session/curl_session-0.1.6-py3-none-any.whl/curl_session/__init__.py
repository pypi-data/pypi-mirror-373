"""curl_session package exports.

Keep this file minimal: implementation lives in `curl_session.curl_session`.
"""

from .curl_session import CurlSession  # re-export main class
from . import kv  # provide `kv` module

__all__ = ["CurlSession", "kv"]