"""
Example test demonstrating the enhanced conftest.py utilities for optional server management.
"""

import pytest
import numpy as np
from vectordb_client import VectorDBClient
from vectordb_client.types import CollectionConfig, Vector, DistanceMetric

# Import the utility functions from conftest
from .conftest import (
    start_server_if_available, 
    check_server_package_available,
    TEST_HOST,
    TEST_PORT
)


def test_available_testing_options():
    """Show what testing options are available in this environment."""
    print("\n" + "="*50)
    print("d-vecDB Python Client Testing Options")
    print("="*50)
    
    embedded_available = check_server_package_available()
    print(f"Embedded server available: {'✅ Yes' if embedded_available else '❌ No'}")
    
    if embedded_available:
        print("Available testing modes:")
        print("  🚀 Isolated testing with embedded server")
        print("  📊 Performance testing with embedded server") 
        print("  🔄 Rapid iteration workflows")
        print("  🧪 Automatic server lifecycle management")
    else:
        print("Available testing modes:")
        print("  📡 External server testing (manual startup required)")
        print("  🔧 Basic client functionality testing")
        print("\nTo enable embedded server testing:")
        print("  pip install d-vecdb-server")
    
    print("="*50)
    
    # This test always passes - it's just informational
    assert True


class TestServerUtilities:
    """Test the enhanced server utilities in conftest.py"""
    
    def test_server_package_detection(self):
        """Test detection of d-vecdb-server package."""
        # This test always passes, just shows package availability
        available = check_server_package_available()
        print(f"d-vecdb-server package available: {available}")
        
        if available:
            print("✅ Can use embedded server utilities")
        else:
            print("ℹ️  External server required for testing")
        
        # Test always passes
        assert True
    
    def test_optional_server_management(self):
        """Test optional server management for isolated testing."""
        # Try to start a server on a different port for isolation
        test_port = 8888
        server = start_server_if_available(port=test_port)
        
        if server:
            print(f"✅ Started isolated server on port {test_port}")
            
            try:
                # Test with isolated server
                client = VectorDBClient(host=TEST_HOST, port=test_port)
                assert client.ping(), "Isolated server should be reachable"
                
                # Quick functionality test
                collection_config = CollectionConfig(
                    name="isolated_test",
                    dimension=64,
                    distance_metric=DistanceMetric.COSINE
                )
                
                client.create_collection(collection_config)
                
                # Insert a test vector
                test_vector = Vector(
                    id="test_001",
                    data=np.random.random(64).astype(np.float32).tolist(),
                    metadata={"test": True}
                )
                
                client.insert_vectors("isolated_test", [test_vector])
                
                # Verify insertion
                vectors = client.get_vectors("isolated_test", ["test_001"])
                assert len(vectors) == 1
                assert vectors[0].id == "test_001"
                
                print("✅ Isolated server test completed successfully")
                
                # Cleanup
                client.delete_collection("isolated_test")
                client.close()
                
            finally:
                # Always stop the isolated server
                server.stop()
                print("🛑 Isolated server stopped")
                
        else:
            pytest.skip("d-vecdb-server package not available for isolated testing")


if __name__ == "__main__":
    # When run directly, show testing options
    test_available_testing_options()