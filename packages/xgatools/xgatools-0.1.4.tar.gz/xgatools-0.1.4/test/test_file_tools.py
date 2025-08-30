import asyncio
import base64

import click
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

from xgatools.utils.setup_env import setup_logging

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="localhost", help="MCP server host")
@click.option("--port", default=16060, help="MCP server port")
def main(transport: str, host: str, port: int):
    """测试文件工具功能的MCP客户端程序"""
    task_id = "file_ops_task_001"  # 固定任务ID
    test_content = "Hello World!\nThis is a test file."
    binary_content = base64.b64encode(b"Binary data \x00\x01\x02\x03").decode()

    if transport == "sse":
        url = f"http://{host}:{port}/sse"

        async def run_sse(url):
            try:
                async with sse_client(url, sse_read_timeout=300) as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()

                        print("=== 开始文件操作测试 ===")

                        # 创建新文件
                        create_result = await session.call_tool("create_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "file_contents": test_content,
                            "permissions": "644"
                        })
                        print("\n[创建文件结果]:")
                        print(create_result)

                        # 在文件中替换字符串
                        replace_result = await session.call_tool("str_replace", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "old_str": "Hello",
                            "new_str": "Hi"
                        })
                        print("\n[字符串替换结果]:")
                        print(replace_result)

                        # 测试文件下载 (文本文件)
                        download_result = await session.call_tool("download_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "encoding": "utf-8"
                        })
                        print("\n[文件下载结果 - 文本]:")
                        print(download_result)

                        # 测试二进制文件上传
                        upload_result = await session.call_tool("upload_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin",
                            "file_contents": binary_content,
                            "encoding": "base64"
                        })
                        print("\n[二进制文件上传结果]:")
                        print(upload_result)

                        # 测试二进制文件下载
                        bin_download_result = await session.call_tool("download_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin",
                            "encoding": "base64"
                        })
                        print("\n[文件下载结果 - 二进制]:")
                        print(bin_download_result)

                        # 完全重写文件内容
                        rewrite_result = await session.call_tool("full_file_rewrite", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "file_contents": "This file has been completely rewritten!",
                            "permissions": "644"
                        })
                        print("\n[文件重写结果]:")
                        print(rewrite_result)

                        # 删除文件
                        delete_result = await session.call_tool("delete_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt"
                        })
                        print("\n[删除文件结果]:")
                        print(delete_result)

                        # 删除二进制文件
                        delete_bin_result = await session.call_tool("delete_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin"
                        })
                        print("\n[删除二进制文件结果]:")
                        print(delete_bin_result)

                        # 结束任务
                        await session.call_tool("end_task", {"task_id": task_id})
                        print("\n✅ 文件操作测试完成")
            except Exception as e:
                print(f"测试过程中发生异常: {e}")
                raise

        asyncio.run(run_sse(url))
    else:
        async def run_stdio():
            try:
                async with stdio_client(
                        StdioServerParameters(command="uv", args=["run", "xgatools", "--transport", "stdio"])
                ) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()

                        print("=== 开始文件操作测试 ===")

                        # 创建新文件
                        create_result = await session.call_tool("create_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "file_contents": test_content,
                            "permissions": "644"
                        })
                        print("\n[创建文件结果]:")
                        print(create_result)

                        # 在文件中替换字符串
                        replace_result = await session.call_tool("str_replace", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "old_str": "Hello",
                            "new_str": "Hi"
                        })
                        print("\n[字符串替换结果]:")
                        print(replace_result)

                        # 测试文件下载 (文本文件)
                        download_result = await session.call_tool("download_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "encoding": "utf-8"
                        })
                        print("\n[文件下载结果 - 文本]:")
                        print(download_result)

                        # 测试二进制文件上传
                        upload_result = await session.call_tool("upload_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin",
                            "file_contents": binary_content,
                            "encoding": "base64"
                        })
                        print("\n[二进制文件上传结果]:")
                        print(upload_result)

                        # 测试二进制文件下载
                        bin_download_result = await session.call_tool("download_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin",
                            "encoding": "base64"
                        })
                        print("\n[文件下载结果 - 二进制]:")
                        print(bin_download_result)

                        # 完全重写文件内容
                        rewrite_result = await session.call_tool("full_file_rewrite", {
                            "task_id": task_id,
                            "file_path": "test_file.txt",
                            "file_contents": "This file has been completely rewritten!",
                            "permissions": "644"
                        })
                        print("\n[文件重写结果]:")
                        print(rewrite_result)

                        # 删除文件
                        delete_result = await session.call_tool("delete_file", {
                            "task_id": task_id,
                            "file_path": "test_file.txt"
                        })
                        print("\n[删除文件结果]:")
                        print(delete_result)

                        # 删除二进制文件
                        delete_bin_result = await session.call_tool("delete_file", {
                            "task_id": task_id,
                            "file_path": "binary_file.bin"
                        })
                        print("\n[删除二进制文件结果]:")
                        print(delete_bin_result)

                        # 结束任务
                        await session.call_tool("end_task", {"task_id": task_id})
                        print("\n✅ 文件操作测试完成")
            except Exception as e:
                print(f"测试过程中发生异常: {e}")
                raise

        asyncio.run(run_stdio())

if __name__ == "__main__":
    setup_logging()
    main()