"""Skald - Universal Execution Monitoring & Feedback Library

A comprehensive monitoring and feedback collection system for Python applications,
supporting MCP servers, functions, shell commands, and more.

Key features:
- MCP server monitoring with transparent tool wrapping and trace_id generation
- Function execution monitoring with decorators and timing metrics
- Shell command monitoring with subprocess tracking and output collection
- Universal structured feedback collection across all execution contexts
- Opt-out controls via decorators and context managers
- Smart feedback invitation based on errors, latency, and sampling
- SQLite storage with optional Parquet export and data redaction
- Support for stdio, TCP, and Unix socket transports
"""

from __future__ import annotations

__version__ = "0.1.0"

from skald.core import SurveyingProxy
from skald.decorators import opt_out, suppressed
from skald.schema import FeedbackReport, ToolRunMetadata, ExecutionMetadata, UniversalFeedbackReport, ExecutionContext
from skald.monitor import (
    FunctionMonitor,
    ShellMonitor,
    monitor,
    shell_monitor,
    trace_function,
    trace_shell_command
)

__all__ = [
    # MCP Server Support
    "SurveyingProxy",
    "opt_out",
    "suppressed", 
    "FeedbackReport",
    "ToolRunMetadata",
    
    # Universal Monitoring
    "ExecutionMetadata",
    "UniversalFeedbackReport",
    "ExecutionContext",
    "FunctionMonitor",
    "ShellMonitor",
    "monitor",
    "shell_monitor",
    "trace_function",
    "trace_shell_command",
]