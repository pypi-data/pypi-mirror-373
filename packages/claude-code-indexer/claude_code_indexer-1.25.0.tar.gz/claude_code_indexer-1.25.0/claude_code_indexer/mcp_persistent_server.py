#!/usr/bin/env python3
"""
Persistent MCP Server with WebSocket support for reduced overhead
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import signal

# Try different server implementations
try:
    from aiohttp import web
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from .mcp_server import (
    index_codebase, get_project_stats, query_important_code,
    search_code, list_indexed_projects, manage_cache,
    get_ignore_patterns, enhance_metadata, query_enhanced_nodes,
    get_codebase_insights, get_critical_components, update_node_metadata
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersistentMCPServer:
    """Persistent server to avoid process spawn overhead"""
    
    def __init__(self, host='127.0.0.1', port=8765):
        self.host = host
        self.port = port
        self.tools = {
            'index_codebase': index_codebase,
            'get_project_stats': get_project_stats,
            'query_important_code': query_important_code,
            'search_code': search_code,
            'list_indexed_projects': list_indexed_projects,
            'manage_cache': manage_cache,
            'get_ignore_patterns': get_ignore_patterns,
            'enhance_metadata': enhance_metadata,
            'query_enhanced_nodes': query_enhanced_nodes,
            'get_codebase_insights': get_codebase_insights,
            'get_critical_components': get_critical_components,
            'update_node_metadata': update_node_metadata,
        }
        self._shutdown = False
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single MCP request"""
        try:
            method = request.get('method')
            
            if method == 'tools/call':
                params = request.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name in self.tools:
                    # Call the tool function
                    result = self.tools[tool_name](**arguments)
                    
                    return {
                        'jsonrpc': '2.0',
                        'result': {
                            'content': [{
                                'type': 'text',
                                'text': result
                            }]
                        },
                        'id': request.get('id', 1)
                    }
                else:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': -32601,
                            'message': f'Unknown tool: {tool_name}'
                        },
                        'id': request.get('id', 1)
                    }
            
            elif method == 'tools/list':
                # Return available tools
                tools_list = []
                for name, func in self.tools.items():
                    tools_list.append({
                        'name': name,
                        'description': func.__doc__ or f'{name} tool',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {},
                            'required': []
                        }
                    })
                
                return {
                    'jsonrpc': '2.0',
                    'result': {'tools': tools_list},
                    'id': request.get('id', 1)
                }
            
            else:
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32601,
                        'message': f'Unknown method: {method}'
                    },
                    'id': request.get('id', 1)
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': str(e)
                },
                'id': request.get('id', 1)
            }
    
    async def websocket_handler(self, websocket):
        """Handle WebSocket connections"""
        logger.info(f"New WebSocket connection")
        
        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self.handle_request(request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError as e:
                    error_response = {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': -32700,
                            'message': f'Parse error: {e}'
                        },
                        'id': None
                    }
                    await websocket.send(json.dumps(error_response))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    async def http_handler(self, request):
        """Handle HTTP POST requests"""
        try:
            data = await request.json()
            response = await self.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            return web.json_response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32700,
                    'message': f'Parse error: {e}'
                },
                'id': None
            }, status=400)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping server...")
        self._shutdown = True
        asyncio.get_event_loop().stop()
    
    async def start_websocket_server(self):
        """Start WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets package not installed. Install with: pip install websockets")
            return
            
        logger.info(f"Starting WebSocket MCP server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.websocket_handler, self.host, self.port):
            logger.info("WebSocket server ready for connections")
            await asyncio.Future()  # Run forever
    
    async def start_http_server(self):
        """Start HTTP server"""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp package not installed. Install with: pip install aiohttp")
            return
            
        app = web.Application()
        app.router.add_post('/mcp', self.http_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        
        logger.info(f"Starting HTTP MCP server on http://{self.host}:{self.port}/mcp")
        await site.start()
        
        # Keep server running
        await asyncio.Future()
    
    def run(self, protocol='websocket'):
        """Run the persistent server"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Choose protocol
        if protocol == 'websocket':
            asyncio.run(self.start_websocket_server())
        elif protocol == 'http':
            asyncio.run(self.start_http_server())
        else:
            logger.error(f"Unknown protocol: {protocol}")


def main():
    """Main entry point for persistent MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Persistent MCP Server for Claude Code Indexer')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8765, help='Port to bind to')
    parser.add_argument('--protocol', choices=['websocket', 'http'], default='websocket',
                        help='Protocol to use (websocket or http)')
    
    args = parser.parse_args()
    
    server = PersistentMCPServer(args.host, args.port)
    server.run(args.protocol)


if __name__ == '__main__':
    main()