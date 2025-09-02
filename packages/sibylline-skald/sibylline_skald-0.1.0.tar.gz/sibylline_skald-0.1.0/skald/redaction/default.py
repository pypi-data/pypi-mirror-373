"""Default redaction implementation for Skald."""

from __future__ import annotations

import re
from typing import Any, Dict, Set

from skald.redaction.base import Redactor


class DefaultRedactor(Redactor):
    """Default redactor that removes common sensitive data patterns."""
    
    def __init__(
        self, 
        sensitive_keys: Set[str] | None = None,
        patterns: Dict[str, str] | None = None
    ) -> None:
        """Initialize default redactor.
        
        Args:
            sensitive_keys: Set of key names to redact completely
            patterns: Dict of regex patterns to replacement strings
        """
        self.sensitive_keys = sensitive_keys or {
            "password", "token", "key", "secret", "credential",
            "api_key", "auth", "authorization", "bearer", "passphrase",
            "private_key", "access_token", "refresh_token", "session_id",
            "cookie", "jwt", "oauth", "client_secret"
        }
        
        self.patterns = patterns or {
            # Email addresses
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL_REDACTED]',
            
            # Credit card numbers (basic pattern)
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b': '[CARD_REDACTED]',
            
            # Social Security Numbers (US format)
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN_REDACTED]',
            
            # Phone numbers (various formats)
            r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b': '[PHONE_REDACTED]',
            
            # IP addresses
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b': '[IP_REDACTED]',
            
            # URLs with sensitive paths
            r'https?://[^\s]+(?:token|key|secret|password|auth)[^\s]*': '[URL_REDACTED]',
        }
        
        # Compile regex patterns for performance
        self.compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): replacement
            for pattern, replacement in self.patterns.items()
        }
    
    def redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive data from a dictionary."""
        return self._redact_recursive(data)
    
    def _redact_recursive(self, obj: Any) -> Any:
        """Recursively redact sensitive data."""
        if isinstance(obj, dict):
            return {
                key: self._redact_value(key, value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._redact_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return self._redact_string(obj)
        else:
            return obj
    
    def _redact_value(self, key: str, value: Any) -> Any:
        """Redact a value based on its key and content."""
        # Check if key is sensitive
        if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
            return "[REDACTED]"
        
        # Recursively process the value
        return self._redact_recursive(value)
    
    def _redact_string(self, text: str) -> str:
        """Apply pattern-based redaction to a string."""
        if not isinstance(text, str):
            return text
        
        result = text
        for pattern, replacement in self.compiled_patterns.items():
            result = pattern.sub(replacement, result)
        
        return result
    
    def add_sensitive_key(self, key: str) -> None:
        """Add a new sensitive key to redact."""
        self.sensitive_keys.add(key.lower())
    
    def add_pattern(self, pattern: str, replacement: str = "[PATTERN_REDACTED]") -> None:
        """Add a new regex pattern to redact."""
        self.patterns[pattern] = replacement
        self.compiled_patterns[re.compile(pattern, re.IGNORECASE)] = replacement
    
    def remove_sensitive_key(self, key: str) -> None:
        """Remove a sensitive key from redaction."""
        self.sensitive_keys.discard(key.lower())
    
    def clear_patterns(self) -> None:
        """Clear all regex patterns."""
        self.patterns.clear()
        self.compiled_patterns.clear()