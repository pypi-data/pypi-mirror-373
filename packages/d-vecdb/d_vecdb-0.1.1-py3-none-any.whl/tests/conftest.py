"""
Pytest configuration and fixtures for d-vecDB client tests.
"""

import pytest
import asyncio
import numpy as np
from typing import Generator, AsyncGenerator
import os
import subprocess
import time

from vectordb_client import VectorDBClient, AsyncVectorDBClient
from vectordb_client.types import CollectionConfig, Vector, DistanceMetric


# Test configuration
TEST_HOST = os.getenv("VECTORDB_TEST_HOST", "localhost")
TEST_PORT = int(os.getenv("VECTORDB_TEST_PORT", "8080"))
TEST_GRPC_PORT = int(os.getenv("VECTORDB_TEST_GRPC_PORT", "9090"))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[VectorDBClient, None, None]:
    """Synchronous VectorDB client fixture."""
    client = VectorDBClient(host=TEST_HOST, port=TEST_PORT)
    
    # Skip tests if server is not available
    if not client.ping():
        pytest.skip("VectorDB-RS server not available for testing")
    
    yield client
    client.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncVectorDBClient, None, None]:
    """Asynchronous VectorDB client fixture."""
    client = AsyncVectorDBClient(host=TEST_HOST, port=TEST_PORT)
    await client.connect()
    
    # Skip tests if server is not available
    if not await client.ping():
        pytest.skip("VectorDB-RS server not available for async testing")
    
    yield client
    await client.close()


@pytest.fixture
def test_collection_config() -> CollectionConfig:
    """Standard test collection configuration."""
    return CollectionConfig(
        name="test_collection",
        dimension=128,
        distance_metric=DistanceMetric.COSINE
    )


@pytest.fixture
def sample_vectors() -> list[Vector]:
    """Generate sample vectors for testing."""
    np.random.seed(42)  # For reproducible tests
    
    vectors = []
    for i in range(10):
        data = np.random.random(128).astype(np.float32)
        # Normalize for cosine similarity
        data = data / np.linalg.norm(data)
        
        vector = Vector(
            id=f"test_vector_{i:03d}",
            data=data.tolist(),
            metadata={
                "index": i,
                "category": "test",
                "value": float(np.random.random()),
            }
        )
        vectors.append(vector)
    
    return vectors


@pytest.fixture
def large_sample_vectors() -> list[Vector]:
    """Generate larger set of sample vectors for performance tests."""
    np.random.seed(123)
    
    vectors = []
    for i in range(1000):
        data = np.random.random(256).astype(np.float32)
        data = data / np.linalg.norm(data)
        
        vector = Vector(
            id=f"large_test_vector_{i:05d}",
            data=data.tolist(),
            metadata={
                "index": i,
                "batch": i // 100,
                "category": "performance_test",
            }
        )
        vectors.append(vector)
    
    return vectors


@pytest.fixture
def query_vector() -> np.ndarray:
    """Generate a query vector for search tests."""
    np.random.seed(999)
    vector = np.random.random(128).astype(np.float32)
    return vector / np.linalg.norm(vector)


@pytest.fixture(scope="function")
def clean_collection(client: VectorDBClient, test_collection_config: CollectionConfig):
    """Ensure clean test collection before each test."""
    collection_name = test_collection_config.name
    
    # Clean up before test
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    yield collection_name
    
    # Clean up after test
    try:
        client.delete_collection(collection_name)
    except:
        pass


@pytest.fixture(scope="function")
async def async_clean_collection(
    async_client: AsyncVectorDBClient, 
    test_collection_config: CollectionConfig
):
    """Ensure clean test collection before each async test."""
    collection_name = test_collection_config.name
    
    # Clean up before test
    try:
        await async_client.delete_collection(collection_name)
    except:
        pass
    
    yield collection_name
    
    # Clean up after test
    try:
        await async_client.delete_collection(collection_name)
    except:
        pass


@pytest.fixture
def setup_test_collection(
    client: VectorDBClient, 
    test_collection_config: CollectionConfig,
    sample_vectors: list[Vector],
    clean_collection: str
) -> str:
    """Set up a test collection with sample data."""
    collection_name = clean_collection
    
    # Create collection
    client.create_collection(test_collection_config)
    
    # Insert sample vectors
    client.insert_vectors(collection_name, sample_vectors)
    
    return collection_name


@pytest.fixture
async def async_setup_test_collection(
    async_client: AsyncVectorDBClient,
    test_collection_config: CollectionConfig,
    sample_vectors: list[Vector],
    async_clean_collection: str
) -> str:
    """Set up a test collection with sample data (async)."""
    collection_name = async_clean_collection
    
    # Create collection
    await async_client.create_collection(test_collection_config)
    
    # Insert sample vectors
    await async_client.insert_vectors(collection_name, sample_vectors)
    
    return collection_name


# Test data generators
def generate_random_vectors(count: int, dimension: int, seed: int = None) -> list[Vector]:
    """Generate random vectors for testing."""
    if seed is not None:
        np.random.seed(seed)
    
    vectors = []
    for i in range(count):
        data = np.random.random(dimension).astype(np.float32)
        data = data / np.linalg.norm(data)  # Normalize
        
        vector = Vector(
            id=f"random_vector_{i:05d}",
            data=data.tolist(),
            metadata={
                "index": i,
                "generated": True,
                "norm": float(np.linalg.norm(data)),
            }
        )
        vectors.append(vector)
    
    return vectors


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip conditions
def skip_if_no_server():
    """Skip test if VectorDB server is not available."""
    try:
        client = VectorDBClient(host=TEST_HOST, port=TEST_PORT)
        available = client.ping()
        client.close()
        return not available
    except:
        return True


# Custom assertions
def assert_vectors_equal(v1: Vector, v2: Vector, tolerance: float = 1e-6):
    """Assert that two vectors are equal within tolerance."""
    assert v1.id == v2.id
    assert len(v1.data) == len(v2.data)
    
    for a, b in zip(v1.data, v2.data):
        assert abs(a - b) < tolerance
    
    # Compare metadata if both have it
    if v1.metadata is not None and v2.metadata is not None:
        assert v1.metadata == v2.metadata


def assert_query_results_valid(results: list, expected_count: int = None):
    """Assert that query results are valid."""
    if expected_count is not None:
        assert len(results) == expected_count
    
    for result in results:
        assert hasattr(result, 'id')
        assert hasattr(result, 'distance')
        assert isinstance(result.distance, (int, float))
        assert result.distance >= 0
    
    # Results should be sorted by distance (ascending)
    distances = [r.distance for r in results]
    assert distances == sorted(distances)