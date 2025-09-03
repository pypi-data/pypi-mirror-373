"""
Pytest configuration and fixtures for d-vecDB client tests with embedded server support.
This version automatically starts and stops the d-vecDB server using the d-vecdb-server package.
"""

import pytest
import asyncio
import numpy as np
from typing import Generator, AsyncGenerator
import os
import time
import socket
import sys

from vectordb_client import VectorDBClient, AsyncVectorDBClient
from vectordb_client.types import CollectionConfig, Vector, DistanceMetric

# Try to import the server package
try:
    from d_vecdb_server import DVecDBServer
    EMBEDDED_SERVER_AVAILABLE = True
except ImportError:
    EMBEDDED_SERVER_AVAILABLE = False
    DVecDBServer = None

# Test configuration
TEST_HOST = os.getenv("VECTORDB_TEST_HOST", "localhost")
TEST_PORT = int(os.getenv("VECTORDB_TEST_PORT", "8080"))
TEST_GRPC_PORT = int(os.getenv("VECTORDB_TEST_GRPC_PORT", "9090"))

# Server management configuration
USE_EMBEDDED_SERVER = os.getenv("VECTORDB_USE_EMBEDDED_SERVER", "true").lower() == "true"
AUTO_START_SERVER = os.getenv("VECTORDB_AUTO_START_SERVER", "true").lower() == "true"


def find_free_port(start_port: int = 8080) -> int:
    """Find a free port starting from the given port."""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result != 0:
                return port
    raise RuntimeError("No free ports found")


@pytest.fixture(scope="session")
def server_ports():
    """Allocate free ports for testing."""
    if USE_EMBEDDED_SERVER and EMBEDDED_SERVER_AVAILABLE:
        rest_port = find_free_port(8080)
        grpc_port = find_free_port(9090)
        return {"rest_port": rest_port, "grpc_port": grpc_port}
    else:
        return {"rest_port": TEST_PORT, "grpc_port": TEST_GRPC_PORT}


@pytest.fixture(scope="session")
def vectordb_server(server_ports):
    """
    Session-scoped fixture that manages the d-vecDB server lifecycle.
    
    This fixture will:
    1. Check if embedded server is available and configured to be used
    2. Start the server if AUTO_START_SERVER is enabled
    3. Yield the server instance or None
    4. Clean up the server at the end of the test session
    """
    server = None
    
    if USE_EMBEDDED_SERVER and EMBEDDED_SERVER_AVAILABLE and AUTO_START_SERVER:
        try:
            print(f"\n🚀 Starting embedded d-vecDB server...")
            server = DVecDBServer(
                host=TEST_HOST,
                port=server_ports["rest_port"],
                grpc_port=server_ports["grpc_port"]
            )
            
            # Start the server
            if server.start(background=True, timeout=30):
                print(f"✅ Server started on ports {server_ports['rest_port']} (REST) / {server_ports['grpc_port']} (gRPC)")
                # Wait a bit for server to fully initialize
                time.sleep(2)
            else:
                print("❌ Failed to start embedded server")
                server = None
                
        except Exception as e:
            print(f"❌ Error starting embedded server: {e}")
            server = None
    
    # Yield server instance (may be None)
    yield server
    
    # Cleanup
    if server is not None:
        try:
            print(f"\n🛑 Stopping embedded d-vecDB server...")
            server.stop()
            print("✅ Server stopped successfully")
        except Exception as e:
            print(f"⚠️  Error stopping server: {e}")


@pytest.fixture(scope="session")
def test_config(vectordb_server, server_ports):
    """Test configuration that adapts based on server availability."""
    if vectordb_server is not None:
        # Use embedded server ports
        host = vectordb_server.host
        port = vectordb_server.port
        grpc_port = vectordb_server.grpc_port
    else:
        # Use configured ports (external server)
        host = TEST_HOST
        port = server_ports["rest_port"]
        grpc_port = server_ports["grpc_port"]
    
    return {
        "host": host,
        "port": port, 
        "grpc_port": grpc_port,
        "embedded_server": vectordb_server,
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client(test_config) -> Generator[VectorDBClient, None, None]:
    """Synchronous VectorDB client fixture."""
    client = VectorDBClient(host=test_config["host"], port=test_config["port"])
    
    # Skip tests if server is not available
    try:
        if not client.ping():
            if test_config["embedded_server"] is not None:
                pytest.skip("Embedded server not responding")
            else:
                pytest.skip("External VectorDB server not available for testing")
    except Exception as e:
        if test_config["embedded_server"] is not None:
            pytest.skip(f"Embedded server connection failed: {e}")
        else:
            pytest.skip(f"External VectorDB server not available: {e}")
    
    yield client
    
    try:
        client.close()
    except:
        pass


@pytest.fixture
async def async_client(test_config) -> AsyncGenerator[AsyncVectorDBClient, None, None]:
    """Asynchronous VectorDB client fixture."""
    client = AsyncVectorDBClient(host=test_config["host"], port=test_config["port"])
    
    try:
        await client.connect()
        
        # Skip tests if server is not available
        if not await client.ping():
            if test_config["embedded_server"] is not None:
                pytest.skip("Embedded server not responding to async client")
            else:
                pytest.skip("External VectorDB server not available for async testing")
    except Exception as e:
        if test_config["embedded_server"] is not None:
            pytest.skip(f"Embedded server async connection failed: {e}")
        else:
            pytest.skip(f"External VectorDB server not available for async testing: {e}")
    
    yield client
    
    try:
        await client.close()
    except:
        pass


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
    config.addinivalue_line(
        "markers", "requires_server: mark test as requiring a running server"
    )


# Environment info for debugging
def pytest_sessionstart(session):
    """Print environment info at start of test session."""
    print(f"\n{'='*60}")
    print("d-vecDB Python Client Test Session")
    print(f"{'='*60}")
    print(f"Embedded server available: {EMBEDDED_SERVER_AVAILABLE}")
    print(f"Use embedded server: {USE_EMBEDDED_SERVER}")
    print(f"Auto-start server: {AUTO_START_SERVER}")
    print(f"Test host: {TEST_HOST}")
    print(f"Test ports: REST={TEST_PORT}, gRPC={TEST_GRPC_PORT}")
    if not EMBEDDED_SERVER_AVAILABLE:
        print("⚠️  d-vecdb-server package not found - install with: pip install d-vecdb-server")
    print(f"{'='*60}")


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


# Skip conditions
def skip_if_no_server():
    """Skip test if VectorDB server is not available."""
    # This function is kept for backward compatibility
    # The new fixtures handle server availability automatically
    return False