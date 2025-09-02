#!/usr/bin/env python3
"""Test script to follow the exact CCAPI MCP server workflow."""

import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ccapi_workflow():
    """Test CCAPI following the exact required workflow."""
    logger.info("Testing CCAPI MCP server with correct workflow...")
    
    try:
        # Start the server process
        process = await asyncio.create_subprocess_exec(
            "uvx", "awslabs.ccapi-mcp-server@latest",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        logger.info("Started CCAPI process")
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "AutoPurple-Test",
                    "version": "0.1.0"
                }
            }
        }
        
        # Send message
        message_str = json.dumps(init_message) + "\n"
        process.stdin.write(message_str.encode())
        await process.stdin.drain()
        
        logger.info("Sent initialization to CCAPI")
        
        # Read response
        line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if line:
            response = json.loads(line.decode().strip())
            logger.info(f"CCAPI initialization response: {response}")
        
        # Step 1: check_environment_variables (MANDATORY FIRST STEP)
        check_env_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "check_environment_variables",
                "arguments": {}
            }
        }
        
        message_str = json.dumps(check_env_message) + "\n"
        process.stdin.write(message_str.encode())
        await process.stdin.drain()
        
        logger.info("Called check_environment_variables")
        
        # Read response
        line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if line:
            env_response = json.loads(line.decode().strip())
            logger.info(f"Environment check response: {env_response}")
            
            # Extract the result for the next step
            env_check_result = env_response.get("result", {})
            
            # Step 2: get_aws_session_info (MANDATORY SECOND STEP)
            session_info_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_aws_session_info",
                    "arguments": {
                        "env_check_result": env_check_result
                    }
                }
            }
            
            message_str = json.dumps(session_info_message) + "\n"
            process.stdin.write(message_str.encode())
            await process.stdin.drain()
            
            logger.info("Called get_aws_session_info")
            
            # Read response
            line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if line:
                session_response = json.loads(line.decode().strip())
                logger.info(f"Session info response: {session_response}")
        
        # Clean up
        process.terminate()
        await process.wait()
        logger.info("Stopped CCAPI")
        
    except Exception as e:
        logger.error(f"Error testing CCAPI: {e}")

if __name__ == "__main__":
    asyncio.run(test_ccapi_workflow())
