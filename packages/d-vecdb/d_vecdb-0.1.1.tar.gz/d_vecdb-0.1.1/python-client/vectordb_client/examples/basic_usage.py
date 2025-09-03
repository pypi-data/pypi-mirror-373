#!/usr/bin/env python3
"""
Basic usage examples for d-vecDB Python client.

This example demonstrates:
- Creating collections
- Inserting vectors
- Searching for similar vectors
- Managing collections and vectors
"""

import numpy as np
from vectordb_client import VectorDBClient
from vectordb_client.types import (
    CollectionConfig, Vector, DistanceMetric, 
    IndexConfig, VectorType
)


def main():
    """Run basic usage examples."""
    
    # Initialize client
    print("🚀 Connecting to d-vecDB...")
    client = VectorDBClient(host="localhost", port=8080)
    
    # Test connection
    if not client.ping():
        print("❌ Could not connect to d-vecDB server")
        print("   Make sure the server is running on localhost:8080")
        return
    
    print("✅ Connected to VectorDB-RS!")
    
    try:
        # Example 1: Simple Collection Creation
        print("\n📁 Creating a simple collection...")
        
        collection_name = "basic_example"
        
        # Clean up any existing collection
        try:
            client.delete_collection(collection_name)
            print(f"   Deleted existing '{collection_name}' collection")
        except:
            pass
        
        # Create new collection
        response = client.create_collection_simple(
            name=collection_name,
            dimension=128,
            distance_metric="cosine"
        )
        print(f"✅ Created collection: {collection_name}")
        
        # Example 2: Advanced Collection Configuration
        print("\n🔧 Creating an advanced collection...")
        
        advanced_name = "advanced_example"
        
        try:
            client.delete_collection(advanced_name)
        except:
            pass
        
        # Advanced configuration with custom index settings
        config = CollectionConfig(
            name=advanced_name,
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
        print(f"✅ Created advanced collection: {advanced_name}")
        
        # Example 3: List Collections
        print("\n📋 Listing collections...")
        collections = client.list_collections()
        print(f"   Found {len(collections.collections)} collections:")
        for name in collections.collections:
            print(f"   - {name}")
        
        # Example 4: Insert Simple Vectors
        print(f"\n📝 Inserting vectors into '{collection_name}'...")
        
        # Generate sample data
        num_vectors = 50
        dimension = 128
        vectors_data = np.random.random((num_vectors, dimension))
        
        # Insert vectors one by one (for demonstration)
        for i in range(10):  # Just first 10 for individual inserts
            response = client.insert_simple(
                collection_name=collection_name,
                vector_id=f"doc_{i:03d}",
                vector_data=vectors_data[i],
                metadata={
                    "title": f"Document {i}",
                    "category": "example",
                    "score": float(np.random.random())
                }
            )
        print(f"✅ Inserted 10 vectors individually")
        
        # Example 5: Batch Insert
        print(f"\n📦 Batch inserting remaining vectors...")
        
        # Prepare batch data
        batch_vectors = []
        for i in range(10, num_vectors):
            vector = Vector(
                id=f"doc_{i:03d}",
                data=vectors_data[i].tolist(),
                metadata={
                    "title": f"Document {i}",
                    "category": "batch",
                    "score": float(np.random.random()),
                    "batch_id": i // 10
                }
            )
            batch_vectors.append(vector)
        
        response = client.insert_vectors(collection_name, batch_vectors)
        print(f"✅ Batch inserted {response.inserted_count} vectors")
        
        # Example 6: Collection Statistics
        print(f"\n📊 Collection statistics for '{collection_name}':")
        stats = client.get_collection_stats(collection_name)
        print(f"   Vectors: {stats.vector_count}")
        print(f"   Dimension: {stats.dimension}")
        print(f"   Index size: {stats.index_size} bytes")
        print(f"   Memory usage: {stats.memory_usage} bytes")
        
        # Example 7: Vector Search
        print(f"\n🔍 Searching for similar vectors...")
        
        # Create a query vector
        query_vector = np.random.random(dimension)
        
        # Simple search
        results = client.search_simple(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5
        )
        
        print(f"   Found {len(results)} similar vectors:")
        for i, result in enumerate(results):
            print(f"   {i+1}. ID: {result.id}")
            print(f"      Distance: {result.distance:.6f}")
            print(f"      Metadata: {result.metadata}")
            print()
        
        # Example 8: Advanced Search with Filtering
        print(f"\n🎯 Advanced search with metadata filtering...")
        
        # Search with metadata filter
        response = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            ef_search=150,  # Higher accuracy
            filter={"category": "batch"}  # Only search batch-inserted vectors
        )
        
        print(f"   Found {len(response.results)} vectors with category='batch':")
        for result in response.results[:3]:  # Show first 3
            print(f"   - {result.id}: distance={result.distance:.6f}")
        
        print(f"   Search took {response.query_time_ms}ms")
        
        # Example 9: Retrieve Specific Vector
        print(f"\n🎯 Retrieving specific vector...")
        
        vector_id = "doc_005"
        vector = client.get_vector(collection_name, vector_id)
        print(f"   Retrieved vector '{vector.id}':")
        print(f"   Dimension: {len(vector.data)}")
        print(f"   Metadata: {vector.metadata}")
        
        # Example 10: Update Vector
        print(f"\n✏️  Updating vector metadata...")
        
        # Modify metadata
        vector.metadata["updated"] = True
        vector.metadata["update_count"] = 1
        
        response = client.update_vector(collection_name, vector)
        print(f"✅ Updated vector '{vector.id}'")
        
        # Verify update
        updated_vector = client.get_vector(collection_name, vector_id)
        print(f"   New metadata: {updated_vector.metadata}")
        
        # Example 11: Server Statistics
        print(f"\n🖥️  Server statistics...")
        server_stats = client.get_server_stats()
        print(f"   Total vectors: {server_stats.total_vectors}")
        print(f"   Total collections: {server_stats.total_collections}")
        print(f"   Memory usage: {server_stats.memory_usage:,} bytes")
        print(f"   Disk usage: {server_stats.disk_usage:,} bytes")
        print(f"   Uptime: {server_stats.uptime_seconds:,} seconds")
        
        # Example 12: Delete Operations
        print(f"\n🗑️  Cleaning up...")
        
        # Delete a specific vector
        response = client.delete_vector(collection_name, "doc_001")
        print(f"✅ Deleted vector 'doc_001'")
        
        # Verify deletion
        try:
            client.get_vector(collection_name, "doc_001")
            print("❌ Vector should have been deleted!")
        except Exception:
            print("✅ Vector successfully deleted")
        
        # Final statistics
        final_stats = client.get_collection_stats(collection_name)
        print(f"\n📊 Final collection statistics:")
        print(f"   Vectors: {final_stats.vector_count}")
        
    except Exception as e:
        print(f"❌ Error during example: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up collections (optional)
        try:
            client.delete_collection(collection_name)
            client.delete_collection(advanced_name)
            print(f"\n🧹 Cleaned up example collections")
        except:
            pass
        
        # Close client connection
        client.close()
        print("👋 Disconnected from VectorDB-RS")


if __name__ == "__main__":
    main()