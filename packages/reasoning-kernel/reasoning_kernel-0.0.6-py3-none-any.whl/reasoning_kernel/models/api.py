"""
API Models
==========

Pydantic models for API requests and responses.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ReasoningRequest(BaseModel):
    """Request model for reasoning endpoint"""
    
    vignette: str = Field(..., description="The scenario or vignette to analyze")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration parameters")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")
    
    class Config:
        schema_extra = {
            "example": {
                "vignette": "A person is deciding whether to invest in a new technology startup...",
                "config": {
                    "enable_parallel_stages": True,
                    "confidence_threshold": 0.8
                },
                "session_id": "session_123"
            }
        }


class ReasoningResponse(BaseModel):
    """Response model for reasoning endpoint"""
    
    success: bool = Field(..., description="Whether the reasoning was successful")
    session_id: str = Field(..., description="Session ID for this reasoning request")
    result: Optional[Dict[str, Any]] = Field(None, description="Reasoning results")
    error: Optional[str] = Field(None, description="Error message if reasoning failed")
    processing_time: float = Field(..., description="Total processing time in seconds")
    stage_results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from each MSA stage")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "session_id": "session_123",
                "result": {
                    "final_conclusion": "Investment recommendation: Proceed with caution",
                    "confidence_score": 0.85,
                    "key_insights": ["Market analysis shows potential", "Risk factors identified"]
                },
                "error": None,
                "processing_time": 12.5,
                "stage_results": [
                    {
                        "stage": "parse",
                        "success": True,
                        "confidence": 0.9
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Timestamp of health check")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Status of individual services")
    version: str = Field(..., description="Application version")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "services": {
                    "gpt5": {"status": "connected", "response_time": 0.5},
                    "redis": {"status": "connected", "response_time": 0.1},
                    "daytona": {"status": "connected", "response_time": 0.3}
                },
                "version": "2.0.0"
            }
        }


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    
    total_requests: int = Field(..., description="Total number of requests processed")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    average_processing_time: float = Field(..., description="Average processing time in seconds")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    memory_usage_mb: float = Field(..., description="Current memory usage in MB")
    
    class Config:
        schema_extra = {
            "example": {
                "total_requests": 1250,
                "successful_requests": 1200,
                "failed_requests": 50,
                "average_processing_time": 8.5,
                "uptime_seconds": 86400,
                "memory_usage_mb": 512.5
            }
        }


class StreamingMessage(BaseModel):
    """Model for streaming messages"""
    
    type: str = Field(..., description="Message type (stage_start, stage_complete, progress, error, complete)")
    stage: Optional[str] = Field(None, description="Current MSA stage")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    timestamp: str = Field(..., description="Message timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "stage_complete",
                "stage": "parse",
                "progress": 20.0,
                "message": "Parse stage completed successfully",
                "data": {
                    "entities_found": 15,
                    "confidence": 0.92
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid input provided",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "vignette",
                    "issue": "Field is required"
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
