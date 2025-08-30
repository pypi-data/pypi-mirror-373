import asyncio
import click

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

from xgatools.utils.setup_env import setup_logging

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="localhost", help="Host to listen on for MCP")
@click.option("--port", default=16060, help="Port to listen on for MCP")
@click.option("--test-port", type=int, default=8080, help="Port number to test exposure")
def main(transport: str, host: str, port: int, test_port: int):
    """Test client for ExposeTool functionality"""

    if transport == "sse":
        url = f"http://{host}:{port}/sse"

        async def run_sse(url):
            async with sse_client(url, sse_read_timeout=300) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    task_id="expose_123"
                    # List available tools
                    response = await session.list_tools()
                    tools = response.tools
                    print("\nAvailable Tools:")
                    for tool in tools:
                        print(f" - {tool.name}: {tool.description}")

                    wait_time=30
                    # Test expose_port tool
                    print(f"\nTesting expose_port on port {test_port}...")
                    result = await session.call_tool("expose_port", {"task_id":task_id,"port": test_port})
                    print(result)
                    print(f"\nWaiting \033[1;33m{wait_time}\033[0m seconds for manual verification...")
                    print("Please open the URL in your browser to verify accessibility")
                    print("Press Ctrl+C to exit early")

                    try:
                        # 异步等待30秒
                        for remaining in range(wait_time, 0, -1):
                            print(f"Time remaining: \033[1;32m{remaining}\033[0m seconds", end='\r')
                            await asyncio.sleep(1)
                        print("\nVerification period ended")
                    except asyncio.CancelledError:
                        print("\n\nVerification interrupted")
                    # End the session
                    await session.call_tool("end_task", {"task_id": task_id})

        asyncio.run(run_sse(url))
    else:
        async def run_stdio():
            async with stdio_client(
                    StdioServerParameters(command="uv", args=["run", "xgatools", "--transport", "stdio"])
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # List available tools
                    response = await session.list_tools()
                    tools = response.tools
                    print("\nAvailable Tools:")
                    for tool in tools:
                        print(f" - {tool.name}: {tool.description}")

                    # Test expose_port tool
                    print(f"\nTesting expose_port on port {test_port}...")
                    result = await session.call_tool("expose_port", {"port": test_port})
                    print(f"\nExpose Tool Result:")
                    print(f"Success: {result.success}")
                    print(f"Output: {result.output}")

                    # End the session
                    await session.call_tool("end_task", {"task_id": "expose_test_task"})

        asyncio.run(run_stdio())


if __name__ == "__main__":
    setup_logging()
    main()