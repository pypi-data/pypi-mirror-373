"""Type definitions for the Sovant SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memories."""
    
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    DECISION = "decision"
    EMOTION = "emotion"
    LEARNING = "learning"
    PREFERENCE = "preference"
    EVENT = "event"
    CONVERSATION = "conversation"
    TASK = "task"
    REMINDER = "reminder"
    QUESTION = "question"
    INSIGHT = "insight"
    JOURNAL = "journal"
    ROUTINE = "routine"
    META = "meta"


class EmotionType(str, Enum):
    """Types of emotions."""
    
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    SAD = "sad"
    STRESSED = "stressed"
    CALM = "calm"
    REFLECTIVE = "reflective"
    POSITIVE = "positive"
    NEGATIVE = "negative"


class ThreadStatus(str, Enum):
    """Status of a thread."""
    
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class EmotionalContext(BaseModel):
    """Emotional context of a memory."""
    
    type: EmotionType
    intensity: Optional[float] = Field(None, ge=0, le=1)
    tone_tags: Optional[List[str]] = Field(None, alias="toneTags")


class Memory(BaseModel):
    """A memory object."""
    
    id: str
    content: str
    type: MemoryType
    importance: float = Field(ge=0, le=1)
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    emotion: Optional[EmotionalContext] = None
    decisions: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_due: Optional[datetime] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    title: Optional[str] = None
    thread_ids: Optional[List[str]] = None


class CreateMemoryInput(BaseModel):
    """Input for creating a memory."""
    
    content: str
    type: Optional[MemoryType] = MemoryType.OBSERVATION
    importance: Optional[float] = Field(0.5, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    emotion: Optional[EmotionalContext] = None
    decisions: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_due: Optional[datetime] = None
    title: Optional[str] = None
    thread_ids: Optional[List[str]] = None


class UpdateMemoryInput(BaseModel):
    """Input for updating a memory."""
    
    content: Optional[str] = None
    type: Optional[MemoryType] = None
    importance: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    emotion: Optional[EmotionalContext] = None
    decisions: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_due: Optional[datetime] = None
    title: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class SearchOptions(BaseModel):
    """Options for searching memories."""
    
    query: str
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    type: Optional[Union[MemoryType, List[MemoryType]]] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search_type: Optional[Literal["semantic", "keyword", "hybrid"]] = "hybrid"
    include_archived: Optional[bool] = False
    metadata_filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[Literal["relevance", "created_at", "importance"]] = "relevance"
    sort_order: Optional[Literal["asc", "desc"]] = "desc"


class SearchResult(Memory):
    """A search result with relevance score."""
    
    relevance_score: float = Field(ge=0, le=1)
    highlights: Optional[List[str]] = None


class Thread(BaseModel):
    """A thread object."""
    
    id: str
    name: str
    description: Optional[str] = None
    memory_ids: List[str]
    status: ThreadStatus
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    user_id: Optional[str] = None


class CreateThreadInput(BaseModel):
    """Input for creating a thread."""
    
    name: str
    description: Optional[str] = None
    memory_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[ThreadStatus] = ThreadStatus.ACTIVE


class UpdateThreadInput(BaseModel):
    """Input for updating a thread."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[ThreadStatus] = None


class ThreadStats(BaseModel):
    """Statistics for a thread."""
    
    memory_count: int
    memory_types: Dict[str, int]
    emotion_types: Dict[str, int]
    avg_importance: float
    follow_up_count: int
    earliest_memory: datetime
    latest_memory: datetime
    total_decisions: int
    total_questions: int
    total_action_items: int


class BatchCreateResult(BaseModel):
    """Result of batch create operation."""
    
    success: List[Memory]
    failed: List[Dict[str, Any]]
    success_count: int
    failed_count: int


class PaginatedResponse(BaseModel):
    """Paginated response."""
    
    data: List[Any]
    total: int
    limit: int
    offset: int
    has_more: bool


class Config(BaseModel):
    """Configuration for the Sovant client."""
    
    api_key: str
    base_url: str = "https://api.sovant.ai/v1"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0