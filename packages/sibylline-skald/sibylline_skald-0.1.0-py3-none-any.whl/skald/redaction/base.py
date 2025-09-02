"""Base redaction interface for Skald."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class Redactor(ABC):
    """Abstract base class for data redactors."""
    
    @abstractmethod
    def redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive data from a dictionary.
        
        Args:
            data: Dictionary containing potentially sensitive data
            
        Returns:
            Dictionary with sensitive data redacted
        """
        pass