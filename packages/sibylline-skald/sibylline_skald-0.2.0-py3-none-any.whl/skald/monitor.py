"""Function and command monitoring decorators for Skald."""

from __future__ import annotations

import asyncio
import functools
import os
import subprocess
import time
import uuid
import psutil
from datetime import datetime, timezone
from typing import Any, Callable, Optional, TypeVar, Union, Dict, List
import asyncio.subprocess

import structlog

from skald.schema.models import ExecutionMetadata, ExecutionContext
from skald.storage.base import StorageBackend

logger = structlog.get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class FunctionMonitor:
    """Monitor function executions with Skald feedback collection."""
    
    def __init__(
        self,
        storage: Optional[StorageBackend] = None,
        auto_invite_feedback: bool = False,
        collect_memory_stats: bool = True,
        collect_performance_stats: bool = True,
        redaction_func: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """Initialize function monitor.
        
        Args:
            storage: Storage backend for execution metadata
            auto_invite_feedback: Whether to automatically invite feedback
            collect_memory_stats: Whether to collect memory usage statistics
            collect_performance_stats: Whether to collect CPU/timing statistics
            redaction_func: Optional function to redact sensitive arguments
        """
        self.storage = storage
        self.auto_invite_feedback = auto_invite_feedback
        self.collect_memory_stats = collect_memory_stats
        self.collect_performance_stats = collect_performance_stats
        self.redaction_func = redaction_func or (lambda x: x)
    
    def __call__(
        self,
        func: Optional[F] = None,
        *,
        invite_feedback: Optional[bool] = None,
        name_override: Optional[str] = None,
        collect_args: bool = True,
        collect_result: bool = False
    ) -> Union[F, Callable[[F], F]]:
        """Decorator to monitor function execution.
        
        Args:
            func: The function to monitor
            invite_feedback: Override feedback invitation for this function
            name_override: Override the function name in monitoring
            collect_args: Whether to collect function arguments
            collect_result: Whether to collect function return value
        """
        def decorator(f: F) -> F:
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return self._monitor_sync(
                    f, args, kwargs,
                    invite_feedback=invite_feedback,
                    name_override=name_override,
                    collect_args=collect_args,
                    collect_result=collect_result
                )
            
            @functools.wraps(f)
            async def async_wrapper(*args, **kwargs):
                return await self._monitor_async(
                    f, args, kwargs,
                    invite_feedback=invite_feedback,
                    name_override=name_override,
                    collect_args=collect_args,
                    collect_result=collect_result
                )
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(f):
                return async_wrapper
            else:
                return wrapper
        
        # Handle both @monitor and @monitor() usage
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def _monitor_sync(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        invite_feedback: Optional[bool],
        name_override: Optional[str],
        collect_args: bool,
        collect_result: bool
    ) -> Any:
        """Monitor synchronous function execution."""
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        
        # Collect pre-execution stats
        process = psutil.Process() if self.collect_memory_stats else None
        memory_before = process.memory_info().rss / 1024 / 1024 if process else None
        cpu_percent_start = process.cpu_percent() if self.collect_performance_stats and process else None
        
        result = None
        error = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            # Calculate execution time
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Collect post-execution stats
            memory_after = process.memory_info().rss / 1024 / 1024 if process else None
            memory_delta = (memory_after - memory_before) if (memory_after and memory_before) else None
            cpu_percent = process.cpu_percent() if self.collect_performance_stats and process else None
            
            # Create execution metadata
            input_args = {}
            if collect_args:
                input_args = self.redaction_func({"args": list(args), "kwargs": kwargs})
            
            extra_fields = {
                "memory_delta_mb": memory_delta,
                "cpu_percent": cpu_percent,
                "invite_feedback": invite_feedback or self.auto_invite_feedback
            }
            
            metadata = ExecutionMetadata.from_function(
                func=func,
                args=args if collect_args else (),
                kwargs=kwargs if collect_args else {},
                result=result if collect_result else None,
                error=error,
                latency_ms=latency_ms,
                trace_id=trace_id,
                **extra_fields
            )
            
            # Override name if specified
            if name_override:
                metadata.name = name_override
            
            # Store metadata asynchronously if storage is available
            if self.storage:
                try:
                    # For sync functions, we need to handle async storage carefully
                    if hasattr(self.storage, 'store_execution'):
                        # Try to store synchronously if possible
                        asyncio.create_task(self._store_metadata(metadata))
                except Exception as storage_error:
                    logger.warning(
                        "Failed to store execution metadata",
                        trace_id=trace_id,
                        error=str(storage_error)
                    )
            
            logger.debug(
                "Function execution monitored",
                trace_id=trace_id,
                function=metadata.name,
                latency_ms=latency_ms,
                status=metadata.status,
                memory_delta_mb=memory_delta
            )
    
    async def _monitor_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        invite_feedback: Optional[bool],
        name_override: Optional[str],
        collect_args: bool,
        collect_result: bool
    ) -> Any:
        """Monitor asynchronous function execution."""
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        
        # Collect pre-execution stats
        process = psutil.Process() if self.collect_memory_stats else None
        memory_before = process.memory_info().rss / 1024 / 1024 if process else None
        
        result = None
        error = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            # Calculate execution time
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Collect post-execution stats
            memory_after = process.memory_info().rss / 1024 / 1024 if process else None
            memory_delta = (memory_after - memory_before) if (memory_after and memory_before) else None
            
            # Create execution metadata
            input_args = {}
            if collect_args:
                input_args = self.redaction_func({"args": list(args), "kwargs": kwargs})
            
            extra_fields = {
                "memory_delta_mb": memory_delta,
                "invite_feedback": invite_feedback or self.auto_invite_feedback
            }
            
            metadata = ExecutionMetadata.from_function(
                func=func,
                args=args if collect_args else (),
                kwargs=kwargs if collect_args else {},
                result=result if collect_result else None,
                error=error,
                latency_ms=latency_ms,
                trace_id=trace_id,
                **extra_fields
            )
            
            # Override name if specified
            if name_override:
                metadata.name = name_override
            
            # Store metadata
            if self.storage:
                try:
                    await self._store_metadata(metadata)
                except Exception as storage_error:
                    logger.warning(
                        "Failed to store execution metadata",
                        trace_id=trace_id,
                        error=str(storage_error)
                    )
            
            logger.debug(
                "Async function execution monitored",
                trace_id=trace_id,
                function=metadata.name,
                latency_ms=latency_ms,
                status=metadata.status,
                memory_delta_mb=memory_delta
            )
    
    async def _store_metadata(self, metadata: ExecutionMetadata) -> None:
        """Store execution metadata."""
        if hasattr(self.storage, 'store_execution'):
            await self.storage.store_execution(metadata)
        else:
            logger.warning("Storage backend does not support execution metadata")


class ShellMonitor:
    """Monitor shell command executions with Skald feedback collection."""
    
    def __init__(
        self,
        storage: Optional[StorageBackend] = None,
        auto_invite_feedback: bool = False,
        collect_output: bool = True,
        max_output_size: int = 1024 * 1024,  # 1MB
        redaction_func: Optional[Callable[[str], str]] = None
    ):
        """Initialize shell monitor.
        
        Args:
            storage: Storage backend for execution metadata
            auto_invite_feedback: Whether to automatically invite feedback
            collect_output: Whether to collect stdout/stderr
            max_output_size: Maximum size of output to collect (bytes)
            redaction_func: Optional function to redact sensitive command content
        """
        self.storage = storage
        self.auto_invite_feedback = auto_invite_feedback
        self.collect_output = collect_output
        self.max_output_size = max_output_size
        self.redaction_func = redaction_func or (lambda x: x)
    
    async def run(
        self,
        command: Union[str, List[str]],
        *,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        invite_feedback: Optional[bool] = None,
        name_override: Optional[str] = None,
        shell: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command with monitoring.
        
        Args:
            command: Command to execute (string or list of strings)
            working_dir: Working directory for command execution
            env: Environment variables for command execution
            timeout: Timeout for command execution
            invite_feedback: Whether to invite feedback for this execution
            name_override: Override the command name in monitoring
            shell: Whether to run the command through the shell
            
        Returns:
            CompletedProcess with stdout, stderr, returncode
        """
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        
        # Convert command to string for logging/storage
        command_str = command if isinstance(command, str) else ' '.join(command)
        redacted_command = self.redaction_func(command_str)
        
        # Use asyncio.subprocess for async execution
        try:
            if shell and isinstance(command, str):
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE if self.collect_output else None,
                    stderr=asyncio.subprocess.PIPE if self.collect_output else None,
                    cwd=working_dir,
                    env=env
                )
            else:
                cmd_args = command.split() if isinstance(command, str) else command
                proc = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE if self.collect_output else None,
                    stderr=asyncio.subprocess.PIPE if self.collect_output else None,
                    cwd=working_dir,
                    env=env
                )
            
            # Wait for completion with optional timeout
            if timeout:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            else:
                stdout, stderr = await proc.communicate()
            
            # Calculate execution time
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Process output
            stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""
            
            # Truncate output if too large
            if len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[:self.max_output_size] + f"\n... (truncated, original size: {len(stdout_str)} bytes)"
            if len(stderr_str) > self.max_output_size:
                stderr_str = stderr_str[:self.max_output_size] + f"\n... (truncated, original size: {len(stderr_str)} bytes)"
            
            # Create execution metadata
            extra_fields = {
                "invite_feedback": invite_feedback or self.auto_invite_feedback
            }
            
            metadata = ExecutionMetadata.from_shell_command(
                command=redacted_command,
                working_dir=working_dir,
                exit_code=proc.returncode,
                process_id=proc.pid,
                stdout=stdout_str if self.collect_output else None,
                stderr=stderr_str if self.collect_output else None,
                latency_ms=latency_ms,
                trace_id=trace_id,
                **extra_fields
            )
            
            # Override name if specified
            if name_override:
                metadata.name = name_override
            
            # Store metadata
            if self.storage:
                try:
                    await self._store_metadata(metadata)
                except Exception as storage_error:
                    logger.warning(
                        "Failed to store execution metadata",
                        trace_id=trace_id,
                        error=str(storage_error)
                    )
            
            logger.debug(
                "Shell command execution monitored",
                trace_id=trace_id,
                command=metadata.name,
                exit_code=proc.returncode,
                latency_ms=latency_ms
            )
            
            # Return CompletedProcess-like object
            return subprocess.CompletedProcess(
                args=command,
                returncode=proc.returncode,
                stdout=stdout_str if self.collect_output else None,
                stderr=stderr_str if self.collect_output else None
            )
            
        except asyncio.TimeoutError:
            # Handle timeout
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            metadata = ExecutionMetadata.from_shell_command(
                command=redacted_command,
                working_dir=working_dir,
                exit_code=None,  # Unknown due to timeout
                process_id=None,
                stdout=None,
                stderr="Command timed out",
                latency_ms=latency_ms,
                trace_id=trace_id,
                invite_feedback=invite_feedback or self.auto_invite_feedback
            )
            metadata.status = metadata.status.__class__.TIMEOUT
            metadata.error_message = f"Command timed out after {timeout}s"
            
            if self.storage:
                try:
                    await self._store_metadata(metadata)
                except Exception:
                    pass
            
            raise
        
        except Exception as e:
            # Handle other errors
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            metadata = ExecutionMetadata.from_shell_command(
                command=redacted_command,
                working_dir=working_dir,
                exit_code=None,
                process_id=None,
                stdout=None,
                stderr=str(e),
                latency_ms=latency_ms,
                trace_id=trace_id,
                invite_feedback=invite_feedback or self.auto_invite_feedback
            )
            metadata.status = metadata.status.__class__.ERROR
            metadata.error_type = type(e).__name__
            metadata.error_message = str(e)
            
            if self.storage:
                try:
                    await self._store_metadata(metadata)
                except Exception:
                    pass
            
            raise
    
    async def _store_metadata(self, metadata: ExecutionMetadata) -> None:
        """Store execution metadata."""
        if hasattr(self.storage, 'store_execution'):
            await self.storage.store_execution(metadata)
        else:
            logger.warning("Storage backend does not support execution metadata")


# Convenience instances for common use cases
monitor = FunctionMonitor()
shell_monitor = ShellMonitor()


# Convenience decorator functions
def trace_function(
    func: Optional[F] = None,
    *,
    storage: Optional[StorageBackend] = None,
    invite_feedback: bool = False,
    name: Optional[str] = None
) -> Union[F, Callable[[F], F]]:
    """Simple function tracing decorator.
    
    Args:
        func: Function to trace
        storage: Optional storage backend
        invite_feedback: Whether to invite feedback
        name: Optional name override
    """
    monitor_instance = FunctionMonitor(storage=storage, auto_invite_feedback=invite_feedback)
    return monitor_instance(func, invite_feedback=invite_feedback, name_override=name)


def trace_shell_command(
    command: Union[str, List[str]],
    *,
    storage: Optional[StorageBackend] = None,
    invite_feedback: bool = False,
    **kwargs
) -> subprocess.CompletedProcess:
    """Simple shell command tracing function.
    
    Args:
        command: Command to execute
        storage: Optional storage backend
        invite_feedback: Whether to invite feedback
        **kwargs: Additional arguments for shell execution
    """
    monitor_instance = ShellMonitor(storage=storage, auto_invite_feedback=invite_feedback)
    return asyncio.run(monitor_instance.run(command, invite_feedback=invite_feedback, **kwargs))