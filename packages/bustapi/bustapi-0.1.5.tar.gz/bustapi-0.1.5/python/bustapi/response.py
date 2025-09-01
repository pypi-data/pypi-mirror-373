"""
Response handling for BustAPI - Flask-compatible response objects
"""

import json
from http import HTTPStatus
from typing import Any, Dict, Iterable, Optional, Union

from werkzeug.datastructures import Headers

ResponseType = Union[str, bytes, dict, list, tuple, "Response"]


class Response:
    """
    Flask-compatible response object.

    This class represents an HTTP response and provides methods to set
    response data, status codes, and headers in a Flask-compatible way.
    """

    def __init__(
        self,
        response: Any = None,
        status: Optional[int] = None,
        headers: Optional[Union[Dict, Headers]] = None,
        mimetype: Optional[str] = None,
        content_type: Optional[str] = None,
    ):
        """
        Initialize response object.

        Args:
            response: Response data (string, bytes, dict, etc.)
            status: HTTP status code
            headers: Response headers
            mimetype: MIME type
            content_type: Content type header
        """
        self.status_code = status or 200
        self.headers = Headers(headers) if headers else Headers()

        # Set response data
        if response is not None:
            self.set_data(response)
        else:
            self.data = b""

        # Set content type
        if content_type:
            self.content_type = content_type
        elif mimetype:
            self.content_type = mimetype
        elif not self.content_type:
            self.content_type = "text/html; charset=utf-8"

    @property
    def status(self) -> str:
        """Status code and reason phrase."""
        try:
            status_obj = HTTPStatus(self.status_code)
            return f"{self.status_code} {status_obj.phrase}"
        except ValueError:
            return str(self.status_code)

    @status.setter
    def status(self, value: Union[str, int]) -> None:
        """Set status code."""
        if isinstance(value, str):
            # Parse "200 OK" format
            self.status_code = int(value.split()[0])
        else:
            self.status_code = value

    @property
    def content_type(self) -> str:
        """Content type header."""
        return self.headers.get("Content-Type", "")

    @content_type.setter
    def content_type(self, value: str) -> None:
        """Set content type header."""
        self.headers["Content-Type"] = value

    def set_data(self, data: Any) -> None:
        """
        Set response data.

        Args:
            data: Response data to set
        """
        if isinstance(data, str):
            self.data = data.encode("utf-8")
            if not self.content_type:
                self.content_type = "text/html; charset=utf-8"
        elif isinstance(data, bytes):
            self.data = data
        elif isinstance(data, (dict, list)):
            # Serialize as JSON
            self.data = json.dumps(data).encode("utf-8")
            self.content_type = "application/json"
        else:
            # Convert to string and encode
            self.data = str(data).encode("utf-8")
            if not self.content_type:
                self.content_type = "text/html; charset=utf-8"

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
    def response(self) -> Iterable[bytes]:
        """Response data as iterable of bytes."""
        return [self.data]

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None,
    ):
        """
        Set a cookie.

        Args:
            key: Cookie name
            value: Cookie value
            max_age: Maximum age in seconds
            expires: Expiration date
            path: Cookie path
            domain: Cookie domain
            secure: Secure flag
            httponly: HttpOnly flag
            samesite: SameSite attribute
        """
        cookie_parts = [f"{key}={value}"]

        if max_age is not None:
            cookie_parts.append(f"Max-Age={max_age}")
        if expires:
            cookie_parts.append(f"Expires={expires}")
        if path:
            cookie_parts.append(f"Path={path}")
        if domain:
            cookie_parts.append(f"Domain={domain}")
        if secure:
            cookie_parts.append("Secure")
        if httponly:
            cookie_parts.append("HttpOnly")
        if samesite:
            cookie_parts.append(f"SameSite={samesite}")

        cookie_string = "; ".join(cookie_parts)

        # Add to existing Set-Cookie headers
        if "Set-Cookie" in self.headers:
            existing = self.headers.getlist("Set-Cookie")
            existing.append(cookie_string)
            self.headers.setlist("Set-Cookie", existing)
        else:
            self.headers["Set-Cookie"] = cookie_string

    def delete_cookie(self, key: str, path: str = "/", domain: Optional[str] = None):
        """
        Delete a cookie by setting it to expire.

        Args:
            key: Cookie name
            path: Cookie path
            domain: Cookie domain
        """
        self.set_cookie(
            key, "", expires="Thu, 01 Jan 1970 00:00:00 GMT", path=path, domain=domain
        )

    def __repr__(self) -> str:
        return f"<Response {self.status_code} [{self.content_type}]>"


def make_response(*args) -> Response:
    """
    Create a Response object from various input types (Flask-compatible).

    Args:
        *args: Response arguments - can be:
            - (response,)
            - (response, status)
            - (response, headers)
            - (response, status, headers)

    Returns:
        Response object
    """
    if not args:
        return Response()

    if len(args) == 1:
        rv = args[0]
        if isinstance(rv, Response):
            return rv
        return Response(rv)

    if len(args) == 2:
        rv, status_or_headers = args
        if isinstance(status_or_headers, (int, str)):
            # (response, status)
            return Response(rv, status=status_or_headers)
        else:
            # (response, headers)
            return Response(rv, headers=status_or_headers)

    if len(args) == 3:
        # (response, status, headers)
        rv, status, headers = args
        return Response(rv, status=status, headers=headers)

    raise TypeError(f"make_response() takes 1 to 3 arguments ({len(args)} given)")


def jsonify(*args, **kwargs) -> Response:
    """
    Create a JSON response (Flask-compatible).

    Args:
        *args: Positional arguments for JSON data
        **kwargs: Keyword arguments for JSON data

    Returns:
        Response object with JSON data

    Examples:
        jsonify({'key': 'value'})
        jsonify(key='value')
        jsonify([1, 2, 3])
    """
    if args and kwargs:
        raise TypeError("jsonify() behavior with mixed arguments is deprecated")

    if args:
        if len(args) == 1:
            data = args[0]
        else:
            data = args
    else:
        data = kwargs

    response = Response()
    response.set_data(data)
    response.content_type = "application/json"

    return response


# HTTP status code helpers
def abort(code: int, description: Optional[str] = None, **kwargs):
    """
    Abort request with HTTP error code.

    Args:
        code: HTTP status code
        description: Error description
        **kwargs: Additional arguments

    Raises:
        HTTPException: HTTP exception with specified code
    """
    from .exceptions import HTTPException

    raise HTTPException(code, description=description)


class HTTPException(Exception):
    """HTTP exception for error responses."""

    def __init__(self, code: int, description: Optional[str] = None):
        self.code = code
        self.description = description or self._get_default_description(code)
        super().__init__(self.description)

    def _get_default_description(self, code: int) -> str:
        """Get default description for HTTP status code."""
        try:
            return HTTPStatus(code).phrase
        except ValueError:
            return f"HTTP {code}"

    def get_response(self) -> Response:
        """Get response object for this exception."""
        return Response(self.description, status=self.code)


# Common HTTP exceptions
class BadRequest(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(400, description)


class Unauthorized(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(401, description)


class Forbidden(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(403, description)


class NotFound(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(404, description)


class MethodNotAllowed(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(405, description)


class InternalServerError(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(500, description)


# Redirect response
def redirect(location: str, code: int = 302, Response: type = Response) -> Response:
    """
    Create a redirect response.

    Args:
        location: Redirect URL
        code: HTTP status code (301, 302, etc.)
        Response: Response class to use

    Returns:
        Redirect response
    """
    response = Response("", status=code)
    response.headers["Location"] = location
    return response


# Static response helpers
def send_file(
    file_path: str,
    mimetype: Optional[str] = None,
    as_attachment: bool = False,
    attachment_filename: Optional[str] = None,
):
    """
    Send a file as response (placeholder implementation).

    Args:
        file_path: Path to file
        mimetype: MIME type
        as_attachment: Send as attachment
        attachment_filename: Attachment filename

    Returns:
        Response object

    Note:
        This is a placeholder implementation. Full file serving
        should be implemented in the Rust backend for performance.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        response = Response(data)

        if mimetype:
            response.content_type = mimetype
        else:
            # Try to guess content type based on file extension
            import mimetypes

            guessed_type, _ = mimetypes.guess_type(file_path)
            if guessed_type:
                response.content_type = guessed_type

        if as_attachment:
            filename = attachment_filename or file_path.split("/")[-1]
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    except FileNotFoundError:
        abort(404, description="File not found")
    except PermissionError:
        abort(403, description="Permission denied")
