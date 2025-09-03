"""
Type definitions for d-vecDB Python client.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict
import numpy as np


class DistanceMetric(str, Enum):
    """Supported distance metrics for vector similarity."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"  
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


class VectorType(str, Enum):
    """Supported vector data types."""
    FLOAT32 = "float32"
    FLOAT16 = "float16"
    INT8 = "int8"


class IndexConfig(BaseModel):
    """Configuration for HNSW index parameters."""
    model_config = ConfigDict(extra="forbid")
    
    max_connections: int = Field(default=16, ge=2, le=512)
    ef_construction: int = Field(default=200, ge=16, le=2000)
    ef_search: int = Field(default=50, ge=1, le=1000)
    max_layer: int = Field(default=16, ge=1, le=32)


class CollectionConfig(BaseModel):
    """Configuration for creating a vector collection."""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(min_length=1, max_length=64)
    dimension: int = Field(ge=1, le=65536)
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    vector_type: VectorType = VectorType.FLOAT32
    index_config: Optional[IndexConfig] = None


class Vector(BaseModel):
    """A vector with optional metadata."""
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(min_length=1, max_length=256)
    data: List[float] = Field(min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_numpy(
        cls, 
        id: str, 
        data: np.ndarray, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Vector":
        """Create a Vector from a numpy array."""
        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy array")
        if data.ndim != 1:
            raise ValueError("data must be a 1D array")
        return cls(id=id, data=data.tolist(), metadata=metadata)
    
    def to_numpy(self) -> np.ndarray:
        """Convert vector data to numpy array."""
        return np.array(self.data, dtype=np.float32)


class QueryResult(BaseModel):
    """Result from a vector similarity search."""
    model_config = ConfigDict(extra="forbid")
    
    id: str
    distance: float = Field(ge=0.0)
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Request for vector similarity search."""
    model_config = ConfigDict(extra="forbid")
    
    query_vector: List[float] = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=10000)
    ef_search: Optional[int] = Field(default=None, ge=1, le=1000)
    filter: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_numpy(
        cls,
        query_vector: np.ndarray,
        limit: int = 10,
        ef_search: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> "SearchRequest":
        """Create a SearchRequest from a numpy array."""
        if not isinstance(query_vector, np.ndarray):
            raise TypeError("query_vector must be a numpy array")
        if query_vector.ndim != 1:
            raise ValueError("query_vector must be a 1D array")
        return cls(
            query_vector=query_vector.tolist(),
            limit=limit,
            ef_search=ef_search,
            filter=filter
        )


class InsertRequest(BaseModel):
    """Request for inserting vectors."""
    model_config = ConfigDict(extra="forbid")
    
    vectors: List[Vector] = Field(min_length=1)


class UpdateRequest(BaseModel):
    """Request for updating a vector."""
    model_config = ConfigDict(extra="forbid")
    
    vector: Vector


class DeleteRequest(BaseModel):
    """Request for deleting a vector."""
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(min_length=1)


class CollectionStats(BaseModel):
    """Statistics for a vector collection."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    vector_count: int = Field(ge=0)
    dimension: int = Field(ge=1)
    index_size: int = Field(ge=0)
    memory_usage: int = Field(ge=0)


class ServerStats(BaseModel):
    """Statistics for the vector database server."""
    model_config = ConfigDict(extra="forbid")
    
    total_vectors: int = Field(ge=0)
    total_collections: int = Field(ge=0)
    memory_usage: int = Field(ge=0)
    disk_usage: int = Field(ge=0)
    uptime_seconds: int = Field(ge=0)


class HealthResponse(BaseModel):
    """Health check response."""
    model_config = ConfigDict(extra="forbid")
    
    healthy: bool
    status: str
    uptime_seconds: Optional[int] = None
    version: Optional[str] = None


# Response wrapper types
class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    model_config = ConfigDict(extra="forbid")
    
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class SearchResponse(ApiResponse):
    """Response from vector search operation."""
    results: List[QueryResult] = Field(default_factory=list)
    query_time_ms: Optional[int] = None


class InsertResponse(ApiResponse):
    """Response from vector insert operation."""
    inserted_count: Optional[int] = None


class CollectionResponse(ApiResponse):
    """Response from collection operations."""
    collection: Optional[CollectionConfig] = None
    stats: Optional[CollectionStats] = None


class ListCollectionsResponse(ApiResponse):
    """Response from list collections operation."""
    collections: List[str] = Field(default_factory=list)


# Type aliases for convenience
VectorData = Union[List[float], np.ndarray]
Metadata = Dict[str, Any]
Filter = Dict[str, Any]