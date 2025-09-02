"""Skald - MCP Feedback Adapter Library

A transparent wrapper for Python MCP servers that enables structured feedback collection
on tool usefulness, clarity, and fit from AI agents.

Key features:
- Transparent tool wrapping with trace_id generation
- Structured feedback collection via feedback.report tool
- Opt-out controls via decorators and context managers
- Smart feedback invitation based on errors, latency, and sampling
- SQLite storage with optional Parquet export and data redaction
- Support for stdio, TCP, and Unix socket transports
"""

from __future__ import annotations

__version__ = "0.1.0"

from skald.core import SurveyingProxy
from skald.decorators import opt_out, suppressed
from skald.schema import FeedbackReport, ToolRunMetadata

__all__ = [
    "SurveyingProxy",
    "opt_out",
    "suppressed", 
    "FeedbackReport",
    "ToolRunMetadata",
]