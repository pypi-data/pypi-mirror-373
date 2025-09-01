"""HTTP transport constants for API Gateway adapter.

These constants are specific to HTTP transport and should not be used
in the transport-agnostic core package.
"""


class HTTPStatusCodes:
    """HTTP status codes for API Gateway responses."""
    OK = 200
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_ACCEPTABLE = 406
    UNSUPPORTED_MEDIA_TYPE = 415
    INTERNAL_SERVER_ERROR = 500


class ContentTypes:
    """HTTP content types for MCP over HTTP."""
    APPLICATION_JSON = "application/json"
    TEXT_EVENT_STREAM = "text/event-stream"
    APPLICATION_WILDCARD = "application/*"
    TEXT_WILDCARD = "text/*"
    ALL_WILDCARD = "*/*"


class HTTPHeaders:
    """Standard HTTP header names."""
    CONTENT_TYPE = "Content-Type"
    ACCEPT = "Accept"
    AUTHORIZATION = "Authorization"


class MCPHeaders:
    """MCP-specific HTTP headers."""
    PROTOCOL_VERSION = "MCP-Protocol-Version"
    SESSION_ID = "Mcp-Session-Id"
    LAST_EVENT_ID = "Last-Event-ID"


class CORSHeaders:
    """CORS header names for API Gateway."""
    ALLOW_ORIGIN = "Access-Control-Allow-Origin"
    ALLOW_METHODS = "Access-Control-Allow-Methods"
    ALLOW_HEADERS = "Access-Control-Allow-Headers"
    MAX_AGE = "Access-Control-Max-Age"


class HTTPDefaults:
    """HTTP transport default values."""
    CORS_ORIGIN = "*"
    CORS_MAX_AGE = "86400"
    AUTH_HEADER = "Authorization"


class HTTPErrorMapping:
    """Maps core transport exceptions to HTTP status codes for MCP compliance."""
    
    @classmethod
    def get_http_status(cls, error: Exception) -> int:
        """Get HTTP status code for a transport error.
        
        Args:
            error: Exception instance to map
            
        Returns:
            Appropriate HTTP status code for the error type
        """
        # Import here to avoid circular imports
        from mcpbytes_lambda.core.exceptions import (
            InvalidRequestError,
            UnsupportedMediaTypeError,
            NotAcceptableError,
            AuthenticationError,
        )
        
        # Exception to HTTP status code mapping
        error_mapping = {
            InvalidRequestError: HTTPStatusCodes.BAD_REQUEST,
            UnsupportedMediaTypeError: HTTPStatusCodes.UNSUPPORTED_MEDIA_TYPE,
            NotAcceptableError: HTTPStatusCodes.NOT_ACCEPTABLE,
            AuthenticationError: HTTPStatusCodes.UNAUTHORIZED,
        }
        
        return error_mapping.get(type(error), HTTPStatusCodes.INTERNAL_SERVER_ERROR)
