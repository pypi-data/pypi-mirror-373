#!/usr/bin/env python3
"""
MCP Proxy that connects to persistent server
This acts as a bridge between Claude Desktop and the persistent server
"""

import json
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_code_indexer.mcp_client import MCPClient


def ensure_daemon_running():
    """Ensure the MCP daemon is running, start if not"""
    # Import here to avoid circular imports
    import os
    import psutil
    from pathlib import Path
    
    # Check if daemon is running
    pid_file = Path.home() / '.claude-code-indexer' / 'mcp_daemon.pid'
    
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            if psutil.pid_exists(pid):
                try:
                    proc = psutil.Process(pid)
                    if 'mcp_persistent_server' in ' '.join(proc.cmdline()):
                        return  # Daemon is running
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass
    
    # Daemon not running, start it
    import subprocess
    log_file = Path.home() / '.claude-code-indexer' / 'mcp_daemon.log'
    
    # Ensure directory exists
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'w') as log:
        process = subprocess.Popen([
            sys.executable, '-m', 'claude_code_indexer.mcp_persistent_server',
            '--port', '8765', '--protocol', 'websocket'
        ], start_new_session=True, stdout=log, stderr=log)
    
    # Save PID
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    
    # Wait for daemon to start
    import time
    time.sleep(1)  # Give it a moment to start


async def main():
    """Main proxy handler"""
    use_daemon = True
    
    # Try to ensure daemon is running
    try:
        ensure_daemon_running()
    except Exception as e:
        # Daemon failed, fallback to direct mode
        use_daemon = False
        print(json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/message",
            "params": {
                "level": "warning",
                "message": f"⚠️ MCP Daemon unavailable, using fallback mode (slower). Error: {str(e)}"
            }
        }), file=sys.stderr)
    
    # Read from stdin (Claude Desktop sends requests here)
    input_data = sys.stdin.read()
    
    try:
        request = json.loads(input_data) if input_data else {}
    except json.JSONDecodeError:
        # Handle line-by-line protocol
        lines = []
        for line in input_data.strip().split('\n'):
            if line.strip():
                lines.append(line)
        
        # Process each request
        for line in lines:
            try:
                request = json.loads(line)
                
                if request.get('method') == 'tools/call':
                    params = request.get('params', {})
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})
                    
                    if use_daemon:
                        # Try daemon first
                        try:
                            client = MCPClient()
                            result = await client.call_tool(tool_name, arguments)
                            await client.close()
                        except Exception as e:
                            # Fallback to direct mode
                            use_daemon = False
                            print(json.dumps({
                                "jsonrpc": "2.0",
                                "method": "notifications/message",
                                "params": {
                                    "level": "warning",
                                    "message": f"⚠️ Daemon connection failed, switching to fallback mode. Error: {str(e)}"
                                }
                            }), file=sys.stderr)
                            
                            # Use direct mode
                            from .mcp_server import TOOLS
                            if tool_name in TOOLS:
                                result = TOOLS[tool_name](**arguments)
                            else:
                                raise Exception(f"Unknown tool: {tool_name}")
                    else:
                        # Direct mode (fallback)
                        from .mcp_server import TOOLS
                        if tool_name in TOOLS:
                            result = TOOLS[tool_name](**arguments)
                        else:
                            raise Exception(f"Unknown tool: {tool_name}")
                    
                    response = {
                        'jsonrpc': '2.0',
                        'result': {
                            'content': [{
                                'type': 'text',
                                'text': result
                            }]
                        },
                        'id': request.get('id', 1)
                    }
                    
                    print(json.dumps(response))
                
            except Exception as e:
                error_response = {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32603,
                        'message': str(e)
                    },
                    'id': request.get('id', 1)
                }
                print(json.dumps(error_response))
        
        return
    
    # Single request mode
    try:
        if request.get('method') == 'tools/call':
            params = request.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if use_daemon:
                # Try daemon first
                try:
                    client = MCPClient()
                    result = await client.call_tool(tool_name, arguments)
                    await client.close()
                except Exception as e:
                    # Fallback to direct mode
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "method": "notifications/message",
                        "params": {
                            "level": "warning",
                            "message": f"⚠️ Daemon unavailable, using fallback mode (slower). Error: {str(e)}"
                        }
                    }), file=sys.stderr)
                    
                    # Use direct mode
                    from .mcp_server import TOOLS
                    if tool_name in TOOLS:
                        result = TOOLS[tool_name](**arguments)
                    else:
                        raise Exception(f"Unknown tool: {tool_name}")
            else:
                # Direct mode (fallback)
                from .mcp_server import TOOLS
                if tool_name in TOOLS:
                    result = TOOLS[tool_name](**arguments)
                else:
                    raise Exception(f"Unknown tool: {tool_name}")
            
            response = {
                'jsonrpc': '2.0',
                'result': {
                    'content': [{
                        'type': 'text',
                        'text': result
                    }]
                },
                'id': request.get('id', 1)
            }
        
        elif request.get('method') == 'tools/list':
            # Handle tools/list in fallback mode
            from .mcp_server import TOOLS
            tools_list = []
            for name, func in TOOLS.items():
                tools_list.append({
                    'name': name,
                    'description': func.__doc__ or f'{name} tool',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                })
            
            response = {
                'jsonrpc': '2.0',
                'result': {'tools': tools_list},
                'id': request.get('id', 1)
            }
        
        else:
            # Other methods
            response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': f'Method not implemented in proxy: {request.get("method")}'
                },
                'id': request.get('id', 1)
            }
        
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': str(e)
            },
            'id': request.get('id', 1)
        }
        print(json.dumps(error_response))


if __name__ == '__main__':
    asyncio.run(main())