#!/usr/bin/env python3
"""
MCP推荐器服务器 - stdio模式专用
解决asyncio事件循环冲突问题
"""

import sys
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource
)
from .server import recommender

def create_stdio_server() -> Server:
    """创建stdio模式的MCP服务器"""
    server = Server("mcp-recommender")
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """列出可用工具"""
        return [
            Tool(
                name="recommend_mcp",
                description="根据关键词推荐MCP服务器",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量限制",
                            "default": 5
                        },
                        "category": {
                            "type": "string",
                            "description": "过滤分类",
                            "default": None
                        },
                        "language": {
                            "type": "string",
                            "description": "编程语言过滤",
                            "default": None
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="list_categories",
                description="列出所有MCP分类",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_functional_keywords",
                description="获取功能关键词映射",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """处理工具调用"""
        try:
            if name == "recommend_mcp":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 5)
                category = arguments.get("category")
                language = arguments.get("language")
                
                results = recommender.search_mcps(
                    query=query,
                    limit=limit,
                    category_filter=category,
                    language_filter=language
                )
                
                response = {
                    "query": query,
                    "total_results": len(results),
                    "recommendations": []
                }
                
                for mcp, score in results:
                    response["recommendations"].append({
                        "name": mcp["name"],
                        "description": mcp["short_description"],
                        "category": mcp.get("category", "Unknown"),
                        "language": mcp.get("language", "Unknown"),
                        "repository": mcp.get("repository", ""),
                        "score": round(score, 3)
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, ensure_ascii=False)
                )]
            
            elif name == "list_categories":
                categories = recommender.get_categories()
                return [TextContent(
                    type="text",
                    text=json.dumps({"categories": categories}, indent=2, ensure_ascii=False)
                )]
            
            elif name == "get_functional_keywords":
                keywords = recommender.get_functional_keywords()
                return [TextContent(
                    type="text",
                    text=json.dumps({"functional_keywords": keywords}, indent=2, ensure_ascii=False)
                )]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"未知工具: {name}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"工具执行错误: {str(e)}"
            )]
    
    return server

def run_stdio_server():
    """运行stdio模式服务器"""
    server = create_stdio_server()
    
    # 直接使用stdio运行，不创建新的事件循环
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server(server) as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    # 检查是否已有事件循环
    try:
        loop = asyncio.get_running_loop()
        # 如果已有循环，创建任务
        task = loop.create_task(main())
        return task
    except RuntimeError:
        # 没有循环，创建新的
        asyncio.run(main())

if __name__ == "__main__":
    run_stdio_server()