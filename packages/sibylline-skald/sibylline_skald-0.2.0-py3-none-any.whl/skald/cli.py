"""Command-line interface for Skald."""

from __future__ import annotations

import asyncio
import sys
from typing import Any, Dict, Optional

import click
import structlog

from skald.core import SurveyingProxy
from skald.transport.stdio import StdioTransport
from skald.transport.tcp import TCPTransport

logger = structlog.get_logger(__name__)


class DummyMCPServer:
    """Dummy MCP server for testing and demonstration."""
    
    def __init__(self) -> None:
        self.tools = {
            "echo": {
                "description": "Echo back the input text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to echo"}
                    },
                    "required": ["text"]
                }
            },
            "math.add": {
                "description": "Add two numbers",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            }
        }
    
    def list_tools(self) -> list[str]:
        """List available tools."""
        return list(self.tools.keys())
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a tool."""
        return self.tools.get(tool_name, {})
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool."""
        if name == "echo":
            text = arguments.get("text", "")
            return MockMCPResponse([{"type": "text", "text": f"Echo: {text}"}])
        
        elif name == "math.add":
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            result = a + b
            return MockMCPResponse([{"type": "text", "text": f"{a} + {b} = {result}"}])
        
        else:
            raise ValueError(f"Unknown tool: {name}")


class MockMCPResponse:
    """Mock MCP response for testing."""
    
    def __init__(self, content: list[Dict[str, Any]], is_error: bool = False) -> None:
        self.content = content
        self.isError = is_error
        self.meta: Dict[str, Any] = {}


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    """Skald MCP feedback adapter."""
    # Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@main.command()
@click.option("--store", default="sqlite:///skald_demo.db", 
              help="Storage backend (default: sqlite:///skald_demo.db)")
@click.option("--ttl-hours", default=24, help="TTL for data in hours")
@click.option("--sample-rate", default=0.1, help="Sampling rate for neutral calls")
def stdio(store: str, ttl_hours: int, sample_rate: float) -> None:
    """Run Skald over standard I/O."""
    async def run_stdio() -> None:
        # Create dummy upstream server
        upstream = DummyMCPServer()
        
        # Create surveying proxy
        proxy = SurveyingProxy(
            upstream=upstream,
            store=store,
            ttl_hours=ttl_hours,
            sample_neutral=sample_rate
        )
        
        # Create and start transport
        transport = StdioTransport(proxy)
        
        try:
            await transport.serve()
        except KeyboardInterrupt:
            logger.info("Shutting down stdio transport")
        finally:
            await transport.stop()
    
    asyncio.run(run_stdio())


@main.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8765, help="Port to bind to")
@click.option("--store", default="sqlite:///skald_demo.db",
              help="Storage backend (default: sqlite:///skald_demo.db)")
@click.option("--ttl-hours", default=24, help="TTL for data in hours")
@click.option("--sample-rate", default=0.1, help="Sampling rate for neutral calls")
def tcp(host: str, port: int, store: str, ttl_hours: int, sample_rate: float) -> None:
    """Run Skald over TCP."""
    async def run_tcp() -> None:
        # Create dummy upstream server
        upstream = DummyMCPServer()
        
        # Create surveying proxy
        proxy = SurveyingProxy(
            upstream=upstream,
            store=store,
            ttl_hours=ttl_hours,
            sample_neutral=sample_rate
        )
        
        # Create and start transport
        transport = TCPTransport(proxy)
        
        try:
            await transport.serve(host=host, port=port)
        except KeyboardInterrupt:
            logger.info("Shutting down TCP transport")
        finally:
            await transport.stop()
    
    asyncio.run(run_tcp())


@main.command()
@click.option("--store", default="sqlite:///skald_demo.db",
              help="Storage backend to query")
@click.option("--agent-id", help="Filter by agent ID")
@click.option("--tool-name", help="Filter by tool name") 
@click.option("--limit", default=10, help="Maximum results to show")
def query(store: str, agent_id: Optional[str], tool_name: Optional[str], limit: int) -> None:
    """Query stored feedback data."""
    async def run_query() -> None:
        from skald.storage.sqlite import SQLiteStorage
        
        # Extract database path from store string
        if store.startswith("sqlite:///"):
            db_path = store[10:]
        else:
            click.echo(f"Unsupported store format: {store}")
            sys.exit(1)
        
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        
        try:
            # Query tool runs
            runs = await storage.list_tool_runs(
                agent_id=agent_id,
                tool_name=tool_name,
                limit=limit
            )
            
            click.echo(f"Found {len(runs)} tool runs:")
            click.echo()
            
            for run in runs:
                click.echo(f"Trace ID: {run.trace_id}")
                click.echo(f"  Agent: {run.agent_id}")
                click.echo(f"  Tool: {run.tool_name}")
                click.echo(f"  Status: {run.status.value}")
                click.echo(f"  Latency: {run.latency_ms:.2f}ms")
                click.echo(f"  Output size: {run.output_bytes} bytes")
                click.echo(f"  Invite feedback: {run.invite_feedback}")
                click.echo(f"  Timestamp: {run.timestamp}")
                
                # Check if feedback exists
                feedback = await storage.get_feedback(run.trace_id)
                if feedback:
                    click.echo(f"  Feedback: {feedback.helpfulness}/5 helpfulness, " +
                             f"{feedback.fit}/5 fit, {feedback.clarity}/5 clarity")
                    if feedback.suggestions:
                        click.echo(f"  Suggestions: {', '.join(feedback.suggestions)}")
                
                click.echo()
        
        finally:
            await storage.close()
    
    asyncio.run(run_query())


@main.command()
@click.option("--store", default="sqlite:///skald_demo.db",
              help="Storage backend to clean up")
@click.option("--ttl-hours", default=24, help="TTL for data in hours")
def cleanup(store: str, ttl_hours: int) -> None:
    """Clean up expired data."""
    async def run_cleanup() -> None:
        from skald.storage.sqlite import SQLiteStorage
        
        # Extract database path from store string
        if store.startswith("sqlite:///"):
            db_path = store[10:]
        else:
            click.echo(f"Unsupported store format: {store}")
            sys.exit(1)
        
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        
        try:
            deleted_count = await storage.cleanup_expired(ttl_hours)
            click.echo(f"Deleted {deleted_count} expired records")
        finally:
            await storage.close()
    
    asyncio.run(run_cleanup())


@main.group()
def export() -> None:
    """Export data to various formats for analytics."""
    pass


@export.command("parquet")
@click.option("--store", default="sqlite:///skald_demo.db",
              help="Source SQLite database")
@click.option("--output-dir", default="parquet_exports",
              help="Output directory for Parquet files")
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Start date for export (YYYY-MM-DD)")
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="End date for export (YYYY-MM-DD)")
@click.option("--tenant-id", help="Filter by specific tenant ID")
@click.option("--yesterday", is_flag=True, help="Export yesterday's data")
@click.option("--force", is_flag=True, help="Overwrite existing files")
@click.option("--compression", default="snappy", 
              type=click.Choice(["snappy", "gzip", "lz4", "brotli"]),
              help="Parquet compression algorithm")
def export_parquet(
    store: str, 
    output_dir: str, 
    start_date: Optional[click.DateTime], 
    end_date: Optional[click.DateTime],
    tenant_id: Optional[str],
    yesterday: bool,
    force: bool,
    compression: str
) -> None:
    """Export event data to Parquet format for analytics."""
    async def run_export() -> None:
        from datetime import datetime, timedelta, timezone
        from skald.storage.sqlite import SQLiteStorage
        from skald.export.parquet import ParquetExporter, ExportConfig
        
        # Extract database path from store string
        if store.startswith("sqlite:///"):
            db_path = store[10:]
        else:
            click.echo(f"Unsupported store format: {store}")
            sys.exit(1)
        
        # Initialize storage and exporter
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        
        config = ExportConfig(
            output_dir=output_dir,
            compression=compression
        )
        exporter = ParquetExporter(storage, config)
        
        try:
            if yesterday:
                click.echo("Exporting yesterday's data...")
                stats = await exporter.export_yesterday(force_overwrite=force)
            elif start_date and end_date:
                click.echo(f"Exporting data from {start_date} to {end_date}...")
                # Convert click.DateTime to datetime
                start_dt = datetime.fromisoformat(start_date.isoformat()).replace(tzinfo=timezone.utc)
                end_dt = datetime.fromisoformat(end_date.isoformat()).replace(tzinfo=timezone.utc)
                stats = await exporter.export_date_range(
                    start_dt, end_dt, tenant_id, force_overwrite=force
                )
            elif start_date:
                click.echo(f"Exporting data for {start_date}...")
                start_dt = datetime.fromisoformat(start_date.isoformat()).replace(tzinfo=timezone.utc)
                stats = await exporter.export_daily(start_dt, force_overwrite=force)
            else:
                click.echo("Error: Must specify --yesterday, --start-date, or both --start-date and --end-date")
                sys.exit(1)
            
            # Display results
            click.echo(f"\n✅ Export completed successfully!")
            click.echo(f"   Files created: {stats['files_created']}")
            click.echo(f"   Rows exported: {stats['rows_exported']:,}")
            click.echo(f"   Bytes written: {stats['bytes_written']:,}")
            click.echo(f"   Execution time: {stats['execution_time_seconds']:.2f}s")
            
        except Exception as e:
            click.echo(f"❌ Export failed: {e}")
            sys.exit(1)
        finally:
            await storage.close()
    
    asyncio.run(run_export())


@export.command("backfill")
@click.option("--store", default="sqlite:///skald_demo.db",
              help="Source SQLite database")
@click.option("--output-dir", default="parquet_exports",
              help="Output directory for Parquet files")
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True,
              help="Start date for backfill (YYYY-MM-DD)")
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="End date for backfill (defaults to yesterday)")
@click.option("--skip-existing", is_flag=True, default=True,
              help="Skip dates that already have exports")
@click.option("--compression", default="snappy",
              type=click.Choice(["snappy", "gzip", "lz4", "brotli"]),
              help="Parquet compression algorithm")
def export_backfill(
    store: str,
    output_dir: str,
    start_date: click.DateTime,
    end_date: Optional[click.DateTime],
    skip_existing: bool,
    compression: str
) -> None:
    """Backfill missing Parquet exports for a date range."""
    async def run_backfill() -> None:
        from datetime import datetime, timezone
        from skald.storage.sqlite import SQLiteStorage
        from skald.export.parquet import ParquetExporter, ExportConfig
        
        # Extract database path from store string
        if store.startswith("sqlite:///"):
            db_path = store[10:]
        else:
            click.echo(f"Unsupported store format: {store}")
            sys.exit(1)
        
        # Initialize storage and exporter
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        
        config = ExportConfig(
            output_dir=output_dir,
            compression=compression
        )
        exporter = ParquetExporter(storage, config)
        
        try:
            # Convert click.DateTime to datetime
            start_dt = datetime.fromisoformat(start_date.isoformat()).replace(tzinfo=timezone.utc)
            end_dt = None
            if end_date:
                end_dt = datetime.fromisoformat(end_date.isoformat()).replace(tzinfo=timezone.utc)
            
            click.echo(f"Starting backfill from {start_dt.strftime('%Y-%m-%d')}...")
            if end_dt:
                click.echo(f"End date: {end_dt.strftime('%Y-%m-%d')}")
            else:
                click.echo("End date: yesterday")
            
            stats = await exporter.backfill_missing_dates(
                start_dt, end_dt, skip_existing=skip_existing
            )
            
            # Display results
            click.echo(f"\n✅ Backfill completed successfully!")
            click.echo(f"   Dates processed: {stats['dates_processed']}")
            click.echo(f"   Dates skipped: {stats['dates_skipped']}")
            click.echo(f"   Total files created: {stats['total_files_created']}")
            click.echo(f"   Total rows exported: {stats['total_rows_exported']:,}")
            click.echo(f"   Total bytes written: {stats['total_bytes_written']:,}")
            
        except Exception as e:
            click.echo(f"❌ Backfill failed: {e}")
            sys.exit(1)
        finally:
            await storage.close()
    
    asyncio.run(run_backfill())


@export.command("cleanup")
@click.option("--output-dir", default="parquet_exports",
              help="Parquet exports directory to clean up")
@click.option("--retention-days", default=90, type=int,
              help="Number of days to retain exports")
@click.confirmation_option(prompt="Are you sure you want to delete old export files?")
def export_cleanup(output_dir: str, retention_days: int) -> None:
    """Clean up old Parquet export files."""
    async def run_cleanup() -> None:
        from skald.storage.sqlite import SQLiteStorage
        from skald.export.parquet import ParquetExporter, ExportConfig
        
        # We don't need storage for cleanup, but ParquetExporter requires it
        # This is a design issue that could be improved
        storage = SQLiteStorage(":memory:")
        await storage.initialize()
        
        config = ExportConfig(
            output_dir=output_dir,
            retention_days=retention_days
        )
        exporter = ParquetExporter(storage, config)
        
        try:
            click.echo(f"Cleaning up exports older than {retention_days} days...")
            
            stats = await exporter.cleanup_old_exports()
            
            # Display results
            if stats["files_deleted"] > 0:
                click.echo(f"✅ Cleanup completed!")
                click.echo(f"   Files deleted: {stats['files_deleted']}")
                click.echo(f"   Bytes freed: {stats['bytes_freed']:,}")
            else:
                click.echo("ℹ️ No old files found to clean up.")
            
        except Exception as e:
            click.echo(f"❌ Cleanup failed: {e}")
            sys.exit(1)
        finally:
            await storage.close()
    
    asyncio.run(run_cleanup())


@main.command()
@click.option("--storage", default="skald_events.db",
              help="SQLite database path")
@click.option("--output-dir", default="parquet_exports",
              help="Output directory for Parquet files")
@click.option("--export-time", default="02:00",
              help="Daily export time (HH:MM UTC)")
@click.option("--check-interval", default=300, type=int,
              help="Check interval in seconds")
@click.option("--disable-cleanup", is_flag=True,
              help="Disable automatic cleanup tasks")
def scheduler(
    storage: str,
    output_dir: str,
    export_time: str,
    check_interval: int,
    disable_cleanup: bool
) -> None:
    """Run the Skald task scheduler daemon."""
    async def run_scheduler() -> None:
        from datetime import time as dt_time
        from skald.scheduler import TaskScheduler, create_default_parquet_exporter
        
        # Parse export time
        try:
            hour, minute = map(int, export_time.split(':'))
            export_dt = dt_time(hour, minute)
        except ValueError:
            click.echo(f"Invalid time format: {export_time}. Use HH:MM format.")
            sys.exit(1)
        
        # Create scheduler
        scheduler_instance = TaskScheduler(check_interval=check_interval)
        
        # Add daily export task
        export_func = await create_default_parquet_exporter(storage, output_dir)
        scheduler_instance.add_task(
            "daily_parquet_export",
            export_func,
            export_dt,
            enabled=True
        )
        
        # Add cleanup task if enabled
        if not disable_cleanup:
            from datetime import datetime, timedelta
            cleanup_time = (datetime.combine(datetime.today(), export_dt) + timedelta(hours=1)).time()
            
            async def cleanup_task():
                from skald.storage.sqlite import SQLiteStorage
                
                storage_instance = SQLiteStorage(storage)
                await storage_instance.initialize()
                
                try:
                    deleted_count = await storage_instance.cleanup_expired(24 * 7)
                    logger.info("Database cleanup completed", deleted_records=deleted_count)
                except Exception as e:
                    logger.error("Database cleanup failed", error=str(e))
                    raise
                finally:
                    await storage_instance.close()
            
            scheduler_instance.add_task(
                "daily_cleanup",
                cleanup_task,
                cleanup_time,
                enabled=True
            )
        
        # Start scheduler
        logger.info(
            "Starting Skald task scheduler",
            storage=storage,
            output_dir=output_dir,
            export_time=export_time,
            check_interval=check_interval,
            cleanup_enabled=not disable_cleanup
        )
        
        try:
            await scheduler_instance.start()
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(60)
                
                # Log status periodically
                status = scheduler_instance.get_status()
                logger.debug("Scheduler status", **status)
                
        except KeyboardInterrupt:
            logger.info("Shutting down task scheduler")
        finally:
            await scheduler_instance.stop()
    
    asyncio.run(run_scheduler())

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=4001, help="Port to bind to")
@click.option("--db", default="skald_events.db", help="SQLite database path")
@click.option("--max-batch-size", default=1000, help="Maximum events per batch")
@click.option("--max-batch-bytes", default=131072, help="Maximum batch size in bytes")
def collector(host: str, port: int, db: str, max_batch_size: int, max_batch_bytes: int) -> None:
    """Run the Skald event collector REST service."""
    import uvicorn
    from skald.collector import collector as collector_instance
    
    # Update collector configuration
    collector_instance.db_path = db
    collector_instance.max_batch_size = max_batch_size
    collector_instance.max_batch_bytes = max_batch_bytes
    
    logger.info(
        "Starting Skald event collector",
        host=host,
        port=port,
        db=db,
        max_batch_size=max_batch_size,
        max_batch_bytes=max_batch_bytes
    )
    
    uvicorn.run(
        "skald.collector:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

# Register commands with the main group
main.add_command(stdio)
main.add_command(tcp)
main.add_command(query)
main.add_command(cleanup)
main.add_command(collector)
main.add_command(export)
main.add_command(scheduler)


if __name__ == "__main__":
    main()