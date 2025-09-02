"""Base storage interface for Skald."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from skald.schema.models import FeedbackReport, ToolRunMetadata


class StorageBackend(ABC):
    """Abstract base class for Skald storage backends."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the storage backend and clean up resources."""
        pass
    
    @abstractmethod
    async def store_tool_run(self, metadata: ToolRunMetadata) -> None:
        """Store tool run metadata.
        
        Args:
            metadata: Tool run metadata to store
        """
        pass
    
    @abstractmethod
    async def store_feedback(self, feedback: FeedbackReport, agent_id: str) -> None:
        """Store feedback report.
        
        Args:
            feedback: Feedback report to store
            agent_id: ID of the agent providing feedback
        """
        pass
    
    @abstractmethod
    async def get_tool_run(self, trace_id: str) -> Optional[ToolRunMetadata]:
        """Get tool run metadata by trace ID.
        
        Args:
            trace_id: Trace ID to look up
            
        Returns:
            Tool run metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_feedback(self, trace_id: str) -> Optional[FeedbackReport]:
        """Get feedback report by trace ID.
        
        Args:
            trace_id: Trace ID to look up
            
        Returns:
            Feedback report if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_tool_runs(
        self, 
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ToolRunMetadata]:
        """List tool runs with optional filtering.
        
        Args:
            agent_id: Optional agent ID filter
            tool_name: Optional tool name filter  
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of tool run metadata
        """
        pass
    
    @abstractmethod
    async def cleanup_expired(self, ttl_hours: int) -> int:
        """Clean up expired records.
        
        Args:
            ttl_hours: TTL in hours for records
            
        Returns:
            Number of records deleted
        """
        pass