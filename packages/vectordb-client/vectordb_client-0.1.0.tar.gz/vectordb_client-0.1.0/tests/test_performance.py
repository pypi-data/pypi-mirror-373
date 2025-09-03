"""
Performance tests for d-vecDB Python client.
"""

import pytest
import time
import asyncio
import numpy as np
from typing import List, Tuple
import statistics

from vectordb_client import VectorDBClient, AsyncVectorDBClient
from vectordb_client.types import Vector, CollectionConfig, DistanceMetric
from .conftest import generate_random_vectors


@pytest.mark.performance
class TestSyncPerformance:
    """Performance tests for synchronous client."""
    
    def test_insertion_performance(self, client: VectorDBClient, clean_collection: str):
        """Test vector insertion performance."""
        collection_name = clean_collection
        
        # Setup
        dimension = 256
        client.create_collection_simple(collection_name, dimension, "cosine")
        
        # Generate test vectors
        num_vectors = 1000
        vectors = generate_random_vectors(num_vectors, dimension, seed=42)
        
        # Test single insertion performance
        single_times = []
        for i in range(10):  # Test first 10 vectors individually
            start_time = time.time()
            client.insert_vector(collection_name, vectors[i])
            end_time = time.time()
            single_times.append(end_time - start_time)
        
        avg_single_time = statistics.mean(single_times)
        single_rate = 1 / avg_single_time
        
        print(f"Single insertion: {avg_single_time:.4f}s avg, {single_rate:.0f} vectors/sec")
        
        # Test batch insertion performance
        batch_vectors = vectors[10:510]  # 500 vectors
        batch_sizes = [50, 100, 200]
        
        for batch_size in batch_sizes:
            batch_times = []
            
            # Insert remaining vectors in batches
            for i in range(0, len(batch_vectors), batch_size):
                batch = batch_vectors[i:i + batch_size]
                
                start_time = time.time()
                response = client.insert_vectors(collection_name, batch)
                end_time = time.time()
                
                batch_time = end_time - start_time
                batch_times.append(batch_time)
                
                assert response.inserted_count == len(batch)
            
            avg_batch_time = statistics.mean(batch_times)
            batch_rate = batch_size / avg_batch_time
            
            print(f"Batch size {batch_size}: {avg_batch_time:.4f}s avg, {batch_rate:.0f} vectors/sec")
        
        # Verify all vectors were inserted
        stats = client.get_collection_stats(collection_name)
        expected_total = 10 + len(batch_vectors)  # Single + batch insertions
        assert stats.vector_count >= expected_total * 0.9  # Allow some tolerance
    
    def test_search_performance(self, client: VectorDBClient, clean_collection: str):
        """Test vector search performance."""
        collection_name = clean_collection
        dimension = 128
        
        # Setup collection with data
        client.create_collection_simple(collection_name, dimension, "cosine")
        
        # Insert test vectors
        num_vectors = 2000
        vectors = generate_random_vectors(num_vectors, dimension, seed=123)
        
        # Insert in batches for faster setup
        batch_size = 200
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            client.insert_vectors(collection_name, batch)
        
        # Generate query vectors
        np.random.seed(456)
        num_queries = 100
        query_vectors = [
            np.random.random(dimension).astype(np.float32) 
            for _ in range(num_queries)
        ]
        
        # Test search performance with different limits
        limits = [5, 10, 50]
        
        for limit in limits:
            search_times = []
            
            for query_vector in query_vectors:
                start_time = time.time()
                results = client.search_simple(collection_name, query_vector, limit)
                end_time = time.time()
                
                search_time = end_time - start_time
                search_times.append(search_time)
                
                assert len(results) <= limit
            
            avg_search_time = statistics.mean(search_times)
            search_rate = 1 / avg_search_time
            
            print(f"Search limit {limit}: {avg_search_time:.4f}s avg, {search_rate:.0f} queries/sec")
            
            # Performance assertion
            assert search_rate > 50, f"Search too slow for limit {limit}: {search_rate:.0f} qps"
    
    def test_mixed_workload_performance(self, client: VectorDBClient, clean_collection: str):
        """Test performance under mixed read/write workload."""
        collection_name = clean_collection
        dimension = 256
        
        # Setup
        client.create_collection_simple(collection_name, dimension, "euclidean")
        
        # Initial data load
        initial_vectors = generate_random_vectors(500, dimension, seed=789)
        client.insert_vectors(collection_name, initial_vectors)
        
        # Mixed workload simulation
        np.random.seed(999)
        operations = []
        total_time_start = time.time()
        
        for i in range(200):  # 200 mixed operations
            operation_type = np.random.choice(['search', 'insert', 'update'], p=[0.7, 0.2, 0.1])
            
            start_time = time.time()
            
            if operation_type == 'search':
                query_vector = np.random.random(dimension)
                results = client.search_simple(collection_name, query_vector, limit=10)
                assert len(results) <= 10
                
            elif operation_type == 'insert':
                new_vector = Vector(
                    id=f"mixed_workload_{i}_{int(time.time() * 1000)}",
                    data=np.random.random(dimension).tolist(),
                    metadata={"workload": "mixed", "operation": i}
                )
                client.insert_vector(collection_name, new_vector)
                
            elif operation_type == 'update':
                # Try to update a random existing vector
                try:
                    vector_id = f"random_vector_{np.random.randint(0, 500):05d}"
                    original = client.get_vector(collection_name, vector_id)
                    updated = Vector(
                        id=original.id,
                        data=original.data,
                        metadata={**original.metadata, "updated": True}
                    )
                    client.update_vector(collection_name, updated)
                except:
                    # Vector might not exist, skip
                    pass
            
            end_time = time.time()
            operation_time = end_time - start_time
            operations.append((operation_type, operation_time))
        
        total_time_end = time.time()
        total_duration = total_time_end - total_time_start
        
        # Analyze performance by operation type
        operation_stats = {}
        for op_type in ['search', 'insert', 'update']:
            op_times = [t for op, t in operations if op == op_type]
            if op_times:
                operation_stats[op_type] = {
                    'count': len(op_times),
                    'avg_time': statistics.mean(op_times),
                    'rate': len(op_times) / sum(op_times)
                }
        
        print(f"Mixed workload performance ({total_duration:.2f}s total):")
        for op_type, stats in operation_stats.items():
            print(f"  {op_type}: {stats['count']} ops, {stats['avg_time']:.4f}s avg, {stats['rate']:.0f} ops/sec")
        
        overall_rate = len(operations) / total_duration
        print(f"  Overall: {overall_rate:.0f} operations/sec")
        
        # Performance assertion
        assert overall_rate > 20, f"Mixed workload too slow: {overall_rate:.0f} ops/sec"


@pytest.mark.performance
@pytest.mark.asyncio
class TestAsyncPerformance:
    """Performance tests for asynchronous client."""
    
    async def test_concurrent_insertion_performance(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test concurrent insertion performance."""
        collection_name = async_clean_collection
        dimension = 256
        
        # Setup
        await async_client.create_collection_simple(collection_name, dimension, "cosine")
        
        # Generate test data
        num_vectors = 2000
        vectors_data = [
            (f"concurrent_vector_{i:05d}", 
             np.random.random(dimension), 
             {"batch": i // 100, "index": i})
            for i in range(num_vectors)
        ]
        
        # Test different concurrency levels
        concurrency_levels = [5, 10, 20]
        batch_sizes = [100, 200]
        
        for batch_size in batch_sizes:
            for max_concurrent in concurrency_levels:
                # Clean collection for each test
                try:
                    await async_client.delete_collection(f"{collection_name}_{batch_size}_{max_concurrent}")
                except:
                    pass
                
                test_collection = f"{collection_name}_{batch_size}_{max_concurrent}"
                await async_client.create_collection_simple(test_collection, dimension, "cosine")
                
                start_time = asyncio.get_event_loop().time()
                
                responses = await async_client.batch_insert_concurrent(
                    collection_name=test_collection,
                    vectors_data=vectors_data[:1000],  # Use subset for performance test
                    batch_size=batch_size,
                    max_concurrent_batches=max_concurrent
                )
                
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                
                total_inserted = sum(r.inserted_count or 0 for r in responses)
                rate = total_inserted / duration
                
                print(f"Batch size {batch_size}, concurrency {max_concurrent}: "
                      f"{total_inserted} vectors in {duration:.2f}s, {rate:.0f} vectors/sec")
                
                # Performance assertion
                assert rate > 200, f"Concurrent insertion too slow: {rate:.0f} vectors/sec"
                
                # Cleanup
                await async_client.delete_collection(test_collection)
    
    async def test_concurrent_search_performance(
        self, 
        async_client: AsyncVectorDBClient, 
        async_clean_collection: str
    ):
        """Test concurrent search performance."""
        collection_name = async_clean_collection
        dimension = 128
        
        # Setup collection with data
        await async_client.create_collection_simple(collection_name, dimension, "cosine")
        
        # Insert test data
        num_vectors = 1000
        vectors_data = [
            (f"search_perf_vector_{i:05d}", 
             np.random.random(dimension), 
             {"category": "performance_test"})
            for i in range(num_vectors)
        ]
        
        await async_client.batch_insert_concurrent(
            collection_name=collection_name,
            vectors_data=vectors_data,
            batch_size=200,
            max_concurrent_batches=5
        )
        
        # Generate query vectors
        num_queries = 200
        query_vectors = [
            np.random.random(dimension).astype(np.float32)
            for _ in range(num_queries)
        ]
        
        # Test concurrent search performance
        concurrency_levels = [10, 20, 50]
        
        for max_concurrent in concurrency_levels:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def search_with_semaphore(query_vector):
                async with semaphore:
                    return await async_client.search_simple(
                        collection_name, query_vector, limit=10
                    )
            
            start_time = asyncio.get_event_loop().time()
            
            tasks = [search_with_semaphore(qv) for qv in query_vectors]
            results = await asyncio.gather(*tasks)
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            search_rate = len(query_vectors) / duration
            
            print(f"Concurrent searches (max {max_concurrent}): "
                  f"{len(query_vectors)} queries in {duration:.2f}s, {search_rate:.0f} qps")
            
            # Verify all searches completed
            assert len(results) == num_queries
            for result_list in results:
                assert len(result_list) <= 10
            
            # Performance assertion
            assert search_rate > 100, f"Concurrent search too slow: {search_rate:.0f} qps"
    
    async def test_async_vs_sync_performance_comparison(self):
        """Compare async vs sync client performance."""
        dimension = 128
        num_operations = 100
        
        # Prepare test data
        np.random.seed(1337)
        vectors_data = [
            (f"comparison_vector_{i:03d}", np.random.random(dimension), {"test": "comparison"})
            for i in range(num_operations)
        ]
        
        query_vectors = [np.random.random(dimension) for _ in range(num_operations)]
        
        collection_name = "performance_comparison"
        
        # Test sync performance
        sync_client = VectorDBClient()
        if sync_client.ping():
            try:
                sync_client.delete_collection(collection_name)
            except:
                pass
            
            sync_client.create_collection_simple(collection_name, dimension, "cosine")
            
            # Sync insertion timing
            sync_insert_start = time.time()
            for vector_id, vector_data, metadata in vectors_data:
                sync_client.insert_simple(collection_name, vector_id, vector_data, metadata)
            sync_insert_end = time.time()
            sync_insert_time = sync_insert_end - sync_insert_start
            
            # Sync search timing
            sync_search_start = time.time()
            for query_vector in query_vectors:
                sync_client.search_simple(collection_name, query_vector, limit=5)
            sync_search_end = time.time()
            sync_search_time = sync_search_end - sync_search_start
            
            sync_client.delete_collection(collection_name)
            sync_client.close()
        else:
            pytest.skip("Sync client not available for performance comparison")
        
        # Test async performance
        async with AsyncVectorDBClient() as async_client:
            if not await async_client.ping():
                pytest.skip("Async client not available for performance comparison")
            
            try:
                await async_client.delete_collection(collection_name)
            except:
                pass
            
            await async_client.create_collection_simple(collection_name, dimension, "cosine")
            
            # Async concurrent insertion timing
            async_insert_start = asyncio.get_event_loop().time()
            await async_client.batch_insert_concurrent(
                collection_name=collection_name,
                vectors_data=vectors_data,
                batch_size=25,
                max_concurrent_batches=8
            )
            async_insert_end = asyncio.get_event_loop().time()
            async_insert_time = async_insert_end - async_insert_start
            
            # Async concurrent search timing
            async_search_start = asyncio.get_event_loop().time()
            search_tasks = [
                async_client.search_simple(collection_name, qv, limit=5)
                for qv in query_vectors
            ]
            await asyncio.gather(*search_tasks)
            async_search_end = asyncio.get_event_loop().time()
            async_search_time = async_search_end - async_search_start
            
            await async_client.delete_collection(collection_name)
        
        # Performance comparison
        insert_speedup = sync_insert_time / async_insert_time
        search_speedup = sync_search_time / async_search_time
        
        print(f"Performance Comparison ({num_operations} operations):")
        print(f"  Insertion - Sync: {sync_insert_time:.2f}s, Async: {async_insert_time:.2f}s, "
              f"Speedup: {insert_speedup:.1f}x")
        print(f"  Search - Sync: {sync_search_time:.2f}s, Async: {async_search_time:.2f}s, "
              f"Speedup: {search_speedup:.1f}x")
        
        # Async should be faster for concurrent operations
        assert async_insert_time < sync_insert_time, "Async insertion should be faster"
        assert async_search_time < sync_search_time, "Async search should be faster"


@pytest.mark.performance
class TestScalabilityBenchmarks:
    """Scalability benchmarks for different workload sizes."""
    
    def test_vector_count_scaling(self, client: VectorDBClient, clean_collection: str):
        """Test how performance scales with vector count."""
        collection_name = clean_collection
        dimension = 128
        
        # Setup
        client.create_collection_simple(collection_name, dimension, "cosine")
        
        vector_counts = [100, 500, 1000, 2000]
        search_times = []
        
        for count in vector_counts:
            # Insert vectors
            vectors = generate_random_vectors(count, dimension, seed=count)
            
            # Clear collection and insert fresh data
            client.delete_collection(collection_name)
            client.create_collection_simple(collection_name, dimension, "cosine")
            
            # Batch insert for faster setup
            batch_size = 200
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                client.insert_vectors(collection_name, batch)
            
            # Measure search performance
            query_vector = np.random.random(dimension)
            
            # Warm up
            client.search_simple(collection_name, query_vector, limit=10)
            
            # Timed search
            start_time = time.time()
            results = client.search_simple(collection_name, query_vector, limit=10)
            end_time = time.time()
            
            search_time = end_time - start_time
            search_times.append(search_time)
            
            print(f"Vector count {count}: search time {search_time:.4f}s")
            assert len(results) <= 10
        
        # Analyze scaling behavior
        print(f"Search time scaling: {[f'{t:.4f}s' for t in search_times]}")
        
        # Search time should scale sub-linearly for HNSW index
        if len(search_times) >= 2:
            scaling_factor = search_times[-1] / search_times[0]
            vector_scaling = vector_counts[-1] / vector_counts[0]
            
            print(f"Search time scaling factor: {scaling_factor:.2f}x for {vector_scaling:.0f}x vectors")
            
            # HNSW should scale logarithmically, so scaling should be much less than linear
            assert scaling_factor < vector_scaling * 0.5, "Search scaling should be sub-linear"
    
    def test_dimension_scaling(self, client: VectorDBClient):
        """Test how performance scales with vector dimension."""
        dimensions = [64, 128, 256, 512]
        insertion_times = []
        search_times = []
        
        num_vectors = 200
        
        for dimension in dimensions:
            collection_name = f"dim_scaling_{dimension}"
            
            # Clean up
            try:
                client.delete_collection(collection_name)
            except:
                pass
            
            # Setup collection
            client.create_collection_simple(collection_name, dimension, "cosine")
            
            # Generate vectors
            vectors = generate_random_vectors(num_vectors, dimension, seed=dimension)
            
            # Measure insertion time
            start_time = time.time()
            client.insert_vectors(collection_name, vectors)
            end_time = time.time()
            
            insertion_time = end_time - start_time
            insertion_times.append(insertion_time)
            
            # Measure search time
            query_vector = np.random.random(dimension)
            
            start_time = time.time()
            results = client.search_simple(collection_name, query_vector, limit=10)
            end_time = time.time()
            
            search_time = end_time - start_time
            search_times.append(search_time)
            
            print(f"Dimension {dimension}: insertion {insertion_time:.3f}s, search {search_time:.4f}s")
            
            # Cleanup
            client.delete_collection(collection_name)
        
        # Analyze dimension scaling
        print(f"Insertion time by dimension: {[f'{t:.3f}s' for t in insertion_times]}")
        print(f"Search time by dimension: {[f'{t:.4f}s' for t in search_times]}")
        
        # Both insertion and search should scale with dimension
        assert all(t > 0 for t in insertion_times), "All insertion times should be positive"
        assert all(t > 0 for t in search_times), "All search times should be positive"


@pytest.mark.performance
class TestMemoryBenchmarks:
    """Memory usage and efficiency benchmarks."""
    
    def test_memory_usage_scaling(self, client: VectorDBClient, clean_collection: str):
        """Test memory usage scaling with vector count."""
        collection_name = clean_collection
        dimension = 256
        
        # Setup
        client.create_collection_simple(collection_name, dimension, "cosine")
        
        batch_sizes = [100, 200, 500, 1000]
        memory_usage = []
        
        for batch_size in batch_sizes:
            # Insert vectors
            vectors = generate_random_vectors(batch_size, dimension, seed=12345)
            client.insert_vectors(collection_name, vectors)
            
            # Measure memory usage
            stats = client.get_collection_stats(collection_name)
            memory_usage.append(stats.memory_usage)
            
            print(f"Vectors: {stats.vector_count}, Memory: {stats.memory_usage:,} bytes "
                  f"({stats.memory_usage / 1024 / 1024:.1f} MB)")
        
        # Analyze memory scaling
        print(f"Memory usage scaling: {[f'{m:,}' for m in memory_usage]}")
        
        # Memory should scale roughly linearly with vector count
        assert all(m > 0 for m in memory_usage), "Memory usage should be positive"
        assert memory_usage[-1] > memory_usage[0], "Memory should increase with vector count"
    
    def test_index_vs_data_memory_ratio(self, client: VectorDBClient, clean_collection: str):
        """Test ratio of index size to data size."""
        collection_name = clean_collection
        dimension = 128
        num_vectors = 1000
        
        # Setup
        client.create_collection_simple(collection_name, dimension, "cosine")
        
        # Insert vectors
        vectors = generate_random_vectors(num_vectors, dimension, seed=54321)
        client.insert_vectors(collection_name, vectors)
        
        # Get memory statistics
        stats = client.get_collection_stats(collection_name)
        
        # Calculate data size (approximate)
        vector_data_size = num_vectors * dimension * 4  # 4 bytes per float32
        
        print(f"Collection stats:")
        print(f"  Vector count: {stats.vector_count:,}")
        print(f"  Total memory: {stats.memory_usage:,} bytes ({stats.memory_usage / 1024 / 1024:.1f} MB)")
        print(f"  Index size: {stats.index_size:,} bytes ({stats.index_size / 1024 / 1024:.1f} MB)")
        print(f"  Estimated data size: {vector_data_size:,} bytes ({vector_data_size / 1024 / 1024:.1f} MB)")
        
        if stats.index_size > 0:
            index_data_ratio = stats.index_size / vector_data_size
            print(f"  Index/Data ratio: {index_data_ratio:.2f}")
            
            # HNSW index should be reasonable size relative to data
            assert index_data_ratio < 5.0, f"Index too large relative to data: {index_data_ratio:.2f}"
        
        memory_per_vector = stats.memory_usage / stats.vector_count
        print(f"  Memory per vector: {memory_per_vector:.0f} bytes")
        
        # Memory per vector should be reasonable
        expected_min = dimension * 4  # At least the vector data size
        assert memory_per_vector >= expected_min, f"Memory per vector too small: {memory_per_vector:.0f}"


if __name__ == "__main__":
    # Run performance tests directly
    pytest.main([
        __file__,
        "-v",
        "-m", "performance",
        "--tb=short"
    ])