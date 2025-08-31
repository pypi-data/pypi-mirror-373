#!/usr/bin/env python3
"""
MCP推荐器模块入口点 - 完全修复版本
解决所有 BufferedWriter buffer 属性错误
"""

import sys
import argparse
import asyncio
import os

# 立即修复buffer属性问题
def fix_buffer_attributes():
    """修复所有stdio流的buffer属性"""
    streams = [sys.stdout, sys.stderr, sys.stdin]
    for stream in streams:
        if hasattr(stream, 'buffer') and not hasattr(stream.buffer, 'buffer'):
            stream.buffer.buffer = stream.buffer

# 在任何其他导入之前修复
fix_buffer_attributes()

# 设置编码
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 现在安全导入其他模块
from .server import recommender

def safe_print(text, file=sys.stderr):
    """安全打印函数"""
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        safe_text = ''.join(c for c in text if ord(c) < 65536 and (c.isprintable() or c in '\n\t '))
        try:
            print(safe_text, file=file)
        except:
            ascii_text = ''.join(c for c in text if ord(c) < 128)
            print(ascii_text, file=file)

def clean_text(text):
    """清理文本中的特殊字符"""
    if not text:
        return text
    cleaned = text.replace('️', '').replace('🏠', '').replace('🚀', '').replace('📊', '').replace('🔍', '')
    return cleaned.strip()

def test_mode():
    """测试模式"""
    safe_print("MCP推荐器测试模式")
    safe_print(f"已加载 {len(recommender.mcps)} 个MCP服务器")
    safe_print("支持的功能:")
    safe_print("  - recommend: 根据关键词推荐MCP服务器")
    safe_print("  - list_categories: 列出所有分类")
    safe_print("  - get_functional_keywords: 获取功能关键词")
    
    # 显示分类统计
    categories = {}
    for mcp in recommender.mcps:
        cat = clean_text(mcp.get('category', 'Unknown'))
        categories[cat] = categories.get(cat, 0) + 1
    
    safe_print(f"\n分类统计 (共{len(categories)}个分类):")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        safe_print(f"  {cat}: {count}个")
    
    # 示例推荐
    safe_print("\n示例推荐 (关键词: 'database'):")
    scored_results = recommender.search_mcps("database", limit=3)
    for i, (mcp, score) in enumerate(scored_results, 1):
        name = clean_text(mcp['name'])
        desc = clean_text(mcp['short_description'][:60])
        safe_print(f"  {i}. {name} - {desc}...")
    
    safe_print("\n测试完成！")

async def server_mode():
    """服务器模式"""
    try:
        # 再次确保buffer属性正确
        fix_buffer_attributes()
        
        from .server import create_server
        safe_print("启动MCP推荐器服务器...")
        safe_print(f"已加载 {len(recommender.mcps)} 个MCP服务器")
        
        server = create_server()
        safe_print("MCP服务器启动中...")
        
        # 启动服务器
        await server.run()
        
    except KeyboardInterrupt:
        safe_print("\n服务器已停止")
    except Exception as e:
        safe_print(f"\n启动失败: {e}")
        # 输出详细错误信息
        import traceback
        safe_print("详细错误信息:")
        safe_print(traceback.format_exc())
        sys.exit(1)

def main():
    """主函数"""
    # 确保在主函数开始时也修复buffer属性
    fix_buffer_attributes()
    
    parser = argparse.ArgumentParser(description="MCP推荐器")
    parser.add_argument("--test", action="store_true", help="运行测试模式")
    parser.add_argument("--server", action="store_true", help="启动服务器模式")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    if args.debug:
        safe_print("调试模式已启用")
        safe_print(f"Python版本: {sys.version}")
        safe_print(f"工作目录: {os.getcwd()}")
        
        # 检查buffer属性状态
        for name, stream in [('stdout', sys.stdout), ('stderr', sys.stderr), ('stdin', sys.stdin)]:
            if hasattr(stream, 'buffer'):
                has_buffer_attr = hasattr(stream.buffer, 'buffer')
                safe_print(f"{name}.buffer.buffer存在: {has_buffer_attr}")
    
    if args.test:
        test_mode()
    elif args.server:
        asyncio.run(server_mode())
    else:
        # 默认运行服务器模式
        asyncio.run(server_mode())

if __name__ == "__main__":
    main()
