"""
Main synchronous client interface for d-vecDB.
"""

from typing import List, Optional, Dict, Any, Union
from .types import (
    CollectionConfig, Vector, QueryResult, SearchResponse,
    CollectionStats, ServerStats, HealthResponse, InsertResponse,
    ListCollectionsResponse, CollectionResponse, VectorData
)
from .rest.client import RestClient
from .grpc.client import GrpcClient
from .exceptions import VectorDBError, ClientConfigurationError


class VectorDBClient:
    """
    Main synchronous client for d-vecDB.
    
    Supports both REST and gRPC protocols with automatic fallback.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: Optional[int] = None,
        grpc_port: Optional[int] = None,
        protocol: str = "rest",
        ssl: bool = False,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        Initialize VectorDB client.
        
        Args:
            host: Server hostname or IP address
            port: Server port (default: 8080 for REST, 9090 for gRPC)
            grpc_port: Explicit gRPC port (overrides port for gRPC)
            protocol: Protocol to use ("rest", "grpc", or "auto")
            ssl: Use secure connection
            timeout: Request timeout in seconds
            **kwargs: Additional protocol-specific parameters
        """
        self.host = host
        self.protocol = protocol.lower()
        self.ssl = ssl
        self.timeout = timeout
        
        # Determine ports
        if self.protocol == "rest":
            self.port = port or 8080
        elif self.protocol == "grpc":
            self.port = grpc_port or port or 9090
        elif self.protocol == "auto":
            self.rest_port = port or 8080
            self.grpc_port = grpc_port or 9090
        else:
            raise ClientConfigurationError(
                f"Unsupported protocol: {protocol}. Use 'rest', 'grpc', or 'auto'"
            )
        
        # Initialize client(s)
        self._rest_client = None
        self._grpc_client = None
        
        if self.protocol == "rest":
            self._rest_client = RestClient(
                host=host, 
                port=self.port,
                ssl=ssl,
                timeout=timeout,
                **kwargs
            )
        elif self.protocol == "grpc":
            self._grpc_client = GrpcClient(
                host=host,
                port=self.port,
                ssl=ssl,
                timeout=timeout,
                **kwargs
            )
        elif self.protocol == "auto":
            # Try gRPC first, fallback to REST
            try:
                self._grpc_client = GrpcClient(
                    host=host,
                    port=self.grpc_port,
                    ssl=ssl,
                    timeout=timeout,
                    **kwargs
                )
                # Test connection
                if self._grpc_client.ping():
                    self.protocol = "grpc"
                else:
                    self._grpc_client.close()
                    self._grpc_client = None
                    raise ConnectionError("gRPC not available")
            except Exception:
                self._rest_client = RestClient(
                    host=host,
                    port=self.rest_port,
                    ssl=ssl,
                    timeout=timeout,
                    **kwargs
                )
                self.protocol = "rest"
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close client connections."""
        if self._rest_client:
            self._rest_client.close()
        if self._grpc_client:
            self._grpc_client.close()
    
    @property
    def client(self):
        """Get the active client instance."""
        if self.protocol == "rest":
            return self._rest_client
        elif self.protocol == "grpc":
            return self._grpc_client
        else:
            raise ClientConfigurationError("No active client")
    
    # Collection Management
    def create_collection(self, config: CollectionConfig) -> CollectionResponse:
        """Create a new vector collection."""
        return self.client.create_collection(config)
    
    def delete_collection(self, name: str) -> CollectionResponse:
        """Delete a vector collection."""
        return self.client.delete_collection(name)
    
    def get_collection(self, name: str) -> CollectionResponse:
        """Get collection information."""
        return self.client.get_collection(name)
    
    def list_collections(self) -> ListCollectionsResponse:
        """List all collections."""
        return self.client.list_collections()
    
    def get_collection_stats(self, name: str) -> CollectionStats:
        """Get collection statistics."""
        return self.client.get_collection_stats(name)
    
    # Vector Operations
    def insert_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Insert a single vector."""
        return self.client.insert_vector(collection_name, vector)
    
    def insert_vectors(self, collection_name: str, vectors: List[Vector]) -> InsertResponse:
        """Insert multiple vectors."""
        return self.client.insert_vectors(collection_name, vectors)
    
    def get_vector(self, collection_name: str, vector_id: str) -> Vector:
        """Retrieve a vector by ID."""
        return self.client.get_vector(collection_name, vector_id)
    
    def update_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Update an existing vector."""
        return self.client.update_vector(collection_name, vector)
    
    def delete_vector(self, collection_name: str, vector_id: str) -> InsertResponse:
        """Delete a vector by ID."""
        return self.client.delete_vector(collection_name, vector_id)
    
    # Search Operations
    def search(
        self, 
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10,
        ef_search: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """Search for similar vectors."""
        return self.client.search(
            collection_name, query_vector, limit, ef_search, filter
        )
    
    # Server Operations
    def get_server_stats(self) -> ServerStats:
        """Get server statistics."""
        return self.client.get_server_stats()
    
    def health_check(self) -> HealthResponse:
        """Check server health."""
        return self.client.health_check()
    
    def ping(self) -> bool:
        """Check if server is reachable."""
        return self.client.ping()
    
    # Convenience methods
    def create_collection_simple(
        self,
        name: str,
        dimension: int,
        distance_metric: str = "cosine"
    ) -> CollectionResponse:
        """Create a collection with minimal configuration."""
        return self.client.create_collection_simple(name, dimension, distance_metric)
    
    def insert_simple(
        self,
        collection_name: str,
        vector_id: str,
        vector_data: VectorData,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InsertResponse:
        """Insert a vector with simple parameters."""
        return self.client.insert_simple(collection_name, vector_id, vector_data, metadata)
    
    def search_simple(
        self,
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10
    ) -> List[QueryResult]:
        """Simple vector search returning just results."""
        return self.client.search_simple(collection_name, query_vector, limit)
    
    # Batch operations
    def batch_insert_simple(
        self,
        collection_name: str,
        vectors_data: List[tuple],  # List of (id, vector_data, metadata)
        batch_size: int = 100
    ) -> List[InsertResponse]:
        """Insert multiple vectors in batches."""
        responses = []
        
        for i in range(0, len(vectors_data), batch_size):
            batch = vectors_data[i:i + batch_size]
            vectors = []
            
            for item in batch:
                if len(item) == 2:
                    vector_id, vector_data = item
                    metadata = None
                elif len(item) == 3:
                    vector_id, vector_data, metadata = item
                else:
                    raise ValueError("Each vector tuple must be (id, data) or (id, data, metadata)")
                
                if hasattr(vector_data, 'tolist'):
                    vector_data = vector_data.tolist()
                
                vectors.append(Vector(id=vector_id, data=vector_data, metadata=metadata))
            
            response = self.insert_vectors(collection_name, vectors)
            responses.append(response)
        
        return responses
    
    # Context and utility methods
    def get_info(self) -> Dict[str, Any]:
        """Get client and server information."""
        try:
            health = self.health_check()
            stats = self.get_server_stats()
            collections = self.list_collections()
            
            return {
                "client": {
                    "protocol": self.protocol,
                    "host": self.host,
                    "port": getattr(self, 'port', None),
                    "ssl": self.ssl,
                },
                "server": {
                    "healthy": health.healthy,
                    "status": health.status,
                    "stats": stats.model_dump(),
                    "collections": collections.collections,
                }
            }
        except Exception as e:
            return {
                "client": {
                    "protocol": self.protocol,
                    "host": self.host,
                    "port": getattr(self, 'port', None),
                    "ssl": self.ssl,
                },
                "server": {
                    "error": str(e)
                }
            }