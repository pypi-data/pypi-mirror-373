"""
Request handling for BustAPI - Flask-compatible request object
"""

import json
from contextvars import ContextVar
from typing import Any, Dict, Optional, Union

from werkzeug.datastructures import ImmutableMultiDict

# Thread-local request context
_request_ctx: ContextVar[Optional["Request"]] = ContextVar("request", default=None)


class Request:
    """
    Flask-compatible request object that wraps the Rust request data.

    This object provides access to request data including headers, form data,
    JSON data, files, and query parameters in a Flask-compatible way.
    """

    def __init__(self, rust_request=None):
        """
        Initialize request object.

        Args:
            rust_request: Rust PyRequest object from the backend
        """
        self._rust_request = rust_request
        self._json_cache = None
        self._form_cache = None
        self._files_cache = None
        self._args_cache = None

    @classmethod
    def _from_rust_request(cls, rust_request) -> "Request":
        """Create Request instance from Rust request object."""
        return cls(rust_request)

    @property
    def method(self) -> str:
        """HTTP method (GET, POST, etc.)"""
        if self._rust_request:
            return self._rust_request.method
        return "GET"

    @property
    def url(self) -> str:
        """Complete URL including query string."""
        if self._rust_request:
            return (
                f"{self.path}?{self.query_string}" if self.query_string else self.path
            )
        return "/"

    @property
    def base_url(self) -> str:
        """Base URL without query string."""
        return self.path

    @property
    def path(self) -> str:
        """URL path component."""
        if self._rust_request:
            return self._rust_request.path
        return "/"

    @property
    def query_string(self) -> bytes:
        """Raw query string as bytes."""
        if self._rust_request:
            return self._rust_request.query_string.encode("utf-8")
        return b""

    @property
    def args(self) -> ImmutableMultiDict:
        """Query parameters as ImmutableMultiDict."""
        if self._args_cache is None:
            if self._rust_request:
                args_dict = self._rust_request.args
                # Convert to ImmutableMultiDict for Flask compatibility
                items = [(k, v) for k, v in args_dict.items()]
            else:
                items = []
            self._args_cache = ImmutableMultiDict(items)
        return self._args_cache

    @property
    def form(self) -> ImmutableMultiDict:
        """Form data as ImmutableMultiDict."""
        if self._form_cache is None:
            if self._rust_request:
                form_dict = self._rust_request.form()
                # Convert to ImmutableMultiDict for Flask compatibility
                items = [(k, v) for k, v in form_dict.items()]
            else:
                items = []
            self._form_cache = ImmutableMultiDict(items)
        return self._form_cache

    @property
    def files(self) -> ImmutableMultiDict:
        """Uploaded files as ImmutableMultiDict."""
        if self._files_cache is None:
            # TODO: Implement file upload handling in Rust backend
            # For now, return empty dict
            self._files_cache = ImmutableMultiDict([])
        return self._files_cache

    @property
    def values(self) -> ImmutableMultiDict:
        """Combined args and form data."""
        combined = []
        combined.extend(self.args.items(multi=True))
        combined.extend(self.form.items(multi=True))
        return ImmutableMultiDict(combined)

    @property
    def json(self) -> Optional[Any]:
        """Request body parsed as JSON."""
        if self._json_cache is None:
            if self._rust_request:
                try:
                    self._json_cache = self._rust_request.json()
                except Exception:
                    self._json_cache = None
            else:
                self._json_cache = None
        return self._json_cache

    @property
    def data(self) -> bytes:
        """Raw request body as bytes."""
        if self._rust_request:
            return self._rust_request.get_data()
        return b""

    def get_data(
        self, cache: bool = True, as_text: bool = False, parse_form_data: bool = False
    ) -> Union[bytes, str]:
        """
        Get request body data.

        Args:
            cache: Whether to cache the result
            as_text: Return as text instead of bytes
            parse_form_data: Parse form data

        Returns:
            Request body as bytes or text
        """
        data = self.data
        if as_text:
            return data.decode("utf-8", errors="replace")
        return data

    @property
    def headers(self) -> "EnvironHeaders":
        """Request headers."""
        if self._rust_request:
            headers_dict = self._rust_request.headers
            return EnvironHeaders(headers_dict)
        return EnvironHeaders({})

    @property
    def cookies(self) -> Dict[str, str]:
        """Request cookies."""
        if self._rust_request:
            return self._rust_request.cookies()
        return {}

    @property
    def environ(self) -> Dict[str, Any]:
        """WSGI environ dictionary (placeholder)."""
        # TODO: Implement WSGI environ compatibility
        return {}

    @property
    def remote_addr(self) -> Optional[str]:
        """Client IP address."""
        # Try common headers for reverse proxy setups
        forwarded_for = self.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP from comma-separated list
            return forwarded_for.split(",")[0].strip()

        real_ip = self.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # TODO: Get from connection info in Rust backend
        return None

    @property
    def user_agent(self) -> Optional[str]:
        """User agent string."""
        return self.headers.get("User-Agent")

    @property
    def referrer(self) -> Optional[str]:
        """HTTP referrer."""
        return self.headers.get("Referer")

    @property
    def is_secure(self) -> bool:
        """Whether request was made over HTTPS."""
        if self._rust_request:
            return (
                self._rust_request.is_secure
                if hasattr(self._rust_request, "is_secure")
                else False
            )
        return False

    @property
    def is_json(self) -> bool:
        """Whether request has JSON content type."""
        if self._rust_request:
            return self._rust_request.is_json()
        return False

    def get_json(
        self, force: bool = False, silent: bool = False, cache: bool = True
    ) -> Optional[Any]:
        """
        Parse request body as JSON.

        Args:
            force: Force parsing even without JSON content type
            silent: Don't raise exception on parse error
            cache: Cache the result

        Returns:
            Parsed JSON data or None
        """
        if not force and not self.is_json:
            return None

        if cache and self._json_cache is not None:
            return self._json_cache

        try:
            data = self.get_data(as_text=True)
            if not data:
                return None
            result = json.loads(data)
            if cache:
                self._json_cache = result
            return result
        except (ValueError, TypeError):
            if not silent:
                raise
            return None

    # Flask compatibility methods
    def wants_json(self) -> bool:
        """Check if client prefers JSON response."""
        accept = self.headers.get("Accept", "")
        return "application/json" in accept and "text/html" not in accept

    def is_xhr(self) -> bool:
        """Check if request was made via XMLHttpRequest."""
        return self.headers.get("X-Requested-With", "").lower() == "xmlhttprequest"


class EnvironHeaders:
    """
    Flask-compatible headers object.
    """

    def __init__(self, headers_dict: Dict[str, str]):
        self._headers = headers_dict

    def get(
        self,
        key: str,
        default: Optional[str] = None,
        type_func: Optional[callable] = None,
    ) -> Any:
        """
        Get header value.

        Args:
            key: Header name
            default: Default value if header not found
            type_func: Function to convert value

        Returns:
            Header value, converted if type_func provided
        """
        # Case-insensitive header lookup
        value = None
        key_lower = key.lower()
        for header_key, header_value in self._headers.items():
            if header_key.lower() == key_lower:
                value = header_value
                break

        if value is None:
            return default

        if type_func:
            try:
                return type_func(value)
            except (ValueError, TypeError):
                return default

        return value

    def getlist(self, key: str) -> list:
        """Get list of values for header (for multiple headers with same name)."""
        # Simplified implementation - assumes single value per header
        value = self.get(key)
        return [value] if value is not None else []

    def __getitem__(self, key: str) -> str:
        """Get header value, raise KeyError if not found."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key: str) -> bool:
        """Check if header exists."""
        return self.get(key) is not None

    def __iter__(self):
        """Iterate over header names."""
        return iter(self._headers.keys())

    def items(self):
        """Iterate over header (name, value) pairs."""
        return self._headers.items()

    def keys(self):
        """Get header names."""
        return self._headers.keys()

    def values(self):
        """Get header values."""
        return self._headers.values()


# Global request proxy object for Flask compatibility
class _RequestProxy:
    """Proxy object that provides access to the current request."""

    def __getattr__(self, name: str) -> Any:
        req = _request_ctx.get()
        if req is None:
            raise RuntimeError(
                "Working outside of request context. This typically happens when "
                "you are trying to access the request object from outside a view "
                "function or from a thread that wasn't started by Flask."
            )
        return getattr(req, name)

    def __setattr__(self, name: str, value: Any) -> None:
        req = _request_ctx.get()
        if req is None:
            raise RuntimeError("Working outside of request context")
        setattr(req, name, value)

    def __repr__(self) -> str:
        req = _request_ctx.get()
        if req is None:
            return "<RequestProxy: no request context>"
        return f"<RequestProxy: {req.method} {req.path}>"


# Global request object (Flask-compatible)
request = _RequestProxy()


def has_request_context() -> bool:
    """Check if we're currently in a request context."""
    return _request_ctx.get() is not None
