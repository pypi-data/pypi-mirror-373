"""Mock storage backend for testing."""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from skald.schema.models import FeedbackReport, ToolRunMetadata
from skald.storage.base import StorageBackend


class MockStorage(StorageBackend):
    """In-memory mock storage for testing."""
    
    def __init__(self):
        """Initialize mock storage."""
        self.tool_runs: Dict[str, ToolRunMetadata] = {}
        self.feedback: Dict[str, FeedbackReport] = {}
        self.feedback_agents: Dict[str, str] = {}  # trace_id -> agent_id
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the mock storage."""
        self.initialized = True
    
    async def close(self) -> None:
        """Close the mock storage."""
        self.initialized = False
        self.tool_runs.clear()
        self.feedback.clear()
        self.feedback_agents.clear()
    
    async def store_tool_run(self, metadata: ToolRunMetadata) -> None:
        """Store tool run metadata."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        self.tool_runs[metadata.trace_id] = metadata
    
    async def store_feedback(self, feedback: FeedbackReport, agent_id: str) -> None:
        """Store feedback report."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        # Check if corresponding tool run exists
        if feedback.trace_id not in self.tool_runs:
            raise ValueError(f"No tool run found for trace_id: {feedback.trace_id}")
        
        self.feedback[feedback.trace_id] = feedback
        self.feedback_agents[feedback.trace_id] = agent_id
    
    async def get_tool_run(self, trace_id: str) -> Optional[ToolRunMetadata]:
        """Get tool run metadata by trace ID."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        return self.tool_runs.get(trace_id)
    
    async def get_feedback(self, trace_id: str) -> Optional[FeedbackReport]:
        """Get feedback report by trace ID."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        return self.feedback.get(trace_id)
    
    async def list_tool_runs(
        self,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ToolRunMetadata]:
        """List tool runs with optional filtering."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        runs = list(self.tool_runs.values())
        
        # Apply filters
        if agent_id:
            runs = [r for r in runs if r.agent_id == agent_id]
        if tool_name:
            runs = [r for r in runs if r.tool_name == tool_name]
        
        # Sort by timestamp (newest first)
        runs.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply pagination
        return runs[offset:offset + limit]
    
    async def cleanup_expired(self, ttl_hours: int = 24) -> int:
        """Clean up expired records."""
        if not self.initialized:
            raise RuntimeError("Mock storage not initialized")
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        
        # Find expired tool runs
        expired_trace_ids = [
            trace_id for trace_id, run in self.tool_runs.items()
            if run.timestamp < cutoff
        ]
        
        # Remove expired records
        deleted_count = len(expired_trace_ids)
        for trace_id in expired_trace_ids:
            self.tool_runs.pop(trace_id, None)
            self.feedback.pop(trace_id, None)
            self.feedback_agents.pop(trace_id, None)
        
        return deleted_count