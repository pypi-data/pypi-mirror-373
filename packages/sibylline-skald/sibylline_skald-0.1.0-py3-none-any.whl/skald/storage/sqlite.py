"""SQLite storage backend for Skald."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

import aiosqlite
import structlog

from skald.schema.models import FeedbackReport, ToolRunMetadata
from skald.storage.base import StorageBackend

logger = structlog.get_logger(__name__)


class SQLiteStorage(StorageBackend):
    """SQLite storage backend for Skald feedback data."""
    
    def __init__(self, database_path: str | Path = "skald_feedback.db") -> None:
        """Initialize SQLite storage.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = Path(database_path)
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """Initialize the SQLite database and create tables."""
        # Ensure parent directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect with aiosqlite and try different settings
        self.connection = await aiosqlite.connect(str(self.database_path))
        
        # Try different PRAGMA settings
        await self.connection.execute("PRAGMA journal_mode = WAL")
        await self.connection.execute("PRAGMA foreign_keys = ON")
        await self.connection.execute("PRAGMA synchronous = NORMAL")
        
        # Create tables using the async method
        await self._create_tables()
        
        await self.connection.commit()
        logger.info("SQLite storage initialized", database_path=str(self.database_path))
    
    async def close(self) -> None:
        """Close the SQLite connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("SQLite storage closed")
    
    async def _create_tables(self) -> None:
        """Create the required tables."""
        # Tool runs table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tool_runs (
                trace_id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                output_bytes INTEGER NOT NULL,
                invite_feedback BOOLEAN NOT NULL,
                opt_out BOOLEAN NOT NULL DEFAULT 0,
                args_redacted TEXT NOT NULL DEFAULT '{}'
            )
        """)
        
        # Tool feedback table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tool_feedback (
                trace_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                helpfulness INTEGER NOT NULL CHECK (helpfulness BETWEEN 1 AND 5),
                fit INTEGER NOT NULL CHECK (fit BETWEEN 1 AND 5),
                clarity INTEGER NOT NULL CHECK (clarity BETWEEN 1 AND 5),
                confidence REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
                better_alternative TEXT NOT NULL DEFAULT '',
                suggestions TEXT NOT NULL DEFAULT '[]',
                notes TEXT NOT NULL DEFAULT '',
                valid BOOLEAN NOT NULL DEFAULT 1,
                raw_json TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for common queries
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_runs_agent_timestamp 
            ON tool_runs (agent_id, timestamp DESC)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_runs_tool_timestamp
            ON tool_runs (tool_name, timestamp DESC)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_runs_timestamp
            ON tool_runs (timestamp DESC)
        """)
    
    async def store_tool_run(self, metadata: ToolRunMetadata) -> None:
        """Store tool run metadata."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        try:
            await self.connection.execute("""
                INSERT INTO tool_runs (
                    trace_id, timestamp, agent_id, tool_name, status,
                    latency_ms, output_bytes, invite_feedback, opt_out, args_redacted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.trace_id,
                metadata.timestamp.isoformat(),
                metadata.agent_id,
                metadata.tool_name,
                metadata.status.value,
                metadata.latency_ms,
                metadata.output_bytes,
                metadata.invite_feedback,
                metadata.opt_out,
                json.dumps(metadata.args_redacted)
            ))
            
            await self.connection.commit()
            logger.debug("Stored tool run", trace_id=metadata.trace_id)
            
        except sqlite3.IntegrityError as e:
            # Handle duplicate trace_id - this is expected for idempotency
            if "UNIQUE constraint failed" in str(e):
                logger.debug("Tool run already exists", trace_id=metadata.trace_id)
            else:
                raise
    
    async def store_feedback(self, feedback: FeedbackReport, agent_id: str) -> None:
        """Store feedback report."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        # Validate that the trace_id exists
        cursor = await self.connection.execute(
            "SELECT 1 FROM tool_runs WHERE trace_id = ?",
            (feedback.trace_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            raise ValueError(f"No tool run found for trace_id: {feedback.trace_id}")
        
        try:
            await self.connection.execute("""
                INSERT OR REPLACE INTO tool_feedback (
                    trace_id, agent_id, helpfulness, fit, clarity, confidence,
                    better_alternative, suggestions, notes, valid, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.trace_id,
                agent_id,
                feedback.helpfulness,
                feedback.fit,
                feedback.clarity,
                feedback.confidence,
                feedback.better_alternative.value if feedback.better_alternative else "",
                json.dumps(feedback.suggestions),
                feedback.notes,
                True,  # valid - we've already validated via Pydantic
                feedback.model_dump_json()
            ))
            
            await self.connection.commit()
            logger.info("Stored feedback", trace_id=feedback.trace_id, agent_id=agent_id)
            
        except Exception as e:
            logger.error("Failed to store feedback", trace_id=feedback.trace_id, error=str(e))
            raise
    
    async def get_tool_run(self, trace_id: str) -> Optional[ToolRunMetadata]:
        """Get tool run metadata by trace ID."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cursor = await self.connection.execute("""
            SELECT trace_id, timestamp, agent_id, tool_name, status,
                   latency_ms, output_bytes, invite_feedback, opt_out, args_redacted
            FROM tool_runs WHERE trace_id = ?
        """, (trace_id,))
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        return ToolRunMetadata(
            trace_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            agent_id=row[2],
            tool_name=row[3],
            status=row[4],
            latency_ms=row[5],
            output_bytes=row[6],
            invite_feedback=bool(row[7]),
            opt_out=bool(row[8]),
            args_redacted=json.loads(row[9])
        )
    
    async def get_feedback(self, trace_id: str) -> Optional[FeedbackReport]:
        """Get feedback report by trace ID.""" 
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cursor = await self.connection.execute("""
            SELECT trace_id, helpfulness, fit, clarity, confidence,
                   better_alternative, suggestions, notes
            FROM tool_feedback WHERE trace_id = ?
        """, (trace_id,))
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        from skald.schema.models import BetterAlternative
        
        # Handle BetterAlternative enum safely
        better_alt = BetterAlternative.NO_ALTERNATIVE  # Default
        if row[5]:  # Only parse if not empty string
            try:
                better_alt = BetterAlternative(row[5])
            except ValueError:
                # If invalid enum value, default to NO_ALTERNATIVE
                better_alt = BetterAlternative.NO_ALTERNATIVE
        
        return FeedbackReport(
            trace_id=row[0],
            helpfulness=row[1],
            fit=row[2],
            clarity=row[3],
            confidence=row[4],
            better_alternative=better_alt,
            suggestions=json.loads(row[6]),
            notes=row[7]
        )
    
    async def list_tool_runs(
        self,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ToolRunMetadata]:
        """List tool runs with optional filtering."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        query = """
            SELECT trace_id, timestamp, agent_id, tool_name, status,
                   latency_ms, output_bytes, invite_feedback, opt_out, args_redacted
            FROM tool_runs
        """
        params = []
        conditions = []
        
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        
        if tool_name:
            conditions.append("tool_name = ?")
            params.append(tool_name)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        
        return [
            ToolRunMetadata(
                trace_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                agent_id=row[2],
                tool_name=row[3],
                status=row[4],
                latency_ms=row[5],
                output_bytes=row[6],
                invite_feedback=bool(row[7]),
                opt_out=bool(row[8]),
                args_redacted=json.loads(row[9])
            )
            for row in rows
        ]
    
    async def cleanup_expired(self, ttl_hours: int) -> int:
        """Clean up expired records."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        
        # First count records that will be deleted
        cursor_count = await self.connection.execute("""
            SELECT COUNT(*) FROM tool_runs WHERE timestamp < ?
        """, (cutoff_time.isoformat(),))
        count_row = await cursor_count.fetchone()
        await cursor_count.close()
        deleted_count = count_row[0] if count_row else 0
        
        # Then delete them
        cursor = await self.connection.execute("""
            DELETE FROM tool_runs WHERE timestamp < ?
        """, (cutoff_time.isoformat(),))
        await cursor.close()
        await self.connection.commit()
        
        if deleted_count > 0:
            logger.info("Cleaned up expired records", count=deleted_count, ttl_hours=ttl_hours)
        
        return deleted_count