"""Base transport interface for Skald."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from skald.core import SurveyingProxy


class Transport(ABC):
    """Abstract base class for MCP transports."""
    
    def __init__(self, proxy: SurveyingProxy) -> None:
        """Initialize transport with a SurveyingProxy.
        
        Args:
            proxy: The SurveyingProxy instance to serve
        """
        self.proxy = proxy
    
    @abstractmethod
    async def serve(self, **kwargs: Any) -> None:
        """Start serving the MCP server over this transport.
        
        Args:
            **kwargs: Transport-specific configuration options
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop serving and clean up resources."""
        pass