"""Thread resource for the Sovant SDK."""

from typing import Any, Dict, List, Optional, Union

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    CreateThreadInput,
    Memory,
    PaginatedResponse,
    Thread,
    ThreadStats,
    ThreadStatus,
    UpdateThreadInput,
)


class Threads(BaseClient):
    """Synchronous thread operations."""
    
    def create(self, data: Union[CreateThreadInput, Dict[str, Any]]) -> Thread:
        """Create a new thread."""
        if isinstance(data, dict):
            data = CreateThreadInput(**data)
        
        response = self.request("POST", "/threads", data.model_dump(exclude_none=True))
        return Thread(**response)
    
    def get(self, thread_id: str, include_memories: bool = False) -> Thread:
        """Get a thread by ID."""
        query_string = "?include_memories=true" if include_memories else ""
        response = self.request("GET", f"/threads/{thread_id}{query_string}")
        
        thread = Thread(**response)
        if include_memories and "memories" in response:
            # Add memories as an attribute
            thread.memories = [Memory(**m) for m in response["memories"]]
        
        return thread
    
    def update(
        self,
        thread_id: str,
        data: Union[UpdateThreadInput, Dict[str, Any]]
    ) -> Thread:
        """Update a thread."""
        if isinstance(data, dict):
            data = UpdateThreadInput(**data)
        
        response = self.request("PUT", f"/threads/{thread_id}", data.model_dump(exclude_none=True))
        return Thread(**response)
    
    def delete(self, thread_id: str, delete_memories: bool = False) -> None:
        """Delete a thread."""
        query_string = "?delete_memories=true" if delete_memories else ""
        self.request("DELETE", f"/threads/{thread_id}{query_string}")
    
    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[ThreadStatus] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """List threads with pagination."""
        params = {
            "limit": limit,
            "offset": offset,
            "status": status,
            "tags": tags,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/threads{query_string}")
        
        # Convert data items to Thread objects
        response["data"] = [Thread(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    def add_memories(self, thread_id: str, memory_ids: List[str]) -> Thread:
        """Add memories to a thread."""
        response = self.request(
            "POST",
            f"/threads/{thread_id}/memories",
            {"add": memory_ids}
        )
        return Thread(**response)
    
    def remove_memories(self, thread_id: str, memory_ids: List[str]) -> Thread:
        """Remove memories from a thread."""
        response = self.request(
            "POST",
            f"/threads/{thread_id}/memories",
            {"remove": memory_ids}
        )
        return Thread(**response)
    
    def get_memories(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: Optional[Union[str, List[str]]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """Get memories in a thread."""
        params = {
            "limit": limit,
            "offset": offset,
            "type": type,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/threads/{thread_id}/memories{query_string}")
        
        # Convert data items to Memory objects
        response["data"] = [Memory(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    def get_stats(self, thread_id: str) -> ThreadStats:
        """Get thread statistics."""
        response = self.request("GET", f"/threads/{thread_id}/stats")
        return ThreadStats(**response)
    
    def archive(self, thread_id: str) -> Thread:
        """Archive a thread."""
        return self.update(thread_id, {"status": ThreadStatus.ARCHIVED})
    
    def unarchive(self, thread_id: str) -> Thread:
        """Unarchive a thread."""
        return self.update(thread_id, {"status": ThreadStatus.ACTIVE})
    
    def complete(self, thread_id: str) -> Thread:
        """Complete a thread."""
        return self.update(thread_id, {"status": ThreadStatus.COMPLETED})
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[ThreadStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> PaginatedResponse:
        """Search threads."""
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "status": status,
            "tags": tags,
        }
        
        query_string = self._build_query_string(params)
        response = self.request("GET", f"/threads/search{query_string}")
        
        # Convert data items to Thread objects
        response["data"] = [Thread(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    def merge(self, target_id: str, source_ids: List[str]) -> Thread:
        """Merge multiple threads into one."""
        response = self.request(
            "POST",
            f"/threads/{target_id}/merge",
            {"source_thread_ids": source_ids}
        )
        return Thread(**response)
    
    def clone(
        self,
        thread_id: str,
        name: Optional[str] = None,
        include_memories: bool = True
    ) -> Thread:
        """Clone a thread."""
        data = {
            "name": name,
            "include_memories": include_memories,
        }
        response = self.request("POST", f"/threads/{thread_id}/clone", data)
        return Thread(**response)


class AsyncThreads(AsyncBaseClient):
    """Asynchronous thread operations."""
    
    async def create(self, data: Union[CreateThreadInput, Dict[str, Any]]) -> Thread:
        """Create a new thread."""
        if isinstance(data, dict):
            data = CreateThreadInput(**data)
        
        response = await self.request("POST", "/threads", data.model_dump(exclude_none=True))
        return Thread(**response)
    
    async def get(self, thread_id: str, include_memories: bool = False) -> Thread:
        """Get a thread by ID."""
        query_string = "?include_memories=true" if include_memories else ""
        response = await self.request("GET", f"/threads/{thread_id}{query_string}")
        
        thread = Thread(**response)
        if include_memories and "memories" in response:
            # Add memories as an attribute
            thread.memories = [Memory(**m) for m in response["memories"]]
        
        return thread
    
    async def update(
        self,
        thread_id: str,
        data: Union[UpdateThreadInput, Dict[str, Any]]
    ) -> Thread:
        """Update a thread."""
        if isinstance(data, dict):
            data = UpdateThreadInput(**data)
        
        response = await self.request("PUT", f"/threads/{thread_id}", data.model_dump(exclude_none=True))
        return Thread(**response)
    
    async def delete(self, thread_id: str, delete_memories: bool = False) -> None:
        """Delete a thread."""
        query_string = "?delete_memories=true" if delete_memories else ""
        await self.request("DELETE", f"/threads/{thread_id}{query_string}")
    
    async def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[ThreadStatus] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """List threads with pagination."""
        params = {
            "limit": limit,
            "offset": offset,
            "status": status,
            "tags": tags,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/threads{query_string}")
        
        # Convert data items to Thread objects
        response["data"] = [Thread(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    async def add_memories(self, thread_id: str, memory_ids: List[str]) -> Thread:
        """Add memories to a thread."""
        response = await self.request(
            "POST",
            f"/threads/{thread_id}/memories",
            {"add": memory_ids}
        )
        return Thread(**response)
    
    async def remove_memories(self, thread_id: str, memory_ids: List[str]) -> Thread:
        """Remove memories from a thread."""
        response = await self.request(
            "POST",
            f"/threads/{thread_id}/memories",
            {"remove": memory_ids}
        )
        return Thread(**response)
    
    async def get_memories(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: Optional[Union[str, List[str]]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> PaginatedResponse:
        """Get memories in a thread."""
        params = {
            "limit": limit,
            "offset": offset,
            "type": type,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/threads/{thread_id}/memories{query_string}")
        
        # Convert data items to Memory objects
        response["data"] = [Memory(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    async def get_stats(self, thread_id: str) -> ThreadStats:
        """Get thread statistics."""
        response = await self.request("GET", f"/threads/{thread_id}/stats")
        return ThreadStats(**response)
    
    async def archive(self, thread_id: str) -> Thread:
        """Archive a thread."""
        return await self.update(thread_id, {"status": ThreadStatus.ARCHIVED})
    
    async def unarchive(self, thread_id: str) -> Thread:
        """Unarchive a thread."""
        return await self.update(thread_id, {"status": ThreadStatus.ACTIVE})
    
    async def complete(self, thread_id: str) -> Thread:
        """Complete a thread."""
        return await self.update(thread_id, {"status": ThreadStatus.COMPLETED})
    
    async def search(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[ThreadStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> PaginatedResponse:
        """Search threads."""
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "status": status,
            "tags": tags,
        }
        
        query_string = self._build_query_string(params)
        response = await self.request("GET", f"/threads/search{query_string}")
        
        # Convert data items to Thread objects
        response["data"] = [Thread(**item) for item in response["data"]]
        return PaginatedResponse(**response)
    
    async def merge(self, target_id: str, source_ids: List[str]) -> Thread:
        """Merge multiple threads into one."""
        response = await self.request(
            "POST",
            f"/threads/{target_id}/merge",
            {"source_thread_ids": source_ids}
        )
        return Thread(**response)
    
    async def clone(
        self,
        thread_id: str,
        name: Optional[str] = None,
        include_memories: bool = True
    ) -> Thread:
        """Clone a thread."""
        data = {
            "name": name,
            "include_memories": include_memories,
        }
        response = await self.request("POST", f"/threads/{thread_id}/clone", data)
        return Thread(**response)