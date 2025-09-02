"""Stdio-based MCP client for AWS MCP servers."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from ...config import get_settings
from ...logging import get_logger

logger = get_logger(__name__)


class StdioMCPClient:
    """MCP client that communicates via stdio with MCP servers."""
    
    def __init__(self, server_command: str):
        """Initialize the stdio MCP client."""
        self.server_command = server_command
        self.process: Optional[asyncio.subprocess.Process] = None
        self.message_id = 0
    
    async def start(self) -> None:
        """Start the MCP server process."""
        try:
            logger.info(f"Starting MCP server: {self.server_command}")
            
            # Start the server process
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command.split(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialization message
            await self._send_message({
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "AutoPurple",
                        "version": "0.1.0"
                    }
                }
            })
            
            # Read initialization response
            response = await self._read_message()
            logger.info("MCP server initialized", response=response)
            
        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
                logger.info("MCP server stopped")
            except Exception as e:
                logger.error("Error stopping MCP server", error=str(e))
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        try:
            # Send tool call message
            message = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            await self._send_message(message)
            
            # Read response
            response = await self._read_message()
            
            if "error" in response:
                raise RuntimeError(f"MCP tool error: {response['error']}")
            
            return response.get("result", {})
            
        except Exception as e:
            logger.error("MCP tool call failed", tool=tool_name, error=str(e))
            raise
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools on the MCP server."""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        try:
            message = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            await self._send_message(message)
            response = await self._read_message()
            
            return response.get("result", {})
            
        except Exception as e:
            logger.error("Failed to list MCP tools", error=str(e))
            raise
    
    async def _send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to the MCP server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process not available")
        
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str.encode())
        await self.process.stdin.drain()
        
        logger.debug("Sent MCP message", message_id=message.get("id"))
    
    async def _read_message(self) -> Dict[str, Any]:
        """Read a message from the MCP server."""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Process not available")
        
        line = await self.process.stdout.readline()
        if not line:
            raise RuntimeError("No response from MCP server")
        
        try:
            response = json.loads(line.decode().strip())
            logger.debug("Received MCP message", message_id=response.get("id"))
            return response
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response from MCP server", line=line.decode())
            raise
    
    def _get_next_id(self) -> int:
        """Get the next message ID."""
        self.message_id += 1
        return self.message_id


class AWSDocsMCPClient(StdioMCPClient):
    """AWS Documentation MCP client."""
    
    def __init__(self):
        super().__init__("uvx awslabs.aws-documentation-mcp-server@latest")
    
    async def search_documentation(self, query: str, service: Optional[str] = None) -> Dict[str, Any]:
        """Search AWS documentation."""
        arguments = {"query": query}
        if service:
            arguments["service"] = service
        
        return await self.call_tool("search_documentation", arguments)
    
    async def call(self, action: str, payload: Dict[str, Any], *, dry_run: bool = True) -> Dict[str, Any]:
        """Call method for compatibility with existing HTTP client interface."""
        return await self.call_tool(action, payload)


class AWSCCAPIMCPClient(StdioMCPClient):
    """AWS CCAPI MCP client following the mandatory workflow."""
    
    def __init__(self):
        super().__init__("uvx awslabs.ccapi-mcp-server@latest")
        self.session_info = None
        self.env_check_result = None
    
    async def start(self) -> None:
        """Start the MCP server and perform mandatory workflow."""
        await super().start()
        
        # Step 1: MANDATORY - check_environment_variables
        logger.info("Performing mandatory environment check")
        self.env_check_result = await self.call_tool("check_environment_variables", {})
        
        # Step 2: MANDATORY - get_aws_session_info
        logger.info("Getting AWS session info")
        self.session_info = await self.call_tool("get_aws_session_info", {
            "env_check_result": self.env_check_result
        })
        
        logger.info("CCAPI workflow initialization completed")
    
    async def update_security_group_rules(self, security_group_id: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Update security group rules following CCAPI workflow."""
        if not self.session_info:
            raise RuntimeError("Must call start() first to initialize CCAPI workflow")
        
        # For resource updates, we need to follow this sequence:
        # 1. generate_infrastructure_code with identifier and patch_document
        # 2. explain with properties_token
        # 3. update_resource with execution_token
        
        # Step 1: Generate infrastructure code for the security group update
        patch_document = {
            "op": "replace",
            "path": "/SecurityGroupRules",
            "value": rules
        }
        
        properties_result = await self.call_tool("generate_infrastructure_code", {
            "aws_session_info": self.session_info,
            "identifier": security_group_id,
            "patch_document": patch_document,
            "tags": {
                "MANAGED_BY": "CCAPI-MCP-SERVER",
                "MCP_SERVER_SOURCE_CODE": "https://github.com/awslabs/mcp/tree/main/src/ccapi-mcp-server",
                "MCP_SERVER_VERSION": "1.0.0",
                "AUTOPURPLE_MANAGED": "true"
            }
        })
        
        # Step 2: Explain the changes
        explanation_result = await self.call_tool("explain", {
            "properties_token": properties_result.get("properties_token")
        })
        
        # Step 3: Execute the update
        update_result = await self.call_tool("update_resource", {
            "aws_session_info": self.session_info,
            "execution_token": explanation_result.get("execution_token")
        })
        
        return update_result
    
    async def call(self, action: str, payload: Dict[str, Any], *, dry_run: bool = True) -> Dict[str, Any]:
        """Call method for compatibility with existing HTTP client interface."""
        if action == "update_security_group_rules":
            return await self.update_security_group_rules(
                payload.get("securityGroupId"),
                payload.get("rules", {})
            )
        else:
            return await self.call_tool(action, payload)
