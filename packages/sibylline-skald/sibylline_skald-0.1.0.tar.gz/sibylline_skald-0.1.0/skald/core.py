"""Core SurveyingProxy implementation for Skald."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

import structlog

from skald.decorators import is_opted_out
from skald.emitter import EmitterConfig, SkaldEmitter
from skald.schema.models import (
    EventType,
    FeedbackReport,
    InvitePolicy,
    MCPResponse,
    ToolRunMetadata,
    ToolStatus,
)
from skald.storage.base import StorageBackend
from skald.storage.sqlite import SQLiteStorage

logger = structlog.get_logger(__name__)


class SurveyingProxy:
    """Main proxy class that wraps MCP servers for feedback collection.
    
    This class intercepts MCP tool calls, adds trace IDs and metrics collection,
    and provides a feedback.report tool for structured feedback collection.
    """
    
    def __init__(
        self,
        upstream: Any,  # MCP server instance
        store: Union[str, StorageBackend] = "sqlite:///skald_feedback.db",
        invite_policy: Optional[Dict[str, Any]] = None,
        sample_neutral: float = 0.1,
        ttl_hours: int = 24,
        agent_id_extractor: Optional[Callable[[Dict[str, Any]], str]] = None,
        redactor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        emitter_config: Optional[EmitterConfig] = None,
        enable_streaming: bool = False,
    ) -> None:
        """Initialize the SurveyingProxy.
        
        Args:
            upstream: The upstream MCP server to wrap
            store: Storage backend (string for SQLite path or StorageBackend instance)
            invite_policy: Policy for when to invite feedback
            sample_neutral: Sampling rate for neutral calls (0.0-1.0)
            ttl_hours: TTL for stored data in hours
            agent_id_extractor: Function to extract agent ID from request context
            redactor: Function to redact sensitive data from tool arguments
            emitter_config: Configuration for event streaming emitter
            enable_streaming: Whether to enable event streaming (v2 feature)
        """
        self.upstream = upstream
        self.ttl_hours = ttl_hours
        self.sample_neutral = sample_neutral
        self.enable_streaming = enable_streaming
        
        # Initialize storage backend
        if isinstance(store, str):
            if store.startswith("sqlite:///"):
                db_path = store[10:]  # Remove sqlite:/// prefix
                self.storage = SQLiteStorage(db_path)
            else:
                raise ValueError(f"Unsupported store format: {store}")
        else:
            self.storage = store
        
        # Initialize invite policy
        default_policy = {
            "error": True,
            "timeout": True,
            "p95_ms": 5000.0,
            "large_output_kb": 256.0,
        }
        policy_dict = {**default_policy, **(invite_policy or {})}
        self.invite_policy = InvitePolicy(**policy_dict, sample_neutral=sample_neutral)
        
        # Set up extractors
        self.agent_id_extractor = agent_id_extractor or self._default_agent_id_extractor
        self.redactor = redactor or self._default_redactor
        
        # Initialize emitter if streaming is enabled
        self.emitter = None
        if self.enable_streaming:
            self.emitter = SkaldEmitter(emitter_config or EmitterConfig())
        
        # Track if we've been initialized
        self._initialized = False
        
        # Add our feedback tool to the upstream server
        self._register_feedback_tool()
    
    async def initialize(self) -> None:
        """Initialize the proxy and storage backend."""
        await self.storage.initialize()
        
        # Start emitter if streaming is enabled
        if self.emitter:
            await self.emitter.start()
            
        self._initialized = True
        logger.info("SurveyingProxy initialized", streaming_enabled=self.enable_streaming)
    
    async def close(self) -> None:
        """Close the proxy and clean up resources."""
        # Stop emitter first to flush remaining events
        if self.emitter:
            await self.emitter.stop()
            
        if self.storage:
            await self.storage.close()
            
        self._initialized = False
        logger.info("SurveyingProxy closed")
    
    def _default_agent_id_extractor(self, context: Dict[str, Any]) -> str:
        """Default agent ID extractor."""
        # Try common headers/fields for agent identification
        return (
            context.get("agent_id")
            or context.get("user_id") 
            or context.get("client_id")
            or "unknown"
        )
    
    def _default_redactor(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Default data redactor - removes common sensitive fields."""
        redacted = args.copy()
        
        sensitive_keys = {
            "password", "token", "key", "secret", "credential",
            "api_key", "auth", "authorization", "bearer"
        }
        
        for key in list(redacted.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                redacted[key] = "[REDACTED]"
        
        return redacted
    
    def _should_invite_feedback(
        self, 
        status: ToolStatus, 
        latency_ms: float, 
        output_bytes: int
    ) -> bool:
        """Determine if feedback should be invited for this tool call."""
        # Always invite on errors or timeouts
        if self.invite_policy.error and status == ToolStatus.ERROR:
            return True
        
        if self.invite_policy.timeout and status == ToolStatus.TIMEOUT:
            return True
        
        # Invite on high latency
        if latency_ms > self.invite_policy.p95_ms:
            return True
        
        # Invite on large output
        if output_bytes > (self.invite_policy.large_output_kb * 1024):
            return True
        
        # Sample neutral calls
        if status == ToolStatus.SUCCESS:
            import random
            return random.random() < self.invite_policy.sample_neutral
        
        return False
    
    def _register_feedback_tool(self) -> None:
        """Register the feedback.report tool with the upstream server."""
        # This would need to be adapted based on the specific MCP server implementation
        # For now, we'll add it to our own tool registry
        self._feedback_tool_registered = True
    
    async def call_tool(
        self, 
        name: str, 
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """Intercept and wrap MCP tool calls.
        
        This is the main interception point where we add tracing and metrics.
        """
        if not self._initialized:
            await self.initialize()
        
        context = context or {}
        
        # Handle feedback.report tool specially
        if name == "feedback.report":
            return await self._handle_feedback_report(arguments, context)
        
        # Check if opted out
        opted_out, opt_out_reason = is_opted_out()
        
        # Generate trace ID and span ID
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        start_time = time.time()
        t_request = datetime.now(timezone.utc)
        agent_id = self.agent_id_extractor(context)
        
        # Emit tool_run_started event if streaming is enabled
        if self.emitter and not opted_out:
            asyncio.create_task(self.emitter.emit_event(
                event_type=EventType.TOOL_RUN_STARTED,
                trace_id=trace_id,
                tool_name=name,
                span_id=span_id,
                agent_session_id=context.get("agent_session_id"),
                mcp_id=context.get("mcp_id"),
                tool_version=context.get("tool_version"),
                model_id=context.get("model_id"),
                tenant_id=context.get("tenant_id", self.emitter.config.tenant_id),
                t_request=t_request,
                timestamp=t_request,
                status=ToolStatus.SUCCESS,  # Started successfully 
                latency_ms=0.0,
                output_bytes=0,
                invite_feedback=False,
                opt_out=opted_out,
                args_redacted=self.redactor(arguments),
                in_bytes=len(json.dumps(arguments).encode('utf-8'))
            ))
        
        try:
            # Call the upstream tool
            t_upstream_start = datetime.now(timezone.utc)
            response = await self._call_upstream_tool(name, arguments)
            t_upstream_end = datetime.now(timezone.utc)
            
            # Calculate metrics
            end_time = time.time()
            t_response = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time) * 1000
            
            # Calculate output size
            output_bytes = len(json.dumps(response.content).encode('utf-8'))
            
            status = ToolStatus.ERROR if response.isError else ToolStatus.SUCCESS
            
            # Determine if we should invite feedback
            invite_feedback = (
                not opted_out and 
                self._should_invite_feedback(status, latency_ms, output_bytes)
            )
            
            # Calculate timing breakdowns
            queue_ms = 0.0  # Not implemented yet
            network_ms = (t_upstream_end - t_upstream_start).total_seconds() * 1000
            server_ms = latency_ms - network_ms  # Approximate
            serialize_ms = 0.0  # Not implemented yet
            
            # Store metadata if not opted out (v1 storage)
            if not opted_out:
                metadata = ToolRunMetadata(
                    trace_id=trace_id,
                    timestamp=t_request,
                    agent_id=agent_id,
                    tool_name=name,
                    status=status,
                    latency_ms=latency_ms,
                    output_bytes=output_bytes,
                    invite_feedback=invite_feedback,
                    opt_out=False,
                    args_redacted=self.redactor(arguments)
                )
                
                # Store in background to not block response
                asyncio.create_task(self._store_metadata_safely(metadata))
            
            # Emit tool_run_finished event if streaming is enabled
            if self.emitter and not opted_out:
                event_type = EventType.TOOL_RUN_ERROR if response.isError else EventType.TOOL_RUN_FINISHED
                asyncio.create_task(self.emitter.emit_event(
                    event_type=event_type,
                    trace_id=trace_id,
                    tool_name=name,
                    span_id=span_id,
                    agent_session_id=context.get("agent_session_id"),
                    mcp_id=context.get("mcp_id"), 
                    tool_version=context.get("tool_version"),
                    model_id=context.get("model_id"),
                    tenant_id=context.get("tenant_id", self.emitter.config.tenant_id),
                    t_request=t_request,
                    t_upstream_start=t_upstream_start,
                    t_upstream_end=t_upstream_end,
                    t_response=t_response,
                    timestamp=t_response,
                    queue_ms=queue_ms,
                    network_ms=network_ms,
                    server_ms=server_ms,
                    serialize_ms=serialize_ms,
                    in_bytes=len(json.dumps(arguments).encode('utf-8')),
                    out_bytes=output_bytes,
                    error_class=response.__class__.__name__ if response.isError else None,
                    status=status,
                    latency_ms=latency_ms,
                    output_bytes=output_bytes,
                    invite_feedback=invite_feedback,
                    opt_out=opted_out,
                    args_redacted=self.redactor(arguments)
                ))
            
            # Add Skald metadata to response
            return MCPResponse.with_skald_meta(
                content=response.content,
                trace_id=trace_id,
                invite_feedback=invite_feedback and not opted_out,
                is_error=response.isError,
                original_meta=response.meta
            )
            
        except asyncio.TimeoutError:
            # Handle timeout
            end_time = time.time()
            t_response = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time) * 1000
            
            if not opted_out:
                metadata = ToolRunMetadata(
                    trace_id=trace_id,
                    timestamp=t_request,
                    agent_id=agent_id,
                    tool_name=name,
                    status=ToolStatus.TIMEOUT,
                    latency_ms=latency_ms,
                    output_bytes=0,
                    invite_feedback=True,
                    opt_out=False,
                    args_redacted=self.redactor(arguments)
                )
                
                asyncio.create_task(self._store_metadata_safely(metadata))
            
            # Emit timeout error event if streaming is enabled
            if self.emitter and not opted_out:
                asyncio.create_task(self.emitter.emit_event(
                    event_type=EventType.TOOL_RUN_ERROR,
                    trace_id=trace_id,
                    tool_name=name,
                    span_id=span_id,
                    t_request=t_request,
                    t_response=t_response,
                    timestamp=t_response,
                    error_class="TimeoutError",
                    error_code="TIMEOUT",
                    status=ToolStatus.TIMEOUT,
                    latency_ms=latency_ms,
                    output_bytes=0,
                    invite_feedback=True,
                    opt_out=opted_out,
                    args_redacted=self.redactor(arguments)
                ))
            
            # Return timeout response
            return MCPResponse.with_skald_meta(
                content=[{"type": "text", "text": "Tool call timed out"}],
                trace_id=trace_id,
                invite_feedback=not opted_out,
                is_error=True
            )
            
        except Exception as e:
            # Handle other errors
            end_time = time.time()
            t_response = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time) * 1000
            
            if not opted_out:
                metadata = ToolRunMetadata(
                    trace_id=trace_id,
                    timestamp=t_request,
                    agent_id=agent_id,
                    tool_name=name,
                    status=ToolStatus.ERROR,
                    latency_ms=latency_ms,
                    output_bytes=0,
                    invite_feedback=True,
                    opt_out=False,
                    args_redacted=self.redactor(arguments)
                )
                
                asyncio.create_task(self._store_metadata_safely(metadata))
            
            # Emit error event if streaming is enabled
            if self.emitter and not opted_out:
                asyncio.create_task(self.emitter.emit_event(
                    event_type=EventType.TOOL_RUN_ERROR,
                    trace_id=trace_id,
                    tool_name=name,
                    span_id=span_id,
                    t_request=t_request,
                    t_response=t_response,
                    timestamp=t_response,
                    error_class=e.__class__.__name__,
                    error_code=str(e),
                    status=ToolStatus.ERROR,
                    latency_ms=latency_ms,
                    output_bytes=0,
                    invite_feedback=True,
                    opt_out=opted_out,
                    args_redacted=self.redactor(arguments)
                ))
            
            # Return error response
            return MCPResponse.with_skald_meta(
                content=[{"type": "text", "text": f"Tool call failed: {str(e)}"}],
                trace_id=trace_id,
                invite_feedback=not opted_out,
                is_error=True
            )
    
    async def _call_upstream_tool(
        self, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> MCPResponse:
        """Call the upstream MCP tool."""
        # This needs to be adapted based on the upstream MCP server interface
        # For now, assume it has a call_tool method
        try:
            if hasattr(self.upstream, 'call_tool'):
                response = await self.upstream.call_tool(name, arguments)
                # Convert to our MCPResponse format
                if hasattr(response, 'content'):
                    return MCPResponse(
                        content=response.content,
                        isError=getattr(response, 'isError', False),
                        meta=getattr(response, 'meta', {})
                    )
                else:
                    # Assume response is the content directly
                    return MCPResponse(content=[{"type": "text", "text": str(response)}])
            else:
                raise AttributeError("Upstream server does not have call_tool method")
        except Exception as e:
            logger.error("Upstream tool call failed", tool=name, error=str(e))
            raise
    
    async def _handle_feedback_report(
        self, 
        arguments: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MCPResponse:
        """Handle the feedback.report tool call."""
        try:
            # Validate and parse feedback
            feedback = FeedbackReport(**arguments)
            agent_id = self.agent_id_extractor(context)
            
            # Validate trace_id exists and is not expired
            tool_run = await self.storage.get_tool_run(feedback.trace_id)
            if not tool_run:
                return MCPResponse(
                    content=[{
                        "type": "text", 
                        "text": f"No tool run found for trace_id: {feedback.trace_id}"
                    }],
                    isError=True
                )
            
            # Check if feedback is within TTL window
            age_hours = (datetime.now(timezone.utc) - tool_run.timestamp).total_seconds() / 3600
            if age_hours > self.ttl_hours:
                return MCPResponse(
                    content=[{
                        "type": "text",
                        "text": f"Feedback window expired for trace_id: {feedback.trace_id}"
                    }],
                    isError=True
                )
            
            # Store the feedback
            await self.storage.store_feedback(feedback, agent_id)
            
            # Emit feedback_submitted event if streaming is enabled
            if self.emitter:
                asyncio.create_task(self.emitter.emit_event(
                    event_type=EventType.FEEDBACK_SUBMITTED,
                    trace_id=feedback.trace_id,
                    tool_name="feedback.report",
                    span_id=str(uuid.uuid4()),
                    agent_session_id=context.get("agent_session_id"),
                    timestamp=datetime.now(timezone.utc),
                    tenant_id=context.get("tenant_id", self.emitter.config.tenant_id),
                    status=ToolStatus.SUCCESS,
                    latency_ms=0.0,  # Feedback submission latency not tracked
                    output_bytes=len(json.dumps(feedback.model_dump()).encode('utf-8')),
                    invite_feedback=False,
                    opt_out=False,
                    args_redacted={"feedback_summary": f"helpfulness={feedback.helpfulness}, fit={feedback.fit}, clarity={feedback.clarity}"}
                ))
            
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Feedback recorded for trace_id: {feedback.trace_id}"
                }]
            )
            
        except Exception as e:
            logger.error("Failed to handle feedback report", error=str(e))
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Failed to record feedback: {str(e)}"
                }],
                isError=True
            )
    
    async def _store_metadata_safely(self, metadata: ToolRunMetadata) -> None:
        """Store metadata with error handling."""
        try:
            await self.storage.store_tool_run(metadata)
        except Exception as e:
            logger.error("Failed to store tool run metadata", 
                        trace_id=metadata.trace_id, error=str(e))
    
    async def cleanup_expired(self) -> int:
        """Clean up expired data."""
        if not self._initialized:
            await self.initialize()
        
        return await self.storage.cleanup_expired(self.ttl_hours)
    
    def list_available_tools(self) -> List[str]:
        """List all available tools including feedback.report."""
        tools = []
        
        # Get tools from upstream server
        if hasattr(self.upstream, 'list_tools'):
            upstream_tools = self.upstream.list_tools()
            tools.extend(upstream_tools)
        elif hasattr(self.upstream, 'tools'):
            tools.extend(list(self.upstream.tools.keys()))
        
        # Add our feedback tool
        tools.append("feedback.report")
        
        return tools
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get the schema for a tool."""
        if tool_name == "feedback.report":
            return {
                "name": "feedback.report",
                "description": "Report structured feedback on a tool execution",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trace_id": {"type": "string", "description": "UUID trace ID"},
                        "helpfulness": {
                            "type": "integer", 
                            "minimum": 1, 
                            "maximum": 5,
                            "description": "How helpful was the tool (1-5)"
                        },
                        "fit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5, 
                            "description": "How well did the tool fit the task (1-5)"
                        },
                        "clarity": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "description": "How clear was the tool output (1-5)"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in this feedback (0.0-1.0)"
                        },
                        "better_alternative": {
                            "type": "string",
                            "enum": [
                                "different_tool",
                                "different_parameters", 
                                "sequence_of_tools",
                                "manual_intervention",
                                ""
                            ],
                            "description": "Suggestion for better alternative"
                        },
                        "suggestions": {
                            "type": "array",
                            "items": {"type": "string", "maxLength": 100},
                            "maxItems": 3,
                            "description": "Up to 3 short suggestions"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional additional notes"
                        }
                    },
                    "required": ["trace_id", "helpfulness", "fit", "clarity", "confidence"]
                }
            }
        
        # Delegate to upstream server
        if hasattr(self.upstream, 'get_tool_schema'):
            return self.upstream.get_tool_schema(tool_name)
        
        return {}