"""
Asynchronous REST API client for d-vecDB.
"""

import json
from typing import List, Optional, Dict, Any
import httpx

from ..types import (
    CollectionConfig, Vector, QueryResult, SearchRequest, SearchResponse,
    CollectionStats, ServerStats, HealthResponse, InsertResponse,
    ListCollectionsResponse, CollectionResponse, VectorData
)
from ..exceptions import (
    VectorDBError, ConnectionError, create_exception_from_response
)


class AsyncRestClient:
    """Asynchronous REST API client for d-vecDB."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        ssl: bool = False,
        timeout: float = 30.0,
        connection_pool_size: int = 10,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[httpx.Auth] = None
    ):
        """
        Initialize async REST client.
        
        Args:
            host: Server hostname or IP address
            port: Server port number
            ssl: Use HTTPS if True, HTTP if False
            timeout: Request timeout in seconds
            connection_pool_size: Maximum connection pool size
            headers: Additional HTTP headers
            auth: HTTP authentication
        """
        self.host = host
        self.port = port
        self.ssl = ssl
        self.timeout = timeout
        
        # Build base URL
        protocol = "https" if ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        
        # Setup HTTP client
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "vectordb-client-python/0.1.0"
        }
        if headers:
            default_headers.update(headers)
            
        # Connection limits for the pool
        limits = httpx.Limits(
            max_keepalive_connections=connection_pool_size,
            max_connections=connection_pool_size * 2
        )
            
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=default_headers,
            timeout=timeout,
            auth=auth,
            follow_redirects=True,
            limits=limits
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'client'):
            await self.client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an async HTTP request with error handling."""
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=json_data,
                params=params
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("message", f"HTTP {response.status_code}")
                    details = error_data.get("details", {})
                except (json.JSONDecodeError, KeyError):
                    message = f"HTTP {response.status_code}: {response.text}"
                    details = {}
                
                raise create_exception_from_response(
                    response.status_code, message, details
                )
            
            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                raise VectorDBError(f"Invalid JSON response: {e}")
                
        except httpx.RequestError as e:
            raise ConnectionError(f"Request failed: {e}")
        except httpx.TimeoutException:
            raise VectorDBError("Request timed out")
    
    # Collection Management
    async def create_collection(self, config: CollectionConfig) -> CollectionResponse:
        """Create a new vector collection."""
        response_data = await self._make_request(
            "POST", 
            "/collections",
            json_data=config.model_dump()
        )
        return CollectionResponse(**response_data)
    
    async def delete_collection(self, name: str) -> CollectionResponse:
        """Delete a vector collection."""
        response_data = await self._make_request("DELETE", f"/collections/{name}")
        return CollectionResponse(**response_data)
    
    async def get_collection(self, name: str) -> CollectionResponse:
        """Get collection information."""
        response_data = await self._make_request("GET", f"/collections/{name}")
        return CollectionResponse(**response_data)
    
    async def list_collections(self) -> ListCollectionsResponse:
        """List all collections."""
        response_data = await self._make_request("GET", "/collections")
        return ListCollectionsResponse(**response_data)
    
    async def get_collection_stats(self, name: str) -> CollectionStats:
        """Get collection statistics."""
        response_data = await self._make_request("GET", f"/collections/{name}/stats")
        return CollectionStats(**response_data["stats"])
    
    # Vector Operations
    async def insert_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Insert a single vector."""
        response_data = await self._make_request(
            "POST",
            f"/collections/{collection_name}/vectors",
            json_data=vector.model_dump()
        )
        return InsertResponse(**response_data)
    
    async def insert_vectors(self, collection_name: str, vectors: List[Vector]) -> InsertResponse:
        """Insert multiple vectors."""
        response_data = await self._make_request(
            "POST",
            f"/collections/{collection_name}/vectors/batch",
            json_data={"vectors": [v.model_dump() for v in vectors]}
        )
        return InsertResponse(**response_data)
    
    async def get_vector(self, collection_name: str, vector_id: str) -> Vector:
        """Retrieve a vector by ID."""
        response_data = await self._make_request(
            "GET", 
            f"/collections/{collection_name}/vectors/{vector_id}"
        )
        return Vector(**response_data["vector"])
    
    async def update_vector(self, collection_name: str, vector: Vector) -> InsertResponse:
        """Update an existing vector."""
        response_data = await self._make_request(
            "PUT",
            f"/collections/{collection_name}/vectors/{vector.id}",
            json_data=vector.model_dump()
        )
        return InsertResponse(**response_data)
    
    async def delete_vector(self, collection_name: str, vector_id: str) -> InsertResponse:
        """Delete a vector by ID."""
        response_data = await self._make_request(
            "DELETE",
            f"/collections/{collection_name}/vectors/{vector_id}"
        )
        return InsertResponse(**response_data)
    
    # Search Operations  
    async def search(
        self, 
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10,
        ef_search: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """Search for similar vectors."""
        if hasattr(query_vector, 'tolist'):
            query_vector = query_vector.tolist()
        
        search_request = SearchRequest(
            query_vector=query_vector,
            limit=limit,
            ef_search=ef_search,
            filter=filter
        )
        
        response_data = await self._make_request(
            "POST",
            f"/collections/{collection_name}/search",
            json_data=search_request.model_dump(exclude_none=True)
        )
        
        return SearchResponse(**response_data)
    
    # Server Operations
    async def get_server_stats(self) -> ServerStats:
        """Get server statistics."""
        response_data = await self._make_request("GET", "/stats")
        return ServerStats(**response_data["stats"])
    
    async def health_check(self) -> HealthResponse:
        """Check server health."""
        response_data = await self._make_request("GET", "/health")
        return HealthResponse(**response_data)
    
    # Convenience methods
    async def ping(self) -> bool:
        """Check if server is reachable."""
        try:
            await self.health_check()
            return True
        except VectorDBError:
            return False
    
    async def create_collection_simple(
        self,
        name: str,
        dimension: int,
        distance_metric: str = "cosine"
    ) -> CollectionResponse:
        """Create a collection with minimal configuration."""
        from ..types import DistanceMetric
        
        config = CollectionConfig(
            name=name,
            dimension=dimension,
            distance_metric=DistanceMetric(distance_metric)
        )
        return await self.create_collection(config)
    
    async def insert_simple(
        self,
        collection_name: str,
        vector_id: str,
        vector_data: VectorData,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InsertResponse:
        """Insert a vector with simple parameters."""
        if hasattr(vector_data, 'tolist'):
            vector_data = vector_data.tolist()
            
        vector = Vector(id=vector_id, data=vector_data, metadata=metadata)
        return await self.insert_vector(collection_name, vector)
    
    async def search_simple(
        self,
        collection_name: str,
        query_vector: VectorData,
        limit: int = 10
    ) -> List[QueryResult]:
        """Simple vector search returning just results."""
        response = await self.search(collection_name, query_vector, limit)
        return response.results