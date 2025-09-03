"""
Unit tests for synchronous VectorDB client.
"""

import pytest
import numpy as np
from typing import List

from vectordb_client import VectorDBClient
from vectordb_client.types import (
    CollectionConfig, Vector, DistanceMetric, VectorType, IndexConfig
)
from vectordb_client.exceptions import (
    VectorDBError, CollectionNotFoundError, VectorNotFoundError
)
from .conftest import assert_vectors_equal, assert_query_results_valid


class TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_default_initialization(self):
        """Test default client initialization."""
        client = VectorDBClient()
        assert client.host == "localhost"
        assert client.port == 8080
        assert client.protocol == "rest"
        assert not client.ssl
        client.close()
    
    def test_custom_initialization(self):
        """Test custom client configuration."""
        client = VectorDBClient(
            host="example.com",
            port=9000,
            protocol="rest",
            ssl=True,
            timeout=60.0
        )
        assert client.host == "example.com"
        assert client.port == 9000
        assert client.ssl
        assert client.timeout == 60.0
        client.close()
    
    def test_context_manager(self, client: VectorDBClient):
        """Test client as context manager."""
        with client:
            assert client.ping()


class TestCollectionManagement:
    """Test collection management operations."""
    
    def test_create_collection_simple(self, client: VectorDBClient, clean_collection: str):
        """Test simple collection creation."""
        collection_name = clean_collection
        
        response = client.create_collection_simple(
            name=collection_name,
            dimension=128,
            distance_metric="cosine"
        )
        assert response.success
        
        # Verify collection exists
        collections = client.list_collections()
        assert collection_name in collections.collections
    
    def test_create_collection_advanced(self, client: VectorDBClient, clean_collection: str):
        """Test advanced collection creation."""
        collection_name = clean_collection
        
        config = CollectionConfig(
            name=collection_name,
            dimension=256,
            distance_metric=DistanceMetric.EUCLIDEAN,
            vector_type=VectorType.FLOAT32,
            index_config=IndexConfig(
                max_connections=32,
                ef_construction=400,
                ef_search=100,
                max_layer=16
            )
        )
        
        response = client.create_collection(config)
        assert response.success
        
        # Verify collection properties
        collection_info = client.get_collection(collection_name)
        assert collection_info.success
    
    def test_list_collections(self, client: VectorDBClient):
        """Test listing collections."""
        # Create test collection
        test_name = "test_list_collection"
        try:
            client.delete_collection(test_name)
        except:
            pass
        
        client.create_collection_simple(test_name, 64, "cosine")
        
        collections = client.list_collections()
        assert collections.success
        assert isinstance(collections.collections, list)
        assert test_name in collections.collections
        
        # Cleanup
        client.delete_collection(test_name)
    
    def test_delete_collection(self, client: VectorDBClient):
        """Test collection deletion."""
        test_name = "test_delete_collection"
        
        # Create collection
        client.create_collection_simple(test_name, 64, "cosine")
        
        # Verify it exists
        collections = client.list_collections()
        assert test_name in collections.collections
        
        # Delete collection
        response = client.delete_collection(test_name)
        assert response.success
        
        # Verify it's gone
        collections = client.list_collections()
        assert test_name not in collections.collections
    
    def test_get_collection_stats(self, client: VectorDBClient, setup_test_collection: str):
        """Test getting collection statistics."""
        collection_name = setup_test_collection
        
        stats = client.get_collection_stats(collection_name)
        assert stats.vector_count > 0
        assert stats.dimension == 128
        assert stats.memory_usage > 0
        assert stats.index_size >= 0


class TestVectorOperations:
    """Test vector CRUD operations."""
    
    def test_insert_single_vector(self, client: VectorDBClient, clean_collection: str):
        """Test inserting a single vector."""
        collection_name = clean_collection
        
        # Create collection
        client.create_collection_simple(collection_name, 128, "cosine")
        
        # Create and insert vector
        vector_data = np.random.random(128).astype(np.float32)
        vector = Vector(
            id="test_vector_001",
            data=vector_data.tolist(),
            metadata={"category": "test", "value": 42}
        )
        
        response = client.insert_vector(collection_name, vector)
        assert response.success
        
        # Verify insertion
        retrieved = client.get_vector(collection_name, "test_vector_001")
        assert_vectors_equal(vector, retrieved)
    
    def test_insert_multiple_vectors(
        self, 
        client: VectorDBClient, 
        clean_collection: str,
        sample_vectors: List[Vector]
    ):
        """Test batch vector insertion."""
        collection_name = clean_collection
        
        # Create collection
        client.create_collection_simple(collection_name, 128, "cosine")
        
        # Insert vectors
        response = client.insert_vectors(collection_name, sample_vectors)
        assert response.success
        assert response.inserted_count == len(sample_vectors)
        
        # Verify all vectors were inserted
        for vector in sample_vectors:
            retrieved = client.get_vector(collection_name, vector.id)
            assert_vectors_equal(vector, retrieved, tolerance=1e-5)
    
    def test_get_vector(self, client: VectorDBClient, setup_test_collection: str):
        """Test retrieving vectors by ID."""
        collection_name = setup_test_collection
        
        # Get a known vector
        vector = client.get_vector(collection_name, "test_vector_000")
        assert vector.id == "test_vector_000"
        assert len(vector.data) == 128
        assert vector.metadata is not None
        assert vector.metadata["category"] == "test"
    
    def test_get_nonexistent_vector(self, client: VectorDBClient, setup_test_collection: str):
        """Test retrieving a non-existent vector."""
        collection_name = setup_test_collection
        
        with pytest.raises(VectorNotFoundError):
            client.get_vector(collection_name, "nonexistent_vector")
    
    def test_update_vector(self, client: VectorDBClient, setup_test_collection: str):
        """Test updating an existing vector."""
        collection_name = setup_test_collection
        
        # Get original vector
        original = client.get_vector(collection_name, "test_vector_000")
        
        # Update metadata
        updated = Vector(
            id=original.id,
            data=original.data,
            metadata={**original.metadata, "updated": True, "timestamp": 123456}
        )
        
        response = client.update_vector(collection_name, updated)
        assert response.success
        
        # Verify update
        retrieved = client.get_vector(collection_name, original.id)
        assert retrieved.metadata["updated"] is True
        assert retrieved.metadata["timestamp"] == 123456
    
    def test_delete_vector(self, client: VectorDBClient, setup_test_collection: str):
        """Test deleting a vector."""
        collection_name = setup_test_collection
        
        vector_id = "test_vector_000"
        
        # Verify vector exists
        original = client.get_vector(collection_name, vector_id)
        assert original.id == vector_id
        
        # Delete vector
        response = client.delete_vector(collection_name, vector_id)
        assert response.success
        
        # Verify deletion
        with pytest.raises(VectorNotFoundError):
            client.get_vector(collection_name, vector_id)
    
    def test_batch_operations(self, client: VectorDBClient, clean_collection: str):
        """Test batch vector operations."""
        collection_name = clean_collection
        
        # Create collection
        client.create_collection_simple(collection_name, 64, "euclidean")
        
        # Generate test data
        vectors_data = [
            (f"batch_vector_{i:03d}", np.random.random(64), {"batch": i // 10})
            for i in range(50)
        ]
        
        # Use batch insert convenience method
        responses = client.batch_insert_simple(
            collection_name=collection_name,
            vectors_data=vectors_data,
            batch_size=20
        )
        
        assert len(responses) == 3  # 50 vectors / 20 batch_size = 3 batches
        total_inserted = sum(r.inserted_count or 0 for r in responses)
        assert total_inserted == 50
        
        # Verify random samples
        for i in [0, 25, 49]:
            vector = client.get_vector(collection_name, f"batch_vector_{i:03d}")
            assert vector.metadata["batch"] == i // 10


class TestSearchOperations:
    """Test vector search functionality."""
    
    def test_simple_search(self, client: VectorDBClient, setup_test_collection: str, query_vector):
        """Test basic vector search."""
        collection_name = setup_test_collection
        
        results = client.search_simple(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5
        )
        
        assert_query_results_valid(results, expected_count=5)
        
        # All results should have valid IDs and distances
        for result in results:
            assert result.id.startswith("test_vector_")
            assert 0 <= result.distance <= 2  # Cosine distance range
    
    def test_advanced_search(self, client: VectorDBClient, setup_test_collection: str, query_vector):
        """Test advanced search with parameters."""
        collection_name = setup_test_collection
        
        response = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            ef_search=150,
            filter={"category": "test"}
        )
        
        assert response.success
        assert_query_results_valid(response.results, expected_count=10)
        assert response.query_time_ms is not None
        assert response.query_time_ms > 0
        
        # All results should match filter
        for result in response.results:
            assert result.metadata["category"] == "test"
    
    def test_search_with_metadata_filter(
        self, 
        client: VectorDBClient, 
        setup_test_collection: str, 
        query_vector
    ):
        """Test search with metadata filtering."""
        collection_name = setup_test_collection
        
        # Search for vectors with specific index values
        response = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5,
            filter={"index": "5"}  # Note: metadata values are strings in filters
        )
        
        # Should find at most 1 result (since index values are unique)
        assert len(response.results) <= 1
        
        if response.results:
            assert response.results[0].metadata["index"] == 5
    
    def test_search_empty_collection(self, client: VectorDBClient, clean_collection: str):
        """Test search in empty collection."""
        collection_name = clean_collection
        
        # Create empty collection
        client.create_collection_simple(collection_name, 128, "cosine")
        
        query_vector = np.random.random(128)
        results = client.search_simple(collection_name, query_vector, limit=10)
        
        assert len(results) == 0
    
    def test_search_limit_boundary(self, client: VectorDBClient, setup_test_collection: str, query_vector):
        """Test search limit boundary conditions."""
        collection_name = setup_test_collection
        
        # Test limit larger than collection size
        results = client.search_simple(collection_name, query_vector, limit=100)
        assert len(results) == 10  # Collection only has 10 vectors
        
        # Test limit of 1
        results = client.search_simple(collection_name, query_vector, limit=1)
        assert len(results) == 1
        
        # Test limit of 0 (should return empty)
        results = client.search_simple(collection_name, query_vector, limit=0)
        assert len(results) == 0


class TestServerOperations:
    """Test server-level operations."""
    
    def test_ping(self, client: VectorDBClient):
        """Test server ping."""
        result = client.ping()
        assert isinstance(result, bool)
        assert result is True  # Assuming server is running
    
    def test_health_check(self, client: VectorDBClient):
        """Test server health check."""
        health = client.health_check()
        assert health.healthy
        assert health.status is not None
    
    def test_server_stats(self, client: VectorDBClient):
        """Test getting server statistics."""
        stats = client.get_server_stats()
        assert stats.total_vectors >= 0
        assert stats.total_collections >= 0
        assert stats.memory_usage >= 0
        assert stats.disk_usage >= 0
        assert stats.uptime_seconds > 0
    
    def test_get_info(self, client: VectorDBClient):
        """Test getting client and server info."""
        info = client.get_info()
        
        assert "client" in info
        assert "server" in info
        
        # Client info should contain configuration
        assert info["client"]["protocol"] == "rest"
        assert info["client"]["host"] == client.host
        
        # Server info should contain health and stats
        if "error" not in info["server"]:
            assert "healthy" in info["server"]
            assert "stats" in info["server"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_collection_not_found(self, client: VectorDBClient):
        """Test operations on non-existent collection."""
        nonexistent = "nonexistent_collection_12345"
        
        with pytest.raises(CollectionNotFoundError):
            client.get_collection_stats(nonexistent)
        
        with pytest.raises(CollectionNotFoundError):
            vector = Vector(id="test", data=[0.1] * 128)
            client.insert_vector(nonexistent, vector)
    
    def test_invalid_vector_dimensions(self, client: VectorDBClient, clean_collection: str):
        """Test inserting vector with wrong dimensions."""
        collection_name = clean_collection
        
        # Create collection with 128 dimensions
        client.create_collection_simple(collection_name, 128, "cosine")
        
        # Try to insert vector with wrong dimensions
        wrong_vector = Vector(
            id="wrong_dims",
            data=[0.1] * 64,  # Wrong dimension (64 instead of 128)
        )
        
        with pytest.raises(VectorDBError):
            client.insert_vector(collection_name, wrong_vector)
    
    def test_duplicate_vector_id(self, client: VectorDBClient, clean_collection: str):
        """Test inserting vectors with duplicate IDs."""
        collection_name = clean_collection
        
        # Create collection
        client.create_collection_simple(collection_name, 128, "cosine")
        
        # Insert first vector
        vector1 = Vector(id="duplicate_id", data=[0.1] * 128)
        response1 = client.insert_vector(collection_name, vector1)
        assert response1.success
        
        # Try to insert another vector with same ID
        vector2 = Vector(id="duplicate_id", data=[0.2] * 128)
        # This might succeed as an update or fail depending on implementation
        # We'll just test that it doesn't crash
        try:
            response2 = client.insert_vector(collection_name, vector2)
        except VectorDBError:
            pass  # Expected behavior for duplicates


class TestConvenienceMethods:
    """Test convenience and helper methods."""
    
    def test_create_collection_simple(self, client: VectorDBClient, clean_collection: str):
        """Test simple collection creation method."""
        collection_name = clean_collection
        
        response = client.create_collection_simple(
            name=collection_name,
            dimension=256,
            distance_metric="euclidean"
        )
        
        assert response.success
        
        # Verify collection properties
        stats = client.get_collection_stats(collection_name)
        assert stats.dimension == 256
    
    def test_insert_simple(self, client: VectorDBClient, clean_collection: str):
        """Test simple vector insertion method."""
        collection_name = clean_collection
        
        # Create collection
        client.create_collection_simple(collection_name, 128, "cosine")
        
        # Insert using simple method
        vector_data = np.random.random(128)
        metadata = {"type": "simple_test", "value": 3.14}
        
        response = client.insert_simple(
            collection_name=collection_name,
            vector_id="simple_vector",
            vector_data=vector_data,
            metadata=metadata
        )
        
        assert response.success
        
        # Verify insertion
        retrieved = client.get_vector(collection_name, "simple_vector")
        assert retrieved.id == "simple_vector"
        assert retrieved.metadata["type"] == "simple_test"
        assert retrieved.metadata["value"] == 3.14


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests for common usage scenarios."""
    
    def test_full_workflow(self, client: VectorDBClient):
        """Test complete workflow from creation to cleanup."""
        collection_name = "integration_test_workflow"
        
        try:
            # Step 1: Create collection
            config = CollectionConfig(
                name=collection_name,
                dimension=128,
                distance_metric=DistanceMetric.COSINE
            )
            client.create_collection(config)
            
            # Step 2: Generate and insert vectors
            vectors = []
            for i in range(20):
                data = np.random.random(128).astype(np.float32)
                data = data / np.linalg.norm(data)  # Normalize
                
                vector = Vector(
                    id=f"workflow_vector_{i:03d}",
                    data=data.tolist(),
                    metadata={"step": "insertion", "index": i}
                )
                vectors.append(vector)
            
            response = client.insert_vectors(collection_name, vectors)
            assert response.inserted_count == 20
            
            # Step 3: Perform searches
            query_vector = np.random.random(128)
            query_vector = query_vector / np.linalg.norm(query_vector)
            
            results = client.search_simple(collection_name, query_vector, limit=5)
            assert len(results) == 5
            
            # Step 4: Update some vectors
            for i in range(5):
                vector_id = f"workflow_vector_{i:03d}"
                original = client.get_vector(collection_name, vector_id)
                
                updated = Vector(
                    id=original.id,
                    data=original.data,
                    metadata={**original.metadata, "updated": True}
                )
                
                client.update_vector(collection_name, updated)
            
            # Step 5: Verify updates
            for i in range(5):
                vector_id = f"workflow_vector_{i:03d}"
                updated = client.get_vector(collection_name, vector_id)
                assert updated.metadata["updated"] is True
            
            # Step 6: Delete some vectors
            for i in range(15, 20):
                vector_id = f"workflow_vector_{i:03d}"
                client.delete_vector(collection_name, vector_id)
            
            # Step 7: Final verification
            stats = client.get_collection_stats(collection_name)
            assert stats.vector_count == 15  # 20 - 5 deleted
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass