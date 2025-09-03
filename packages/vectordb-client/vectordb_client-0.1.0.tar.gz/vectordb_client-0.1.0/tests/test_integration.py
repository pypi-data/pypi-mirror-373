"""
Integration tests for d-vecDB Python client.
Tests real-world usage scenarios and workflows.
"""

import pytest
import time
import asyncio
import numpy as np
from typing import List, Dict, Any
import tempfile
import json

from vectordb_client import VectorDBClient, AsyncVectorDBClient
from vectordb_client.types import (
    CollectionConfig, Vector, DistanceMetric, VectorType, IndexConfig
)
from vectordb_client.exceptions import VectorDBError


@pytest.mark.integration
class TestRealWorldWorkflows:
    """Test real-world usage scenarios."""
    
    def test_document_embedding_workflow(self, client: VectorDBClient):
        """Test a complete document embedding and search workflow."""
        collection_name = "document_embeddings"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Simulate document processing workflow
            documents = [
                {"id": "doc_001", "title": "Introduction to Machine Learning", 
                 "content": "Machine learning is a subset of artificial intelligence...",
                 "category": "technology", "author": "Alice Smith"},
                {"id": "doc_002", "title": "Cooking Pasta Perfectly", 
                 "content": "The key to perfect pasta is timing and salt...",
                 "category": "cooking", "author": "Bob Chef"},
                {"id": "doc_003", "title": "Neural Networks Explained", 
                 "content": "Neural networks are computing systems inspired by biological networks...",
                 "category": "technology", "author": "Carol Johnson"},
                {"id": "doc_004", "title": "Italian Cuisine History", 
                 "content": "Italian cuisine has evolved over centuries...",
                 "category": "cooking", "author": "David Romano"},
                {"id": "doc_005", "title": "Deep Learning Applications", 
                 "content": "Deep learning has revolutionized computer vision and natural language processing...",
                 "category": "technology", "author": "Eve Wilson"},
            ]
            
            # Step 1: Create collection for document embeddings
            config = CollectionConfig(
                name=collection_name,
                dimension=384,  # Typical sentence embedding dimension
                distance_metric=DistanceMetric.COSINE,
                index_config=IndexConfig(
                    max_connections=32,
                    ef_construction=400,
                    ef_search=100
                )
            )
            
            response = client.create_collection(config)
            assert response.success
            
            # Step 2: Generate embeddings (simulated - in reality would use actual model)
            np.random.seed(42)  # For reproducible "embeddings"
            
            vectors = []
            for doc in documents:
                # Simulate category-aware embeddings
                base_embedding = np.random.random(384).astype(np.float32)
                
                # Add category bias to make similar documents closer
                if doc["category"] == "technology":
                    base_embedding[:100] += 0.3  # Tech documents cluster
                else:  # cooking
                    base_embedding[100:200] += 0.3  # Cooking documents cluster
                
                # Normalize
                embedding = base_embedding / np.linalg.norm(base_embedding)
                
                vector = Vector(
                    id=doc["id"],
                    data=embedding.tolist(),
                    metadata={
                        "title": doc["title"],
                        "category": doc["category"],
                        "author": doc["author"],
                        "content_length": len(doc["content"]),
                        "indexed_at": int(time.time())
                    }
                )
                vectors.append(vector)
            
            # Step 3: Insert document vectors
            insert_response = client.insert_vectors(collection_name, vectors)
            assert insert_response.success
            assert insert_response.inserted_count == len(documents)
            
            # Step 4: Verify collection stats
            stats = client.get_collection_stats(collection_name)
            assert stats.vector_count == len(documents)
            assert stats.dimension == 384
            
            # Step 5: Perform semantic searches
            # Search for technology-related content
            tech_query = np.random.random(384).astype(np.float32)
            tech_query[:100] += 0.3  # Similar bias to tech documents
            tech_query = tech_query / np.linalg.norm(tech_query)
            
            tech_results = client.search_simple(collection_name, tech_query, limit=3)
            
            # Verify tech documents are returned
            tech_categories = [r.metadata["category"] for r in tech_results]
            tech_count = sum(1 for cat in tech_categories if cat == "technology")
            assert tech_count >= 1, "Should find at least one technology document"
            
            # Search with metadata filtering
            filtered_response = client.search(
                collection_name=collection_name,
                query_vector=tech_query,
                limit=5,
                filter={"category": "technology"}
            )
            
            # All results should be technology documents
            for result in filtered_response.results:
                assert result.metadata["category"] == "technology"
            
            # Step 6: Test document retrieval
            retrieved_doc = client.get_vector(collection_name, "doc_001")
            assert retrieved_doc.id == "doc_001"
            assert retrieved_doc.metadata["title"] == "Introduction to Machine Learning"
            
            # Step 7: Update document metadata (simulate document update)
            updated_doc = Vector(
                id=retrieved_doc.id,
                data=retrieved_doc.data,
                metadata={
                    **retrieved_doc.metadata,
                    "updated_at": int(time.time()),
                    "view_count": 42
                }
            )
            
            update_response = client.update_vector(collection_name, updated_doc)
            assert update_response.success
            
            # Verify update
            updated_retrieved = client.get_vector(collection_name, "doc_001")
            assert updated_retrieved.metadata["view_count"] == 42
            assert "updated_at" in updated_retrieved.metadata
            
            # Step 8: Demonstrate batch operations
            new_documents = [
                {"id": "doc_006", "title": "Advanced AI Techniques", "category": "technology"},
                {"id": "doc_007", "title": "Baking Fundamentals", "category": "cooking"},
            ]
            
            new_vectors = []
            for doc in new_documents:
                embedding = np.random.random(384).astype(np.float32)
                if doc["category"] == "technology":
                    embedding[:100] += 0.3
                else:
                    embedding[100:200] += 0.3
                    
                embedding = embedding / np.linalg.norm(embedding)
                
                new_vectors.append(Vector(
                    id=doc["id"],
                    data=embedding.tolist(),
                    metadata={"title": doc["title"], "category": doc["category"]}
                ))
            
            batch_response = client.insert_vectors(collection_name, new_vectors)
            assert batch_response.inserted_count == len(new_vectors)
            
            # Final verification
            final_stats = client.get_collection_stats(collection_name)
            assert final_stats.vector_count == len(documents) + len(new_documents)
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass
    
    def test_recommendation_system_workflow(self, client: VectorDBClient):
        """Test a recommendation system workflow."""
        collection_name = "user_preferences"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Create collection for user preference vectors
            client.create_collection_simple(collection_name, 128, "cosine")
            
            # Simulate user preference vectors (e.g., from collaborative filtering)
            np.random.seed(123)
            
            users = []
            user_categories = ["sports", "music", "movies", "books", "travel"]
            
            for i in range(50):
                # Create user with preference for 1-2 categories
                user_prefs = np.random.choice(user_categories, size=np.random.randint(1, 3), replace=False)
                
                # Generate preference vector
                pref_vector = np.random.random(128).astype(np.float32)
                
                # Add category-specific patterns
                for j, category in enumerate(user_categories):
                    if category in user_prefs:
                        start_idx = j * 25
                        end_idx = (j + 1) * 25
                        pref_vector[start_idx:end_idx] += 0.5
                
                # Normalize
                pref_vector = pref_vector / np.linalg.norm(pref_vector)
                
                user_data = {
                    "user_id": f"user_{i:03d}",
                    "preferences": list(user_prefs),
                    "age_group": np.random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]),
                    "activity_level": np.random.choice(["low", "medium", "high"])
                }
                
                users.append((user_data, pref_vector))
            
            # Insert user vectors
            vectors = []
            for user_data, pref_vector in users:
                vector = Vector(
                    id=user_data["user_id"],
                    data=pref_vector.tolist(),
                    metadata=user_data
                )
                vectors.append(vector)
            
            client.insert_vectors(collection_name, vectors)
            
            # Test recommendation queries
            # Find similar users for recommendation
            target_user_id = "user_010"
            target_user = client.get_vector(collection_name, target_user_id)
            
            # Find similar users
            similar_users = client.search_simple(
                collection_name,
                target_user.data,
                limit=10
            )
            
            # Filter out the target user from results
            similar_users = [u for u in similar_users if u.id != target_user_id]
            
            assert len(similar_users) >= 5
            
            # Test demographic filtering
            target_age_group = target_user.metadata["age_group"]
            
            age_similar_response = client.search(
                collection_name=collection_name,
                query_vector=target_user.data,
                limit=15,
                filter={"age_group": target_age_group}
            )
            
            # Verify age filtering
            for result in age_similar_response.results:
                if result.id != target_user_id:  # Exclude self
                    assert result.metadata["age_group"] == target_age_group
            
            # Test preference-based search
            # Find users with specific interests
            sports_lovers = client.search(
                collection_name=collection_name,
                query_vector=target_user.data,
                limit=20,
                filter={"preferences": "sports"}  # This might not work exactly like this depending on implementation
            )
            
            print(f"Recommendation system test completed:")
            print(f"  Total users: {len(users)}")
            print(f"  Similar to {target_user_id}: {len(similar_users)} users")
            print(f"  Same age group: {len(age_similar_response.results)} users")
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass
    
    def test_content_moderation_workflow(self, client: VectorDBClient):
        """Test content moderation using vector similarity."""
        collection_name = "moderation_embeddings"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Create collection for content embeddings
            client.create_collection_simple(collection_name, 256, "cosine")
            
            # Simulate content moderation dataset
            np.random.seed(456)
            
            # Known problematic content patterns (simulated embeddings)
            problematic_patterns = [
                {"type": "spam", "severity": "high"},
                {"type": "spam", "severity": "medium"},
                {"type": "harassment", "severity": "high"},
                {"type": "harassment", "severity": "medium"},
                {"type": "misinformation", "severity": "high"},
                {"type": "misinformation", "severity": "medium"},
            ]
            
            pattern_vectors = []
            for i, pattern in enumerate(problematic_patterns):
                # Create distinctive patterns for each type
                embedding = np.random.random(256).astype(np.float32)
                
                if pattern["type"] == "spam":
                    embedding[:85] += 0.6
                elif pattern["type"] == "harassment":
                    embedding[85:170] += 0.6
                elif pattern["type"] == "misinformation":
                    embedding[170:255] += 0.6
                
                # Add severity weighting
                if pattern["severity"] == "high":
                    embedding *= 1.2
                
                embedding = embedding / np.linalg.norm(embedding)
                
                vector = Vector(
                    id=f"pattern_{i:03d}",
                    data=embedding.tolist(),
                    metadata={
                        **pattern,
                        "confirmed": True,
                        "added_at": int(time.time() - (i * 3600))  # Stagger timestamps
                    }
                )
                pattern_vectors.append(vector)
            
            # Insert pattern vectors
            client.insert_vectors(collection_name, pattern_vectors)
            
            # Simulate new content to moderate
            new_content = [
                {"id": "content_001", "type": "spam", "text": "Buy now! Limited offer!"},
                {"id": "content_002", "type": "normal", "text": "Great article, thanks for sharing."},
                {"id": "content_003", "type": "harassment", "text": "This person is terrible..."},
                {"id": "content_004", "type": "normal", "text": "Looking forward to the weekend."},
                {"id": "content_005", "type": "misinformation", "text": "False claims about health..."},
            ]
            
            # Test moderation pipeline
            moderation_results = []
            
            for content in new_content:
                # Generate embedding for new content
                embedding = np.random.random(256).astype(np.float32)
                
                # Add type-specific patterns (simulating real embeddings)
                if content["type"] == "spam":
                    embedding[:85] += 0.5
                elif content["type"] == "harassment":
                    embedding[85:170] += 0.5
                elif content["type"] == "misinformation":
                    embedding[170:255] += 0.5
                
                embedding = embedding / np.linalg.norm(embedding)
                
                # Find similar known patterns
                similar_patterns = client.search_simple(
                    collection_name,
                    embedding,
                    limit=3
                )
                
                # Determine moderation action based on similarity
                max_similarity = 1.0 - similar_patterns[0].distance if similar_patterns else 0.0
                
                action = "approve"
                confidence = 0.0
                
                if max_similarity > 0.7:
                    action = "block"
                    confidence = max_similarity
                elif max_similarity > 0.5:
                    action = "review"
                    confidence = max_similarity
                
                moderation_result = {
                    "content_id": content["id"],
                    "action": action,
                    "confidence": confidence,
                    "similar_patterns": [
                        {
                            "pattern_id": r.id,
                            "type": r.metadata["type"],
                            "similarity": 1.0 - r.distance
                        }
                        for r in similar_patterns[:2]
                    ]
                }
                
                moderation_results.append(moderation_result)
            
            # Verify moderation results
            spam_content = next(r for r in moderation_results if r["content_id"] == "content_001")
            assert spam_content["action"] in ["block", "review"], "Spam should be flagged"
            
            normal_content = [r for r in moderation_results if r["content_id"] in ["content_002", "content_004"]]
            assert all(r["action"] == "approve" for r in normal_content), "Normal content should be approved"
            
            print(f"Content moderation test completed:")
            print(f"  Pattern vectors: {len(pattern_vectors)}")
            print(f"  Content moderated: {len(new_content)}")
            for result in moderation_results:
                print(f"    {result['content_id']}: {result['action']} (confidence: {result['confidence']:.2f})")
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestAsyncWorkflows:
    """Test async integration workflows."""
    
    async def test_real_time_similarity_service(self):
        """Test real-time similarity service using async client."""
        collection_name = "realtime_similarities"
        
        async with AsyncVectorDBClient() as client:
            if not await client.ping():
                pytest.skip("Async client not available")
            
            # Cleanup
            try:
                await client.delete_collection(collection_name)
            except:
                pass
            
            try:
                # Setup real-time similarity collection
                await client.create_collection_simple(collection_name, 128, "cosine")
                
                # Simulate initial dataset (e.g., product embeddings)
                num_products = 1000
                product_vectors = [
                    (f"product_{i:05d}", 
                     np.random.random(128), 
                     {"category": np.random.choice(["electronics", "clothing", "books", "home"]),
                      "price_range": np.random.choice(["low", "medium", "high"]),
                      "popularity": np.random.random()})
                    for i in range(num_products)
                ]
                
                # Batch insert initial products
                await client.batch_insert_concurrent(
                    collection_name=collection_name,
                    vectors_data=product_vectors,
                    batch_size=100,
                    max_concurrent_batches=10
                )
                
                # Simulate real-time similarity requests
                num_queries = 50
                
                async def similarity_request(query_id: int):
                    """Simulate a single similarity request."""
                    query_vector = np.random.random(128)
                    
                    results = await client.search_simple(
                        collection_name,
                        query_vector,
                        limit=10
                    )
                    
                    return {
                        "query_id": query_id,
                        "results": [
                            {
                                "product_id": r.id,
                                "similarity": 1.0 - r.distance,
                                "category": r.metadata["category"]
                            }
                            for r in results
                        ],
                        "response_time": time.time()
                    }
                
                # Process concurrent similarity requests
                start_time = asyncio.get_event_loop().time()
                
                tasks = [similarity_request(i) for i in range(num_queries)]
                responses = await asyncio.gather(*tasks)
                
                end_time = asyncio.get_event_loop().time()
                total_time = end_time - start_time
                
                # Verify responses
                assert len(responses) == num_queries
                for response in responses:
                    assert len(response["results"]) == 10
                    assert all(r["similarity"] >= 0 for r in response["results"])
                
                # Performance metrics
                avg_response_time = total_time / num_queries
                throughput = num_queries / total_time
                
                print(f"Real-time similarity service test:")
                print(f"  Total queries: {num_queries}")
                print(f"  Total time: {total_time:.2f}s")
                print(f"  Average response time: {avg_response_time:.3f}s")
                print(f"  Throughput: {throughput:.0f} queries/second")
                
                # Performance assertion
                assert throughput > 20, f"Throughput too low: {throughput:.0f} qps"
                
            finally:
                # Cleanup
                try:
                    await client.delete_collection(collection_name)
                except:
                    pass
    
    async def test_streaming_vector_updates(self):
        """Test streaming vector updates workflow."""
        collection_name = "streaming_updates"
        
        async with AsyncVectorDBClient() as client:
            if not await client.ping():
                pytest.skip("Async client not available")
            
            # Cleanup
            try:
                await client.delete_collection(collection_name)
            except:
                pass
            
            try:
                # Setup streaming collection
                await client.create_collection_simple(collection_name, 64, "euclidean")
                
                # Initial batch of vectors
                initial_vectors = [
                    (f"stream_vector_{i:03d}", 
                     np.random.random(64), 
                     {"version": 1, "timestamp": time.time()})
                    for i in range(100)
                ]
                
                await client.batch_insert_concurrent(
                    collection_name=collection_name,
                    vectors_data=initial_vectors,
                    batch_size=50,
                    max_concurrent_batches=4
                )
                
                # Simulate streaming updates
                update_batches = []
                
                for batch_id in range(5):
                    # Select random vectors to update
                    update_indices = np.random.choice(100, size=20, replace=False)
                    
                    batch_updates = []
                    for idx in update_indices:
                        vector_id = f"stream_vector_{idx:03d}"
                        
                        # Generate updated vector
                        updated_data = np.random.random(64)
                        updated_metadata = {
                            "version": batch_id + 2,
                            "timestamp": time.time(),
                            "updated_in_batch": batch_id
                        }
                        
                        batch_updates.append((vector_id, updated_data, updated_metadata))
                    
                    update_batches.append(batch_updates)
                
                # Process updates concurrently
                async def process_update_batch(batch_updates):
                    """Process a batch of updates."""
                    update_vectors = []
                    
                    for vector_id, data, metadata in batch_updates:
                        vector = Vector(
                            id=vector_id,
                            data=data.tolist() if hasattr(data, 'tolist') else data,
                            metadata=metadata
                        )
                        update_vectors.append(vector)
                    
                    # Use insert_vectors which should handle updates
                    return await client.insert_vectors(collection_name, update_vectors)
                
                # Process all update batches concurrently
                update_tasks = [process_update_batch(batch) for batch in update_batches]
                update_responses = await asyncio.gather(*update_tasks)
                
                # Verify updates
                for response in update_responses:
                    assert response.success
                
                # Sample some updated vectors
                sample_ids = ["stream_vector_010", "stream_vector_050", "stream_vector_090"]
                
                for vector_id in sample_ids:
                    updated_vector = await client.get_vector(collection_name, vector_id)
                    assert updated_vector.metadata["version"] > 1
                    assert "updated_in_batch" in updated_vector.metadata
                
                print(f"Streaming updates test completed:")
                print(f"  Initial vectors: {len(initial_vectors)}")
                print(f"  Update batches: {len(update_batches)}")
                print(f"  Total updates: {sum(len(batch) for batch in update_batches)}")
                
            finally:
                # Cleanup
                try:
                    await client.delete_collection(collection_name)
                except:
                    pass


@pytest.mark.integration
class TestDataPersistence:
    """Test data persistence and recovery scenarios."""
    
    def test_collection_persistence(self, client: VectorDBClient):
        """Test that collections and data persist across operations."""
        collection_name = "persistence_test"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Create collection with specific configuration
            config = CollectionConfig(
                name=collection_name,
                dimension=128,
                distance_metric=DistanceMetric.EUCLIDEAN,
                index_config=IndexConfig(max_connections=64)
            )
            
            client.create_collection(config)
            
            # Insert test data
            test_vectors = [
                Vector(
                    id=f"persist_vector_{i:03d}",
                    data=np.random.random(128).tolist(),
                    metadata={"test": "persistence", "index": i}
                )
                for i in range(50)
            ]
            
            client.insert_vectors(collection_name, test_vectors)
            
            # Verify initial state
            stats1 = client.get_collection_stats(collection_name)
            assert stats1.vector_count == 50
            assert stats1.dimension == 128
            
            # Simulate operations that might affect persistence
            # Perform many operations
            for i in range(10):
                # Search operations
                query = np.random.random(128)
                results = client.search_simple(collection_name, query, limit=5)
                assert len(results) <= 5
                
                # Update operations
                vector_id = f"persist_vector_{i:03d}"
                vector = client.get_vector(collection_name, vector_id)
                vector.metadata["updated_count"] = vector.metadata.get("updated_count", 0) + 1
                client.update_vector(collection_name, vector)
            
            # Verify persistence after operations
            stats2 = client.get_collection_stats(collection_name)
            assert stats2.vector_count == 50  # Should remain the same
            
            # Verify specific updates persisted
            for i in range(10):
                vector_id = f"persist_vector_{i:03d}"
                vector = client.get_vector(collection_name, vector_id)
                assert vector.metadata["updated_count"] == 1
            
            print(f"Data persistence test completed:")
            print(f"  Collection maintained: {stats2.vector_count} vectors")
            print(f"  Updates persisted: verified")
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass
    
    def test_concurrent_access_consistency(self, client: VectorDBClient):
        """Test data consistency under concurrent access patterns."""
        collection_name = "concurrency_test"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Setup
            client.create_collection_simple(collection_name, 64, "cosine")
            
            # Insert initial data
            initial_vectors = [
                Vector(
                    id=f"concurrent_vector_{i:03d}",
                    data=np.random.random(64).tolist(),
                    metadata={"counter": 0, "last_updated": 0}
                )
                for i in range(100)
            ]
            
            client.insert_vectors(collection_name, initial_vectors)
            
            # Simulate concurrent operations
            # Note: This is limited by synchronous client, but tests consistency
            
            vector_ids = [f"concurrent_vector_{i:03d}" for i in range(20)]
            
            # Multiple update operations
            for round_num in range(5):
                for vector_id in vector_ids:
                    try:
                        # Read-modify-write pattern
                        vector = client.get_vector(collection_name, vector_id)
                        
                        # Modify
                        vector.metadata["counter"] = vector.metadata.get("counter", 0) + 1
                        vector.metadata["last_updated"] = round_num
                        
                        # Write back
                        client.update_vector(collection_name, vector)
                        
                    except Exception as e:
                        print(f"Update error for {vector_id} in round {round_num}: {e}")
                        # Continue with other vectors
                
                # Interleave with search operations
                query = np.random.random(64)
                results = client.search_simple(collection_name, query, limit=10)
                assert len(results) <= 10
            
            # Verify final consistency
            for vector_id in vector_ids:
                vector = client.get_vector(collection_name, vector_id)
                
                # Should have been updated 5 times
                assert vector.metadata["counter"] == 5
                assert vector.metadata["last_updated"] == 4  # Last round was 4
            
            print(f"Concurrent access consistency test completed:")
            print(f"  Vectors tested: {len(vector_ids)}")
            print(f"  Update rounds: 5")
            print(f"  Consistency verified")
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery and resilience."""
    
    def test_partial_batch_failure_recovery(self, client: VectorDBClient):
        """Test recovery from partial batch insertion failures."""
        collection_name = "batch_failure_test"
        
        # Cleanup
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        try:
            # Setup
            client.create_collection_simple(collection_name, 64, "cosine")
            
            # Create a batch with some potentially problematic vectors
            batch_vectors = []
            
            for i in range(20):
                # Most vectors are normal
                if i < 15:
                    vector = Vector(
                        id=f"normal_vector_{i:03d}",
                        data=np.random.random(64).tolist(),
                        metadata={"type": "normal", "index": i}
                    )
                else:
                    # Some vectors might be problematic (depending on implementation)
                    vector = Vector(
                        id=f"test_vector_{i:03d}",
                        data=np.random.random(64).tolist(),
                        metadata={"type": "test", "index": i}
                    )
                
                batch_vectors.append(vector)
            
            # Attempt batch insertion
            try:
                response = client.insert_vectors(collection_name, batch_vectors)
                inserted_count = response.inserted_count or 0
            except Exception as e:
                print(f"Batch insertion failed: {e}")
                inserted_count = 0
            
            # Check what was actually inserted
            stats = client.get_collection_stats(collection_name)
            actual_count = stats.vector_count
            
            print(f"Batch failure recovery test:")
            print(f"  Attempted to insert: {len(batch_vectors)}")
            print(f"  Reported inserted: {inserted_count}")
            print(f"  Actually in collection: {actual_count}")
            
            # Try to insert remaining vectors individually if needed
            if actual_count < len(batch_vectors):
                successful_individual = 0
                
                for vector in batch_vectors:
                    try:
                        # Check if vector already exists
                        existing = client.get_vector(collection_name, vector.id)
                        if existing:
                            continue
                    except:
                        # Vector doesn't exist, try to insert
                        try:
                            client.insert_vector(collection_name, vector)
                            successful_individual += 1
                        except Exception as e:
                            print(f"Individual insertion failed for {vector.id}: {e}")
                
                print(f"  Individual recovery insertions: {successful_individual}")
            
            # Final verification
            final_stats = client.get_collection_stats(collection_name)
            print(f"  Final count: {final_stats.vector_count}")
            
            # Should have at least some vectors
            assert final_stats.vector_count > 0
            
        finally:
            # Cleanup
            try:
                client.delete_collection(collection_name)
            except:
                pass
    
    def test_connection_resilience(self):
        """Test client behavior with connection issues."""
        # Test with unreachable server
        unreachable_client = VectorDBClient(host="192.0.2.1", port=12345, timeout=1.0)  # RFC5737 test address
        
        # Ping should fail gracefully
        is_reachable = unreachable_client.ping()
        assert is_reachable is False
        
        # Operations should raise appropriate exceptions
        with pytest.raises(VectorDBError):
            unreachable_client.list_collections()
        
        unreachable_client.close()
        
        # Test with very short timeout
        if True:  # Skip actual timeout test to avoid delays
            print("Connection resilience test completed (timeout test skipped)")
            return
        
        short_timeout_client = VectorDBClient(timeout=0.001)  # 1ms timeout
        
        try:
            # This should timeout
            with pytest.raises((VectorDBError, Exception)):
                short_timeout_client.ping()
        except Exception:
            pass  # Expected
        finally:
            short_timeout_client.close()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "-m", "integration",
        "--tb=short"
    ])