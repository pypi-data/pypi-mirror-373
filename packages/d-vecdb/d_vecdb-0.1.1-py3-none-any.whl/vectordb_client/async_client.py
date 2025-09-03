"""
Main asynchronous client interface for d-vecDB.
"""

from typing import List, Optional, Dict, Any
from .types import (
    CollectionConfig, Vector, QueryResult, SearchResponse,
    CollectionStats, ServerStats, HealthResponse, InsertResponse,
    ListCollectionsResponse, CollectionResponse, VectorData
)
from .rest.async_client import AsyncRestClient
from .exceptions import VectorDBError, ClientConfigurationError


class AsyncVectorDBClient:
    """
    Main asynchronous client for d-vecDB.
    
    Supports both REST and gRPC protocols with automatic fallback.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: Optional[int] = None,
        grpc_port: Optional[int] = None,
        protocol: str = "rest",
        ssl: bool = False,
        timeout: float = 30.0,
        connection_pool_size: int = 10,
        **kwargs
    ):
        """
        Initialize async VectorDB client.
        
        Args:
            host: Server hostname or IP address
            port: Server port (default: 8080 for REST, 9090 for gRPC)
            grpc_port: Explicit gRPC port (overrides port for gRPC)
            protocol: Protocol to use ("rest", "grpc", or "auto")
            ssl: Use secure connection
            timeout: Request timeout in seconds
            connection_pool_size: Connection pool size for HTTP client
            **kwargs: Additional protocol-specific parameters
        """
        self.host = host
        self.protocol = protocol.lower()
        self.ssl = ssl
        self.timeout = timeout
        self.connection_pool_size = connection_pool_size
        self.kwargs = kwargs
        
        # Determine ports
        if self.protocol == "rest":
            self.port = port or 8080
        elif self.protocol == "grpc":
            self.port = grpc_port or port or 9090
        elif self.protocol == "auto":
            self.rest_port = port or 8080
            self.grpc_port = grpc_port or 9090
        else:
            raise ClientConfigurationError(
                f"Unsupported protocol: {protocol}. Use 'rest', 'grpc', or 'auto'"
            )
        
        # Initialize client(s) - will be set during connect()
        self._rest_client = None
        self._grpc_client = None
        self._connected = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Establish connection to the server."""
        if self._connected:
            return
        
        if self.protocol == "rest":
            self._rest_client = AsyncRestClient(
                host=self.host, 
                port=self.port,
                ssl=self.ssl,
                timeout=self.timeout,
                connection_pool_size=self.connection_pool_size,
                **self.kwargs
            )
        elif self.protocol == "grpc":
            # For now, gRPC async client would be implemented similarly
            # to the sync version but with async methods
            raise NotImplementedError("Async gRPC client not yet implemented")
        elif self.protocol == "auto":
            # Try REST for now (gRPC async implementation pending)
            self._rest_client = AsyncRestClient(
                host=self.host,
                port=self.rest_port,
                ssl=self.ssl,
                timeout=self.timeout,
                connection_pool_size=self.connection_pool_size,
                **self.kwargs
            )
            self.protocol = "rest"
        
        self._connected = True
    
    async def close(self):
        """Close client connections."""
        if self._rest_client:
            await self._rest_client.close()
        if self._grpc_client:
            await self._grpc_client.close()
        self._connected = False
    
    @property
    def client(self):
        """Get the active client instance."""
        if not self._connected:
            raise ClientConfigurationError("Client not connected. Call await client.connect() first.")
        
        if self.protocol == "rest":
            return self._rest_client
        elif self.protocol == "grpc":
            return self._grpc_client
        else:
            raise ClientConfigurationError("No active client")
    
    # Collection Management
    async def create_collection(self, config: CollectionConfig) -> CollectionResponse:
        """Create a new vector collection."""
        return await self.client.create_collection(config)
    
    async def delete_collection(self, name: str) -> CollectionResponse:
        """Delete a vector collection."""
        return await self.client.delete_collection(name)
    
    async def get_collection(self, name: str) -> CollectionResponse:
        """Get collection information."""
        return await self.client.get_collection(name)
    
    async def list_collections(self) -> ListCollectionsResponse:
        """List all collections."""
        return await self.client.list_collections()
    
    async def get_collection_stats(self, name: str) -> CollectionStats:
        """Get collection statistics."""
        return await self.client.get_collection_stats(name)
    
    # Vector Operations
    async def insert_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Insert a single vector."""
        return await self.client.insert_vector(collection_name, vector)
    
    async def insert_vectors(self, collection_name: str, vectors: List[Vector]) -> InsertResponse:
        """Insert multiple vectors."""
        return await self.client.insert_vectors(collection_name, vectors)
    
    async def get_vector(self, collection_name: str, vector_id: str) -> Vector:
        """Retrieve a vector by ID."""
        return await self.client.get_vector(collection_name, vector_id)
    
    async def update_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Update an existing vector."""
        return await self.client.update_vector(collection_name, vector)
    
    async def delete_vector(self, collection_name: str, vector_id: str) -> InsertResponse:
        """Delete a vector by ID."""
        return await self.client.delete_vector(collection_name, vector_id)
    
    # Search Operations
    async def search(
        self, 
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10,
        ef_search: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """Search for similar vectors."""
        return await self.client.search(
            collection_name, query_vector, limit, ef_search, filter
        )
    
    # Server Operations
    async def get_server_stats(self) -> ServerStats:
        """Get server statistics."""
        return await self.client.get_server_stats()
    
    async def health_check(self) -> HealthResponse:
        """Check server health."""
        return await self.client.health_check()
    
    async def ping(self) -> bool:
        """Check if server is reachable."""
        return await self.client.ping()
    
    # Convenience methods
    async def create_collection_simple(
        self,
        name: str,
        dimension: int,
        distance_metric: str = "cosine"
    ) -> CollectionResponse:
        """Create a collection with minimal configuration."""
        return await self.client.create_collection_simple(name, dimension, distance_metric)
    
    async def insert_simple(
        self,
        collection_name: str,
        vector_id: str,
        vector_data: VectorData,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InsertResponse:
        """Insert a vector with simple parameters."""
        return await self.client.insert_simple(collection_name, vector_id, vector_data, metadata)
    
    async def search_simple(
        self,
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10
    ) -> List[QueryResult]:
        """Simple vector search returning just results."""
        return await self.client.search_simple(collection_name, query_vector, limit)
    
    # Batch operations with concurrency
    async def batch_insert_concurrent(
        self,
        collection_name: str,
        vectors_data: List[tuple],  # List of (id, vector_data, metadata)
        batch_size: int = 100,
        max_concurrent_batches: int = 5
    ) -> List[InsertResponse]:
        """Insert multiple vectors in concurrent batches."""
        import asyncio
        
        # Prepare batches
        batches = []
        for i in range(0, len(vectors_data), batch_size):
            batch = vectors_data[i:i + batch_size]
            vectors = []
            
            for item in batch:
                if len(item) == 2:
                    vector_id, vector_data = item
                    metadata = None
                elif len(item) == 3:
                    vector_id, vector_data, metadata = item
                else:
                    raise ValueError("Each vector tuple must be (id, data) or (id, data, metadata)")
                
                if hasattr(vector_data, 'tolist'):
                    vector_data = vector_data.tolist()
                
                vectors.append(Vector(id=vector_id, data=vector_data, metadata=metadata))
            
            batches.append(vectors)
        
        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent_batches)
        
        async def process_batch(batch_vectors):
            async with semaphore:
                return await self.insert_vectors(collection_name, batch_vectors)
        
        tasks = [process_batch(batch) for batch in batches]
        responses = await asyncio.gather(*tasks)
        
        return responses
    
    # Context and utility methods
    async def get_info(self) -> Dict[str, Any]:
        """Get client and server information."""
        try:
            health = await self.health_check()
            stats = await self.get_server_stats()
            collections = await self.list_collections()
            
            return {
                "client": {
                    "protocol": self.protocol,
                    "host": self.host,
                    "port": getattr(self, 'port', None),
                    "ssl": self.ssl,
                    "connection_pool_size": self.connection_pool_size,
                },
                "server": {
                    "healthy": health.healthy,
                    "status": health.status,
                    "stats": stats.model_dump(),
                    "collections": collections.collections,
                }
            }
        except Exception as e:
            return {
                "client": {
                    "protocol": self.protocol,
                    "host": self.host,
                    "port": getattr(self, 'port', None),
                    "ssl": self.ssl,
                    "connection_pool_size": self.connection_pool_size,
                },
                "server": {
                    "error": str(e)
                }
            }