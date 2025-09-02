"""Pydantic models for Skald feedback system."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import inspect

from pydantic import BaseModel, Field, field_validator, computed_field


class ToolStatus(str, Enum):
    """Status of a tool execution."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class ExecutionContext(str, Enum):
    """Type of execution being monitored."""
    MCP_TOOL = "mcp_tool"
    FUNCTION = "function" 
    SHELL_COMMAND = "shell_command"
    HTTP_REQUEST = "http_request"


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


class ExecutionMetadata(BaseModel):
    """Universal execution metadata for any monitored operation."""
    
    # Core identification
    trace_id: str = Field(..., description="UUID trace ID")
    execution_context: ExecutionContext = Field(..., description="Type of execution")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Context-specific identification
    name: str = Field(..., description="Name of function, command, or tool")
    module_name: Optional[str] = Field(None, description="Module name for functions")
    file_path: Optional[str] = Field(None, description="File path for functions") 
    line_number: Optional[int] = Field(None, description="Line number for functions")
    command_line: Optional[str] = Field(None, description="Full command line for shell commands")
    working_directory: Optional[str] = Field(None, description="Working directory for shell commands")
    
    # Execution details
    status: ToolStatus = Field(..., description="Execution status")
    latency_ms: float = Field(..., ge=0, description="Execution latency in milliseconds")
    memory_delta_mb: Optional[float] = Field(None, description="Memory usage change in MB")
    cpu_percent: Optional[float] = Field(None, ge=0, description="CPU usage percentage during execution")
    
    # Input/Output metrics
    input_args: Dict[str, Any] = Field(default_factory=dict, description="Input arguments (potentially redacted)")
    input_size_bytes: int = Field(default=0, ge=0, description="Size of input in bytes")
    output_size_bytes: int = Field(default=0, ge=0, description="Size of output in bytes")
    return_value_type: Optional[str] = Field(None, description="Type of return value")
    
    # Error information
    error_type: Optional[str] = Field(None, description="Exception type if error occurred")
    error_message: Optional[str] = Field(None, description="Error message if error occurred")
    stack_trace: Optional[str] = Field(None, description="Stack trace if error occurred")
    
    # Process information (for shell commands)
    process_id: Optional[int] = Field(None, description="Process ID for shell commands")
    exit_code: Optional[int] = Field(None, description="Exit code for shell commands")
    
    # Feedback invitation
    invite_feedback: bool = Field(default=False, description="Whether feedback is invited")
    opt_out: bool = Field(default=False, description="Whether collection was opted out")
    
    # Privacy controls
    redaction_applied: bool = Field(default=False, description="Whether redaction was applied")
    redaction_rule_id: Optional[str] = Field(None, description="ID of applied redaction rule")
    
    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("trace_id must be a valid UUID")
        return v
    
    @classmethod
    def from_function(
        cls,
        func: Callable,
        args: tuple,
        kwargs: dict,
        result: Any = None,
        error: Optional[Exception] = None,
        latency_ms: float = 0.0,
        trace_id: Optional[str] = None,
        **extra_fields
    ) -> 'ExecutionMetadata':
        """Create metadata from function execution."""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
            
        # Get function information
        func_name = getattr(func, '__name__', str(func))
        module_name = getattr(func, '__module__', None)
        
        # Try to get file and line info
        file_path = None
        line_number = None
        try:
            source_info = inspect.getsourcefile(func)
            if source_info:
                file_path = source_info
            line_info = inspect.getsourcelines(func)
            if line_info:
                line_number = line_info[1]
        except (OSError, TypeError):
            pass
        
        # Calculate input size (rough estimate)
        input_size = len(str(args)) + len(str(kwargs))
        output_size = len(str(result)) if result is not None else 0
        
        # Determine status and error info
        status = ToolStatus.SUCCESS if error is None else ToolStatus.ERROR
        error_type = type(error).__name__ if error else None
        error_message = str(error) if error else None
        
        return cls(
            trace_id=trace_id,
            execution_context=ExecutionContext.FUNCTION,
            name=func_name,
            module_name=module_name,
            file_path=file_path,
            line_number=line_number,
            status=status,
            latency_ms=latency_ms,
            input_args={"args": list(args), "kwargs": kwargs},
            input_size_bytes=input_size,
            output_size_bytes=output_size,
            return_value_type=type(result).__name__ if result is not None else None,
            error_type=error_type,
            error_message=error_message,
            **extra_fields
        )
    
    @classmethod
    def from_shell_command(
        cls,
        command: str,
        working_dir: Optional[str] = None,
        exit_code: Optional[int] = None,
        process_id: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        latency_ms: float = 0.0,
        trace_id: Optional[str] = None,
        **extra_fields
    ) -> 'ExecutionMetadata':
        """Create metadata from shell command execution."""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        # Determine status from exit code
        if exit_code is None:
            status = ToolStatus.SUCCESS  # Still running or unknown
        elif exit_code == 0:
            status = ToolStatus.SUCCESS
        else:
            status = ToolStatus.ERROR
            
        # Calculate output sizes
        stdout_size = len(stdout.encode('utf-8')) if stdout else 0
        stderr_size = len(stderr.encode('utf-8')) if stderr else 0
        output_size = stdout_size + stderr_size
        
        return cls(
            trace_id=trace_id,
            execution_context=ExecutionContext.SHELL_COMMAND,
            name=command.split()[0] if command.split() else command,
            command_line=command,
            working_directory=working_dir,
            status=status,
            latency_ms=latency_ms,
            input_size_bytes=len(command.encode('utf-8')),
            output_size_bytes=output_size,
            process_id=process_id,
            exit_code=exit_code,
            error_message=stderr if stderr and exit_code != 0 else None,
            **extra_fields
        )


class UniversalFeedbackReport(BaseModel):
    """Universal feedback report that works for any execution context."""
    
    trace_id: str = Field(..., description="UUID trace ID of the execution")
    execution_context: ExecutionContext = Field(..., description="Type of execution")
    
    # Core feedback dimensions (1-5 scale)
    effectiveness: int = Field(..., ge=1, le=5, description="How effective was this execution (1-5)")
    efficiency: int = Field(..., ge=1, le=5, description="How efficient was this execution (1-5)")
    clarity: int = Field(..., ge=1, le=5, description="How clear was the output/result (1-5)")
    reliability: int = Field(..., ge=1, le=5, description="How reliable was this execution (1-5)")
    
    # Context-specific feedback
    ease_of_use: Optional[int] = Field(None, ge=1, le=5, description="Ease of use (for functions/commands)")
    documentation_quality: Optional[int] = Field(None, ge=1, le=5, description="Quality of documentation")
    error_handling: Optional[int] = Field(None, ge=1, le=5, description="Quality of error handling")
    
    # Overall assessment
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this feedback (0.0-1.0)")
    would_recommend: bool = Field(..., description="Would you recommend this to others?")
    
    # Improvement suggestions
    better_alternative: BetterAlternative = Field(
        default=BetterAlternative.NO_ALTERNATIVE,
        description="Suggestion for a better alternative approach"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Up to 5 specific suggestions for improvement"
    )
    
    # Open-ended feedback
    what_worked_well: str = Field(default="", description="What worked well")
    what_could_improve: str = Field(default="", description="What could be improved")
    notes: str = Field(default="", description="Additional notes")
    
    # Context for this feedback
    user_expertise_level: Optional[str] = Field(None, description="Beginner/Intermediate/Advanced")
    use_case_category: Optional[str] = Field(None, description="Category of use case")
    
    @field_validator("suggestions")
    @classmethod
    def validate_suggestions(cls, v: List[str]) -> List[str]:
        """Validate suggestions are not too long and limit to 5."""
        if len(v) > 5:
            raise ValueError("Maximum 5 suggestions allowed")
        
        for suggestion in v:
            if len(suggestion) > 200:
                raise ValueError("Each suggestion must be ≤200 characters")
        
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
    
    @field_validator("what_worked_well", "what_could_improve", "notes")
    @classmethod
    def validate_text_fields(cls, v: str) -> str:
        """Validate text fields are not too long."""
        if len(v) > 1000:
            raise ValueError("Text fields must be ≤1000 characters")
        return v