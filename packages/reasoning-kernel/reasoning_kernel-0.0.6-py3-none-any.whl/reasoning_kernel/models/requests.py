"""
Request models for MSA API endpoints
"""

import html
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from ..core.constants import (
    MAX_SCENARIO_LENGTH,
    MIN_SCENARIO_LENGTH,
    MAX_CONTEXT_DEPTH,
    MAX_ARRAY_LENGTH,
    MAX_STRING_LENGTH,
    MAX_SESSION_ID_LENGTH,
    MAX_CONTEXT_KEYS,
    MAX_CONTEXT_KEY_LENGTH,
    DEFAULT_REASONING_TIMEOUT,
    MIN_EXECUTION_TIMEOUT,
    MAX_EXECUTION_TIMEOUT,
    DEFAULT_INFERENCE_SAMPLES,
    MIN_INFERENCE_SAMPLES,
    MAX_INFERENCE_SAMPLES,
    DEFAULT_INFERENCE_CHAINS,
    MIN_INFERENCE_CHAINS,
    MAX_INFERENCE_CHAINS,
    PATTERN_SESSION_ID,
    PRIORITY_LOW,
    PRIORITY_NORMAL,
    PRIORITY_HIGH,
    MODE_KNOWLEDGE,
    MODE_PROBABILISTIC,
    MODE_BOTH,
)

# Dangerous patterns for security validation
DANGEROUS_PATTERNS = [
    r"(?i)\b(eval|exec|import|__import__|compile|globals|locals|vars|dir|getattr|setattr|delattr|hasattr)\b",
    r"(?i)\b(open|file|input|raw_input)\b",
    r"(?i)\b(os\.|sys\.|subprocess|shlex|pickle|marshal|shelve)\b",
    r"(?i)<script[^>]*>.*?</script>",
    r"(?i)javascript:",
    r"(?i)vbscript:",
    r"\${.*}",  # Template injection
    r"{{.*}}",  # Template injection
]

SQL_INJECTION_PATTERNS = [
    r"(?i)\bunion\s+select\b",
    r"(?i)\bselect\s+.*\bfrom\b",
    r"(?i)\bdrop\s+table\b",
    r"(?i)\bdelete\s+from\b",
    r"(?i)'\s*(or|and)\s*'[^']*'\s*=\s*'",
]


def sanitize_html_content(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    if not isinstance(content, str):
        return content

    # Remove dangerous HTML tags using regex
    dangerous_tags = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"<form[^>]*>.*?</form>",
        r"<input[^>]*>",
        r"<button[^>]*>.*?</button>",
    ]

    # Remove dangerous attributes
    dangerous_attrs = [
        r'\s+on\w+\s*=\s*["\'][^"\']*["\']',  # onclick, onload, etc.
        r'\s+href\s*=\s*["\']javascript:[^"\']*["\']',
        r'\s+src\s*=\s*["\']javascript:[^"\']*["\']',
    ]

    # Clean content
    sanitized = content

    # Remove dangerous tags
    for tag_pattern in dangerous_tags:
        sanitized = re.sub(tag_pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    # Remove dangerous attributes
    for attr_pattern in dangerous_attrs:
        sanitized = re.sub(attr_pattern, "", sanitized, flags=re.IGNORECASE)

    # HTML escape any remaining content to prevent XSS
    sanitized = html.escape(sanitized, quote=False)  # Keep quotes for now

    return sanitized


def validate_no_dangerous_patterns(value: str, field_name: str) -> str:
    """Check for dangerous patterns in input"""
    if not isinstance(value, str):
        return value

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, value):
            raise ValueError(f"{field_name} contains potentially dangerous content")

    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value):
            raise ValueError(f"{field_name} contains potential SQL injection attempt")

    return value


def validate_context_depth(context: Any, current_depth: int = 0) -> None:
    """Recursively validate context object depth and structure"""
    if current_depth > MAX_CONTEXT_DEPTH:
        raise ValueError(f"Context object depth exceeds maximum allowed ({MAX_CONTEXT_DEPTH})")

    if isinstance(context, dict):
        if len(context) > MAX_CONTEXT_KEYS:  # Use constant instead of magic number
            raise ValueError("Context object has too many keys")

        for key, value in context.items():
            if not isinstance(key, str):
                raise ValueError("Context keys must be strings")

            if len(key) > MAX_CONTEXT_KEY_LENGTH:  # Use constant
                raise ValueError("Context key too long")

            validate_no_dangerous_patterns(key, "context key")

            if isinstance(value, (dict, list)):
                validate_context_depth(value, current_depth + 1)
            elif isinstance(value, str):
                if len(value) > MAX_STRING_LENGTH:
                    raise ValueError("Context string value too long")
                validate_no_dangerous_patterns(value, "context value")

    elif isinstance(context, list):
        if len(context) > MAX_ARRAY_LENGTH:
            raise ValueError("Context array too long")

        for i, item in enumerate(context):
            if isinstance(item, (dict, list)):
                validate_context_depth(item, current_depth + 1)
            elif isinstance(item, str):
                validate_no_dangerous_patterns(item, f"context array item {i}")


class MSAReasoningRequest(BaseModel):
    """Request model for MSA reasoning endpoint with enhanced security validation"""

    scenario: str = Field(
        ...,
        min_length=MIN_SCENARIO_LENGTH,
        max_length=MAX_SCENARIO_LENGTH,
        description="The scenario or question to reason about",
    )

    session_id: Optional[str] = Field(
        None,
        max_length=MAX_SESSION_ID_LENGTH,
        pattern=PATTERN_SESSION_ID,
        description="Optional session ID for tracking reasoning across requests (alphanumeric, underscore, hyphen only)",
    )

    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional additional context, constraints, or observations"
    )

    mode: Optional[str] = Field(MODE_BOTH, description="Reasoning mode: 'knowledge', 'probabilistic', or 'both'")

    priority: Optional[str] = Field(PRIORITY_NORMAL, description="Request priority: 'low', 'normal', 'high'")

    max_execution_time: Optional[int] = Field(
        DEFAULT_REASONING_TIMEOUT,
        ge=MIN_EXECUTION_TIMEOUT,
        le=MAX_EXECUTION_TIMEOUT,
        description="Maximum execution time in seconds",
    )

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        valid_modes = [MODE_KNOWLEDGE, MODE_PROBABILISTIC, MODE_BOTH]
        if v not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        valid_priorities = [PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_HIGH]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        return v

    @field_validator("scenario", mode="before")
    @classmethod
    def validate_scenario(cls, v):
        if not isinstance(v, str):
            raise ValueError("Scenario must be a string")

        v = v.strip()
        if not v:
            raise ValueError("Scenario cannot be empty")

        # Security validation
        validate_no_dangerous_patterns(v, "scenario")

        # Sanitize HTML content
        v = sanitize_html_content(v)

        return v

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v):
        if v is None:
            return None

        if not isinstance(v, str):
            raise ValueError("Session ID must be a string")

        v = v.strip()
        if not v:
            return None

        # Security check for session ID
        if not re.match(PATTERN_SESSION_ID, v):
            raise ValueError("Session ID can only contain alphanumeric characters, underscores, and hyphens")

        return v

    @field_validator("context")
    @classmethod
    def validate_context(cls, v):
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Context must be a dictionary")

        # Deep validation of context structure
        validate_context_depth(v)

        return v

    @model_validator(mode="after")
    def validate_request_combination(self):
        """Validate the combination of fields makes sense"""

        # If mode is probabilistic, we might need additional context
        if self.mode == "probabilistic" and not self.context:
            import warnings

            warnings.warn("Probabilistic mode often benefits from additional context")

        # Validate priority vs execution time
        if self.priority == "high" and self.max_execution_time and self.max_execution_time > 600:  # 10 minutes
            raise ValueError("High priority requests should have shorter execution times")

        return self


class KnowledgeExtractionRequest(BaseModel):
    """Request model for knowledge extraction only with enhanced validation"""

    scenario: str = Field(
        ...,
        min_length=MIN_SCENARIO_LENGTH,
        max_length=MAX_SCENARIO_LENGTH,
        description="The scenario to extract knowledge from",
    )

    extract_types: Optional[List[str]] = Field(
        None,
        description="Specific types of knowledge to extract: entities, relationships, causal_factors, constraints, domain_knowledge",
    )

    @field_validator("scenario", mode="before")
    @classmethod
    def validate_scenario(cls, v):
        if not isinstance(v, str):
            raise ValueError("Scenario must be a string")

        v = v.strip()
        if not v:
            raise ValueError("Scenario cannot be empty")

        # Security validation
        validate_no_dangerous_patterns(v, "scenario")

        # Sanitize HTML content
        v = sanitize_html_content(v)

        return v

    @field_validator("extract_types")
    @classmethod
    def validate_extract_types(cls, v):
        if v is None:
            return None

        if not isinstance(v, list):
            raise ValueError("Extract types must be a list")

        valid_types = {
            "entities",
            "relationships",
            "causal_factors",
            "constraints",
            "domain_knowledge",
            "temporal_patterns",
            "dependencies",
            "assumptions",
        }

        for extract_type in v:
            if not isinstance(extract_type, str):
                raise ValueError("Extract type must be a string")

            if extract_type not in valid_types:
                raise ValueError(f"Invalid extract type: {extract_type}. Must be one of {valid_types}")

        return v


class ProbabilisticModelRequest(BaseModel):
    """Request model for probabilistic model synthesis with enhanced validation"""

    model_specifications: Dict[str, Any] = Field(..., description="Model specifications from knowledge extraction")

    observations: Optional[Dict[str, Any]] = Field(
        None, description="Optional observations or evidence to condition the model on"
    )

    inference_samples: Optional[int] = Field(
        DEFAULT_INFERENCE_SAMPLES,
        ge=MIN_INFERENCE_SAMPLES,
        le=MAX_INFERENCE_SAMPLES,
        description="Number of MCMC samples for inference",
    )

    inference_chains: Optional[int] = Field(
        DEFAULT_INFERENCE_CHAINS,
        ge=MIN_INFERENCE_CHAINS,
        le=MAX_INFERENCE_CHAINS,
        description="Number of MCMC chains for inference",
    )

    random_seed: Optional[int] = Field(None, ge=0, le=2**31 - 1, description="Random seed for reproducible inference")

    @field_validator("model_specifications")
    @classmethod
    def validate_model_specifications(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Model specifications must be a dictionary")

        # Validate structure depth and content
        validate_context_depth(v)

        # Check for required fields in model specifications
        if not v:
            raise ValueError("Model specifications cannot be empty")

        return v

    @field_validator("observations")
    @classmethod
    def validate_observations(cls, v):
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Observations must be a dictionary")

        # Validate structure depth and content
        validate_context_depth(v)

        return v


class SessionStatusRequest(BaseModel):
    """Request model for session status queries with enhanced validation"""

    session_id: str = Field(
        ...,
        max_length=MAX_SESSION_ID_LENGTH,
        pattern=PATTERN_SESSION_ID,
        description="Session ID to query (alphanumeric, underscore, hyphen only)",
    )

    include_details: Optional[bool] = Field(False, description="Include detailed session information in response")

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v):
        if not isinstance(v, str):
            raise ValueError("Session ID must be a string")

        v = v.strip()
        if not v:
            raise ValueError("Session ID cannot be empty")

        # Security check for session ID
        if not re.match(PATTERN_SESSION_ID, v):
            raise ValueError("Session ID can only contain alphanumeric characters, underscores, and hyphens")

        return v
