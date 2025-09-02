"""Skald Event Collector - REST service for receiving batched events."""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from skald.schema.models import BatchEventRequest, BatchEventResponse, ToolRunMetadataV2
from skald.storage.sqlite import SQLiteStorage

logger = structlog.get_logger(__name__)


class EventCollector:
    """Event collector service with SQLite storage and health monitoring."""
    
    def __init__(
        self,
        db_path: str = "skald_events.db",
        max_batch_size: int = 1000,
        max_batch_bytes: int = 128 * 1024,  # 128KB
    ) -> None:
        self.db_path = db_path
        self.max_batch_size = max_batch_size
        self.max_batch_bytes = max_batch_bytes
        
        # Storage backend
        self.storage: Optional[SQLiteStorage] = None
        
        # Statistics
        self.stats = {
            "events_received": 0,
            "events_accepted": 0,
            "events_rejected": 0,
            "batches_processed": 0,
            "errors_total": 0,
            "uptime_start": time.time(),
        }
        
        # Rate limiting (simple in-memory)
        self._client_requests: Dict[str, List[float]] = {}
        self._rate_limit_window = 60  # 60 seconds
        self._rate_limit_requests = 100  # 100 requests per minute per client
    
    async def initialize(self) -> None:
        """Initialize the collector storage."""
        self.storage = SQLiteStorage(self.db_path)
        await self.storage.initialize()
        logger.info("EventCollector initialized", db_path=self.db_path)
    
    async def close(self) -> None:
        """Close the collector and storage."""
        if self.storage:
            await self.storage.close()
        logger.info("EventCollector closed")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address for rate limiting."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits."""
        now = time.time()
        
        # Clean old requests
        if client_ip not in self._client_requests:
            self._client_requests[client_ip] = []
        
        # Remove requests older than window
        self._client_requests[client_ip] = [
            req_time for req_time in self._client_requests[client_ip]
            if now - req_time < self._rate_limit_window
        ]
        
        # Check if under limit
        if len(self._client_requests[client_ip]) >= self._rate_limit_requests:
            return False
        
        # Add current request
        self._client_requests[client_ip].append(now)
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        uptime_seconds = time.time() - self.stats["uptime_start"]
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "uptime_seconds": uptime_seconds,
            "database": {
                "connected": self.storage is not None,
                "path": self.db_path,
            },
            "statistics": self.stats.copy()
        }
    
    async def process_events(
        self, 
        batch: BatchEventRequest,
        client_ip: str
    ) -> BatchEventResponse:
        """Process a batch of events."""
        if not self.storage:
            raise HTTPException(status_code=503, detail="Storage not initialized")
        
        self.stats["batches_processed"] += 1
        self.stats["events_received"] += len(batch.events)
        
        accepted = 0
        rejected = 0
        errors: List[Dict[str, Any]] = []
        
        for idx, event in enumerate(batch.events):
            try:
                # Validate event (Pydantic already did basic validation)
                await self._validate_event(event, idx)
                
                # Store event (convert to v1 format for now)
                await self._store_event(event)
                
                accepted += 1
                self.stats["events_accepted"] += 1
                
            except Exception as e:
                rejected += 1
                self.stats["events_rejected"] += 1
                self.stats["errors_total"] += 1
                
                errors.append({
                    "idx": idx,
                    "reason": str(e),
                    "event_id": getattr(event, "event_id", "unknown")
                })
                
                logger.warning(
                    "Event validation failed",
                    idx=idx,
                    event_id=getattr(event, "event_id", "unknown"),
                    error=str(e)
                )
        
        return BatchEventResponse(
            accepted=accepted,
            rejected=rejected,
            errors=errors
        )
    
    async def _validate_event(self, event: ToolRunMetadataV2, idx: int) -> None:
        """Validate individual event."""
        # Check for duplicate event_id (simple check)
        if self.storage:
            # This would need proper deduplication logic in a real implementation
            # For now, we'll assume deduplication is handled at storage level
            pass
        
        # Validate required fields
        if not event.trace_id:
            raise ValueError("trace_id is required")
        
        if not event.tool_name:
            raise ValueError("tool_name is required")
        
        # Validate tenant_id
        if not event.tenant_id:
            raise ValueError("tenant_id is required")
        
        # Validate timing if provided
        if event.t_upstream_start and event.t_upstream_end:
            if event.t_upstream_end < event.t_upstream_start:
                raise ValueError("t_upstream_end must be after t_upstream_start")
    
    async def _store_event(self, event: ToolRunMetadataV2) -> None:
        """Store event in storage backend."""
        if not self.storage:
            raise ValueError("Storage not initialized")
        
        # For MVP, we'll store as v1 ToolRunMetadata for compatibility
        # In a full implementation, we'd extend storage to handle v2 events
        
        # Convert v2 to v1 for storage compatibility
        from skald.schema.models import ToolRunMetadata
        
        v1_metadata = ToolRunMetadata(
            trace_id=event.trace_id,
            timestamp=event.timestamp,
            agent_id=event.tenant_id,  # Using tenant_id as agent_id for now
            tool_name=event.tool_name,
            status=event.status,
            latency_ms=event.latency_ms,
            output_bytes=event.output_bytes,
            invite_feedback=event.invite_feedback,
            opt_out=event.opt_out,
            args_redacted=event.args_redacted
        )
        
        await self.storage.store_tool_run(v1_metadata)


# FastAPI application
collector = EventCollector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    await collector.initialize()
    yield
    # Shutdown
    await collector.close()


app = FastAPI(
    title="Skald Event Collector",
    description="REST service for collecting MCP tool execution events",
    version="2.0.0",
    lifespan=lifespan
)


@app.post("/v2/events", response_model=BatchEventResponse)
async def submit_events(
    batch: BatchEventRequest,
    request: Request,
    response: Response
) -> BatchEventResponse:
    """Submit a batch of events for processing.
    
    Accepts batches of events in JSON format with proper error handling,
    rate limiting, and size validation.
    """
    client_ip = collector._get_client_ip(request)
    
    # Rate limiting check
    if not collector._check_rate_limit(client_ip):
        response.headers["Retry-After"] = str(collector._rate_limit_window)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(collector._rate_limit_window)}
        )
    
    # Batch size validation
    if len(batch.events) > collector.max_batch_size:
        raise HTTPException(
            status_code=413,
            detail=f"Batch too large: {len(batch.events)} events, max {collector.max_batch_size}",
            headers={"maxBatchSize": str(collector.max_batch_size)}
        )
    
    # Batch byte size validation
    payload_size = len(json.dumps(batch.model_dump()).encode('utf-8'))
    if payload_size > collector.max_batch_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Payload too large: {payload_size} bytes, max {collector.max_batch_bytes}",
            headers={"maxBatchBytes": str(collector.max_batch_bytes)}
        )
    
    try:
        return await collector.process_events(batch, client_ip)
    except Exception as e:
        logger.error("Failed to process events batch", client_ip=client_ip, error=str(e))
        collector.stats["errors_total"] += 1
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v2/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return await collector.health_check()


@app.get("/v2/stats")
async def get_stats() -> Dict[str, Any]:
    """Get collector statistics."""
    return {
        "statistics": collector.stats.copy(),
        "configuration": {
            "max_batch_size": collector.max_batch_size,
            "max_batch_bytes": collector.max_batch_bytes,
            "rate_limit_window": collector._rate_limit_window,
            "rate_limit_requests": collector._rate_limit_requests,
        }
    }


@app.post("/v2/export/parquet")
async def trigger_parquet_export(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tenant_id: Optional[str] = None,
    output_dir: str = "parquet_exports"
) -> Dict[str, Any]:
    """Manually trigger Parquet export for analytics."""
    if not collector.storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    try:
        from datetime import datetime, timedelta, timezone
        from skald.export.parquet import ParquetExporter, ExportConfig
        
        # Configure exporter
        config = ExportConfig(output_dir=output_dir)
        exporter = ParquetExporter(collector.storage, config)
        
        # Default to yesterday if no dates specified
        if not start_date and not end_date:
            export_stats = await exporter.export_yesterday()
        else:
            # Parse dates
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc) if start_date else None
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) if end_date else None
            
            if start_dt and end_dt:
                export_stats = await exporter.export_date_range(
                    start_dt, end_dt, tenant_id, force_overwrite=True
                )
            elif start_dt:
                export_stats = await exporter.export_daily(start_dt, force_overwrite=True)
            else:
                raise HTTPException(status_code=400, detail="Invalid date range")
        
        return {
            "status": "success",
            "message": "Parquet export completed",
            **export_stats
        }
        
    except Exception as e:
        logger.error("Parquet export failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Error handlers
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Handle Pydantic validation errors."""
    collector.stats["errors_total"] += 1
    return JSONResponse(
        status_code=422,
        content={
            "accepted": 0,
            "rejected": 1,
            "errors": [{"idx": 0, "reason": "Validation error", "detail": str(exc)}]
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "skald.collector:app",
        host="0.0.0.0",
        port=4001,
        log_level="info",
        access_log=True
    )