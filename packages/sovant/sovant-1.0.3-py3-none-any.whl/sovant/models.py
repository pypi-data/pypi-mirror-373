from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal

class MemoryCreate(BaseModel):
    data: Any
    type: Optional[Literal['journal', 'insight', 'observation', 'task', 'preference']] = 'journal'
    ttl: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    thread_id: Optional[str] = None

class MemoryResult(BaseModel):
    id: str
    content: str
    type: str
    ttl: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    thread_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SearchQuery(BaseModel):
    query: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = None
    thread_id: Optional[str] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    from_date: Optional[str] = None
    to_date: Optional[str] = None