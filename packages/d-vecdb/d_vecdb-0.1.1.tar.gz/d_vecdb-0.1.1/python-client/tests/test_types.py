"""
Unit tests for d-vecDB type definitions and validation.
"""

import pytest
import numpy as np
from pydantic import ValidationError

from vectordb_client.types import (
    CollectionConfig, Vector, QueryResult, SearchRequest, SearchResponse,
    CollectionStats, ServerStats, HealthResponse, InsertResponse,
    ListCollectionsResponse, CollectionResponse, 
    DistanceMetric, VectorType, IndexConfig
)


class TestDistanceMetric:
    """Test distance metric enum."""
    
    def test_distance_metric_values(self):
        """Test distance metric enum values."""
        assert DistanceMetric.COSINE == "cosine"
        assert DistanceMetric.EUCLIDEAN == "euclidean"
        assert DistanceMetric.DOT_PRODUCT == "dot_product"
        assert DistanceMetric.MANHATTAN == "manhattan"
    
    def test_distance_metric_from_string(self):
        """Test creating distance metric from string."""
        assert DistanceMetric("cosine") == DistanceMetric.COSINE
        assert DistanceMetric("euclidean") == DistanceMetric.EUCLIDEAN


class TestVectorType:
    """Test vector type enum."""
    
    def test_vector_type_values(self):
        """Test vector type enum values."""
        assert VectorType.FLOAT32 == "float32"
        assert VectorType.FLOAT16 == "float16"
        assert VectorType.INT8 == "int8"


class TestIndexConfig:
    """Test index configuration model."""
    
    def test_valid_index_config(self):
        """Test creating valid index configuration."""
        config = IndexConfig(
            max_connections=32,
            ef_construction=400,
            ef_search=100,
            max_layer=16
        )
        
        assert config.max_connections == 32
        assert config.ef_construction == 400
        assert config.ef_search == 100
        assert config.max_layer == 16
    
    def test_default_index_config(self):
        """Test default index configuration values."""
        config = IndexConfig()
        
        assert config.max_connections == 16
        assert config.ef_construction == 200
        assert config.ef_search == 50
        assert config.max_layer == 0
    
    def test_invalid_index_config(self):
        """Test validation of invalid index configuration."""
        # Test negative max_connections
        with pytest.raises(ValidationError):
            IndexConfig(max_connections=-1)
        
        # Test zero ef_construction
        with pytest.raises(ValidationError):
            IndexConfig(ef_construction=0)
        
        # Test negative max_layer
        with pytest.raises(ValidationError):
            IndexConfig(max_layer=-5)


class TestCollectionConfig:
    """Test collection configuration model."""
    
    def test_valid_collection_config(self):
        """Test creating valid collection configuration."""
        config = CollectionConfig(
            name="test_collection",
            dimension=256,
            distance_metric=DistanceMetric.COSINE,
            vector_type=VectorType.FLOAT32
        )
        
        assert config.name == "test_collection"
        assert config.dimension == 256
        assert config.distance_metric == DistanceMetric.COSINE
        assert config.vector_type == VectorType.FLOAT32
    
    def test_collection_config_with_index(self):
        """Test collection configuration with index config."""
        index_config = IndexConfig(max_connections=64, ef_construction=800)
        
        config = CollectionConfig(
            name="advanced_collection",
            dimension=512,
            distance_metric=DistanceMetric.EUCLIDEAN,
            index_config=index_config
        )
        
        assert config.index_config.max_connections == 64
        assert config.index_config.ef_construction == 800
    
    def test_collection_config_defaults(self):
        """Test default values in collection configuration."""
        config = CollectionConfig(
            name="minimal_collection",
            dimension=128
        )
        
        assert config.distance_metric == DistanceMetric.COSINE
        assert config.vector_type == VectorType.FLOAT32
        assert config.index_config is None
    
    def test_invalid_collection_config(self):
        """Test validation of invalid collection configuration."""
        # Test empty name
        with pytest.raises(ValidationError):
            CollectionConfig(name="", dimension=128)
        
        # Test too long name
        with pytest.raises(ValidationError):
            CollectionConfig(name="x" * 100, dimension=128)
        
        # Test zero dimension
        with pytest.raises(ValidationError):
            CollectionConfig(name="test", dimension=0)
        
        # Test negative dimension
        with pytest.raises(ValidationError):
            CollectionConfig(name="test", dimension=-10)
        
        # Test dimension too large
        with pytest.raises(ValidationError):
            CollectionConfig(name="test", dimension=100000)


class TestVector:
    """Test vector model."""
    
    def test_valid_vector(self):
        """Test creating valid vector."""
        vector_data = [0.1, 0.2, 0.3, 0.4]
        metadata = {"category": "test", "value": 42}
        
        vector = Vector(
            id="test_vector_001",
            data=vector_data,
            metadata=metadata
        )
        
        assert vector.id == "test_vector_001"
        assert vector.data == vector_data
        assert vector.metadata == metadata
    
    def test_vector_with_numpy_array(self):
        """Test creating vector with NumPy array."""
        np_array = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        
        vector = Vector(
            id="numpy_vector",
            data=np_array.tolist()
        )
        
        assert len(vector.data) == 4
        assert all(isinstance(x, float) for x in vector.data)
    
    def test_vector_without_metadata(self):
        """Test vector without metadata."""
        vector = Vector(
            id="simple_vector",
            data=[1.0, 2.0, 3.0]
        )
        
        assert vector.metadata is None
    
    def test_invalid_vector(self):
        """Test validation of invalid vector."""
        # Test empty ID
        with pytest.raises(ValidationError):
            Vector(id="", data=[1.0, 2.0])
        
        # Test empty data
        with pytest.raises(ValidationError):
            Vector(id="test", data=[])
        
        # Test non-numeric data
        with pytest.raises(ValidationError):
            Vector(id="test", data=["a", "b", "c"])
    
    def test_vector_methods(self):
        """Test vector utility methods."""
        vector_data = np.array([3.0, 4.0, 0.0], dtype=np.float32)
        
        vector = Vector(
            id="method_test",
            data=vector_data.tolist()
        )
        
        # Test to_numpy conversion
        np_array = vector.to_numpy()
        assert isinstance(np_array, np.ndarray)
        assert np_array.dtype == np.float32
        assert np.array_equal(np_array, vector_data)
        
        # Test from_numpy class method
        new_vector = Vector.from_numpy(
            id="from_numpy",
            data=vector_data,
            metadata={"source": "numpy"}
        )
        
        assert new_vector.id == "from_numpy"
        assert len(new_vector.data) == 3
        assert new_vector.metadata["source"] == "numpy"


class TestQueryResult:
    """Test query result model."""
    
    def test_valid_query_result(self):
        """Test creating valid query result."""
        result = QueryResult(
            id="result_001",
            distance=0.1234,
            metadata={"score": 0.95}
        )
        
        assert result.id == "result_001"
        assert result.distance == 0.1234
        assert result.metadata["score"] == 0.95
    
    def test_query_result_without_metadata(self):
        """Test query result without metadata."""
        result = QueryResult(
            id="simple_result",
            distance=0.5
        )
        
        assert result.metadata is None
    
    def test_invalid_query_result(self):
        """Test validation of invalid query result."""
        # Test negative distance (depends on implementation)
        # Some distance metrics might allow negative values
        try:
            QueryResult(id="test", distance=-0.1)
        except ValidationError:
            pass  # Negative distances might be invalid
        
        # Test empty ID
        with pytest.raises(ValidationError):
            QueryResult(id="", distance=0.5)


class TestSearchRequest:
    """Test search request model."""
    
    def test_valid_search_request(self):
        """Test creating valid search request."""
        query_vector = [0.1, 0.2, 0.3, 0.4]
        filter_dict = {"category": "test"}
        
        request = SearchRequest(
            query_vector=query_vector,
            limit=10,
            ef_search=100,
            filter=filter_dict
        )
        
        assert request.query_vector == query_vector
        assert request.limit == 10
        assert request.ef_search == 100
        assert request.filter == filter_dict
    
    def test_search_request_defaults(self):
        """Test default values in search request."""
        request = SearchRequest(
            query_vector=[1.0, 0.0, 0.0]
        )
        
        assert request.limit == 10
        assert request.ef_search is None
        assert request.filter is None
    
    def test_invalid_search_request(self):
        """Test validation of invalid search request."""
        # Test empty query vector
        with pytest.raises(ValidationError):
            SearchRequest(query_vector=[])
        
        # Test negative limit
        with pytest.raises(ValidationError):
            SearchRequest(query_vector=[1.0], limit=-1)
        
        # Test zero limit
        with pytest.raises(ValidationError):
            SearchRequest(query_vector=[1.0], limit=0)


class TestSearchResponse:
    """Test search response model."""
    
    def test_valid_search_response(self):
        """Test creating valid search response."""
        results = [
            QueryResult(id="result_1", distance=0.1),
            QueryResult(id="result_2", distance=0.2)
        ]
        
        response = SearchResponse(
            success=True,
            results=results,
            query_time_ms=15.5
        )
        
        assert response.success is True
        assert len(response.results) == 2
        assert response.query_time_ms == 15.5
    
    def test_empty_search_response(self):
        """Test search response with no results."""
        response = SearchResponse(
            success=True,
            results=[],
            query_time_ms=2.3
        )
        
        assert response.success is True
        assert len(response.results) == 0


class TestServerStats:
    """Test server statistics model."""
    
    def test_valid_server_stats(self):
        """Test creating valid server statistics."""
        stats = ServerStats(
            total_vectors=1000000,
            total_collections=50,
            memory_usage=2147483648,  # 2GB
            disk_usage=5368709120,    # 5GB
            uptime_seconds=86400      # 1 day
        )
        
        assert stats.total_vectors == 1000000
        assert stats.total_collections == 50
        assert stats.memory_usage == 2147483648
        assert stats.disk_usage == 5368709120
        assert stats.uptime_seconds == 86400
    
    def test_invalid_server_stats(self):
        """Test validation of invalid server statistics."""
        # Test negative values
        with pytest.raises(ValidationError):
            ServerStats(
                total_vectors=-1,
                total_collections=1,
                memory_usage=1000,
                disk_usage=2000,
                uptime_seconds=100
            )


class TestCollectionStats:
    """Test collection statistics model."""
    
    def test_valid_collection_stats(self):
        """Test creating valid collection statistics."""
        stats = CollectionStats(
            vector_count=50000,
            dimension=256,
            memory_usage=134217728,  # 128MB
            index_size=67108864      # 64MB
        )
        
        assert stats.vector_count == 50000
        assert stats.dimension == 256
        assert stats.memory_usage == 134217728
        assert stats.index_size == 67108864
    
    def test_collection_stats_validation(self):
        """Test collection statistics validation."""
        # Test zero dimension
        with pytest.raises(ValidationError):
            CollectionStats(
                vector_count=100,
                dimension=0,
                memory_usage=1000,
                index_size=500
            )


class TestResponseModels:
    """Test various response models."""
    
    def test_health_response(self):
        """Test health response model."""
        response = HealthResponse(
            healthy=True,
            status="OK"
        )
        
        assert response.healthy is True
        assert response.status == "OK"
    
    def test_insert_response(self):
        """Test insert response model."""
        response = InsertResponse(
            success=True,
            message="Vectors inserted successfully",
            inserted_count=25
        )
        
        assert response.success is True
        assert response.message == "Vectors inserted successfully"
        assert response.inserted_count == 25
    
    def test_collection_response(self):
        """Test collection response model."""
        response = CollectionResponse(
            success=True,
            message="Collection created successfully"
        )
        
        assert response.success is True
        assert response.message == "Collection created successfully"
    
    def test_list_collections_response(self):
        """Test list collections response model."""
        collections = ["collection1", "collection2", "collection3"]
        
        response = ListCollectionsResponse(
            success=True,
            collections=collections
        )
        
        assert response.success is True
        assert len(response.collections) == 3
        assert "collection1" in response.collections


class TestDataValidation:
    """Test data validation and conversion."""
    
    def test_numeric_data_validation(self):
        """Test validation of numeric vector data."""
        # Valid float data
        vector = Vector(id="float_test", data=[1.5, 2.7, -0.3])
        assert all(isinstance(x, (int, float)) for x in vector.data)
        
        # Valid integer data (should be converted to float)
        vector = Vector(id="int_test", data=[1, 2, 3])
        assert all(isinstance(x, (int, float)) for x in vector.data)
        
        # Mixed numeric data
        vector = Vector(id="mixed_test", data=[1, 2.5, 3])
        assert all(isinstance(x, (int, float)) for x in vector.data)
    
    def test_metadata_validation(self):
        """Test metadata validation."""
        # Valid metadata types
        valid_metadata = {
            "string_field": "test",
            "int_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "none_field": None
        }
        
        vector = Vector(
            id="metadata_test",
            data=[1.0, 2.0],
            metadata=valid_metadata
        )
        
        assert vector.metadata == valid_metadata
    
    def test_model_serialization(self):
        """Test model serialization and deserialization."""
        # Create a complex configuration
        config = CollectionConfig(
            name="serialization_test",
            dimension=512,
            distance_metric=DistanceMetric.EUCLIDEAN,
            vector_type=VectorType.FLOAT32,
            index_config=IndexConfig(
                max_connections=64,
                ef_construction=800
            )
        )
        
        # Test model_dump
        data = config.model_dump()
        assert data["name"] == "serialization_test"
        assert data["dimension"] == 512
        assert data["distance_metric"] == "euclidean"
        
        # Test model_validate
        recreated = CollectionConfig.model_validate(data)
        assert recreated.name == config.name
        assert recreated.dimension == config.dimension
        assert recreated.distance_metric == config.distance_metric
        assert recreated.index_config.max_connections == config.index_config.max_connections
    
    def test_json_compatibility(self):
        """Test JSON serialization compatibility."""
        import json
        
        # Create a vector with complex data
        vector = Vector(
            id="json_test",
            data=np.random.random(10).tolist(),
            metadata={
                "category": "test",
                "tags": ["json", "serialization"],
                "score": 0.95
            }
        )
        
        # Test JSON serialization
        json_data = json.dumps(vector.model_dump())
        assert isinstance(json_data, str)
        
        # Test JSON deserialization
        parsed_data = json.loads(json_data)
        recreated = Vector.model_validate(parsed_data)
        
        assert recreated.id == vector.id
        assert len(recreated.data) == len(vector.data)
        assert recreated.metadata == vector.metadata