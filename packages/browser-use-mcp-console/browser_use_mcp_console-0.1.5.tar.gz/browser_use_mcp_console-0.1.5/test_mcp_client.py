#!/usr/bin/env python3
"""
MCP Client Test Script for stdio server
基于 company_client.py 改编，用于测试 browser-use-mcp-console 服务器
"""
import asyncio
import argparse
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认测试任务
DEFAULT_TASK = """访问 https://obsidian.md/changelog/ 找到最新的版本和最旧的版本分别是什么"""

async def check_mcp_connection(server_command: list[str]):
    """检查MCP服务器连接（stdio模式）"""

    from mcp import ClientSession, types, StdioServerParameters
    from mcp.client.stdio import stdio_client

    
    try:
        # 创建 StdioServerParameters 对象，传递环境变量
        import os
        env = os.environ.copy()  # 复制当前环境变量
        server_params = StdioServerParameters(
            command=server_command[0],
            args=server_command[1:] if len(server_command) > 1 else [],
            env=env  # 传递包含 API key 的环境变量
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            logger.info("✅ 成功启动服务器")
            async with ClientSession(read_stream, write_stream) as session:
                # 初始化会话
                await session.initialize()
                logger.info("✅ 会话初始化成功")
                
                # 列出可用工具
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                logger.info(f"📋 可用工具: {tool_names}")
                
                if "run_browser_tasks" not in tool_names:
                    logger.error("❌ 服务器未提供 'run_browser_tasks' 工具")
                    return False
                
                return True
                
    except Exception as e:
        logger.error(f"❌ 连接失败: {e}")
        return False

async def execute_browser_task(server_command: list[str], task: str, headless: bool = True):
    """执行浏览器任务（stdio模式）"""
    try:
        from mcp import ClientSession, types, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        logger.error("MCP SDK未安装")
        return None
    
    try:
        # 创建 StdioServerParameters 对象，传递环境变量
        import os
        env = os.environ.copy()  # 复制当前环境变量
        server_params = StdioServerParameters(
            command=server_command[0],
            args=server_command[1:] if len(server_command) > 1 else [],
            env=env  # 传递包含 API key 的环境变量
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                logger.info("🚀 正在执行任务...")
                
                # 调用远程工具
                result = await session.call_tool(
                    "run_browser_tasks",
                    {
                        "tasks": [task],
                        "headless": headless,
                        "max_steps": 30
                    }
                )
                
                # 返回结果
                if result.content and hasattr(result.content[0], 'text'):
                    return result.content[0].text
                else:
                    return str(result)
                    
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_test(task: str = DEFAULT_TASK, headless: bool = True):
    """运行测试"""
    print("\n" + "="*60)
    print("🧪 Browser-Use MCP 测试客户端")
    print("="*60)
    
    # 构建服务器启动命令
    # 使用本地模块进行测试（确保测试的是当前代码）
    server_command = [sys.executable, "-m", "browser_use_mcp.server"]
    
    print(f"服务器命令: {' '.join(server_command)}")
    print("="*60 + "\n")
    
    # 检查连接
    print("📡 检查服务器连接...")
    connected = await check_mcp_connection(server_command)
    if not connected:
        print("\n❌ 无法连接到服务器")
        return 1
    
    print("\n✅ 服务器连接成功！")
    
    # 执行任务
    print(f"\n📝 执行任务：{task}")
    print("\n执行中，请稍候...")
    
    result = await execute_browser_task(server_command, task, headless)
    
    if result:
        print("\n" + "="*60)
        print("📊 执行结果：")
        print("="*60)
        print(result)
        print("="*60)
        print("\n✅ 任务执行完成！")
        return 0
    else:
        print("\n❌ 任务执行失败")
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Browser-Use MCP 测试客户端")
    parser.add_argument(
        "--task", 
        type=str,
        default=DEFAULT_TASK,
        help="要执行的任务描述"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="使用无头模式运行浏览器"
    )
    
    args = parser.parse_args()
    
    # 设置测试API key
    import os
    os.environ['OPENROUTER_API_KEY'] = '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'
    
    # Windows事件循环策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行测试
    return asyncio.run(run_test(args.task, args.headless))

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)