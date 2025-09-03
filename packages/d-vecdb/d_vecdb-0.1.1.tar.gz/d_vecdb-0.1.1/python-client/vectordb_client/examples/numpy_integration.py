#!/usr/bin/env python3
"""
NumPy integration examples for d-vecDB Python client.

This example demonstrates:
- Working with NumPy arrays directly
- Efficient vector data handling
- Scientific computing workflows
- Embeddings management
"""

import numpy as np
from typing import List, Tuple
import time
from vectordb_client import VectorDBClient
from vectordb_client.types import Vector, CollectionConfig, DistanceMetric


def generate_embeddings(num_samples: int, dimension: int) -> np.ndarray:
    """Generate synthetic embeddings for demonstration."""
    # Simulate document embeddings with some structure
    base_embeddings = np.random.randn(num_samples, dimension).astype(np.float32)
    
    # Add some clustering structure
    cluster_centers = np.random.randn(10, dimension).astype(np.float32)
    cluster_assignments = np.random.randint(0, 10, num_samples)
    
    for i, cluster_id in enumerate(cluster_assignments):
        # Add cluster bias
        base_embeddings[i] += 0.3 * cluster_centers[cluster_id]
    
    # Normalize vectors (good practice for cosine similarity)
    norms = np.linalg.norm(base_embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    normalized_embeddings = base_embeddings / norms
    
    return normalized_embeddings


def create_metadata_from_array(embeddings: np.ndarray) -> List[dict]:
    """Generate metadata for embeddings."""
    metadata_list = []
    
    for i in range(len(embeddings)):
        # Calculate some features from the embedding
        mean_val = float(np.mean(embeddings[i]))
        std_val = float(np.std(embeddings[i]))
        max_val = float(np.max(embeddings[i]))
        min_val = float(np.min(embeddings[i]))
        
        metadata = {
            "doc_id": i,
            "mean": mean_val,
            "std": std_val,
            "max": max_val,
            "min": min_val,
            "category": "positive" if mean_val > 0 else "negative",
            "magnitude": float(np.linalg.norm(embeddings[i])),
        }
        metadata_list.append(metadata)
    
    return metadata_list


def main():
    """Run NumPy integration examples."""
    
    print("🧮 NumPy Integration Examples for VectorDB-RS")
    print("=" * 50)
    
    # Initialize client
    client = VectorDBClient(host="localhost", port=8080)
    
    if not client.ping():
        print("❌ Could not connect to VectorDB-RS server")
        print("   Make sure the server is running on localhost:8080")
        return
    
    print("✅ Connected to VectorDB-RS!")
    
    collection_name = "numpy_embeddings"
    
    try:
        # Clean up existing collection
        try:
            client.delete_collection(collection_name)
            print(f"   Deleted existing '{collection_name}' collection")
        except:
            pass
        
        # Example 1: Working with NumPy Arrays
        print("\n📊 Generating synthetic embeddings with NumPy...")
        
        # Generate embeddings using NumPy
        num_documents = 2000
        embedding_dimension = 256
        
        start_time = time.time()
        embeddings = generate_embeddings(num_documents, embedding_dimension)
        generation_time = time.time() - start_time
        
        print(f"✅ Generated {num_documents} embeddings ({embedding_dimension}D) in {generation_time:.3f}s")
        print(f"   Array shape: {embeddings.shape}")
        print(f"   Array dtype: {embeddings.dtype}")
        print(f"   Memory usage: {embeddings.nbytes / 1024 / 1024:.2f} MB")
        
        # Example 2: Create Collection for Embeddings
        print(f"\n📁 Creating collection for embeddings...")
        
        config = CollectionConfig(
            name=collection_name,
            dimension=embedding_dimension,
            distance_metric=DistanceMetric.COSINE  # Best for normalized embeddings
        )
        
        client.create_collection(config)
        print(f"✅ Created collection with cosine distance metric")
        
        # Example 3: Efficient Batch Processing with NumPy
        print(f"\n📦 Processing embeddings efficiently...")
        
        # Generate metadata using NumPy operations
        metadata_list = create_metadata_from_array(embeddings)
        
        # Convert to Vector objects
        vectors = []
        for i in range(len(embeddings)):
            vector = Vector(
                id=f"doc_{i:05d}",
                data=embeddings[i].tolist(),  # Convert NumPy array to list
                metadata=metadata_list[i]
            )
            vectors.append(vector)
        
        print(f"📊 Prepared {len(vectors)} vector objects for insertion")
        
        # Example 4: Batch Insert with Performance Monitoring
        print(f"\n📈 Batch inserting vectors...")
        
        batch_size = 200
        insertion_times = []
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            batch_start = time.time()
            response = client.insert_vectors(collection_name, batch)
            batch_time = time.time() - batch_start
            
            insertion_times.append(batch_time)
            
            print(f"   Batch {i//batch_size + 1}: {len(batch)} vectors in {batch_time:.3f}s "
                  f"({len(batch)/batch_time:.0f} vec/s)")
        
        # Calculate statistics
        total_time = sum(insertion_times)
        avg_batch_time = np.mean(insertion_times)
        std_batch_time = np.std(insertion_times)
        
        print(f"✅ Inserted all {len(vectors)} vectors in {total_time:.2f}s")
        print(f"   Average batch time: {avg_batch_time:.3f}s ± {std_batch_time:.3f}s")
        print(f"   Overall rate: {len(vectors)/total_time:.0f} vectors/second")
        
        # Example 5: NumPy-based Query Generation and Search
        print(f"\n🔍 Performing searches with NumPy-generated queries...")
        
        # Generate query vectors using NumPy
        num_queries = 50
        query_embeddings = generate_embeddings(num_queries, embedding_dimension)
        
        search_times = []
        all_results = []
        
        for i, query_vector in enumerate(query_embeddings):
            search_start = time.time()
            
            results = client.search_simple(
                collection_name=collection_name,
                query_vector=query_vector,  # NumPy array is automatically converted
                limit=10
            )
            
            search_time = time.time() - search_start
            search_times.append(search_time)
            all_results.append(results)
            
            if i < 3:  # Show details for first few queries
                print(f"   Query {i+1}: Found {len(results)} results in {search_time:.3f}s")
                if results:
                    print(f"      Best match: {results[0].id} (distance: {results[0].distance:.4f})")
        
        # Search performance statistics
        avg_search_time = np.mean(search_times)
        std_search_time = np.std(search_times)
        
        print(f"✅ Completed {num_queries} searches")
        print(f"   Average search time: {avg_search_time:.3f}s ± {std_search_time:.3f}s")
        print(f"   Search rate: {1/avg_search_time:.0f} queries/second")
        
        # Example 6: Advanced NumPy Analysis
        print(f"\n🧮 Advanced analysis using NumPy...")
        
        # Extract distances for analysis
        all_distances = []
        for results in all_results:
            distances = [r.distance for r in results]
            all_distances.extend(distances)
        
        distances_array = np.array(all_distances)
        
        print(f"📊 Distance statistics across all search results:")
        print(f"   Mean distance: {np.mean(distances_array):.4f}")
        print(f"   Std distance: {np.std(distances_array):.4f}")
        print(f"   Min distance: {np.min(distances_array):.4f}")
        print(f"   Max distance: {np.max(distances_array):.4f}")
        print(f"   Median distance: {np.median(distances_array):.4f}")
        
        # Example 7: Vector Similarity Analysis
        print(f"\n🔬 Analyzing vector similarity patterns...")
        
        # Get a sample of vectors for analysis
        sample_vectors = []
        sample_ids = [f"doc_{i:05d}" for i in range(0, min(100, len(vectors)), 10)]
        
        for vec_id in sample_ids:
            vector = client.get_vector(collection_name, vec_id)
            sample_vectors.append(np.array(vector.data))
        
        sample_matrix = np.vstack(sample_vectors)
        
        # Compute pairwise cosine similarities
        normalized_samples = sample_matrix / np.linalg.norm(sample_matrix, axis=1, keepdims=True)
        similarity_matrix = np.dot(normalized_samples, normalized_samples.T)
        
        # Remove diagonal (self-similarity)
        mask = ~np.eye(similarity_matrix.shape[0], dtype=bool)
        similarities = similarity_matrix[mask]
        
        print(f"📈 Pairwise similarity analysis ({len(sample_vectors)} vectors):")
        print(f"   Mean similarity: {np.mean(similarities):.4f}")
        print(f"   Std similarity: {np.std(similarities):.4f}")
        print(f"   Min similarity: {np.min(similarities):.4f}")
        print(f"   Max similarity: {np.max(similarities):.4f}")
        
        # Example 8: Memory-Efficient Operations
        print(f"\n💾 Memory-efficient operations...")
        
        # Demonstrate working with large arrays efficiently
        large_query_batch = np.random.randn(10, embedding_dimension).astype(np.float32)
        
        # Process in chunks to manage memory
        chunk_results = []
        for chunk_query in large_query_batch:
            results = client.search_simple(collection_name, chunk_query, limit=5)
            chunk_results.append(len(results))
        
        print(f"✅ Processed {len(large_query_batch)} queries in memory-efficient chunks")
        print(f"   Results per query: {chunk_results}")
        
        # Final collection statistics
        stats = client.get_collection_stats(collection_name)
        print(f"\n📊 Final collection statistics:")
        print(f"   Total vectors: {stats.vector_count:,}")
        print(f"   Dimension: {stats.dimension}")
        print(f"   Memory usage: {stats.memory_usage:,} bytes ({stats.memory_usage/1024/1024:.2f} MB)")
        
    except Exception as e:
        print(f"❌ Error during NumPy operations: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            client.delete_collection(collection_name)
            print(f"\n🧹 Cleaned up collection '{collection_name}'")
        except:
            pass
        
        client.close()
        print("👋 Disconnected from VectorDB-RS")


def numpy_performance_tips():
    """Demonstrate NumPy performance optimization tips."""
    print("\n" + "="*60)
    print("⚡ NumPy Performance Tips for VectorDB-RS")
    print("="*60)
    
    # Tip 1: Data type optimization
    print("\n1. 🎯 Data Type Optimization")
    
    # Generate sample data in different precisions
    dimension = 128
    num_vectors = 1000
    
    # Float64 (default)
    vectors_f64 = np.random.random((num_vectors, dimension))
    
    # Float32 (more efficient)
    vectors_f32 = np.random.random((num_vectors, dimension)).astype(np.float32)
    
    print(f"   Float64 memory: {vectors_f64.nbytes / 1024 / 1024:.2f} MB")
    print(f"   Float32 memory: {vectors_f32.nbytes / 1024 / 1024:.2f} MB")
    print(f"   Memory savings: {(1 - vectors_f32.nbytes/vectors_f64.nbytes)*100:.1f}%")
    
    # Tip 2: Vectorized operations
    print("\n2. ⚡ Vectorized Operations")
    
    # Inefficient: Loop-based normalization
    start_time = time.time()
    normalized_slow = np.zeros_like(vectors_f32)
    for i in range(len(vectors_f32)):
        norm = np.linalg.norm(vectors_f32[i])
        if norm > 0:
            normalized_slow[i] = vectors_f32[i] / norm
    slow_time = time.time() - start_time
    
    # Efficient: Vectorized normalization
    start_time = time.time()
    norms = np.linalg.norm(vectors_f32, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized_fast = vectors_f32 / norms
    fast_time = time.time() - start_time
    
    print(f"   Loop-based: {slow_time:.3f}s")
    print(f"   Vectorized: {fast_time:.3f}s")
    print(f"   Speedup: {slow_time/fast_time:.1f}x faster")
    
    # Tip 3: Memory layout optimization
    print("\n3. 🗂️  Memory Layout Optimization")
    
    # C-contiguous (row-major) is typically faster for VectorDB operations
    vectors_c = np.ascontiguousarray(vectors_f32)
    vectors_f = np.asfortranarray(vectors_f32)
    
    print(f"   C-contiguous: {vectors_c.flags.c_contiguous}")
    print(f"   Fortran-contiguous: {vectors_f.flags.f_contiguous}")
    print("   Recommendation: Use C-contiguous arrays for better performance")
    
    print("\n✅ Performance optimization tips completed!")


if __name__ == "__main__":
    main()
    numpy_performance_tips()