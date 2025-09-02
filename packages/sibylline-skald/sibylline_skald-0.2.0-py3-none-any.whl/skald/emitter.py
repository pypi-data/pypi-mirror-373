"""SkaldEmitter - Fire-and-forget event batching for event streaming."""

import asyncio
import json
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
import structlog

from skald.schema.models import (
    EventType,
    ToolRunMetadataV2,
    BatchEventRequest,
    BatchEventResponse,
)

logger = structlog.get_logger(__name__)


class EmitterConfig:
    """Configuration for the SkaldEmitter."""
    
    def __init__(
        self,
        endpoint: str = "http://localhost:4001/v2/events",
        batch_size: int = 64,
        flush_ms: int = 5000,
        max_batch_bytes: int = 128 * 1024,  # 128KB
        initial_backoff_ms: int = 1000,
        max_backoff_ms: int = 30000,
        backoff_multiplier: float = 2.0,
        tenant_id: str = "default",
    ) -> None:
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.flush_ms = flush_ms
        self.max_batch_bytes = max_batch_bytes
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_multiplier = backoff_multiplier
        self.tenant_id = tenant_id


class SkaldEmitter:
    """Fire-and-forget event emitter with batching and error handling.
    
    Integrates with SurveyingProxy to emit events to a REST collector service
    with minimal coupling and robust error handling.
    """
    
    def __init__(self, config: Optional[EmitterConfig] = None) -> None:
        self.config = config or EmitterConfig()
        
        # Ring buffer for events
        self._buffer: deque[ToolRunMetadataV2] = deque(maxlen=self.config.batch_size * 2)
        self._buffer_lock = asyncio.Lock()
        
        # Flush control
        self._flush_task: Optional[asyncio.Task] = None
        self._last_flush_time = time.time()
        self._shutdown = False
        
        # Backoff state
        self._backoff_ms = self.config.initial_backoff_ms
        self._consecutive_failures = 0
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Fallback queue for failed sends (simple in-memory for now)
        self._fallback_queue: deque[ToolRunMetadataV2] = deque(maxlen=10000)
        
        # Statistics
        self._stats = {
            "events_buffered": 0,
            "events_sent": 0,
            "events_failed": 0,
            "events_dropped": 0,
            "batches_sent": 0,
            "batches_failed": 0,
        }
    
    async def start(self) -> None:
        """Start the emitter and background flush task."""
        if self._flush_task is not None:
            return
        
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10.0),
            headers={"Content-Type": "application/json"}
        )
        
        self._flush_task = asyncio.create_task(self._flush_worker())
        logger.info("SkaldEmitter started", endpoint=self.config.endpoint)
    
    async def stop(self) -> None:
        """Stop the emitter and flush remaining events."""
        self._shutdown = True
        
        if self._flush_task:
            # Cancel the flush worker
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_events(force=True)
        
        if self._session:
            await self._session.close()
            self._session = None
        
        logger.info("SkaldEmitter stopped", stats=self._stats)
    
    async def emit_event(
        self,
        event_type: EventType,
        trace_id: str,
        tool_name: str,
        **kwargs: Any
    ) -> None:
        """Emit an event to the buffer."""
        if self._shutdown:
            logger.warning("Emitter is shutdown, dropping event", trace_id=trace_id)
            return
        
        try:
            # Generate UUIDv7 for event_id (time-ordered UUID)
            event_id = str(uuid.uuid4())  # Using uuid4 for now, could upgrade to UUIDv7
            
            # Create event with v2 schema
            event = ToolRunMetadataV2(
                event_id=event_id,
                trace_id=trace_id,
                span_id=kwargs.get("span_id", str(uuid.uuid4())),
                parent_span_id=kwargs.get("parent_span_id"),
                event_type=event_type,
                timestamp=kwargs.get("timestamp", datetime.now(timezone.utc)),
                
                # Context fields
                agent_session_id=kwargs.get("agent_session_id"),
                mcp_id=kwargs.get("mcp_id"),
                tool_name=tool_name,
                tool_version=kwargs.get("tool_version"),
                model_id=kwargs.get("model_id"),
                tenant_id=kwargs.get("tenant_id", self.config.tenant_id),
                
                # Timing fields
                t_request=kwargs.get("t_request", datetime.now(timezone.utc)),
                t_upstream_start=kwargs.get("t_upstream_start"),
                t_upstream_end=kwargs.get("t_upstream_end"),
                t_response=kwargs.get("t_response", datetime.now(timezone.utc)),
                
                # Computed timing breakdowns
                queue_ms=kwargs.get("queue_ms"),
                network_ms=kwargs.get("network_ms"),
                server_ms=kwargs.get("server_ms"),
                serialize_ms=kwargs.get("serialize_ms"),
                
                # Size metrics
                in_bytes=kwargs.get("in_bytes"),
                out_bytes=kwargs.get("out_bytes"),
                
                # Error information
                error_class=kwargs.get("error_class"),
                error_code=kwargs.get("error_code"),
                
                # Legacy v1 fields (required)
                status=kwargs["status"],  # Required
                latency_ms=kwargs["latency_ms"],  # Required
                output_bytes=kwargs["output_bytes"],  # Required
                invite_feedback=kwargs.get("invite_feedback", False),
                opt_out=kwargs.get("opt_out", False),
                
                # Privacy & security
                args_redacted=kwargs.get("args_redacted", {}),
                redaction_rule_id=kwargs.get("redaction_rule_id"),
            )
            
            async with self._buffer_lock:
                self._buffer.append(event)
                self._stats["events_buffered"] += 1
                
                # Check if we should flush immediately
                if len(self._buffer) >= self.config.batch_size:
                    asyncio.create_task(self._flush_events())
                    
        except Exception as e:
            logger.error("Failed to emit event", trace_id=trace_id, error=str(e))
            self._stats["events_failed"] += 1
    
    async def _flush_worker(self) -> None:
        """Background worker that periodically flushes events."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.config.flush_ms / 1000.0)
                
                # Check if it's time to flush
                if time.time() - self._last_flush_time >= (self.config.flush_ms / 1000.0):
                    await self._flush_events()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Flush worker error", error=str(e))
                await asyncio.sleep(1.0)  # Brief pause before retrying
    
    async def _flush_events(self, force: bool = False) -> None:
        """Flush buffered events to the collector."""
        if not self._buffer and not self._fallback_queue:
            return
        
        async with self._buffer_lock:
            # Get events to send (prefer fallback queue first)
            events_to_send: List[ToolRunMetadataV2] = []
            
            # First, try to send events from fallback queue
            while self._fallback_queue and len(events_to_send) < self.config.batch_size:
                events_to_send.append(self._fallback_queue.popleft())
            
            # Then add events from main buffer
            while self._buffer and len(events_to_send) < self.config.batch_size:
                events_to_send.append(self._buffer.popleft())
            
            if not events_to_send:
                return
        
        # Check batch size limit
        batch_data = BatchEventRequest(events=events_to_send)
        payload = batch_data.model_dump_json()
        
        if len(payload.encode('utf-8')) > self.config.max_batch_bytes:
            # Split batch in half and retry
            mid = len(events_to_send) // 2
            if mid > 0:
                # Put back the second half and retry with first half
                async with self._buffer_lock:
                    for event in reversed(events_to_send[mid:]):
                        self._buffer.appendleft(event)
                
                await self._send_batch(events_to_send[:mid])
            return
        
        await self._send_batch(events_to_send)
        self._last_flush_time = time.time()
    
    async def _send_batch(self, events: List[ToolRunMetadataV2]) -> None:
        """Send a batch of events to the collector."""
        if not events or not self._session:
            return
        
        try:
            batch_request = BatchEventRequest(events=events)
            payload = batch_request.model_dump_json()
            
            async with self._session.post(
                self.config.endpoint,
                data=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    # Success
                    response_data = await response.json()
                    batch_response = BatchEventResponse(**response_data)
                    
                    self._stats["events_sent"] += batch_response.accepted
                    self._stats["events_failed"] += batch_response.rejected
                    self._stats["batches_sent"] += 1
                    
                    # Reset backoff on success
                    self._backoff_ms = self.config.initial_backoff_ms
                    self._consecutive_failures = 0
                    
                    if batch_response.errors:
                        logger.warning(
                            "Batch partially failed",
                            accepted=batch_response.accepted,
                            rejected=batch_response.rejected,
                            errors=batch_response.errors[:3]  # Log first 3 errors
                        )
                    
                elif response.status == 413:
                    # Payload too large - should not happen due to our checks
                    logger.warning("Payload too large", batch_size=len(events))
                    await self._handle_batch_failure(events, "payload_too_large")
                    
                elif response.status in (429, 503):
                    # Rate limited or service unavailable
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        await asyncio.sleep(int(retry_after))
                    await self._handle_batch_failure(events, f"http_{response.status}")
                    
                else:
                    # Other HTTP errors
                    logger.error("HTTP error", status=response.status, url=self.config.endpoint)
                    await self._handle_batch_failure(events, f"http_{response.status}")
                    
        except asyncio.TimeoutError:
            logger.warning("Request timeout", endpoint=self.config.endpoint)
            await self._handle_batch_failure(events, "timeout")
            
        except Exception as e:
            logger.error("Failed to send batch", endpoint=self.config.endpoint, error=str(e))
            await self._handle_batch_failure(events, "exception")
    
    async def _handle_batch_failure(
        self, 
        events: List[ToolRunMetadataV2], 
        reason: str
    ) -> None:
        """Handle failed batch send with drop policy."""
        self._stats["batches_failed"] += 1
        self._consecutive_failures += 1
        
        # Apply exponential backoff
        if self._consecutive_failures > 1:
            self._backoff_ms = min(
                self._backoff_ms * self.config.backoff_multiplier,
                self.config.max_backoff_ms
            )
            await asyncio.sleep(self._backoff_ms / 1000.0)
        
        # Apply drop policy based on event priority
        events_to_save = []
        for event in events:
            if self._should_drop_event(event):
                self._stats["events_dropped"] += 1
                logger.debug("Dropping event", event_type=event.event_type, reason=reason)
            else:
                events_to_save.append(event)
        
        # Save high-priority events to fallback queue
        for event in events_to_save:
            if len(self._fallback_queue) < self._fallback_queue.maxlen:
                self._fallback_queue.append(event)
            else:
                self._stats["events_dropped"] += 1
                logger.warning("Fallback queue full, dropping event", event_type=event.event_type)
    
    def _should_drop_event(self, event: ToolRunMetadataV2) -> bool:
        """Determine if an event should be dropped under sustained failure.
        
        Drop policy priority:
        1. neutral_success_events (drop first)
        2. tool_run_started_events  
        3. tool_run_finished_events
        4. never_drop: errors and invite_feedback=true events
        """
        # Never drop errors or feedback invitations
        if (event.event_type == EventType.TOOL_RUN_ERROR or 
            event.invite_feedback or
            event.event_type == EventType.FEEDBACK_SUBMITTED):
            return False
        
        # Drop neutral success events first
        if (event.event_type == EventType.TOOL_RUN_FINISHED and 
            not event.invite_feedback and 
            event.status.value == "success"):
            return True
        
        # Drop started events next
        if event.event_type == EventType.TOOL_RUN_STARTED:
            return True
        
        # Keep everything else (finished events with errors/invitations)
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get emitter statistics."""
        return {
            **self._stats,
            "buffer_size": len(self._buffer),
            "fallback_queue_size": len(self._fallback_queue),
            "consecutive_failures": self._consecutive_failures,
            "current_backoff_ms": self._backoff_ms,
        }