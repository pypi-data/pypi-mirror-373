"""SQLite storage backend for Skald."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

import aiosqlite
import structlog

from skald.schema.models import FeedbackReport, ToolRunMetadata, ExecutionMetadata, UniversalFeedbackReport
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
        
        # Universal execution metadata table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                trace_id TEXT PRIMARY KEY,
                execution_context TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                name TEXT NOT NULL,
                module_name TEXT,
                file_path TEXT,
                line_number INTEGER,
                command_line TEXT,
                working_directory TEXT,
                status TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                memory_delta_mb REAL,
                cpu_percent REAL,
                input_args TEXT NOT NULL DEFAULT '{}',
                input_size_bytes INTEGER NOT NULL DEFAULT 0,
                output_size_bytes INTEGER NOT NULL DEFAULT 0,
                return_value_type TEXT,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT,
                process_id INTEGER,
                exit_code INTEGER,
                invite_feedback BOOLEAN NOT NULL DEFAULT 0,
                opt_out BOOLEAN NOT NULL DEFAULT 0,
                redaction_applied BOOLEAN NOT NULL DEFAULT 0,
                redaction_rule_id TEXT
            )
        """)
        
        # Universal feedback table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS universal_feedback (
                trace_id TEXT PRIMARY KEY,
                execution_context TEXT NOT NULL,
                effectiveness INTEGER NOT NULL CHECK (effectiveness BETWEEN 1 AND 5),
                efficiency INTEGER NOT NULL CHECK (efficiency BETWEEN 1 AND 5),
                clarity INTEGER NOT NULL CHECK (clarity BETWEEN 1 AND 5),
                reliability INTEGER NOT NULL CHECK (reliability BETWEEN 1 AND 5),
                ease_of_use INTEGER CHECK (ease_of_use BETWEEN 1 AND 5),
                documentation_quality INTEGER CHECK (documentation_quality BETWEEN 1 AND 5),
                error_handling INTEGER CHECK (error_handling BETWEEN 1 AND 5),
                confidence REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
                would_recommend BOOLEAN NOT NULL,
                better_alternative TEXT NOT NULL DEFAULT '',
                suggestions TEXT NOT NULL DEFAULT '[]',
                what_worked_well TEXT NOT NULL DEFAULT '',
                what_could_improve TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                user_expertise_level TEXT,
                use_case_category TEXT,
                raw_json TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for execution queries
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_context_timestamp
            ON executions (execution_context, timestamp DESC)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_name_timestamp
            ON executions (name, timestamp DESC)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_timestamp
            ON executions (timestamp DESC)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_status
            ON executions (status, timestamp DESC)
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
    
    async def store_execution(self, metadata: ExecutionMetadata) -> None:
        """Store universal execution metadata."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        try:
            await self.connection.execute("""
                INSERT INTO executions (
                    trace_id, execution_context, timestamp, name, module_name,
                    file_path, line_number, command_line, working_directory,
                    status, latency_ms, memory_delta_mb, cpu_percent,
                    input_args, input_size_bytes, output_size_bytes, return_value_type,
                    error_type, error_message, stack_trace, process_id, exit_code,
                    invite_feedback, opt_out, redaction_applied, redaction_rule_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.trace_id,
                metadata.execution_context.value,
                metadata.timestamp.isoformat(),
                metadata.name,
                metadata.module_name,
                metadata.file_path,
                metadata.line_number,
                metadata.command_line,
                metadata.working_directory,
                metadata.status.value,
                metadata.latency_ms,
                metadata.memory_delta_mb,
                metadata.cpu_percent,
                json.dumps(metadata.input_args),
                metadata.input_size_bytes,
                metadata.output_size_bytes,
                metadata.return_value_type,
                metadata.error_type,
                metadata.error_message,
                metadata.stack_trace,
                metadata.process_id,
                metadata.exit_code,
                metadata.invite_feedback,
                metadata.opt_out,
                metadata.redaction_applied,
                metadata.redaction_rule_id
            ))
            
            await self.connection.commit()
            logger.debug("Stored execution metadata", trace_id=metadata.trace_id)
            
        except sqlite3.IntegrityError as e:
            # Handle duplicate trace_id - this is expected for idempotency
            if "UNIQUE constraint failed" in str(e):
                logger.debug("Execution metadata already exists", trace_id=metadata.trace_id)
            else:
                raise
    
    async def store_universal_feedback(self, feedback: UniversalFeedbackReport) -> None:
        """Store universal feedback report."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        # Validate that the trace_id exists
        cursor = await self.connection.execute(
            "SELECT 1 FROM executions WHERE trace_id = ?",
            (feedback.trace_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            raise ValueError(f"No execution found for trace_id: {feedback.trace_id}")
        
        try:
            await self.connection.execute("""
                INSERT OR REPLACE INTO universal_feedback (
                    trace_id, execution_context, effectiveness, efficiency, clarity, reliability,
                    ease_of_use, documentation_quality, error_handling, confidence, would_recommend,
                    better_alternative, suggestions, what_worked_well, what_could_improve, notes,
                    user_expertise_level, use_case_category, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.trace_id,
                feedback.execution_context.value,
                feedback.effectiveness,
                feedback.efficiency,
                feedback.clarity,
                feedback.reliability,
                feedback.ease_of_use,
                feedback.documentation_quality,
                feedback.error_handling,
                feedback.confidence,
                feedback.would_recommend,
                feedback.better_alternative.value if feedback.better_alternative else "",
                json.dumps(feedback.suggestions),
                feedback.what_worked_well,
                feedback.what_could_improve,
                feedback.notes,
                feedback.user_expertise_level,
                feedback.use_case_category,
                feedback.model_dump_json()
            ))
            
            await self.connection.commit()
            logger.info("Stored universal feedback", trace_id=feedback.trace_id)
            
        except Exception as e:
            logger.error("Failed to store universal feedback", trace_id=feedback.trace_id, error=str(e))
            raise
    
    async def get_execution(self, trace_id: str) -> Optional[ExecutionMetadata]:
        """Get execution metadata by trace ID."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cursor = await self.connection.execute("""
            SELECT trace_id, execution_context, timestamp, name, module_name,
                   file_path, line_number, command_line, working_directory,
                   status, latency_ms, memory_delta_mb, cpu_percent,
                   input_args, input_size_bytes, output_size_bytes, return_value_type,
                   error_type, error_message, stack_trace, process_id, exit_code,
                   invite_feedback, opt_out, redaction_applied, redaction_rule_id
            FROM executions WHERE trace_id = ?
        """, (trace_id,))
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        from skald.schema.models import ExecutionContext
        
        return ExecutionMetadata(
            trace_id=row[0],
            execution_context=ExecutionContext(row[1]),
            timestamp=datetime.fromisoformat(row[2]),
            name=row[3],
            module_name=row[4],
            file_path=row[5],
            line_number=row[6],
            command_line=row[7],
            working_directory=row[8],
            status=row[9],
            latency_ms=row[10],
            memory_delta_mb=row[11],
            cpu_percent=row[12],
            input_args=json.loads(row[13]),
            input_size_bytes=row[14],
            output_size_bytes=row[15],
            return_value_type=row[16],
            error_type=row[17],
            error_message=row[18],
            stack_trace=row[19],
            process_id=row[20],
            exit_code=row[21],
            invite_feedback=bool(row[22]),
            opt_out=bool(row[23]),
            redaction_applied=bool(row[24]),
            redaction_rule_id=row[25]
        )
    
    async def get_universal_feedback(self, trace_id: str) -> Optional[UniversalFeedbackReport]:
        """Get universal feedback report by trace ID."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cursor = await self.connection.execute("""
            SELECT trace_id, execution_context, effectiveness, efficiency, clarity, reliability,
                   ease_of_use, documentation_quality, error_handling, confidence, would_recommend,
                   better_alternative, suggestions, what_worked_well, what_could_improve, notes,
                   user_expertise_level, use_case_category
            FROM universal_feedback WHERE trace_id = ?
        """, (trace_id,))
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        from skald.schema.models import ExecutionContext, BetterAlternative
        
        # Handle BetterAlternative enum safely
        better_alt = BetterAlternative.NO_ALTERNATIVE  # Default
        if row[11]:  # Only parse if not empty string
            try:
                better_alt = BetterAlternative(row[11])
            except ValueError:
                better_alt = BetterAlternative.NO_ALTERNATIVE
        
        return UniversalFeedbackReport(
            trace_id=row[0],
            execution_context=ExecutionContext(row[1]),
            effectiveness=row[2],
            efficiency=row[3],
            clarity=row[4],
            reliability=row[5],
            ease_of_use=row[6],
            documentation_quality=row[7],
            error_handling=row[8],
            confidence=row[9],
            would_recommend=bool(row[10]),
            better_alternative=better_alt,
            suggestions=json.loads(row[12]),
            what_worked_well=row[13],
            what_could_improve=row[14],
            notes=row[15],
            user_expertise_level=row[16],
            use_case_category=row[17]
        )
    
    async def list_executions(
        self,
        execution_context: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExecutionMetadata]:
        """List executions with optional filtering."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        query = """
            SELECT trace_id, execution_context, timestamp, name, module_name,
                   file_path, line_number, command_line, working_directory,
                   status, latency_ms, memory_delta_mb, cpu_percent,
                   input_args, input_size_bytes, output_size_bytes, return_value_type,
                   error_type, error_message, stack_trace, process_id, exit_code,
                   invite_feedback, opt_out, redaction_applied, redaction_rule_id
            FROM executions
        """
        params = []
        conditions = []
        
        if execution_context:
            conditions.append("execution_context = ?")
            params.append(execution_context)
        
        if name:
            conditions.append("name = ?")
            params.append(name)
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        
        from skald.schema.models import ExecutionContext
        
        return [
            ExecutionMetadata(
                trace_id=row[0],
                execution_context=ExecutionContext(row[1]),
                timestamp=datetime.fromisoformat(row[2]),
                name=row[3],
                module_name=row[4],
                file_path=row[5],
                line_number=row[6],
                command_line=row[7],
                working_directory=row[8],
                status=row[9],
                latency_ms=row[10],
                memory_delta_mb=row[11],
                cpu_percent=row[12],
                input_args=json.loads(row[13]),
                input_size_bytes=row[14],
                output_size_bytes=row[15],
                return_value_type=row[16],
                error_type=row[17],
                error_message=row[18],
                stack_trace=row[19],
                process_id=row[20],
                exit_code=row[21],
                invite_feedback=bool(row[22]),
                opt_out=bool(row[23]),
                redaction_applied=bool(row[24]),
                redaction_rule_id=row[25]
            )
            for row in rows
        ]
    
    async def cleanup_expired_executions(self, ttl_hours: int) -> int:
        """Clean up expired execution records."""
        if not self.connection:
            raise RuntimeError("SQLite storage not initialized")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        
        # First count records that will be deleted
        cursor_count = await self.connection.execute("""
            SELECT COUNT(*) FROM executions WHERE timestamp < ?
        """, (cutoff_time.isoformat(),))
        count_row = await cursor_count.fetchone()
        await cursor_count.close()
        deleted_count = count_row[0] if count_row else 0
        
        # Delete them
        cursor = await self.connection.execute("""
            DELETE FROM executions WHERE timestamp < ?
        """, (cutoff_time.isoformat(),))
        await cursor.close()
        await self.connection.commit()
        
        if deleted_count > 0:
            logger.info("Cleaned up expired execution records", count=deleted_count, ttl_hours=ttl_hours)
        
        return deleted_count