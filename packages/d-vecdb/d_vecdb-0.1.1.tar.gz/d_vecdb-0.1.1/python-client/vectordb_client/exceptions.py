"""
Exception classes for d-vecDB Python client.
"""

from typing import Optional, Dict, Any


class VectorDBError(Exception):
    """Base exception for all d-vecDB client errors."""
    
    def __init__(
        self, 
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(status: {self.status_code})")
        if self.details:
            parts.append(f"details: {self.details}")
        return " ".join(parts)


class ConnectionError(VectorDBError):
    """Raised when unable to connect to the VectorDB server."""
    pass


class TimeoutError(VectorDBError):
    """Raised when a request times out."""
    pass


class AuthenticationError(VectorDBError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(VectorDBError):
    """Raised when authorization fails."""
    pass


class CollectionNotFoundError(VectorDBError):
    """Raised when a collection is not found."""
    
    def __init__(self, collection_name: str):
        super().__init__(f"Collection '{collection_name}' not found", status_code=404)
        self.collection_name = collection_name


class CollectionExistsError(VectorDBError):
    """Raised when trying to create a collection that already exists."""
    
    def __init__(self, collection_name: str):
        super().__init__(f"Collection '{collection_name}' already exists", status_code=409)
        self.collection_name = collection_name


class VectorNotFoundError(VectorDBError):
    """Raised when a vector is not found."""
    
    def __init__(self, vector_id: str, collection_name: Optional[str] = None):
        msg = f"Vector '{vector_id}' not found"
        if collection_name:
            msg += f" in collection '{collection_name}'"
        super().__init__(msg, status_code=404)
        self.vector_id = vector_id
        self.collection_name = collection_name


class InvalidParameterError(VectorDBError):
    """Raised when invalid parameters are provided."""
    pass


class ValidationError(VectorDBError):
    """Raised when input validation fails."""
    pass


class ServerError(VectorDBError):
    """Raised when the server encounters an internal error."""
    pass


class RateLimitError(VectorDBError):
    """Raised when rate limit is exceeded."""
    pass


class QuotaExceededError(VectorDBError):
    """Raised when quota is exceeded."""
    pass


# HTTP status code to exception mapping
HTTP_EXCEPTION_MAP = {
    400: InvalidParameterError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: VectorNotFoundError,  # Default, may be overridden
    409: CollectionExistsError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: TimeoutError,
}


def create_exception_from_response(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> VectorDBError:
    """Create an appropriate exception based on HTTP status code."""
    exception_class = HTTP_EXCEPTION_MAP.get(status_code, VectorDBError)
    return exception_class(message, status_code, details)


def create_exception_from_grpc_error(grpc_error) -> VectorDBError:
    """Create an appropriate exception from a gRPC error."""
    try:
        import grpc
        
        code_to_exception = {
            grpc.StatusCode.NOT_FOUND: VectorNotFoundError,
            grpc.StatusCode.ALREADY_EXISTS: CollectionExistsError,
            grpc.StatusCode.INVALID_ARGUMENT: InvalidParameterError,
            grpc.StatusCode.UNAUTHENTICATED: AuthenticationError,
            grpc.StatusCode.PERMISSION_DENIED: AuthorizationError,
            grpc.StatusCode.RESOURCE_EXHAUSTED: QuotaExceededError,
            grpc.StatusCode.DEADLINE_EXCEEDED: TimeoutError,
            grpc.StatusCode.INTERNAL: ServerError,
            grpc.StatusCode.UNAVAILABLE: ConnectionError,
        }
        
        status_code = grpc_error.code()
        message = grpc_error.details()
        
        exception_class = code_to_exception.get(status_code, VectorDBError)
        return exception_class(message)
        
    except ImportError:
        # Fallback if grpc is not available
        return VectorDBError(str(grpc_error))


class ClientConfigurationError(VectorDBError):
    """Raised when client is misconfigured."""
    pass


class ProtocolError(VectorDBError):
    """Raised when there's a protocol-level error."""
    pass


class SerializationError(VectorDBError):
    """Raised when serialization/deserialization fails."""
    pass