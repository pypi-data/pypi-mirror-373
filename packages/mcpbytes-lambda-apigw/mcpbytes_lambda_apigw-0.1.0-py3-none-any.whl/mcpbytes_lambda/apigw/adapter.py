"""AWS API Gateway transport adapter for MCP Lambda servers.

Supports both REST API Gateway and HTTP API Gateway formats with proper
CORS handling, authentication, and content negotiation.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Callable, Union

from mcpbytes_lambda.core.exceptions import (
    TransportError,
    InvalidRequestError,
    UnsupportedMediaTypeError,
    NotAcceptableError,
    AuthenticationError,
)
from mcpbytes_lambda.core.types import MCPErrorCodes
from .constants import (
    HTTPStatusCodes,
    ContentTypes,
    HTTPHeaders,
    MCPHeaders,
    CORSHeaders,
    HTTPDefaults,
    HTTPErrorMapping,
)


class ApiGatewayAdapter:
    """Zero-boilerplate transport adapter for AWS API Gateway Lambda Proxy Integration.
    
    Supports both REST API Gateway (v1.0) and HTTP API Gateway (v2.0) formats.
    Automatically handles CORS, authentication, and content negotiation according to MCP HTTP transport spec.
    
    USAGE:
    ```python
    # Basic usage (no authentication)
    def lambda_handler(event, context):
        adapter = ApiGatewayAdapter()
        return adapter.handle(event, mcp_server)
    
    # With Lambda Authorizer (auto-detected)
    def lambda_handler(event, context):
        adapter = ApiGatewayAdapter(require_auth=True)
        user_info = adapter.get_user_context(event)  # From authorizer
        return adapter.handle(event, mcp_server)
    
    # With custom token validation
    def my_validator(token: str) -> Union[Dict[str, Any], bool]:
        # Your validation logic here
        return {"user_id": "123", "role": "admin"}  # or True/False
    
    def lambda_handler(event, context):
        adapter = ApiGatewayAdapter(require_auth=True, token_validator=my_validator)
        user_info = adapter.get_user_context(event)  # From validator
        return adapter.handle(event, mcp_server)
    ```
    
    MCP STREAMABLE HTTP COMPLIANCE:
    ✅ Dual content-type Accept header validation (application/json + text/event-stream)
    ✅ MCP protocol version header support (handled by core layer)
    ✅ Session management headers in CORS (Mcp-Session-Id, Last-Event-ID)
    ✅ Proper JSON-RPC over HTTP with correct status codes
    ✅ Bearer token authentication format validation
    ✅ Dual API Gateway format support (REST v1.0 + HTTP v2.0)
    ✅ Automatic CORS preflight handling
    ✅ Comprehensive error handling with proper JSON-RPC responses
    
    LAMBDA LIMITATIONS:
    ❌ Server-Sent Events (SSE) streaming not supported
    ❌ Real-time server-to-client notifications not supported  
    ❌ HTTP GET for stream initiation not supported
    ❌ Stream resumability not supported
    
    For full streaming support, deploy as a long-running server process.
    """
    
    def __init__(self, 
                 cors_origin: str = HTTPDefaults.CORS_ORIGIN,
                 require_auth: bool = False,
                 auth_header: str = HTTPDefaults.AUTH_HEADER,
                 token_validator: Optional[Callable[[str], Union[Dict[str, Any], bool]]] = None):
        """Initialize the adapter.
        
        Args:
            cors_origin: CORS origin header value
            require_auth: Whether to require Bearer token authentication
            auth_header: Header name for authentication token
            token_validator: Optional custom token validation function.
                           Should return Dict[str, Any] for user context on success,
                           False for explicit rejection, or True for accept without context.
                           May raise exceptions for validation errors.
        """
        self.cors_origin = cors_origin
        self.require_auth = require_auth
        self.auth_header = auth_header
        self.token_validator = token_validator
        self.logger = logging.getLogger(__name__)
        self._user_context: Optional[Dict[str, Any]] = None
    
    def to_core_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract MCP request from API Gateway event.
        
        Args:
            event: API Gateway Lambda event
            
        Returns:
            Parsed JSON-RPC request
            
        Raises:
            InvalidRequestError: If event format is invalid
            UnsupportedMediaTypeError: If Content-Type is not application/json
            NotAcceptableError: If Accept header doesn't include application/json
            AuthenticationError: If authentication is required but invalid
        """
        # Detect API Gateway format and extract fields using helper method
        method, headers, body = self._detect_api_gateway_format(event)
        
        # Validate HTTP method
        if method != "POST":
            raise InvalidRequestError(f"Method {method} not allowed, only POST supported")
        
        # Validate Content-Type using case-insensitive lookup
        content_type = self._get_header(headers, HTTPHeaders.CONTENT_TYPE)
        if not content_type.startswith(ContentTypes.APPLICATION_JSON):
            raise UnsupportedMediaTypeError(content_type)
        
        # Validate Accept header
        accept = self._get_header(headers, HTTPHeaders.ACCEPT)
        if accept:
            accept_parts = self._parse_accept_header(accept)
            if not self._accepts_json_and_sse(accept_parts):
                raise NotAcceptableError(accept)
        
        # Handle authentication if required
        if self.require_auth:
            self._validate_auth(headers, event)
        
        # Parse request body
        if not body:
            raise InvalidRequestError("Request body is required")
        
        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise InvalidRequestError(f"Invalid JSON in request body: {e}")
    
    def from_core_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format MCP response as API Gateway response.
        
        Args:
            response_data: JSON-RPC response data
            
        Returns:
            API Gateway Lambda response
        """
        try:
            return {
                "statusCode": HTTPStatusCodes.ACCEPTED,
                "headers": {
                    HTTPHeaders.CONTENT_TYPE: ContentTypes.APPLICATION_JSON,
                    **self._get_cors_headers()
                },
                "body": json.dumps(response_data)
            }
        except Exception as e:
            self.logger.error(f"Error formatting response: {e}")
            # Return a basic error response
            return self._build_error_response(
                MCPErrorCodes.INTERNAL_ERROR,
                "Internal error formatting response",
                HTTPStatusCodes.INTERNAL_SERVER_ERROR
            )
    
    def handle_preflight(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CORS preflight OPTIONS request.
        
        Args:
            event: API Gateway Lambda event
            
        Returns:
            CORS preflight response
        """
        return {
            "statusCode": HTTPStatusCodes.OK,
            "headers": {
                **self._get_cors_headers(),
                CORSHeaders.MAX_AGE: HTTPDefaults.CORS_MAX_AGE,
            },
            "body": ""
        }
    
    def _accepts_json(self, accept_header: str) -> bool:
        """Check if Accept header includes both application/json AND text/event-stream (MCP requirement).
        
        Args:
            accept_header: HTTP Accept header value
            
        Returns:
            True if both application/json and text/event-stream are acceptable
        """
        # Parse Accept header properly - check for exact media type matches
        accept_parts = [part.strip().split(';')[0].strip() for part in accept_header.split(',')]
        
        # MCP Streamable HTTP requires BOTH content types
        has_json = any(part in (ContentTypes.WILDCARD, ContentTypes.APPLICATION_WILDCARD, ContentTypes.APPLICATION_JSON) for part in accept_parts)
        has_sse = any(part in (ContentTypes.WILDCARD, ContentTypes.TEXT_WILDCARD, ContentTypes.TEXT_EVENT_STREAM) for part in accept_parts)
        
        return has_json and has_sse
    
    def handle(self, event: Dict[str, Any], mcp_server) -> Dict[str, Any]:
        """Zero-boilerplate entry point that automatically handles:
        - CORS preflight requests
        - Authentication and content negotiation
        - Error handling with proper JSON-RPC responses
        - CORS headers on all responses
        
        Args:
            event: API Gateway Lambda event
            mcp_server: User's MCP server instance (dependency injection)
            
        Returns:
            Complete API Gateway response with CORS, error handling, etc.
        """
        try:
            # Handle preflight requests automatically
            if _is_preflight_request(event):
                return self.handle_preflight(event)
            
            # Process MCP request through the server
            return mcp_server.handle(event, self, headers=event.get("headers"))
            
        except Exception as e:
            self.logger.exception("Error handling request")
            
            # Two-layer error system: Transport vs Protocol errors
            if isinstance(e, TransportError):
                # Transport errors: use mapped HTTP status code with JSON-RPC error body
                status_code = HTTPErrorMapping.get_http_status(e)
                error_code = e.error_code
                message = str(e)
            else:
                # Protocol errors: use HTTP 202 for MCP compliance with JSON-RPC error body
                status_code = HTTPStatusCodes.ACCEPTED
                error_code = getattr(e, 'error_code', MCPErrorCodes.INTERNAL_ERROR)
                message = str(e)
            
            return self._build_error_response(error_code, message, status_code)
    
    
    def get_user_context(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract user context from authentication.
        
        Returns user context from:
        1. Lambda Authorizer context (if present)
        2. Custom validator result (if stored)
        3. None if no user context available
        
        Args:
            event: API Gateway Lambda event
            
        Returns:
            User context dict or None
        """
        # Check Lambda Authorizer context first
        authorizer_context = event.get("requestContext", {}).get("authorizer")
        if authorizer_context:
            return authorizer_context
        
        # Return stored custom validator context
        return self._user_context
    
    # -------------------------
    # Internal Helper Methods
    # -------------------------
    
    def _get_header(self, headers: Dict[str, str], name: str) -> str:
        """Get header value with case-insensitive lookup.
        
        Args:
            headers: HTTP headers dictionary
            name: Header name to look up
            
        Returns:
            Header value or empty string if not found
        """
        return headers.get(name) or headers.get(name.lower(), "")
    
    def _get_cors_headers(self) -> Dict[str, str]:
        """Generate standard CORS headers - single source of truth.
        
        Returns:
            Dictionary of CORS headers
        """
        return {
            CORSHeaders.ALLOW_ORIGIN: self.cors_origin,
            CORSHeaders.ALLOW_METHODS: "POST, OPTIONS",
            CORSHeaders.ALLOW_HEADERS: f"{HTTPHeaders.CONTENT_TYPE}, {HTTPHeaders.ACCEPT}, {HTTPHeaders.AUTHORIZATION}, {MCPHeaders.PROTOCOL_VERSION}, {MCPHeaders.SESSION_ID}, {MCPHeaders.LAST_EVENT_ID}",
        }
    
    def _parse_accept_header(self, accept_header: str) -> List[str]:
        """Parse Accept header into clean media type list.
        
        Args:
            accept_header: HTTP Accept header value
            
        Returns:
            List of media types without quality parameters
        """
        return [part.strip().split(';')[0].strip() 
                for part in accept_header.split(',')]
    
    def _accepts_json_and_sse(self, accept_parts: List[str]) -> bool:
        """Check MCP dual content-type requirement.
        
        Args:
            accept_parts: Parsed Accept header media types
            
        Returns:
            True if both JSON and SSE are acceptable
        """
        wildcards = {ContentTypes.WILDCARD, ContentTypes.APPLICATION_WILDCARD, ContentTypes.TEXT_WILDCARD}
        json_types = {ContentTypes.APPLICATION_JSON} | wildcards
        sse_types = {ContentTypes.TEXT_EVENT_STREAM} | wildcards
        
        has_json = any(part in json_types for part in accept_parts)
        has_sse = any(part in sse_types for part in accept_parts)
        return has_json and has_sse
    
    def _detect_api_gateway_format(self, event: Dict[str, Any]) -> Tuple[str, Dict[str, str], Optional[str]]:
        """Detect API Gateway format and extract method, headers, body.
        
        Args:
            event: API Gateway Lambda event
            
        Returns:
            Tuple of (method, headers, body)
            
        Raises:
            InvalidRequestError: If format is unrecognized
        """
        if "version" in event and event["version"] == "2.0":
            # HTTP API Gateway (v2.0)
            return (
                event.get("requestContext", {}).get("http", {}).get("method"),
                event.get("headers", {}),
                event.get("body")
            )
        elif "httpMethod" in event:
            # REST API Gateway (v1.0)  
            return (
                event.get("httpMethod"),
                event.get("headers", {}),
                event.get("body")
            )
        else:
            raise InvalidRequestError("Unrecognized API Gateway event format")
    
    def _build_error_response(self, error_code: int, message: str, status_code: int) -> Dict[str, Any]:
        """Build consistent error response with CORS.
        
        Args:
            error_code: JSON-RPC error code
            message: Error message
            status_code: HTTP status code
            
        Returns:
            API Gateway error response with CORS headers
        """
        return {
            "statusCode": status_code,
            "headers": {
                HTTPHeaders.CONTENT_TYPE: ContentTypes.APPLICATION_JSON,
                **self._get_cors_headers()
            },
            "body": json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": error_code, "message": message},
                "id": None
            })
        }
    
    def _validate_auth(self, headers: Dict[str, str], event: Dict[str, Any]) -> None:
        """Validate Bearer token authentication with smart flow detection.
        
        Authentication flow (only when require_auth=True):
        1. Check if Lambda Authorizer already validated (skip if so)
        2. If no Lambda Authorizer, validate token format
        3. If custom validator provided, use it for token validation
        4. Otherwise, format validation only
        
        Args:
            headers: HTTP headers
            event: API Gateway Lambda event
            
        Raises:
            AuthenticationError: If authentication is invalid
        """
        # Step 1: Check for Lambda Authorizer context (auto-detection)
        authorizer_context = event.get("requestContext", {}).get("authorizer")
        if authorizer_context:
            self.logger.debug("Lambda Authorizer context found - skipping validation")
            self._user_context = authorizer_context
            return
        
        # Step 2: Validate token format (always required)
        auth_value = self._get_header(headers, self.auth_header)
        
        if not auth_value:
            raise AuthenticationError("Missing Authorization header")
        
        if not auth_value.startswith("Bearer "):
            raise AuthenticationError("Authorization header must use Bearer scheme")
        
        token = auth_value[7:].strip()  # Remove "Bearer " prefix
        if not token:
            raise AuthenticationError("Bearer token is empty")
        
        # Step 3: Custom validation hook (if provided)
        if self.token_validator:
            try:
                result = self.token_validator(token)
                if result is False:  # Explicit rejection
                    raise AuthenticationError("Token validation failed")
                elif isinstance(result, dict):  # User context returned
                    self._user_context = result
                # result is True: accept without context (self._user_context stays None)
            except Exception as e:
                if isinstance(e, AuthenticationError):
                    raise  # Re-raise auth errors as-is
                raise AuthenticationError(f"Token validation error: {str(e)}")
        
        # Step 4: Format validation only (no custom validator)
        self.logger.debug("Format validation only - no custom validator provided")


def _is_preflight_request(event: Dict[str, Any]) -> bool:
    """Check if this is a CORS preflight OPTIONS request.
    
    Args:
        event: API Gateway Lambda event
        
    Returns:
        True if this is a preflight request
    """
    # HTTP API Gateway (v2.0)
    if "version" in event and event["version"] == "2.0":
        method = event.get("requestContext", {}).get("http", {}).get("method")
        return method == "OPTIONS"
    
    # REST API Gateway (v1.0)
    if "httpMethod" in event:
        return event.get("httpMethod") == "OPTIONS"
    
    return False
