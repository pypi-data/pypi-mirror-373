"""
Annotation models for collaborative reasoning chain analysis
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic import Field


class AnnotationType(str, Enum):
    """Types of annotations that can be made on reasoning chains"""
    COMMENT = "comment"
    QUESTION = "question"
    INSIGHT = "insight"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    HIGHLIGHT = "highlight"

class AnnotationTarget(str, Enum):
    """What part of the reasoning chain the annotation targets"""
    FULL_CHAIN = "full_chain"
    STAGE = "stage"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    CONCLUSION = "conclusion"

class User(BaseModel):
    """User information for annotations"""
    id: str
    name: str
    avatar_url: Optional[str] = None
    color: str = "#3B82F6"  # Default blue color

class AnnotationPosition(BaseModel):
    """Position information for the annotation"""
    stage: Optional[str] = None  # Which reasoning stage
    element_id: Optional[str] = None  # Specific element within stage
    text_range: Optional[Dict[str, int]] = None  # For text selections
    coordinates: Optional[Dict[str, float]] = None  # For visual elements

class Annotation(BaseModel):
    """Single annotation on a reasoning chain"""
    id: str = Field(default_factory=lambda: f"ann_{int(datetime.now().timestamp() * 1000)}")
    reasoning_chain_id: str
    user: User
    type: AnnotationType
    target: AnnotationTarget
    position: AnnotationPosition
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    resolved: bool = False
    replies: List["AnnotationReply"] = Field(default_factory=list)
    votes: int = 0
    voters: List[str] = Field(default_factory=list)

class AnnotationReply(BaseModel):
    """Reply to an annotation"""
    id: str = Field(default_factory=lambda: f"reply_{int(datetime.now().timestamp() * 1000)}")
    user: User
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

class AnnotationUpdate(BaseModel):
    """Update to an existing annotation"""
    content: Optional[str] = None
    resolved: Optional[bool] = None

class CreateAnnotationRequest(BaseModel):
    """Request to create a new annotation"""
    reasoning_chain_id: str
    type: AnnotationType
    target: AnnotationTarget
    position: AnnotationPosition
    content: str
    user: User

class AnnotationEvent(BaseModel):
    """Real-time event for annotation updates"""
    event_type: str  # created, updated, deleted, reply_added
    annotation: Annotation
    user: User
    timestamp: datetime = Field(default_factory=datetime.now)

# Update forward references
Annotation.model_rebuild()