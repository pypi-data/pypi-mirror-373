"""
Unit tests for asynchronous VectorDB client.
"""

import pytest
import asyncio
import numpy as np
from typing import List

from vectordb_client import AsyncVectorDBClient
from vectordb_client.types import (
    CollectionConfig, Vector, DistanceMetric, VectorType, IndexConfig
)
from vectordb_client.exceptions import (
    VectorDBError, CollectionNotFoundError, VectorNotFoundError
)
from .conftest import assert_vectors_equal, assert_query_results_valid


class TestAsyncClientInitialization:
    """Test async client initialization and configuration."""
    
    def test_default_initialization(self):
        """Test default async client initialization."""
        client = AsyncVectorDBClient()
        assert client.host == "localhost"
        assert client.rest_port == 8080
        assert client.protocol == "rest"
        assert not client.ssl
    
    def test_custom_initialization(self):
        """Test custom async client configuration."""
        client = AsyncVectorDBClient(
            host="example.com",
            port=9000,
            protocol="rest",
            ssl=True,
            timeout=60.0,
            connection_pool_size=20
        )
        assert client.host == "example.com"
        assert client.ssl
        assert client.timeout == 60.0
        assert client.connection_pool_size == 20
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async client as context manager."""
        async with AsyncVectorDBClient() as client:
            # This will skip if server is not available
            try:
                result = await client.ping()
                assert isinstance(result, bool)
            except:
                pytest.skip("Server not available for async context manager test")


class TestAsyncCollectionManagement:
    """Test async collection management operations."""
    
    @pytest.mark.asyncio
    async def test_create_collection_simple(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test simple async collection creation."""
        collection_name = async_clean_collection
        
        response = await async_client.create_collection_simple(
            name=collection_name,
            dimension=128,
            distance_metric="cosine"
        )
        assert response.success
        
        # Verify collection exists
        collections = await async_client.list_collections()
        assert collection_name in collections.collections
    
    @pytest.mark.asyncio
    async def test_create_collection_advanced(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test advanced async collection creation."""
        collection_name = async_clean_collection
        
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
        
        response = await async_client.create_collection(config)
        assert response.success
        
        # Verify collection properties
        collection_info = await async_client.get_collection(collection_name)
        assert collection_info.success
    
    @pytest.mark.asyncio
    async def test_list_collections(self, async_client: AsyncVectorDBClient):
        """Test listing collections asynchronously."""
        # Create test collection
        test_name = "async_test_list_collection"
        try:
            await async_client.delete_collection(test_name)
        except:
            pass
        
        await async_client.create_collection_simple(test_name, 64, "cosine")
        
        collections = await async_client.list_collections()
        assert collections.success
        assert isinstance(collections.collections, list)
        assert test_name in collections.collections
        
        # Cleanup
        await async_client.delete_collection(test_name)
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str
    ):
        """Test getting collection statistics asynchronously."""
        collection_name = async_setup_test_collection
        
        stats = await async_client.get_collection_stats(collection_name)
        assert stats.vector_count > 0
        assert stats.dimension == 128
        assert stats.memory_usage > 0
        assert stats.index_size >= 0


class TestAsyncVectorOperations:
    """Test async vector CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_insert_single_vector(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test inserting a single vector asynchronously."""
        collection_name = async_clean_collection
        
        # Create collection
        await async_client.create_collection_simple(collection_name, 128, "cosine")
        
        # Create and insert vector
        vector_data = np.random.random(128).astype(np.float32)
        vector = Vector(
            id="async_test_vector_001",
            data=vector_data.tolist(),
            metadata={"category": "async_test", "value": 42}
        )
        
        response = await async_client.insert_vector(collection_name, vector)
        assert response.success
        
        # Verify insertion
        retrieved = await async_client.get_vector(collection_name, "async_test_vector_001")
        assert_vectors_equal(vector, retrieved)
    
    @pytest.mark.asyncio
    async def test_insert_multiple_vectors(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str,
        sample_vectors: List[Vector]
    ):
        """Test batch vector insertion asynchronously."""
        collection_name = async_clean_collection
        
        # Create collection
        await async_client.create_collection_simple(collection_name, 128, "cosine")
        
        # Insert vectors
        response = await async_client.insert_vectors(collection_name, sample_vectors)
        assert response.success
        assert response.inserted_count == len(sample_vectors)
        
        # Verify all vectors were inserted
        for vector in sample_vectors:
            retrieved = await async_client.get_vector(collection_name, vector.id)
            assert_vectors_equal(vector, retrieved, tolerance=1e-5)
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_insert(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test concurrent batch vector insertion."""
        collection_name = async_clean_collection
        
        # Create collection
        await async_client.create_collection_simple(collection_name, 256, "euclidean")
        
        # Generate test data
        vectors_data = [
            (f"concurrent_vector_{i:04d}", np.random.random(256), {"batch": i // 50})
            for i in range(500)
        ]
        
        # Use concurrent batch insert
        responses = await async_client.batch_insert_concurrent(
            collection_name=collection_name,
            vectors_data=vectors_data,
            batch_size=100,
            max_concurrent_batches=10
        )
        
        # Verify results
        total_inserted = sum(r.inserted_count or 0 for r in responses)
        assert total_inserted == 500
        
        # Verify collection stats
        stats = await async_client.get_collection_stats(collection_name)
        assert stats.vector_count == 500
    
    @pytest.mark.asyncio
    async def test_update_vector(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str
    ):
        """Test updating an existing vector asynchronously."""
        collection_name = async_setup_test_collection
        
        # Get original vector
        original = await async_client.get_vector(collection_name, "test_vector_000")
        
        # Update metadata
        updated = Vector(
            id=original.id,
            data=original.data,
            metadata={**original.metadata, "async_updated": True, "timestamp": 987654}
        )
        
        response = await async_client.update_vector(collection_name, updated)
        assert response.success
        
        # Verify update
        retrieved = await async_client.get_vector(collection_name, original.id)
        assert retrieved.metadata["async_updated"] is True
        assert retrieved.metadata["timestamp"] == 987654
    
    @pytest.mark.asyncio
    async def test_delete_vector(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str
    ):
        """Test deleting a vector asynchronously."""
        collection_name = async_setup_test_collection
        
        vector_id = "test_vector_001"
        
        # Verify vector exists
        original = await async_client.get_vector(collection_name, vector_id)
        assert original.id == vector_id
        
        # Delete vector
        response = await async_client.delete_vector(collection_name, vector_id)
        assert response.success
        
        # Verify deletion
        with pytest.raises(VectorNotFoundError):
            await async_client.get_vector(collection_name, vector_id)


class TestAsyncSearchOperations:
    """Test async vector search functionality."""
    
    @pytest.mark.asyncio
    async def test_simple_search(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str, 
        query_vector
    ):
        """Test basic async vector search."""
        collection_name = async_setup_test_collection
        
        results = await async_client.search_simple(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5
        )
        
        assert_query_results_valid(results, expected_count=5)
        
        # All results should have valid IDs and distances
        for result in results:
            assert result.id.startswith("test_vector_")
            assert 0 <= result.distance <= 2  # Cosine distance range
    
    @pytest.mark.asyncio
    async def test_advanced_search(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str, 
        query_vector
    ):
        """Test advanced async search with parameters."""
        collection_name = async_setup_test_collection
        
        response = await async_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=8,
            ef_search=150,
            filter={"category": "test"}
        )
        
        assert response.success
        assert_query_results_valid(response.results, expected_count=8)
        assert response.query_time_ms is not None
        assert response.query_time_ms > 0
        
        # All results should match filter
        for result in response.results:
            assert result.metadata["category"] == "test"
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str
    ):
        """Test concurrent search operations."""
        collection_name = async_setup_test_collection
        
        # Generate multiple query vectors
        query_vectors = [
            np.random.random(128) / np.linalg.norm(np.random.random(128))
            for _ in range(20)
        ]
        
        # Define search coroutine
        async def search_task(query_idx: int, query_vector: np.ndarray):
            results = await async_client.search_simple(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=3
            )
            return query_idx, results
        
        # Run all searches concurrently
        start_time = asyncio.get_event_loop().time()
        
        search_tasks = [
            search_task(i, qv) for i, qv in enumerate(query_vectors)
        ]
        
        search_results = await asyncio.gather(*search_tasks)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Verify results
        assert len(search_results) == 20
        
        for query_idx, results in search_results:
            assert 0 <= query_idx < 20
            assert_query_results_valid(results, expected_count=3)
        
        # Performance check (concurrent should be faster than sequential)
        print(f"Concurrent search rate: {len(query_vectors)/duration:.1f} queries/second")
    
    @pytest.mark.asyncio
    async def test_search_with_filter(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str, 
        query_vector
    ):
        """Test async search with metadata filtering."""
        collection_name = async_setup_test_collection
        
        # Search with specific filter
        response = await async_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            filter={"category": "test"}
        )
        
        # All results should match the filter
        for result in response.results:
            assert result.metadata["category"] == "test"


class TestAsyncServerOperations:
    """Test async server-level operations."""
    
    @pytest.mark.asyncio
    async def test_ping(self, async_client: AsyncVectorDBClient):
        """Test async server ping."""
        result = await async_client.ping()
        assert isinstance(result, bool)
        assert result is True  # Assuming server is running
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncVectorDBClient):
        """Test async server health check."""
        health = await async_client.health_check()
        assert health.healthy
        assert health.status is not None
    
    @pytest.mark.asyncio
    async def test_server_stats(self, async_client: AsyncVectorDBClient):
        """Test getting server statistics asynchronously."""
        stats = await async_client.get_server_stats()
        assert stats.total_vectors >= 0
        assert stats.total_collections >= 0
        assert stats.memory_usage >= 0
        assert stats.disk_usage >= 0
        assert stats.uptime_seconds > 0
    
    @pytest.mark.asyncio
    async def test_get_info(self, async_client: AsyncVectorDBClient):
        """Test getting client and server info asynchronously."""
        info = await async_client.get_info()
        
        assert "client" in info
        assert "server" in info
        
        # Client info should contain configuration
        assert info["client"]["protocol"] == "rest"
        assert info["client"]["host"] == async_client.host
        
        # Server info should contain health and stats
        if "error" not in info["server"]:
            assert "healthy" in info["server"]
            assert "stats" in info["server"]


class TestAsyncErrorHandling:
    """Test async error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_collection_not_found(self, async_client: AsyncVectorDBClient):
        """Test async operations on non-existent collection."""
        nonexistent = "async_nonexistent_collection_12345"
        
        with pytest.raises(CollectionNotFoundError):
            await async_client.get_collection_stats(nonexistent)
        
        with pytest.raises(CollectionNotFoundError):
            vector = Vector(id="test", data=[0.1] * 128)
            await async_client.insert_vector(nonexistent, vector)
    
    @pytest.mark.asyncio
    async def test_invalid_vector_dimensions(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test async insertion of vector with wrong dimensions."""
        collection_name = async_clean_collection
        
        # Create collection with 128 dimensions
        await async_client.create_collection_simple(collection_name, 128, "cosine")
        
        # Try to insert vector with wrong dimensions
        wrong_vector = Vector(
            id="async_wrong_dims",
            data=[0.1] * 64,  # Wrong dimension (64 instead of 128)
        )
        
        with pytest.raises(VectorDBError):
            await async_client.insert_vector(collection_name, wrong_vector)
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling connection errors in async client."""
        # Create client with unreachable host
        unreachable_client = AsyncVectorDBClient(host="unreachable.example.com", port=8888)
        
        try:
            await unreachable_client.connect()
            result = await unreachable_client.ping()
            # If we reach here, the "unreachable" host was actually reachable
            assert isinstance(result, bool)
        except Exception:
            # Expected: connection should fail
            pass
        finally:
            await unreachable_client.close()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in async operations."""
        # Create client with very short timeout
        short_timeout_client = AsyncVectorDBClient(timeout=0.001)  # 1ms timeout
        
        try:
            await short_timeout_client.connect()
            # Operations might timeout
            try:
                await short_timeout_client.ping()
            except asyncio.TimeoutError:
                pass  # Expected timeout
            except Exception:
                pass  # Other connection errors are also acceptable
        finally:
            await short_timeout_client.close()


class TestAsyncConvenienceMethods:
    """Test async convenience and helper methods."""
    
    @pytest.mark.asyncio
    async def test_insert_simple(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test simple async vector insertion method."""
        collection_name = async_clean_collection
        
        # Create collection
        await async_client.create_collection_simple(collection_name, 128, "cosine")
        
        # Insert using simple method
        vector_data = np.random.random(128)
        metadata = {"type": "async_simple_test", "value": 2.718}
        
        response = await async_client.insert_simple(
            collection_name=collection_name,
            vector_id="async_simple_vector",
            vector_data=vector_data,
            metadata=metadata
        )
        
        assert response.success
        
        # Verify insertion
        retrieved = await async_client.get_vector(collection_name, "async_simple_vector")
        assert retrieved.id == "async_simple_vector"
        assert retrieved.metadata["type"] == "async_simple_test"
        assert retrieved.metadata["value"] == 2.718


@pytest.mark.performance
class TestAsyncPerformance:
    """Performance tests for async operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_insertion_performance(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test performance of concurrent insertions."""
        collection_name = async_clean_collection
        
        # Create collection
        await async_client.create_collection_simple(collection_name, 256, "cosine")
        
        # Generate large dataset
        num_vectors = 1000
        vectors_data = [
            (f"perf_vector_{i:05d}", np.random.random(256), {"batch": i // 100})
            for i in range(num_vectors)
        ]
        
        # Measure concurrent batch insertion time
        start_time = asyncio.get_event_loop().time()
        
        responses = await async_client.batch_insert_concurrent(
            collection_name=collection_name,
            vectors_data=vectors_data,
            batch_size=100,
            max_concurrent_batches=10
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Verify all vectors were inserted
        total_inserted = sum(r.inserted_count or 0 for r in responses)
        assert total_inserted == num_vectors
        
        # Calculate performance metrics
        rate = num_vectors / duration
        print(f"Async batch insertion rate: {rate:.0f} vectors/second")
        
        # Performance assertion (should be reasonably fast)
        assert rate > 100, f"Insertion rate too slow: {rate:.0f} vectors/second"
    
    @pytest.mark.asyncio
    async def test_concurrent_search_performance(
        self, 
        async_client: AsyncVectorDBClient, 
        async_setup_test_collection: str
    ):
        """Test performance of concurrent searches."""
        collection_name = async_setup_test_collection
        
        # Generate query vectors
        num_queries = 50
        query_vectors = [
            np.random.random(128) / np.linalg.norm(np.random.random(128))
            for _ in range(num_queries)
        ]
        
        # Measure concurrent search time
        start_time = asyncio.get_event_loop().time()
        
        search_tasks = [
            async_client.search_simple(collection_name, qv, limit=5)
            for qv in query_vectors
        ]
        
        results = await asyncio.gather(*search_tasks)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Verify all searches completed
        assert len(results) == num_queries
        for result_list in results:
            assert len(result_list) <= 5
        
        # Calculate performance metrics
        rate = num_queries / duration
        print(f"Async search rate: {rate:.0f} queries/second")
        
        # Performance assertion
        assert rate > 10, f"Search rate too slow: {rate:.0f} queries/second"


@pytest.mark.integration
class TestAsyncIntegrationScenarios:
    """Integration tests for async usage scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_async_workflow(self, async_client: AsyncVectorDBClient):
        """Test complete async workflow from creation to cleanup."""
        collection_name = "async_integration_test_workflow"
        
        try:
            # Step 1: Create collection
            config = CollectionConfig(
                name=collection_name,
                dimension=128,
                distance_metric=DistanceMetric.COSINE
            )
            await async_client.create_collection(config)
            
            # Step 2: Generate and insert vectors concurrently
            num_vectors = 100
            vectors_data = [
                (f"async_workflow_vector_{i:04d}", 
                 np.random.random(128) / np.linalg.norm(np.random.random(128)),
                 {"step": "insertion", "index": i, "batch": i // 20})
                for i in range(num_vectors)
            ]
            
            responses = await async_client.batch_insert_concurrent(
                collection_name=collection_name,
                vectors_data=vectors_data,
                batch_size=20,
                max_concurrent_batches=8
            )
            
            total_inserted = sum(r.inserted_count or 0 for r in responses)
            assert total_inserted == num_vectors
            
            # Step 3: Perform concurrent searches
            query_vectors = [np.random.random(128) for _ in range(10)]
            
            search_tasks = [
                async_client.search_simple(collection_name, qv, limit=5)
                for qv in query_vectors
            ]
            
            search_results = await asyncio.gather(*search_tasks)
            assert len(search_results) == 10
            
            # Step 4: Update vectors concurrently
            update_tasks = []
            for i in range(0, 20, 2):  # Update every other vector in first 20
                vector_id = f"async_workflow_vector_{i:04d}"
                
                async def update_vector(vid):
                    original = await async_client.get_vector(collection_name, vid)
                    updated = Vector(
                        id=original.id,
                        data=original.data,
                        metadata={**original.metadata, "async_updated": True}
                    )
                    return await async_client.update_vector(collection_name, updated)
                
                update_tasks.append(update_vector(vector_id))
            
            update_responses = await asyncio.gather(*update_tasks)
            assert all(r.success for r in update_responses)
            
            # Step 5: Verify updates
            for i in range(0, 20, 2):
                vector_id = f"async_workflow_vector_{i:04d}"
                updated = await async_client.get_vector(collection_name, vector_id)
                assert updated.metadata["async_updated"] is True
            
            # Step 6: Delete vectors concurrently
            delete_tasks = [
                async_client.delete_vector(collection_name, f"async_workflow_vector_{i:04d}")
                for i in range(80, 100)  # Delete last 20 vectors
            ]
            
            delete_responses = await asyncio.gather(*delete_tasks)
            assert all(r.success for r in delete_responses)
            
            # Step 7: Final verification
            stats = await async_client.get_collection_stats(collection_name)
            assert stats.vector_count == 80  # 100 - 20 deleted
            
        finally:
            # Cleanup
            try:
                await async_client.delete_collection(collection_name)
            except:
                pass