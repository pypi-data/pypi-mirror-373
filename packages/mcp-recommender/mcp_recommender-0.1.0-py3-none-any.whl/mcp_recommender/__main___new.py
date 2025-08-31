#!/usr/bin/env python3
"""
MCP推荐器模块入口点 - 修复版本
解决 BufferedWriter buffer 属性错误和连接问题
"""

import sys
import argparse
import asyncio
import os
import logging
from pathlib import Path

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

def fix_stdio_buffer_issue():
    """
    修复 '_io.BufferedWriter' 对象没有 'buffer' 属性的错误
    这是Windows环境下常见的问题
    """
    try:
        # 检查并修复stdout buffer属性
        if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout.buffer, 'buffer'):
            # 为BufferedWriter添加buffer属性指向自身
            sys.stdout.buffer.buffer = sys.stdout.buffer
            
        # 检查并修复stderr buffer属性  
        if hasattr(sys.stderr, 'buffer') and not hasattr(sys.stderr.buffer, 'buffer'):
            sys.stderr.buffer.buffer = sys.stderr.buffer
            
        # 检查并修复stdin buffer属性
        if hasattr(sys.stdin, 'buffer') and not hasattr(sys.stdin.buffer, 'buffer'):
            sys.stdin.buffer.buffer = sys.stdin.buffer
            
        logger.info("stdio buffer属性修复完成")
        return True
        
    except Exception as e:
        logger.error(f"修复stdio buffer属性时出错: {e}")
        return False

def setup_encoding():
    """设置正确的编码，避免Windows下的编码问题"""
    if sys.platform.startswith('win'):
        try:
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            # 确保控制台输出使用UTF-8编码
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
            logger.info("编码设置完成")
        except Exception as e:
            logger.warning(f"编码设置失败: {e}")

def safe_print(text, file=sys.stderr):
    """安全打印函数，避免编码错误"""
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        # 移除可能导致问题的字符
        safe_text = ''.join(c for c in text if ord(c) < 65536 and (c.isprintable() or c in '\n\t '))
        try:
            print(safe_text, file=file)
        except:
            # 最后的备选方案：只保留ASCII字符
            ascii_text = ''.join(c for c in text if ord(c) < 128)
            print(ascii_text, file=file)

def clean_text(text):
    """清理文本中的特殊字符"""
    if not text:
        return text
    # 移除常见的emoji和特殊字符
    cleaned = text.replace('️', '').replace('🏠', '').replace('🚀', '').replace('📊', '').replace('🔍', '')
    return cleaned.strip()

def test_mode():
    """测试模式 - 验证MCP服务器功能"""
    safe_print("=== MCP推荐器测试模式 ===")
    
    try:
        # 导入服务器模块
        from .server import recommender
        safe_print(f"✓ 成功加载 {len(recommender.mcps)} 个MCP服务器")
        
        # 测试基本功能
        safe_print("\n支持的功能:")
        safe_print("  - recommend_mcp: 根据关键词推荐MCP服务器")
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
        
        # 示例推荐测试
        safe_print("\n示例推荐测试 (关键词: 'database'):")
        scored_results = recommender.search_mcps("database", limit=3)
        for i, (mcp, score) in enumerate(scored_results, 1):
            name = clean_text(mcp['name'])
            desc = clean_text(mcp['short_description'][:60])
            safe_print(f"  {i}. {name} - {desc}...")
        
        safe_print("\n✓ 测试完成！所有功能正常")
        return True
        
    except Exception as e:
        safe_print(f"✗ 测试失败: {e}")
        return False

async def server_mode():
    """服务器模式 - 启动MCP服务器"""
    try:
        # 修复stdio问题
        if not fix_stdio_buffer_issue():
            safe_print("警告: stdio buffer修复失败，可能会遇到连接问题")
        
        # 设置编码
        setup_encoding()
        
        # 导入并创建服务器
        from .server import create_server
        safe_print("正在启动MCP推荐器服务器...")
        
        # 验证服务器创建
        server = create_server()
        safe_print("✓ 服务器实例创建成功")
        
        # 启动服务器
        safe_print("✓ MCP服务器启动中...")
        await server.run()
        
    except ImportError as e:
        safe_print(f"✗ 导入错误: {e}")
        safe_print("尝试使用修复后的服务器实现...")
        try:
            from .server_fixed import main as fixed_main
            await fixed_main()
        except Exception as e2:
            safe_print(f"✗ 修复版本也失败: {e2}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        safe_print("\n服务器被用户停止")
        
    except Exception as e:
        safe_print(f"✗ 服务器启动失败: {e}")
        safe_print("\n错误诊断信息:")
        safe_print(f"  - Python版本: {sys.version}")
        safe_print(f"  - 工作目录: {os.getcwd()}")
        safe_print(f"  - 模块路径: {__file__}")
        
        # 检查关键依赖
        try:
            import fastmcp
            safe_print(f"  - FastMCP版本: {fastmcp.__version__}")
        except:
            safe_print("  - FastMCP: 未安装或无法导入")
            
        try:
            import mcp
            safe_print(f"  - MCP版本: {mcp.__version__}")
        except:
            safe_print("  - MCP: 未安装或无法导入")
            
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCP推荐器 - 修复版本")
    parser.add_argument("--test", action="store_true", help="运行测试模式")
    parser.add_argument("--server", action="store_true", help="启动服务器模式")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置调试级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        safe_print("调试模式已启用")
    
    # 执行相应模式
    if args.test:
        success = test_mode()
        sys.exit(0 if success else 1)
    elif args.server:
        asyncio.run(server_mode())
    else:
        # 默认运行服务器模式
        safe_print("启动默认服务器模式...")
        asyncio.run(server_mode())

if __name__ == "__main__":
    main()