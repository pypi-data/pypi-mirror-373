#!/usr/bin/env python3
"""
MCP Client for connecting to persistent server
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp
import time

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for persistent MCP server"""
    
    def __init__(self, url='ws://127.0.0.1:8765'):
        self.url = url
        self.websocket = None
        self.session = None
        self._request_id = 0
    
    def _next_id(self):
        """Get next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def connect_websocket(self):
        """Connect to WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets package not installed")
            
        if not self.websocket:
            self.websocket = await websockets.connect(self.url)
            logger.info(f"Connected to WebSocket server at {self.url}")
    
    async def connect_http(self):
        """Create HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close connections"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.session:
            await self.session.close()
            self.session = None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the server"""
        request = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            },
            'id': self._next_id()
        }
        
        if self.url.startswith('ws://'):
            # WebSocket call
            await self.connect_websocket()
            
            start_time = time.time()
            await self.websocket.send(json.dumps(request))
            response = json.loads(await self.websocket.recv())
            elapsed = time.time() - start_time
            
        else:
            # HTTP call
            await self.connect_http()
            
            start_time = time.time()
            async with self.session.post(self.url, json=request) as resp:
                response = await resp.json()
            elapsed = time.time() - start_time
        
        logger.debug(f"Tool {tool_name} took {elapsed*1000:.0f}ms")
        
        if 'error' in response:
            raise Exception(f"MCP Error: {response['error']['message']}")
        
        return response['result']['content'][0]['text']
    
    async def search(self, project_path: str, terms: str, limit: int = 50, 
                     mode: str = 'any', use_fts: bool = True) -> str:
        """Search code using persistent server"""
        return await self.call_tool('search_code', {
            'project_path': project_path,
            'terms': terms,
            'limit': limit,
            'mode': mode,
            'use_fts': use_fts
        })


class SyncMCPClient:
    """Synchronous wrapper for MCP client"""
    
    def __init__(self, url='ws://127.0.0.1:8765'):
        self.client = MCPClient(url)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop
    
    def search(self, project_path: str, terms: str, **kwargs) -> str:
        """Synchronous search"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self.client.search(project_path, terms, **kwargs)
        )
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Synchronous tool call"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self.client.call_tool(tool_name, arguments)
        )
    
    def close(self):
        """Close client"""
        loop = self._get_loop()
        loop.run_until_complete(self.client.close())
        if self._loop:
            self._loop.close()
            self._loop = None


def benchmark_persistent_vs_spawn():
    """Benchmark persistent server vs process spawning"""
    import subprocess
    import time
    
    project_path = "/Users/tuannguyen/Projects/claude-prompts/claude_code_indexer"
    
    print("🚀 MCP Performance Comparison")
    print("=" * 60)
    
    # Test with persistent server
    print("\n✅ With Persistent Server (WebSocket):")
    client = SyncMCPClient()
    
    times = []
    for i in range(5):
        start = time.time()
        result = client.search(project_path, "search cache", limit=50)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.0f}ms")
    
    avg_persistent = sum(times) / len(times)
    client.close()
    
    # Test with process spawning (current method)
    print("\n❌ With Process Spawning (Current):")
    times = []
    for i in range(5):
        start = time.time()
        proc = subprocess.run(
            ["claude-code-indexer", "search", "search", "cache"],
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.0f}ms")
    
    avg_spawn = sum(times) / len(times)
    
    print("\n📊 Results:")
    print(f"  Persistent server avg: {avg_persistent*1000:.0f}ms")
    print(f"  Process spawn avg: {avg_spawn*1000:.0f}ms")
    print(f"  Speedup: {avg_spawn/avg_persistent:.1f}x faster")


if __name__ == '__main__':
    # Run benchmark if called directly
    benchmark_persistent_vs_spawn()