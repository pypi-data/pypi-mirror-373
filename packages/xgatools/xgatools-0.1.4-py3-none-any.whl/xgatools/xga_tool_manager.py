import xgatools.dyatona
#import xgatools.e2b
import xgatools.non_sandbox
import inspect
import logging

from typing import Literal, Any, Dict, Type, Callable

from xgatools.dyatona.sandbox_helper import DyaSandboxHelper
from xgatools.tool_base import XGATool
from xgatools.tool_base import XGASandBoxTool

SANDBOX_TOOL_CLASS_NAME = {
    "web_search": "WebSearchTool",
    "scrape_webpage": "WebSearchTool",  # Same tool handles both functions
    "execute_command":"ShellTool",
    "check_command_output": "ShellTool",
    "terminate_command": "ShellTool",
    "list_commands": "ShellTool",
    "create_file": "FilesTool",
    "str_replace": "FilesTool",
    "full_file_rewrite": "FilesTool",
    "delete_file": "FilesTool",
    "upload_file": "FilesTool",
    "download_file": "FilesTool",
    "expose_port": "ExposeTool",
}

NO_SANDBOX_TOOL_CLASS_NAME = {
    "complete": "MessageTool",
    "ask": "MessageTool",
    "web_browser_takeover": "MessageTool",
}

class XGAToolManager:
    def __init__(self, sandbox_type: Literal["daytona", "e2b"] = "daytona") -> None:
        self.sandbox_type = sandbox_type
        self.task_sandbox_map: Dict[str, Any] = {}
        self.task_tool_instances: Dict[str, Dict[str, Any]] = {}  # Maps task_id to tool instances
        self.sandbox_helper = None
        if sandbox_type == "daytona":
            self.sandbox_helper = DyaSandboxHelper()

    async def call(self, task_id: str, tool_name: str, args: Dict[str, Any] = {}) -> Any:
        """
        Call a tool function for a specific task.

        Args:
            task_id: Unique identifier for the task
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool function

        Returns:
            Result from the tool function
        """
        tool_func = await self.get_tool_function(task_id, tool_name)
        args = args if args else {}

        result = None
        if tool_func:
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)

        return result

    async def end_task(self, task_id: str) -> None:
        """
        End a task and clean up associated resources.

        Args:
            task_id: Task identifier to clean up
        """
        # Clean up tool instances
        if task_id in self.task_tool_instances:
            del self.task_tool_instances[task_id]

        # Clean up sandbox
        sandbox = self.task_sandbox_map.pop(task_id, None)
        if sandbox is None:
            logging.info(f"No sandbox to clean up for task_id: {task_id}")
            return

        # Delete sandbox based on type
        try:
            if self.sandbox_type == "daytona" and self.sandbox_helper:
                # If sandbox is an actual sandbox object, get its ID
                sandbox_id = sandbox.id if hasattr(sandbox, 'id') else sandbox
                await self.sandbox_helper.delete_sandbox(sandbox_id)
                logging.info(f"Deleted Daytona sandbox for task {task_id}")
            elif self.sandbox_type == "e2b":
                # TODO: Implement E2B sandbox cleanup
                pass
        except Exception as e:
            logging.error(f"Error cleaning up sandbox for task {task_id}: {str(e)}")



    async def get_tool_function(self, task_id: str, tool_name: str) -> Callable | None:
        """
        Get a tool function instance for a specific task.

        Args:
            task_id: Task identifier
            tool_name: Name of the tool

        Returns:
            Callable tool function or None if not found
        """
        tool_class = self.get_tool_class(tool_name)

        if not tool_class:
            logging.warning(f"Tool class not found for tool: {tool_name}")
            return None

        # Check if we already have a tool instance for this task
        if task_id not in self.task_tool_instances:
            self.task_tool_instances[task_id] = {}

        tool_instance = self.task_tool_instances[task_id].get(tool_class.__name__)

        if not tool_instance:
            # Create new tool instance
            if issubclass(tool_class, XGASandBoxTool):
                # Get or create sandbox for this task
                sandbox = await self._get_or_create_sandbox(task_id)
                if not sandbox:
                    logging.error(f"Could not get sandbox for task {task_id}")
                    return None
                tool_instance = tool_class(sandbox=sandbox)
            elif issubclass(tool_class, XGATool):
                tool_instance = tool_class()
            else:
                logging.error(f"Unknown tool class type: {tool_class}")
                return None

            # Cache the tool instance
            self.task_tool_instances[task_id][tool_class.__name__] = tool_instance

        # Get the specific tool function
        tool_func = getattr(tool_instance, tool_name, None)
        if not tool_func:
            logging.warning(f"Tool function {tool_name} not found in {tool_class.__name__}")

        return tool_func

    async def _get_or_create_sandbox(self, task_id: str) -> Any:
        """
        Get existing sandbox or create a new one for the task.

        Args:
            task_id: Task identifier

        Returns:
            Sandbox instance or None if creation failed
        """
        # Check if we already have a sandbox for this task
        if task_id in self.task_sandbox_map:
            return self.task_sandbox_map[task_id]

        # Create new sandbox
        try:
            if self.sandbox_type == "daytona" and self.sandbox_helper:
                # Generate a password for the sandbox
                import secrets
                import string
                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

                sandbox = await self.sandbox_helper.create_sandbox(password=password, project_id=task_id)
                self.task_sandbox_map[task_id] = sandbox
                logging.info(f"Created Daytona sandbox for task {task_id}")
                return sandbox
            elif self.sandbox_type == "e2b":
                # TODO: Implement E2B sandbox creation
                logging.warning("E2B sandbox type not yet implemented")
                return None
        except Exception as e:
            logging.error(f"Error creating sandbox for task {task_id}: {str(e)}")
            return None

        return None

    def get_tool_class(self, tool_name: str) -> Type[XGATool] | Type[XGASandBoxTool] | None:
        """
        Get the tool class for a given tool name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool class or None if not found
        """
        tool_class = None

        # Check sandbox tools first
        tool_class_name = SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if self.sandbox_type == "daytona":
                if hasattr(xgatools.dyatona, '__all__') and tool_class_name in xgatools.dyatona.__all__:
                    tool_class = getattr(xgatools.dyatona, tool_class_name)
                    return tool_class
                # Fallback: try to get the class directly
                elif hasattr(xgatools.dyatona, tool_class_name):
                    tool_class = getattr(xgatools.dyatona, tool_class_name)
                    return tool_class
            elif self.sandbox_type == "e2b":
                # TODO: Implement E2B tool loading
                pass

        # Check non-sandbox tools
        tool_class_name = NO_SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if hasattr(xgatools.non_sandbox, '__all__') and tool_class_name in xgatools.non_sandbox.__all__:
                tool_class = getattr(xgatools.non_sandbox, tool_class_name)
                return tool_class
            # Fallback: try to get the class directly
            elif hasattr(xgatools.non_sandbox, tool_class_name):
                tool_class = getattr(xgatools.non_sandbox, tool_class_name)
                return tool_class

        return tool_class


if __name__ == "__main__":
    import asyncio
    async def main() -> None:
        tool_manager = XGAToolManager()
        result = await tool_manager.call(task_id="task_123", tool_name="web_search", args={"query": "hello"})
        print(result)

        result = await tool_manager.call(task_id="task_123", tool_name="complete")
        print(result)
        # await tool_manager.end_task("task_123")
    asyncio.run(main())