import asyncio
import click

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from xgatools.utils.setup_env import setup_logging


@click.command()
@click.option("--host", default="localhost", help="Host to listen on for MCP")
@click.option("--port", default=16060, help="Port to listen on for MCP")
def main(host: str, port: int):
    async def run_shell_tool_test():
        url = f"http://{host}:{port}/sse"
        async with sse_client(url, sse_read_timeout=300) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                task_id = "shell_test_123"  # 固定任务ID便于测试

                # 测试阻塞命令执行
                blocking_result = await session.call_tool(
                    "execute_command",
                    {
                        "task_id": task_id,
                        "command": "echo 'Hello from blocking shell'",
                        "blocking": True,
                        "timeout": 10
                    }
                )
                print(f"\nBlocking command result: {blocking_result}")

                # 测试非阻塞命令执行
                non_blocking_result = await session.call_tool(
                    "execute_command",
                    {
                        "task_id": task_id,
                        "command": "for i in {1..5}; do echo 'Non-blocking $i'; sleep 1; done",
                        "session_name": "long_running",
                        "blocking": False
                    }
                )
                print(f"\nNon-blocking command started: {non_blocking_result}")

                # 等待命令执行一段时间
                await asyncio.sleep(3)

                # 检查命令输出
                check_result = await session.call_tool(
                    "check_command_output",
                    {
                        "task_id": task_id,
                        "session_name": "long_running"
                    }
                )
                print(f"\nPartial command output: {check_result}")

                # 终止命令
                terminate_result = await session.call_tool(
                    "terminate_command",
                    {
                        "task_id": task_id,
                        "session_name": "long_running"
                    }
                )
                print(f"\nCommand termination: {terminate_result}")

                # 列出活动会话
                list_result = await session.call_tool(
                    "list_commands",
                    {"task_id": task_id}
                )
                print(f"\nActive sessions: {list_result}")

                # 清理任务
                await session.call_tool("end_task", {"task_id": task_id})
                print("\nTask cleanup completed")

    asyncio.run(run_shell_tool_test())

if __name__ == "__main__":
    setup_logging()
    main()