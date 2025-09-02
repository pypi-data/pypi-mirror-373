"""TCP transport for Skald."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

import structlog

from skald.transport.base import Transport

logger = structlog.get_logger(__name__)


class TCPTransport(Transport):
    """TCP transport for MCP communication."""
    
    def __init__(self, proxy) -> None:
        super().__init__(proxy)
        self._server: Optional[asyncio.Server] = None
    
    async def serve(self, host: str = "localhost", port: int = 8765, **kwargs: Any) -> None:
        """Start serving over TCP.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional server options
        """
        logger.info("Starting TCP transport", host=host, port=port)
        
        await self.proxy.initialize()
        
        try:
            self._server = await asyncio.start_server(
                self._handle_client,
                host,
                port,
                **kwargs
            )
            
            logger.info("TCP server started", host=host, port=port)
            
            # Keep serving until stopped
            async with self._server:
                await self._server.serve_forever()
                
        except asyncio.CancelledError:
            logger.info("TCP server cancelled")
        except Exception as e:
            logger.error("TCP server error", error=str(e))
            raise
        finally:
            await self.proxy.close()
    
    async def stop(self) -> None:
        """Stop the TCP server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        logger.info("TCP transport stopped")
    
    async def _handle_client(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> None:
        """Handle a client connection."""
        addr = writer.get_extra_info('peername')
        logger.info("Client connected", address=addr)
        
        try:
            while True:
                # Read message length
                data = await reader.readline()
                if not data:
                    break
                
                line = data.decode('utf-8').strip()
                if not line:
                    continue
                
                # Parse JSON-RPC message
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON from client", 
                               address=addr, error=str(e), line=line)
                    continue
                
                # Process message
                response = await self._process_message(message)
                
                # Send response if needed
                if response:
                    response_json = json.dumps(response) + "\n"
                    writer.write(response_json.encode('utf-8'))
                    await writer.drain()
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Error handling client", address=addr, error=str(e))
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info("Client disconnected", address=addr)
    
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
                
                # Extract client context for agent_id
                context = {
                    "client_address": message.get("_client_address"),
                    "agent_id": params.get("agent_id", "tcp_client")
                }
                
                # Call the tool through our proxy
                response = await self.proxy.call_tool(tool_name, arguments, context)
                
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