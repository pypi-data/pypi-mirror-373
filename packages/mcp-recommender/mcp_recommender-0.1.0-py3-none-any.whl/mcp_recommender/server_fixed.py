import asyncio
import json
import sys
from typing import Any, Sequence
import logging

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("mcp-recommender")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri="recommendations://movies",
            name="Movie Recommendations",
            description="Get movie recommendations",
            mimeType="application/json",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    if uri == "recommendations://movies":
        return json.dumps({
            "recommendations": [
                {"title": "The Matrix", "year": 1999, "rating": 8.7},
                {"title": "Inception", "year": 2010, "rating": 8.8},
                {"title": "Interstellar", "year": 2014, "rating": 8.6}
            ]
        })
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="get_recommendation",
            description="Get personalized recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category to get recommendations for"
                    },
                    "preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User preferences"
                    }
                },
                "required": ["category"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """处理工具调用"""
    if name == "get_recommendation":
        category = arguments.get("category", "general")
        preferences = arguments.get("preferences", [])
        
        # 模拟推荐逻辑
        recommendations = {
            "movies": ["The Shawshank Redemption", "The Godfather", "Pulp Fiction"],
            "books": ["1984", "To Kill a Mockingbird", "Pride and Prejudice"],
            "music": ["Bohemian Rhapsody", "Stairway to Heaven", "Hotel California"]
        }
        
        result = recommendations.get(category, ["No recommendations available"])
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "category": category,
                    "preferences": preferences,
                    "recommendations": result
                }, indent=2)
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """主函数 - 修复了stdio处理问题"""
    try:
        # 确保stdin/stdout以二进制模式处理
        if hasattr(sys.stdin, 'buffer'):
            stdin = sys.stdin.buffer
        else:
            stdin = sys.stdin
            
        if hasattr(sys.stdout, 'buffer'):
            stdout = sys.stdout.buffer
        else:
            stdout = sys.stdout
            
        logger.info("Starting MCP server...")
        
        # 使用修复后的stdio服务器
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-recommender",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())