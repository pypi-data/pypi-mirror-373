"""Parquet export functionality for Skald event data.

This module provides functionality to export SQLite event data to Parquet files
partitioned by date and tenant for efficient analytics processing.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog
from pydantic import BaseModel

from skald.storage.sqlite import SQLiteStorage

logger = structlog.get_logger(__name__)


class ExportConfig(BaseModel):
    """Configuration for Parquet export functionality."""
    
    output_dir: str = "parquet_exports"
    partition_by_tenant: bool = True
    partition_by_date: bool = True
    compression: str = "snappy"
    max_rows_per_file: int = 1_000_000
    retention_days: int = 90
    export_batch_size: int = 10_000


class ParquetExporter:
    """Exports Skald event data to partitioned Parquet files for analytics."""
    
    def __init__(self, storage: SQLiteStorage, config: Optional[ExportConfig] = None):
        self.storage = storage
        self.config = config or ExportConfig()
        self.output_dir = Path(self.config.output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ParquetExporter initialized", 
                   output_dir=str(self.output_dir),
                   config=self.config.model_dump())
    
    async def export_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str] = None,
        force_overwrite: bool = False
    ) -> Dict[str, Any]:
        """Export data for a specific date range to Parquet files.
        
        Args:
            start_date: Start date for export (inclusive)
            end_date: End date for export (exclusive)
            tenant_id: Optional tenant filter
            force_overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with export statistics
        """
        stats = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tenant_id": tenant_id,
            "files_created": 0,
            "rows_exported": 0,
            "bytes_written": 0,
            "execution_time_seconds": 0
        }
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get data from SQLite
            logger.info("Starting Parquet export", 
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat(),
                       tenant_id=tenant_id)
            
            # Query tool runs in the date range
            query_conditions = {
                "start_time": start_date,
                "end_time": end_date,
                "limit": None  # Export all matching records
            }
            
            if tenant_id:
                query_conditions["agent_id"] = tenant_id  # Using agent_id as tenant for v1 compatibility
            
            tool_runs = await self._get_tool_runs_for_export(query_conditions)
            
            if not tool_runs:
                logger.info("No data found for export", **query_conditions)
                return stats
            
            # Group by date and tenant for partitioning
            partitioned_data = self._partition_data(tool_runs)
            
            # Export each partition
            for partition_key, records in partitioned_data.items():
                file_stats = await self._export_partition(
                    partition_key, 
                    records, 
                    force_overwrite
                )
                
                stats["files_created"] += file_stats["files_created"]
                stats["rows_exported"] += file_stats["rows_exported"]
                stats["bytes_written"] += file_stats["bytes_written"]
            
            stats["execution_time_seconds"] = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            
            logger.info("Parquet export completed", **stats)
            return stats
            
        except Exception as e:
            logger.error("Parquet export failed", error=str(e), **stats)
            raise
    
    async def export_daily(self, target_date: datetime, force_overwrite: bool = False) -> Dict[str, Any]:
        """Export data for a specific day.
        
        Args:
            target_date: Date to export (will export full day)
            force_overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with export statistics
        """
        # Normalize to start of day
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        return await self.export_date_range(start_date, end_date, force_overwrite=force_overwrite)
    
    async def export_yesterday(self, force_overwrite: bool = False) -> Dict[str, Any]:
        """Export data from yesterday (common use case for daily cron jobs)."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        return await self.export_daily(yesterday, force_overwrite)
    
    async def backfill_missing_dates(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """Backfill missing Parquet exports for a date range.
        
        Args:
            start_date: Start date for backfill
            end_date: End date for backfill (defaults to yesterday)
            skip_existing: Whether to skip dates that already have exports
            
        Returns:
            Dictionary with backfill statistics
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        backfill_stats = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "dates_processed": 0,
            "dates_skipped": 0,
            "total_files_created": 0,
            "total_rows_exported": 0,
            "total_bytes_written": 0
        }
        
        current_date = start_date
        
        while current_date < end_date:
            # Check if export already exists
            if skip_existing and self._export_exists_for_date(current_date):
                logger.debug("Skipping existing export", date=current_date.isoformat())
                backfill_stats["dates_skipped"] += 1
            else:
                try:
                    daily_stats = await self.export_daily(current_date, force_overwrite=not skip_existing)
                    backfill_stats["dates_processed"] += 1
                    backfill_stats["total_files_created"] += daily_stats["files_created"]
                    backfill_stats["total_rows_exported"] += daily_stats["rows_exported"]
                    backfill_stats["total_bytes_written"] += daily_stats["bytes_written"]
                    
                    logger.info("Backfilled date", 
                               date=current_date.isoformat(),
                               **daily_stats)
                               
                except Exception as e:
                    logger.error("Failed to backfill date", 
                               date=current_date.isoformat(),
                               error=str(e))
            
            current_date += timedelta(days=1)
        
        logger.info("Backfill completed", **backfill_stats)
        return backfill_stats
    
    async def cleanup_old_exports(self, retention_days: Optional[int] = None) -> Dict[str, Any]:
        """Clean up old Parquet exports based on retention policy.
        
        Args:
            retention_days: Days to retain (defaults to config value)
            
        Returns:
            Dictionary with cleanup statistics
        """
        retention_days = retention_days or self.config.retention_days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        cleanup_stats = {
            "cutoff_date": cutoff_date.isoformat(),
            "files_deleted": 0,
            "bytes_freed": 0
        }
        
        # Find all Parquet files older than cutoff
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                if not file.endswith('.parquet'):
                    continue
                
                file_path = Path(root) / file
                
                # Extract date from path structure (dt=YYYY-MM-DD)
                if '/dt=' in str(file_path):
                    try:
                        date_str = str(file_path).split('/dt=')[1].split('/')[0]
                        file_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                        
                        if file_date < cutoff_date:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            
                            cleanup_stats["files_deleted"] += 1
                            cleanup_stats["bytes_freed"] += file_size
                            
                            logger.info("Deleted old export file",
                                       file=str(file_path),
                                       date=file_date.isoformat())
                    except (ValueError, IndexError):
                        logger.warning("Could not parse date from file path", file=str(file_path))
        
        # Clean up empty directories
        self._cleanup_empty_directories()
        
        logger.info("Cleanup completed", **cleanup_stats)
        return cleanup_stats
    
    async def _get_tool_runs_for_export(self, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query tool runs from SQLite for export."""
        # This would need to be implemented based on the actual SQLiteStorage schema
        # For now, we'll use a placeholder that works with the existing interface
        
        tool_runs = await self.storage.list_tool_runs(
            agent_id=conditions.get("agent_id"),
            tool_name=None,
            limit=conditions.get("limit"),
            # Note: The existing interface doesn't support date filtering
            # This would need to be extended in SQLiteStorage
        )
        
        # Filter by date in memory (not ideal for large datasets)
        if "start_time" in conditions and "end_time" in conditions:
            start_time = conditions["start_time"]
            end_time = conditions["end_time"]
            
            tool_runs = [
                run for run in tool_runs
                if start_time <= run.timestamp < end_time
            ]
        
        # Convert to dict format for Pandas
        return [
            {
                "trace_id": run.trace_id,
                "timestamp": run.timestamp,
                "agent_id": run.agent_id,
                "tool_name": run.tool_name,
                "status": run.status.value,
                "latency_ms": run.latency_ms,
                "output_bytes": run.output_bytes,
                "invite_feedback": run.invite_feedback,
                "opt_out": run.opt_out,
                "args_redacted": run.args_redacted,
                "date": run.timestamp.strftime('%Y-%m-%d'),
                "hour": run.timestamp.hour
            }
            for run in tool_runs
        ]
    
    def _partition_data(self, tool_runs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Partition data by date and tenant for efficient file organization."""
        partitions = {}
        
        for run in tool_runs:
            # Create partition key
            partition_parts = []
            
            if self.config.partition_by_date:
                partition_parts.append(f"dt={run['date']}")
            
            if self.config.partition_by_tenant:
                partition_parts.append(f"tenant_id={run['agent_id']}")
            
            partition_key = "/".join(partition_parts) if partition_parts else "default"
            
            if partition_key not in partitions:
                partitions[partition_key] = []
            
            partitions[partition_key].append(run)
        
        return partitions
    
    async def _export_partition(
        self,
        partition_key: str,
        records: List[Dict[str, Any]],
        force_overwrite: bool
    ) -> Dict[str, Any]:
        """Export a single partition to Parquet file(s)."""
        partition_dir = self.output_dir / partition_key
        partition_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "files_created": 0,
            "rows_exported": 0,
            "bytes_written": 0
        }
        
        # Split into chunks if needed
        max_rows = self.config.max_rows_per_file
        chunks = [records[i:i + max_rows] for i in range(0, len(records), max_rows)]
        
        for chunk_idx, chunk in enumerate(chunks):
            # Generate filename
            if len(chunks) > 1:
                filename = f"events_part_{chunk_idx:04d}.parquet"
            else:
                filename = "events.parquet"
            
            file_path = partition_dir / filename
            
            # Skip if exists and not forcing overwrite
            if file_path.exists() and not force_overwrite:
                logger.debug("Skipping existing file", file=str(file_path))
                continue
            
            # Convert to DataFrame and write
            df = pd.DataFrame(chunk)
            
            # Ensure timestamp is datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            
            # Write Parquet file
            df.to_parquet(
                file_path,
                compression=self.config.compression,
                index=False
            )
            
            file_size = file_path.stat().st_size
            
            stats["files_created"] += 1
            stats["rows_exported"] += len(chunk)
            stats["bytes_written"] += file_size
            
            logger.info("Created Parquet file",
                       file=str(file_path),
                       rows=len(chunk),
                       size_bytes=file_size)
        
        return stats
    
    def _export_exists_for_date(self, date: datetime) -> bool:
        """Check if export already exists for a given date."""
        date_str = date.strftime('%Y-%m-%d')
        date_dir = self.output_dir / f"dt={date_str}"
        
        if not date_dir.exists():
            return False
        
        # Check if any .parquet files exist in date directory or subdirectories
        return any(date_dir.rglob("*.parquet"))
    
    def _cleanup_empty_directories(self):
        """Remove empty directories after cleanup."""
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.debug("Removed empty directory", dir=str(dir_path))
                except OSError:
                    # Directory not empty or other error
                    pass