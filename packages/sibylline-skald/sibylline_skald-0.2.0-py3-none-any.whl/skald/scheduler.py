"""Background task scheduler for automated Skald operations.

This module provides scheduling capabilities for automated tasks like:
- Daily Parquet exports
- Cleanup of expired data
- Health checks and monitoring
"""

import asyncio
from datetime import datetime, time, timezone
from typing import Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class ScheduledTask:
    """Represents a scheduled task with timing and execution logic."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        schedule_time: time,
        enabled: bool = True,
        timezone_aware: bool = True
    ):
        self.name = name
        self.func = func
        self.schedule_time = schedule_time
        self.enabled = enabled
        self.timezone_aware = timezone_aware
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        
        self._calculate_next_run()
    
    def _calculate_next_run(self) -> None:
        """Calculate the next run time for this task."""
        now = datetime.now(timezone.utc if self.timezone_aware else None)
        today = now.date()
        
        # Calculate next run time
        if self.timezone_aware:
            next_run = datetime.combine(today, self.schedule_time, tzinfo=timezone.utc)
        else:
            next_run = datetime.combine(today, self.schedule_time)
        
        # If the scheduled time has already passed today, schedule for tomorrow
        if next_run <= now:
            from datetime import timedelta
            if self.timezone_aware:
                next_run = datetime.combine(
                    today + timedelta(days=1), 
                    self.schedule_time, 
                    tzinfo=timezone.utc
                )
            else:
                next_run = datetime.combine(
                    today + timedelta(days=1), 
                    self.schedule_time
                )
        
        self.next_run = next_run
        
        logger.debug(
            "Calculated next run time",
            task=self.name,
            next_run=self.next_run.isoformat() if self.next_run else None
        )
    
    async def execute(self) -> bool:
        """Execute the scheduled task."""
        if not self.enabled:
            logger.debug("Task disabled, skipping", task=self.name)
            return False
        
        try:
            logger.info("Executing scheduled task", task=self.name)
            
            # Call the function (may be sync or async)
            if asyncio.iscoroutinefunction(self.func):
                await self.func()
            else:
                self.func()
            
            self.last_run = datetime.now(timezone.utc if self.timezone_aware else None)
            self.run_count += 1
            self._calculate_next_run()
            
            logger.info(
                "Scheduled task completed successfully",
                task=self.name,
                run_count=self.run_count
            )
            return True
            
        except Exception as e:
            self.error_count += 1
            logger.error(
                "Scheduled task failed",
                task=self.name,
                error=str(e),
                error_count=self.error_count
            )
            
            # Still calculate next run even if this one failed
            self._calculate_next_run()
            return False
    
    def should_run_now(self) -> bool:
        """Check if this task should run now."""
        if not self.enabled or not self.next_run:
            return False
        
        now = datetime.now(timezone.utc if self.timezone_aware else None)
        return now >= self.next_run
    
    def get_status(self) -> Dict:
        """Get current status of this task."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "schedule_time": self.schedule_time.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "error_count": self.error_count
        }


class TaskScheduler:
    """Manages and executes scheduled tasks."""
    
    def __init__(self, check_interval: int = 60):
        """Initialize the task scheduler.
        
        Args:
            check_interval: How often to check for tasks to run (seconds)
        """
        self.check_interval = check_interval
        self.tasks: List[ScheduledTask] = []
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def add_task(
        self,
        name: str,
        func: Callable,
        schedule_time: time,
        enabled: bool = True
    ) -> ScheduledTask:
        """Add a new scheduled task."""
        task = ScheduledTask(name, func, schedule_time, enabled)
        self.tasks.append(task)
        
        logger.info(
            "Added scheduled task",
            name=name,
            schedule_time=schedule_time.isoformat(),
            next_run=task.next_run.isoformat() if task.next_run else None
        )
        
        return task
    
    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task by name."""
        for i, task in enumerate(self.tasks):
            if task.name == name:
                del self.tasks[i]
                logger.info("Removed scheduled task", name=name)
                return True
        
        logger.warning("Task not found for removal", name=name)
        return False
    
    def get_task(self, name: str) -> Optional[ScheduledTask]:
        """Get a scheduled task by name."""
        for task in self.tasks:
            if task.name == name:
                return task
        return None
    
    def enable_task(self, name: str) -> bool:
        """Enable a scheduled task."""
        task = self.get_task(name)
        if task:
            task.enabled = True
            task._calculate_next_run()
            logger.info("Enabled scheduled task", name=name)
            return True
        
        logger.warning("Task not found for enabling", name=name)
        return False
    
    def disable_task(self, name: str) -> bool:
        """Disable a scheduled task."""
        task = self.get_task(name)
        if task:
            task.enabled = False
            logger.info("Disabled scheduled task", name=name)
            return True
        
        logger.warning("Task not found for disabling", name=name)
        return False
    
    async def start(self) -> None:
        """Start the task scheduler."""
        if self._running:
            logger.warning("Task scheduler already running")
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info(
            "Task scheduler started",
            check_interval=self.check_interval,
            task_count=len(self.tasks)
        )
    
    async def stop(self) -> None:
        """Stop the task scheduler."""
        self._running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks and executes tasks."""
        while self._running:
            try:
                # Check each task to see if it should run
                for task in self.tasks:
                    if task.should_run_now():
                        # Execute task in the background to avoid blocking
                        asyncio.create_task(task.execute())
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Scheduler loop error", error=str(e))
                await asyncio.sleep(self.check_interval)
    
    def get_status(self) -> Dict:
        """Get status of the scheduler and all tasks."""
        return {
            "running": self._running,
            "check_interval": self.check_interval,
            "task_count": len(self.tasks),
            "tasks": [task.get_status() for task in self.tasks]
        }


async def create_default_parquet_exporter(
    storage_path: str = "skald_events.db",
    output_dir: str = "parquet_exports"
):
    """Create a default Parquet export function for daily scheduling."""
    from skald.storage.sqlite import SQLiteStorage
    from skald.export.parquet import ParquetExporter, ExportConfig
    
    async def daily_export():
        """Perform daily Parquet export of yesterday's data."""
        storage = SQLiteStorage(storage_path)
        await storage.initialize()
        
        try:
            config = ExportConfig(output_dir=output_dir)
            exporter = ParquetExporter(storage, config)
            
            stats = await exporter.export_yesterday()
            logger.info("Daily Parquet export completed", **stats)
            
            # Also perform cleanup of old exports
            cleanup_stats = await exporter.cleanup_old_exports()
            if cleanup_stats["files_deleted"] > 0:
                logger.info("Old Parquet files cleaned up", **cleanup_stats)
            
        except Exception as e:
            logger.error("Daily Parquet export failed", error=str(e))
            raise
        finally:
            await storage.close()
    
    return daily_export


def create_default_scheduler(
    storage_path: str = "skald_events.db",
    output_dir: str = "parquet_exports",
    export_time: time = time(2, 0),  # 2:00 AM UTC
    enable_cleanup: bool = True
) -> TaskScheduler:
    """Create a task scheduler with default Skald maintenance tasks.
    
    Args:
        storage_path: Path to SQLite database
        output_dir: Directory for Parquet exports  
        export_time: Time to run daily export (UTC)
        enable_cleanup: Whether to enable cleanup tasks
        
    Returns:
        Configured TaskScheduler instance
    """
    scheduler = TaskScheduler(check_interval=300)  # Check every 5 minutes
    
    # Add daily Parquet export task
    async def setup_export_task():
        export_func = await create_default_parquet_exporter(storage_path, output_dir)
        scheduler.add_task(
            "daily_parquet_export",
            export_func,
            export_time,
            enabled=True
        )
    
    # We need to set up the export task properly since it's async
    import asyncio
    asyncio.create_task(setup_export_task())
    
    # Add cleanup task (runs at 3:00 AM UTC, 1 hour after export)
    if enable_cleanup:
        from datetime import timedelta
        cleanup_time = (datetime.combine(datetime.today(), export_time) + timedelta(hours=1)).time()
        
        async def cleanup_task():
            """Clean up expired data from SQLite."""
            from skald.storage.sqlite import SQLiteStorage
            
            storage = SQLiteStorage(storage_path)
            await storage.initialize()
            
            try:
                deleted_count = await storage.cleanup_expired(24 * 7)  # 1 week TTL
                logger.info("Database cleanup completed", deleted_records=deleted_count)
            except Exception as e:
                logger.error("Database cleanup failed", error=str(e))
                raise
            finally:
                await storage.close()
        
        scheduler.add_task(
            "daily_cleanup",
            cleanup_task,
            cleanup_time,
            enabled=True
        )
    
    return scheduler