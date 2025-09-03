#!/usr/bin/env python3
"""
Async usage examples for d-vecDB Python client.

This example demonstrates:
- Async context managers
- Concurrent batch operations
- High-performance async patterns
- Error handling in async contexts
"""

import asyncio
import numpy as np
from vectordb_client import AsyncVectorDBClient
from vectordb_client.types import (
    CollectionConfig, Vector, DistanceMetric, 
    IndexConfig, VectorType
)
from vectordb_client.exceptions import (
    VectorDBError, ConnectionError, CollectionNotFoundError
)


async def main():
    """Run async usage examples."""
    
    # Use async context manager for automatic resource management
    async with AsyncVectorDBClient(
        host="localhost", 
        port=8080,
        connection_pool_size=20
    ) as client:
        
        # Test connection
        print("🚀 Connecting to VectorDB-RS (async)...")
        if not await client.ping():
            print("❌ Could not connect to VectorDB-RS server")
            return
        
        print("✅ Connected to VectorDB-RS!")
        
        collection_name = "async_example"
        
        try:
            # Clean up any existing collection
            try:
                await client.delete_collection(collection_name)
                print(f"   Deleted existing '{collection_name}' collection")
            except:
                pass
            
            # Example 1: Async Collection Creation
            print("\n📁 Creating collection asynchronously...")
            config = CollectionConfig(
                name=collection_name,
                dimension=384,
                distance_metric=DistanceMetric.COSINE,
                vector_type=VectorType.FLOAT32,
                index_config=IndexConfig(
                    max_connections=32,
                    ef_construction=400,
                    ef_search=150
                )
            )
            
            await client.create_collection(config)
            print(f"✅ Created collection: {collection_name}")
            
            # Example 2: High-Performance Batch Insert
            print("\n📦 Generating large dataset for batch processing...")
            num_vectors = 5000
            dimension = 384
            
            # Generate dataset
            dataset = np.random.random((num_vectors, dimension)).astype(np.float32)
            
            # Prepare batch data
            vectors_data = [
                (f"doc_{i:05d}", dataset[i], {
                    "title": f"Document {i}",
                    "category": "async_batch",
                    "importance": float(np.random.random()),
                    "tags": ["example", "async", f"batch_{i // 1000}"]
                })
                for i in range(num_vectors)
            ]
            
            # Example 3: Concurrent Batch Processing
            print(f"📊 Inserting {num_vectors} vectors with concurrent batching...")
            start_time = asyncio.get_event_loop().time()
            
            responses = await client.batch_insert_concurrent(
                collection_name=collection_name,
                vectors_data=vectors_data,
                batch_size=250,
                max_concurrent_batches=15
            )
            
            end_time = asyncio.get_event_loop().time()
            
            total_inserted = sum(r.inserted_count or 0 for r in responses)
            duration = end_time - start_time
            rate = total_inserted / duration if duration > 0 else 0
            
            print(f"✅ Inserted {total_inserted} vectors in {duration:.2f}s")
            print(f"🚀 Rate: {rate:.0f} vectors/second")
            
            # Example 4: Concurrent Search Operations
            print(f"\n🔍 Running concurrent search queries...")
            
            # Generate multiple query vectors
            query_vectors = [np.random.random(dimension).astype(np.float32) for _ in range(10)]
            
            async def search_concurrent(query_idx, query_vector):
                """Perform a search operation."""
                results = await client.search_simple(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=5
                )
                return query_idx, results
            
            # Run all searches concurrently
            search_start = asyncio.get_event_loop().time()
            
            search_tasks = [
                search_concurrent(i, qv) for i, qv in enumerate(query_vectors)
            ]
            
            search_results = await asyncio.gather(*search_tasks)
            
            search_end = asyncio.get_event_loop().time()
            search_duration = search_end - search_start
            
            print(f"✅ Completed {len(query_vectors)} concurrent searches in {search_duration:.3f}s")
            print(f"🚀 Search rate: {len(query_vectors)/search_duration:.1f} queries/second")
            
            # Show sample results
            for query_idx, results in search_results[:3]:
                print(f"   Query {query_idx}: Found {len(results)} results")
                if results:
                    print(f"      Best match: {results[0].id} (distance: {results[0].distance:.4f})")
            
            # Example 5: Advanced Search with Filtering
            print(f"\n🎯 Async search with metadata filtering...")
            
            filter_query = np.random.random(dimension).astype(np.float32)
            
            filtered_response = await client.search(
                collection_name=collection_name,
                query_vector=filter_query,
                limit=20,
                ef_search=200,
                filter={"category": "async_batch"}
            )
            
            print(f"   Found {len(filtered_response.results)} filtered results")
            print(f"   Query took {filtered_response.query_time_ms}ms")
            
            # Example 6: Async Collection Statistics
            print(f"\n📊 Collection statistics...")
            stats = await client.get_collection_stats(collection_name)
            print(f"   Vectors: {stats.vector_count:,}")
            print(f"   Memory usage: {stats.memory_usage:,} bytes")
            print(f"   Index size: {stats.index_size:,} bytes")
            
            # Example 7: Server Statistics
            server_stats = await client.get_server_stats()
            print(f"\n🖥️  Server statistics:")
            print(f"   Total vectors: {server_stats.total_vectors:,}")
            print(f"   Collections: {server_stats.total_collections}")
            print(f"   Memory usage: {server_stats.memory_usage:,} bytes")
            print(f"   Uptime: {server_stats.uptime_seconds:,}s")
            
        except Exception as e:
            print(f"❌ Error during async operations: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            try:
                await client.delete_collection(collection_name)
                print(f"\n🧹 Cleaned up collection '{collection_name}'")
            except:
                pass


async def error_handling_example():
    """Demonstrate async error handling patterns."""
    print("\n" + "="*50)
    print("🚨 Async Error Handling Examples")
    print("="*50)
    
    client = AsyncVectorDBClient(host="localhost", port=8080)
    
    try:
        await client.connect()
        
        # Example of handling collection not found
        try:
            await client.get_collection("nonexistent_collection")
        except CollectionNotFoundError:
            print("✅ Handled CollectionNotFoundError correctly")
        
        # Example of handling connection errors
        unreachable_client = AsyncVectorDBClient(host="unreachable.example.com")
        try:
            await unreachable_client.connect()
            await unreachable_client.ping()
        except ConnectionError:
            print("✅ Handled ConnectionError correctly")
        finally:
            await unreachable_client.close()
    
    except Exception as e:
        print(f"🔧 Handling general error: {e}")
    
    finally:
        await client.close()


async def performance_monitoring():
    """Demonstrate performance monitoring patterns."""
    print("\n" + "="*50)
    print("📊 Performance Monitoring Example")
    print("="*50)
    
    async with AsyncVectorDBClient() as client:
        if not await client.ping():
            print("❌ Server not available for performance test")
            return
        
        collection_name = "performance_test"
        
        try:
            # Setup test collection
            await client.create_collection_simple(
                name=collection_name,
                dimension=128,
                distance_metric="cosine"
            )
            
            # Performance test: Insertion throughput
            print("🧪 Testing insertion throughput...")
            test_vectors = [(f"perf_{i}", np.random.random(128), {"test": True}) 
                          for i in range(1000)]
            
            insertion_start = asyncio.get_event_loop().time()
            
            await client.batch_insert_concurrent(
                collection_name=collection_name,
                vectors_data=test_vectors,
                batch_size=100,
                max_concurrent_batches=10
            )
            
            insertion_end = asyncio.get_event_loop().time()
            insertion_rate = len(test_vectors) / (insertion_end - insertion_start)
            
            print(f"📈 Insertion rate: {insertion_rate:.0f} vectors/second")
            
            # Performance test: Search throughput
            print("🧪 Testing search throughput...")
            query_vector = np.random.random(128)
            num_searches = 100
            
            search_start = asyncio.get_event_loop().time()
            
            search_tasks = [
                client.search_simple(collection_name, query_vector, limit=10)
                for _ in range(num_searches)
            ]
            
            await asyncio.gather(*search_tasks)
            
            search_end = asyncio.get_event_loop().time()
            search_rate = num_searches / (search_end - search_start)
            
            print(f"📈 Search rate: {search_rate:.0f} queries/second")
            
        finally:
            try:
                await client.delete_collection(collection_name)
            except:
                pass


if __name__ == "__main__":
    print("🔄 Starting Async VectorDB-RS Examples...")
    
    # Run all examples
    asyncio.run(main())
    asyncio.run(error_handling_example()) 
    asyncio.run(performance_monitoring())
    
    print("\n✅ All async examples completed!")