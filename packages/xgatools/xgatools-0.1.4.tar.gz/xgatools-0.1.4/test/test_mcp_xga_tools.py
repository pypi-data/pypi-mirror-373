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
def main(transport: str, host: str, port: int):
    if transport == "sse":
        url = f"http://{host}:{port}/sse"
        async def run_sse(url):
            async with sse_client(url, sse_read_timeout=300) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()

                    # list available tools
                    response = await session.list_tools()
                    tools = response.tools
                    for tool in tools:
                        print(f"list_tools: TOOL name={tool.name}, description={tool.description}, "
                              f"outputSchema={tool.outputSchema} \ninputSchema=\n{tool.inputSchema}")

                    # call the runmcp tool
                    # result = await session.call_tool("web_search", {"task_id": "task_123", "query": "查询当前黄金价格", "num_results": 20})
                    # print('\n call_tool web_search result:', result)

                    result = await session.call_tool("scrape_webpage", {"task_id": "task_123","urls": "https://baijiahao.baidu.com/s?id=1840679282989511922"})
                    print('\n call_tool scrape_webpage result:', result)

                    result = await session.call_tool("complete", {"task_id": "task_123"})
                    print('\n call_tool complete result:', result)

                    await session.call_tool("end_task", {"task_id": "task_123"})

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
                    for tool in tools:
                        print(f"list_tools: TOOL name={tool.name}, description={tool.description}, "
                              f"outputSchema={tool.outputSchema} \ninputSchema=\n{tool.inputSchema}")

                    # Call tool
                    # result = await session.call_tool("web_search", {"task_id": "task_123", "query": "查询北京天气", "num_results": 5})
                    # print('\n call_tool web_search result:', result)

                    result = await session.call_tool("scrape_webpage",{"task_id": "task_123", "urls": "https://baijiahao.baidu.com/s?id=1840679282989511922"})
                    print('\n call_tool web_search result:', result)

                    result = await session.call_tool("complete", {"task_id": "task_123"})
                    print('\n call_tool complete result:', result)

                    await session.call_tool("end_task", {"task_id": "task_123"})

        asyncio.run(run_stdio())

if __name__ == "__main__":
    setup_logging()
    main()
