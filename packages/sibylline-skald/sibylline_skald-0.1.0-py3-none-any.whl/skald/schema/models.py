"""Pydantic models for Skald feedback system."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, computed_field


class ToolStatus(str, Enum):
    """Status of a tool execution."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class BetterAlternative(str, Enum):
    """Better alternative suggestion for feedback."""
    DIFFERENT_TOOL = "different_tool"
    DIFFERENT_PARAMETERS = "different_parameters"
    SEQUENCE_OF_TOOLS = "sequence_of_tools"
    MANUAL_INTERVENTION = "manual_intervention"
    NO_ALTERNATIVE = ""


class FeedbackReport(BaseModel):
    """Structured feedback report for a tool execution.
    
    This matches the JSON schema defined in the arbiter specification.
    """
    
    trace_id: str = Field(..., description="UUID trace ID of the tool execution")
    helpfulness: int = Field(..., ge=1, le=5, description="How helpful was the tool (1-5)")
    fit: int = Field(..., ge=1, le=5, description="How well did the tool fit the task (1-5)")
    clarity: int = Field(..., ge=1, le=5, description="How clear was the tool output (1-5)")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in this feedback (0.0-1.0)"
    )
    better_alternative: BetterAlternative = Field(
        default=BetterAlternative.NO_ALTERNATIVE,
        description="Suggestion for a better alternative approach"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Up to 3 short suggestions for improvement"
    )
    notes: str = Field(default="", description="Optional additional notes")
    
    @field_validator("suggestions")
    @classmethod
    def validate_suggestions(cls, v: List[str]) -> List[str]:
        """Validate suggestions are not too long and limit to 3."""
        if len(v) > 3:
            raise ValueError("Maximum 3 suggestions allowed")
        
        for suggestion in v:
            if len(suggestion) > 100:
                raise ValueError("Each suggestion must be ≤100 characters")
        
        return v
    
    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("trace_id must be a valid UUID")
        return v


class ToolRunMetadata(BaseModel):
    """Metadata for a tool execution run."""
    
    trace_id: str = Field(..., description="UUID trace ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Execution timestamp")
    agent_id: str = Field(..., description="ID of the agent making the call")
    tool_name: str = Field(..., description="Name of the tool being executed")
    status: ToolStatus = Field(..., description="Execution status")
    latency_ms: float = Field(..., ge=0, description="Execution latency in milliseconds")
    output_bytes: int = Field(..., ge=0, description="Size of output in bytes")
    invite_feedback: bool = Field(..., description="Whether feedback is invited")
    opt_out: bool = Field(default=False, description="Whether collection was opted out")
    args_redacted: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Redacted tool arguments"
    )
    
    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("trace_id must be a valid UUID")
        return v

class EventType(str, Enum):
    """Types of events in the streaming system."""
    TOOL_RUN_STARTED = "tool_run_started"
    TOOL_RUN_FINISHED = "tool_run_finished" 
    TOOL_RUN_ERROR = "tool_run_error"
    FEEDBACK_SUBMITTED = "feedback_submitted"


class ToolRunMetadataV2(BaseModel):
    """Enhanced metadata for tool execution runs with v2 schema."""
    
    # Schema versioning
    schema_version: int = Field(default=2, description="Schema version")
    
    # Core event fields
    event_id: str = Field(..., description="Unique event identifier (UUIDv7)")
    trace_id: str = Field(..., description="Links events in the same trace")
    span_id: str = Field(..., description="Current span identifier")
    parent_span_id: Optional[str] = Field(None, description="Parent span identifier")
    event_type: EventType = Field(..., description="Type of event being recorded")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event occurrence time"
    )
    
    # Context fields  
    agent_session_id: Optional[str] = Field(None, description="Agent session identifier")
    mcp_id: Optional[str] = Field(None, description="MCP server identifier")
    tool_name: str = Field(..., description="Name of the tool being invoked")
    tool_version: Optional[str] = Field(None, description="Version of the tool")
    model_id: Optional[str] = Field(None, description="AI model identifier if known")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    
    # Timing breakdown fields
    t_request: datetime = Field(..., description="Request initiation time")
    t_upstream_start: Optional[datetime] = Field(None, description="Upstream call start time")
    t_upstream_end: Optional[datetime] = Field(None, description="Upstream call end time") 
    t_response: datetime = Field(..., description="Response completion time")
    
    # Computed timing breakdowns (milliseconds)
    queue_ms: Optional[float] = Field(None, ge=0, description="Time spent in queue")
    network_ms: Optional[float] = Field(None, ge=0, description="Network latency")
    server_ms: Optional[float] = Field(None, ge=0, description="Server processing time")
    serialize_ms: Optional[float] = Field(None, ge=0, description="Serialization time")
    
    # Size metrics
    in_bytes: Optional[int] = Field(None, ge=0, description="Input payload size in bytes")
    out_bytes: Optional[int] = Field(None, ge=0, description="Output payload size in bytes")
    
    # Error information
    error_class: Optional[str] = Field(None, description="Error classification")
    error_code: Optional[str] = Field(None, description="Specific error code")
    
    # Legacy v1 fields (for backward compatibility)
    status: ToolStatus = Field(..., description="Execution status")
    latency_ms: float = Field(..., ge=0, description="Execution latency in milliseconds")
    output_bytes: int = Field(..., ge=0, description="Size of output in bytes")
    invite_feedback: bool = Field(..., description="Whether feedback is invited")
    opt_out: bool = Field(default=False, description="Whether collection was opted out")
    
    # Privacy & security
    args_redacted: Dict[str, Any] = Field(
        default_factory=dict,
        description="Redacted tool arguments"
    )
    redaction_rule_id: Optional[str] = Field(None, description="Identifier of redaction rule applied")
    
    @field_validator("event_id")
    @classmethod
    def validate_event_id(cls, v: str) -> str:
        """Validate event_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("event_id must be a valid UUID")
        return v
        
    @field_validator("trace_id")  
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("trace_id must be a valid UUID")
        return v
        
    @field_validator("span_id")
    @classmethod 
    def validate_span_id(cls, v: str) -> str:
        """Validate span_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("span_id must be a valid UUID")
        return v
        
    @field_validator("parent_span_id")
    @classmethod
    def validate_parent_span_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate parent_span_id is a valid UUID if provided."""
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError("parent_span_id must be a valid UUID")
        return v
        
    @computed_field
    @property
    def total_latency_ms(self) -> float:
        """Computed total latency from timing breakdown."""
        if self.queue_ms and self.network_ms and self.server_ms and self.serialize_ms:
            return self.queue_ms + self.network_ms + self.server_ms + self.serialize_ms
        return self.latency_ms


class BatchEventRequest(BaseModel):
    """Request model for batch event submission."""
    
    events: List[ToolRunMetadataV2] = Field(..., min_length=1, max_length=1000)
    
    @field_validator("events")
    @classmethod
    def validate_events(cls, v: List[ToolRunMetadataV2]) -> List[ToolRunMetadataV2]:
        """Validate events list."""
        if len(v) == 0:
            raise ValueError("events list cannot be empty")
        if len(v) > 1000:
            raise ValueError("events list cannot exceed 1000 events")
        return v


class BatchEventResponse(BaseModel):
    """Response model for batch event submission."""
    
    accepted: int = Field(..., ge=0, description="Number of accepted events")
    rejected: int = Field(..., ge=0, description="Number of rejected events")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Per-event errors with idx and reason"
    )
    
    @field_validator("errors")
    @classmethod
    def validate_errors(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate error entries have required fields."""
        for error in v:
            if "idx" not in error or "reason" not in error:
                raise ValueError("Each error must have 'idx' and 'reason' fields")
            if not isinstance(error["idx"], int) or error["idx"] < 0:
                raise ValueError("Error idx must be a non-negative integer")
            if not isinstance(error["reason"], str):
                raise ValueError("Error reason must be a string")
        return v


class InvitePolicy(BaseModel):
    """Configuration for when to invite feedback."""
    
    error: bool = Field(default=True, description="Invite on errors")
    timeout: bool = Field(default=True, description="Invite on timeouts")
    p95_ms: float = Field(default=5000.0, description="Latency threshold for invites (ms)")
    large_output_kb: float = Field(
        default=256.0, 
        description="Output size threshold for invites (KB)"
    )
    sample_neutral: float = Field(
        default=0.1, 
        ge=0.0, 
        le=1.0, 
        description="Sampling rate for neutral calls (0.0-1.0)"
    )


class MCPResponse(BaseModel):
    """MCP tool response with Skald metadata."""
    
    content: List[Dict[str, Any]] = Field(default_factory=list)
    isError: bool = Field(default=False)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def with_skald_meta(
        cls, 
        content: List[Dict[str, Any]], 
        trace_id: str, 
        invite_feedback: bool,
        is_error: bool = False,
        original_meta: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """Create response with Skald metadata merged in."""
        meta = original_meta.copy() if original_meta else {}
        meta.update({
            "trace_id": trace_id,
            "invite_feedback": invite_feedback
        })
        
        return cls(
            content=content,
            isError=is_error,
            meta=meta
        )