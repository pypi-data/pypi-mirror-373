"""Standard I/O transport for Skald."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Dict, Optional

import structlog

from skald.transport.base import Transport

logger = structlog.get_logger(__name__)


class StdioTransport(Transport):
    """Standard I/O transport for MCP communication."""
    
    def __init__(self, proxy) -> None:
        super().__init__(proxy)
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
    
    async def serve(self, **kwargs: Any) -> None:
        """Start serving over stdio."""
        logger.info("Starting stdio transport")
        self._running = True
        
        try:
            await self.proxy.initialize()
            
            # Start the main message loop
            self._task = asyncio.create_task(self._message_loop())
            await self._task
            
        except asyncio.CancelledError:
            logger.info("Stdio transport cancelled")
        except Exception as e:
            logger.error("Stdio transport error", error=str(e))
            raise
        finally:
            await self.proxy.close()
    
    async def stop(self) -> None:
        """Stop the stdio transport."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stdio transport stopped")
    
    async def _message_loop(self) -> None:
        """Main message processing loop."""
        while self._running:
            try:
                # Read from stdin
                line = await self._read_line()
                if not line:
                    break
                
                # Parse JSON-RPC message
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON received", error=str(e), line=line)
                    continue
                
                # Process message
                response = await self._process_message(message)
                
                # Send response if needed
                if response:
                    await self._write_response(response)
                    
            except Exception as e:
                logger.error("Error in message loop", error=str(e))
                break
    
    async def _read_line(self) -> Optional[str]:
        """Read a line from stdin."""
        loop = asyncio.get_event_loop()
        
        try:
            # Read from stdin in a thread to avoid blocking
            line = await loop.run_in_executor(None, sys.stdin.readline)
            return line.strip() if line else None
        except Exception as e:
            logger.error("Failed to read from stdin", error=str(e))
            return None
    
    async def _write_response(self, response: Dict[str, Any]) -> None:
        """Write response to stdout."""
        try:
            json_response = json.dumps(response)
            sys.stdout.write(json_response + "\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error("Failed to write response", error=str(e))
    
    async def _process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming JSON-RPC message."""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            if method == "tools/list":
                tools = self.proxy.list_available_tools()
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {"name": tool, **self.proxy.get_tool_schema(tool)} 
                            for tool in tools
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32602,
                            "message": "Missing tool name"
                        }
                    }
                
                # Call the tool through our proxy
                response = await self.proxy.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": response.content,
                        "isError": response.isError,
                        "_meta": response.meta
                    }
                }
            
            elif method == "initialize":
                return {
                    "jsonrpc": "2.0", 
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "skald",
                            "version": "0.1.0"
                        }
                    }
                }
            
            elif method == "notifications/initialized":
                # No response needed for notification
                return None
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error("Error processing message", method=method, error=str(e))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }