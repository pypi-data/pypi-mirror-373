"""
Testing utilities for BustAPI - Flask-compatible test client
"""

import json
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

from werkzeug.datastructures import Headers


class TestResponse:
    """
    Test response object for BustAPI test client.

    Provides access to response data, status, and headers for testing.
    """

    def __init__(self, response_data: bytes, status_code: int, headers: Dict[str, str]):
        """
        Initialize test response.

        Args:
            response_data: Response body data
            status_code: HTTP status code
            headers: Response headers
        """
        self.data = response_data
        self.status_code = status_code
        self.headers = Headers(headers)
        self._json_cache = None

    @property
    def status(self) -> str:
        """Status code and reason phrase."""
        return f"{self.status_code}"

    def get_data(self, as_text: bool = False) -> Union[bytes, str]:
        """
        Get response data.

        Args:
            as_text: Return as text instead of bytes

        Returns:
            Response data as bytes or text
        """
        if as_text:
            return self.data.decode("utf-8", errors="replace")
        return self.data

    @property
    def text(self) -> str:
        """Response data as text."""
        return self.get_data(as_text=True)

    def get_json(self, force: bool = False, silent: bool = False) -> Optional[Any]:
        """
        Parse response data as JSON.

        Args:
            force: Force parsing even without JSON content type
            silent: Don't raise exception on parse error

        Returns:
            Parsed JSON data or None
        """
        if self._json_cache is not None:
            return self._json_cache

        content_type = self.headers.get("Content-Type", "")
        if not force and "application/json" not in content_type.lower():
            return None

        try:
            self._json_cache = json.loads(self.get_data(as_text=True))
            return self._json_cache
        except (ValueError, TypeError):
            if not silent:
                raise
            return None

    @property
    def json(self) -> Optional[Any]:
        """Response data as JSON (cached)."""
        return self.get_json()

    @property
    def is_json(self) -> bool:
        """Check if response has JSON content type."""
        content_type = self.headers.get("Content-Type", "")
        return "application/json" in content_type.lower()

    def __repr__(self) -> str:
        content_type = self.headers.get("Content-Type", "")
        return f"<TestResponse {self.status_code} [{content_type}]>"


class TestClient:
    """
    Test client for BustAPI applications (Flask-compatible).

    Provides methods to make test requests to the application without
    starting a real HTTP server.

    Example:
        app = BustAPI()

        @app.route('/test')
        def test():
            return {'message': 'Hello, Test!'}

        with app.test_client() as client:
            resp = client.get('/test')
            assert resp.status_code == 200
            assert resp.json['message'] == 'Hello, Test!'
    """

    def __init__(
        self,
        application,
        response_wrapper=None,
        use_cookies=True,
        allow_subdomain_redirects=False,
    ):
        """
        Initialize test client.

        Args:
            application: BustAPI application instance
            response_wrapper: Custom response wrapper class
            use_cookies: Enable cookie support
            allow_subdomain_redirects: Allow subdomain redirects
        """
        self.application = application
        self.response_wrapper = response_wrapper or TestResponse
        self.use_cookies = use_cookies
        self.allow_subdomain_redirects = allow_subdomain_redirects

        # Cookie jar for session management
        self.cookie_jar: Dict[str, str] = {}

    def open(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Union[str, bytes, dict]] = None,
        query_string: Optional[Union[str, dict]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ) -> TestResponse:
        """
        Make a test request to the application.

        Args:
            path: Request path
            method: HTTP method
            data: Request data
            query_string: Query parameters
            headers: Request headers
            content_type: Content type header
            **kwargs: Additional arguments

        Returns:
            TestResponse object
        """
        headers = headers or {}

        # Set content type if provided
        if content_type:
            headers["Content-Type"] = content_type

        # Handle query string
        if query_string:
            if isinstance(query_string, dict):
                query_string = urlencode(query_string)
            if "?" in path:
                path += "&" + query_string
            else:
                path += "?" + query_string

        # Handle request data
        if data is not None:
            if isinstance(data, dict):
                # If data is dict and no content type specified, assume form data
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    data = urlencode(data)
                elif headers.get("Content-Type") == "application/json":
                    data = json.dumps(data)

            if isinstance(data, str):
                data = data.encode("utf-8")

        # Add cookies to headers
        if self.use_cookies and self.cookie_jar:
            cookie_header = "; ".join([f"{k}={v}" for k, v in self.cookie_jar.items()])
            headers["Cookie"] = cookie_header

        # Create mock request object for the Rust backend
        # TODO: This is a simplified mock - in a full implementation,
        # we would need to properly interface with the Rust backend
        # or create a test mode that bypasses the network layer

        mock_request = MockRequest(method, path, headers, data or b"")

        try:
            # Call application handler directly
            # This is a simplified approach - real implementation would
            # need proper integration with the Rust backend
            response_data = self._call_application(mock_request)

            # Parse response
            status_code = getattr(response_data, "status_code", 200)
            response_headers = getattr(response_data, "headers", {})
            body_data = getattr(response_data, "data", b"")

            # Update cookies from response
            if self.use_cookies and "Set-Cookie" in response_headers:
                self._update_cookies(response_headers["Set-Cookie"])

            return self.response_wrapper(body_data, status_code, response_headers)

        except Exception as e:
            # Return error response
            error_msg = f"Test client error: {str(e)}"
            return self.response_wrapper(error_msg.encode(), 500, {})

    def _call_application(self, request):
        """
        Call application with mock request (simplified implementation).

        Args:
            request: Mock request object

        Returns:
            Response object
        """
        # TODO: Implement proper test request handling
        # This would need to interface with the application's route handlers
        # without going through the Rust HTTP server

        # For now, return a mock response
        from .response import Response

        return Response("Test response", status=200)

    def _update_cookies(self, set_cookie_header: str):
        """
        Update cookie jar from Set-Cookie header.

        Args:
            set_cookie_header: Set-Cookie header value
        """
        # Simple cookie parsing - real implementation would be more robust
        if "=" in set_cookie_header:
            cookie_parts = set_cookie_header.split(";")[0]  # Get main cookie part
            if "=" in cookie_parts:
                name, value = cookie_parts.split("=", 1)
                self.cookie_jar[name.strip()] = value.strip()

    def get(self, path: str, **kwargs) -> TestResponse:
        """Make GET request."""
        return self.open(path, method="GET", **kwargs)

    def post(self, path: str, **kwargs) -> TestResponse:
        """Make POST request."""
        return self.open(path, method="POST", **kwargs)

    def put(self, path: str, **kwargs) -> TestResponse:
        """Make PUT request."""
        return self.open(path, method="PUT", **kwargs)

    def delete(self, path: str, **kwargs) -> TestResponse:
        """Make DELETE request."""
        return self.open(path, method="DELETE", **kwargs)

    def patch(self, path: str, **kwargs) -> TestResponse:
        """Make PATCH request."""
        return self.open(path, method="PATCH", **kwargs)

    def head(self, path: str, **kwargs) -> TestResponse:
        """Make HEAD request."""
        return self.open(path, method="HEAD", **kwargs)

    def options(self, path: str, **kwargs) -> TestResponse:
        """Make OPTIONS request."""
        return self.open(path, method="OPTIONS", **kwargs)

    def trace(self, path: str, **kwargs) -> TestResponse:
        """Make TRACE request."""
        return self.open(path, method="TRACE", **kwargs)

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        self.cookie_jar.clear()


class MockRequest:
    """
    Mock request object for testing.
    """

    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

        # Parse query string from path
        if "?" in path:
            self.path, query_string = path.split("?", 1)
            self.query_params = dict(
                item.split("=", 1) if "=" in item else (item, "")
                for item in query_string.split("&")
                if item
            )
        else:
            self.query_params = {}

    def get_header(self, name: str) -> Optional[str]:
        """Get header value (case-insensitive)."""
        name_lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == name_lower:
                return value
        return None

    def is_json(self) -> bool:
        """Check if request has JSON content type."""
        content_type = self.get_header("content-type") or ""
        return "application/json" in content_type.lower()

    def get_json(self):
        """Get request body as JSON."""
        if not self.is_json():
            return None
        try:
            return json.loads(self.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None


# Flask-compatible test utilities


def make_test_environ_builder(*args, **kwargs):
    """
    Create test environ builder (Flask compatibility placeholder).

    Returns:
        Mock environ builder
    """
    # TODO: Implement proper environ builder for WSGI compatibility
    return {}


class FlaskClient(TestClient):
    """Alias for Flask compatibility."""

    pass


# Re-export for convenience
__all__ = [
    "TestClient",
    "TestResponse",
    "FlaskClient",
    "MockRequest",
    "make_test_environ_builder",
]
