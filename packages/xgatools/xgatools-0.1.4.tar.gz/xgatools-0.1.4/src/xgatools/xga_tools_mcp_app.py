import logging

import click
import yaml
from mcp.server.fastmcp import FastMCP
from typing import Literal, Annotated, Optional
from pydantic import Field

from xgatools.tool_base import XGAToolNote, XGAToolResult
from xgatools.xga_tool_manager import XGAToolManager
from xgatools.utils.setup_env import setup_env_logging

class XGAMcpTools:
    mcp = FastMCP(name="Extreme General Agent Tools")
    sandbox_type: Literal["daytona", "e2b"] = "daytona"
    tool_manager: XGAToolManager = None

    with open("tool_schemas.yaml") as f:
        TOOL_SCHEMAS = yaml.safe_load(f)

    def __init__(self, host: str, port: int, transport: Literal["stdio", "sse", "streamable-http"] = "sse",
                 sandbox_type: Literal["daytona", "e2b"] = "daytona") -> None:
        self.transport = transport

        if transport != "stdio":
            XGAMcpTools.mcp.settings.host = host
            XGAMcpTools.mcp.settings.port = port

        XGAMcpTools.sandbox_type = sandbox_type
        XGAMcpTools.tool_manager = XGAToolManager(sandbox_type)

    def run(self):
        self.mcp.run(transport=self.transport)

    # =============   System Tools    =============
    @mcp.tool()
    async def end_task(task_id: str):
        print(f"end_task, task_id: {task_id}")
        await XGAMcpTools.tool_manager.end_task(task_id)
        return XGAToolResult(success=True, output="")

    # =============   Message Tools    =============
    @mcp.tool(
        description=TOOL_SCHEMAS["complete"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["complete"]["example"]))
    async def complete(task_id: str,
                       text: Annotated[Optional[str], Field(
                           description="Completion summary. Include: 1) Task summary 2) Key deliverables 3) Next steps 4) Impact achieved")] = None,
                       attachments: Annotated[Optional[str], Field(
                           description="Comma-separated list of final outputs. Use when: 1) Completion relates to files 2) User needs to review outputs 3) Deliverables in files")] = None):
        print(f"Marking task complete, task_id: {task_id}, text: {text}, attachments: {attachments}")
        return await XGAMcpTools.tool_manager.call(task_id, "complete", {"text": text, "attachments": attachments})

    @mcp.tool(
        description=TOOL_SCHEMAS["ask"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["ask"]["example"]))
    async def ask(task_id: str,
                  text: Annotated[str, Field(
                      description="Question text to present to user. Include: 1) Clear question/request 2) Context why input is needed 3) Available options 4) Impact of choices 5) Relevant constraints")],
                  attachments: Annotated[Optional[str], Field(
                      description="Comma-separated list of files/URLs to attach. Use when: 1) Question relates to files/configs 2) User needs to review content 3) Options documented in files 4) Supporting evidence needed")] = None):
        print(f"Starting user question, task_id: {task_id}, text: {text}, attachments: {attachments}")
        return await XGAMcpTools.tool_manager.call(task_id, "ask", {"text": text, "attachments": attachments})

    @mcp.tool(
        description=TOOL_SCHEMAS["web_browser_takeover"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["web_browser_takeover"]["example"]))
    async def web_browser_takeover(task_id: str,
                                   text: Annotated[str, Field(
                                       description="Instructions for user actions. Include: 1) Why takeover needed 2) Specific steps 3) Info to extract 4) Completion signal 5) Page state context")],
                                   attachments: Annotated[Optional[str], Field(
                                       description="Comma-separated list of files/URLs. Use when: 1) Visual references needed 2) Previous search results relevant 3) Supporting docs required")] = None):
        print(f"Starting browser takeover, task_id: {task_id}, text: {text}, attachments: {attachments}")
        return await XGAMcpTools.tool_manager.call(task_id, "web_browser_takeover",
                                                   {"text": text, "attachments": attachments})

    # =============   WebSearch Tools    =============
    @mcp.tool(
        description=TOOL_SCHEMAS["web_search"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["web_search"]["example"]))
    async def web_search(task_id: str,
                         query: Annotated[str, Field(
                             description="The search query to find relevant web pages. Be specific and include key terms to improve search accuracy. For best results, "
                                         "use natural language questions or keyword combinations that precisely describe what you're looking for.")],
                         num_results: Annotated[int, Field(default=20,description="The number of search results to return. Increase for more comprehensive research or decrease for focused, high-relevance results.")]):
        print(f"Starting web search, task_id: {task_id}, query: {query}, num_results: {num_results}")
        return await XGAMcpTools.tool_manager.call(task_id, "web_search", {"query": query, "num_results": num_results})

    @mcp.tool(
        description=TOOL_SCHEMAS["scrape_webpage"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["scrape_webpage"]["example"]))
    async def scrape_webpage(task_id: str,
                             urls: Annotated[str, Field(
                                 description="Multiple URLs to scrape, separated by commas. You should ALWAYS include several URLs when possible for efficiency. Example: 'https://example.com/page1,https://example.com/page2,https://example.com/page3'")]):
        print(f"Starting web scraping, task_id: {task_id}, urls: {urls}")
        return await XGAMcpTools.tool_manager.call(task_id, "scrape_webpage", {"urls": urls})

    # =============   Shell Tools    =============
    @mcp.tool(
        description=TOOL_SCHEMAS["execute_command"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["execute_command"]["example"]))
    async def execute_command(task_id: str,
                              command: Annotated[str, Field(description="Shell command to execute")],
                              folder: Annotated[Optional[str], Field(description="Workspace subdirectory")] = None,
                              session_name: Annotated[Optional[str], Field(description="Tmux session name")] = None,
                              blocking: Annotated[bool, Field(description="Wait for completion")] = False,
                              timeout: Annotated[int, Field(description="Timeout in seconds")] = 60):
        return await XGAMcpTools.tool_manager.call(
            task_id,"execute_command",
            {"command": command, "folder": folder, "session_name": session_name, "blocking": blocking,"timeout": timeout})

    @mcp.tool(
        description=TOOL_SCHEMAS["check_command_output"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["check_command_output"]["example"]))
    async def check_command_output(task_id: str,
                                   session_name: Annotated[str, Field(description="Tmux session name")],
                                   kill_session: Annotated[bool, Field(description="Terminate after check")] = False):
        return await XGAMcpTools.tool_manager.call(
            task_id,"check_command_output",
            {"session_name": session_name, "kill_session": kill_session})

    @mcp.tool(
        description=TOOL_SCHEMAS["terminate_command"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["terminate_command"]["example"]))
    async def terminate_command(task_id: str,
                                session_name: Annotated[str, Field(description="Tmux session name")]):
        return await XGAMcpTools.tool_manager.call(
            task_id,
            "terminate_command",
            {"session_name": session_name})

    @mcp.tool(
        description=TOOL_SCHEMAS["list_commands"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["list_commands"]["example"]))
    async def list_commands(task_id: str):
        return await XGAMcpTools.tool_manager.call(task_id, "list_commands", {})

    # =============   File Tools    =============
    @mcp.tool(
        description=TOOL_SCHEMAS["create_file"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["create_file"]["example"]))
    async def create_file(task_id: str,
                          file_path: Annotated[str, Field(description="Path to the file to be created, relative to /workspace (e.g., 'src/main.py')")],
                          file_contents: Annotated[str, Field(description="The content to write to the file")],
                          permissions: Annotated[Optional[str], Field(description="File permissions in octal format (e.g., '644')")] = "644"):
        return await XGAMcpTools.tool_manager.call(task_id,"create_file",
            {"file_path": file_path, "file_contents": file_contents, "permissions": permissions})

    @mcp.tool(
        description=TOOL_SCHEMAS["str_replace"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["str_replace"]["example"]))
    async def str_replace(task_id: str,
                          file_path: Annotated[str, Field(description="Path to the target file, relative to /workspace (e.g., 'src/main.py')")],
                          old_str: Annotated[str, Field(description="Text to be replaced (must appear exactly once)")],
                          new_str: Annotated[str, Field(description="Replacement text")]):
        return await XGAMcpTools.tool_manager.call(task_id,"str_replace",
            {"file_path": file_path, "old_str": old_str, "new_str": new_str})

    @mcp.tool(
        description=TOOL_SCHEMAS["full_file_rewrite"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["full_file_rewrite"]["example"]))
    async def full_file_rewrite(task_id: str,
                                file_path: Annotated[str, Field(description="Path to the file to be rewritten, relative to /workspace (e.g., 'src/main.py')")],
                                file_contents: Annotated[str, Field(description="The new content to write to the file, replacing all existing content")],
                                permissions: Annotated[Optional[str], Field(description="File permissions in octal format (e.g., '644')")] = "644"):
        return await XGAMcpTools.tool_manager.call(
            task_id,"full_file_rewrite",
            {"file_path": file_path, "file_contents": file_contents, "permissions": permissions})

    @mcp.tool(
        description=TOOL_SCHEMAS["delete_file"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["delete_file"]["example"]))
    async def delete_file(task_id: str,
                          file_path: Annotated[str, Field(description="Path to the file to be deleted, relative to /workspace (e.g., 'src/main.py')")]):
        return await XGAMcpTools.tool_manager.call(
            task_id,"delete_file",
            {"file_path": file_path})

    @mcp.tool(
        description=TOOL_SCHEMAS["upload_file"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["upload_file"]["example"]))
    async def upload_file(task_id: str,
                          file_path: Annotated[
                              str, Field(description="Path to the file to be uploaded, relative to /workspace")],
                          file_contents: Annotated[str, Field(description="File content to upload")],
                          encoding: Annotated[
                              Optional[str], Field(description="Encoding type ('utf-8' or 'base64')")] = "utf-8"):
        return await XGAMcpTools.tool_manager.call(
            task_id, "upload_file",
            {"file_path": file_path, "file_contents": file_contents, "encoding": encoding})

    @mcp.tool(
        description=TOOL_SCHEMAS["download_file"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["download_file"]["example"]))
    async def download_file(task_id: str,
                            file_path: Annotated[
                                str, Field(description="Path to the file to download, relative to /workspace")],
                            encoding: Annotated[
                                Optional[str], Field(description="Encoding type ('utf-8' or 'base64')")] = "utf-8"):
        return await XGAMcpTools.tool_manager.call(
            task_id, "download_file",
            {"file_path": file_path, "encoding": encoding})

    # =============   Expose Tools    =============
    @mcp.tool(
        description=TOOL_SCHEMAS["expose_port"]["description"],
        annotations=XGAToolNote(example=TOOL_SCHEMAS["expose_port"]["example"]))
    async def expose_port(task_id: str,
                          port: Annotated[int, Field(description="The port number to expose. Must be a valid port number between 1 and 65535.", minimum=1,maximum=65535)]):
        print(f"Exposing port, task_id: {task_id}, port: {port}")
        return await XGAMcpTools.tool_manager.call(task_id, "expose_port", {"port": port})



@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="sse",help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for MCP")
@click.option("--port", default=16060, help="Port to listen on for MCP")
@click.option("--sandbox_type", type=click.Choice(["daytona", "e2b"]), default="daytona", help="Sandbox type")
def main(transport: str, host: str, port: int, sandbox_type: str):
    setup_env_logging()

    logging.info("****** Starting XGA Tools MCP Server ******")
    logging.info(f"sandbox_type={sandbox_type}, transport={transport}, host={host}, port={port}")

    xga_mcp_tools = XGAMcpTools(host, port, transport, sandbox_type)
    xga_mcp_tools.run()


if __name__ == "__main__":
    main()