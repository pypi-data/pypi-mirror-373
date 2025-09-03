"""Memory resource for the Sovant SDK."""

from typing import Any, Dict, List, Optional, Union

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    BatchCreateResult,
    CreateMemoryInput,
    Memory,
    MemoryType,
    PaginatedResponse,
    SearchOptions,
    SearchResult,
    UpdateMemoryInput,
)


class Memories(BaseClient):
    """Synchronous memory operations."""
    
    def create(self, data: Union[CreateMemoryInput, Dict[str, Any]]) -> Memory:
        """Create a new memory."""
        if isinstance(data, dict):
            data = CreateMemoryInput(**data)
        
        response = self.request("POST", "/memory", data.model_dump(exclude_none=True))
        return Memory(**response)
    
    def get(self, memory_id: str) -> Memory:
        """Get a memory by ID."""
        response = self.request("GET", f"/memory/{memory_id}")
        return Memory(**response)
    
    def update(
        self, 
        memory_id: str, 
        data: Union[UpdateMemoryInput, Dict[str, Any]]
    ) -> Memory:
        """Update a memory."""
        if isinstance(data, dict):
            data = UpdateMemoryInput(**data)
        
        response = self.request("PUT", f"/memory/{memory_id}", data.model_dump(exclude_none=True))
        return Memory(**response)
    
    def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        self.request("DELETE", f"/memory/{memory_id}")
    
    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: Optional[Union[MemoryType, List[MemoryType]]] = None,
        tags: Optional[List[str]] = None,
        is_archived: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """List memories with pagination."""
        params = {
            "limit": limit,
            "offset": offset,
            "type": type,
            "tags": tags,
            "is_archived": is_archived,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/memory{query_string}")
        
        # Convert data items to Memory objects
        response["data"] = [Memory(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    def search(self, options: Union[SearchOptions, Dict[str, Any]]) -> List[SearchResult]:
        """Search memories."""
        if isinstance(options, dict):
            options = SearchOptions(**options)
        
        params = {
            "q": options.query,
            "limit": options.limit,
            "offset": options.offset,
            "type": options.type,
            "tags": options.tags,
            "created_after": options.created_after,
            "created_before": options.created_before,
            "search_type": options.search_type,
            "include_archived": options.include_archived,
            "sort_by": options.sort_by,
            "sort_order": options.sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/memory/search{query_string}")
        
        return [SearchResult(**result) for result in response.get("results", [])]
    
    def create_batch(self, memories: List[Union[CreateMemoryInput, Dict[str, Any]]]) -> BatchCreateResult:
        """Batch create memories."""
        memories_data = []
        for memory in memories:
            if isinstance(memory, dict):
                memory = CreateMemoryInput(**memory)
            memories_data.append(memory.model_dump(exclude_none=True))
        
        response = self.request("POST", "/memory/batch", {"memories": memories_data})
        
        # Convert success items to Memory objects
        response["success"] = [Memory(**item) for item in response["success"]]
        return BatchCreateResult(**response)
    
    def delete_batch(self, ids: List[str]) -> Dict[str, int]:
        """Batch delete memories."""
        response = self.request("POST", "/memory/batch/delete", {"ids": ids})
        return response
    
    def get_insights(
        self,
        time_range: Optional[str] = None,
        group_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get memory insights and analytics."""
        params = {
            "time_range": time_range,
            "group_by": group_by,
        }
        
        query_string = self._build_query_string(params)
        return self.request("GET", f"/memory/insights{query_string}")
    
    def archive(self, memory_id: str) -> Memory:
        """Archive a memory."""
        return self.update(memory_id, {"is_archived": True})
    
    def unarchive(self, memory_id: str) -> Memory:
        """Unarchive a memory."""
        return self.update(memory_id, {"is_archived": False})
    
    def pin(self, memory_id: str) -> Memory:
        """Pin a memory."""
        return self.update(memory_id, {"is_pinned": True})
    
    def unpin(self, memory_id: str) -> Memory:
        """Unpin a memory."""
        return self.update(memory_id, {"is_pinned": False})
    
    def get_related(
        self,
        memory_id: str,
        limit: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """Get related memories."""
        params = {
            "limit": limit,
            "threshold": threshold,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/memory/{memory_id}/related{query_string}")
        
        return [SearchResult(**result) for result in response.get("results", [])]


class AsyncMemories(AsyncBaseClient):
    """Asynchronous memory operations."""
    
    async def create(self, data: Union[CreateMemoryInput, Dict[str, Any]]) -> Memory:
        """Create a new memory."""
        if isinstance(data, dict):
            data = CreateMemoryInput(**data)
        
        response = await self.request("POST", "/memory", data.model_dump(exclude_none=True))
        return Memory(**response)
    
    async def get(self, memory_id: str) -> Memory:
        """Get a memory by ID."""
        response = await self.request("GET", f"/memory/{memory_id}")
        return Memory(**response)
    
    async def update(
        self, 
        memory_id: str, 
        data: Union[UpdateMemoryInput, Dict[str, Any]]
    ) -> Memory:
        """Update a memory."""
        if isinstance(data, dict):
            data = UpdateMemoryInput(**data)
        
        response = await self.request("PUT", f"/memory/{memory_id}", data.model_dump(exclude_none=True))
        return Memory(**response)
    
    async def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        await self.request("DELETE", f"/memory/{memory_id}")
    
    async def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: Optional[Union[MemoryType, List[MemoryType]]] = None,
        tags: Optional[List[str]] = None,
        is_archived: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """List memories with pagination."""
        params = {
            "limit": limit,
            "offset": offset,
            "type": type,
            "tags": tags,
            "is_archived": is_archived,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/memory{query_string}")
        
        # Convert data items to Memory objects
        response["data"] = [Memory(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    async def search(self, options: Union[SearchOptions, Dict[str, Any]]) -> List[SearchResult]:
        """Search memories."""
        if isinstance(options, dict):
            options = SearchOptions(**options)
        
        params = {
            "q": options.query,
            "limit": options.limit,
            "offset": options.offset,
            "type": options.type,
            "tags": options.tags,
            "created_after": options.created_after,
            "created_before": options.created_before,
            "search_type": options.search_type,
            "include_archived": options.include_archived,
            "sort_by": options.sort_by,
            "sort_order": options.sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/memory/search{query_string}")
        
        return [SearchResult(**result) for result in response.get("results", [])]
    
    async def create_batch(self, memories: List[Union[CreateMemoryInput, Dict[str, Any]]]) -> BatchCreateResult:
        """Batch create memories."""
        memories_data = []
        for memory in memories:
            if isinstance(memory, dict):
                memory = CreateMemoryInput(**memory)
            memories_data.append(memory.model_dump(exclude_none=True))
        
        response = await self.request("POST", "/memory/batch", {"memories": memories_data})
        
        # Convert success items to Memory objects
        response["success"] = [Memory(**item) for item in response["success"]]
        return BatchCreateResult(**response)
    
    async def delete_batch(self, ids: List[str]) -> Dict[str, int]:
        """Batch delete memories."""
        response = await self.request("POST", "/memory/batch/delete", {"ids": ids})
        return response
    
    async def get_insights(
        self,
        time_range: Optional[str] = None,
        group_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get memory insights and analytics."""
        params = {
            "time_range": time_range,
            "group_by": group_by,
        }
        
        query_string = self._build_query_string(params)
        return await self.request("GET", f"/memory/insights{query_string}")
    
    async def archive(self, memory_id: str) -> Memory:
        """Archive a memory."""
        return await self.update(memory_id, {"is_archived": True})
    
    async def unarchive(self, memory_id: str) -> Memory:
        """Unarchive a memory."""
        return await self.update(memory_id, {"is_archived": False})
    
    async def pin(self, memory_id: str) -> Memory:
        """Pin a memory."""
        return await self.update(memory_id, {"is_pinned": True})
    
    async def unpin(self, memory_id: str) -> Memory:
        """Unpin a memory."""
        return await self.update(memory_id, {"is_pinned": False})
    
    async def get_related(
        self,
        memory_id: str,
        limit: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """Get related memories."""
        params = {
            "limit": limit,
            "threshold": threshold,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/memory/{memory_id}/related{query_string}")
        
        return [SearchResult(**result) for result in response.get("results", [])]