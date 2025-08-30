import asyncio
import json
from typing import Optional, Dict, Any
from xgatools.tool_base import XGASandBoxTool, XGAToolResult
from daytona_sdk import AsyncSandbox
import time
from uuid import uuid4

class ShellTool(XGASandBoxTool):
    def __init__(self, sandbox: AsyncSandbox):
        super().__init__(sandbox)
        self.sandbox = sandbox
        self._sessions: Dict[str, str] = {}  # Maps session names to session IDs
        self.workspace_path = "/workspace"  # Ensure we're always operating in /workspace

    async def _ensure_session(self, session_name: str = "default") -> str:
        """Ensure a session exists and return its ID."""
        if session_name not in self._sessions:
            session_id = str(uuid4())
            try:
                await self.sandbox.process.create_session(session_id)
                self._sessions[session_name] = session_id
            except Exception as e:
                raise RuntimeError(f"Failed to create session: {str(e)}")
        return self._sessions[session_name]

    async def _cleanup_session(self, session_name: str):
        """Clean up a session if it exists."""
        if session_name in self._sessions:
            try:
                await self.sandbox.process.delete_session(self._sessions[session_name])
                del self._sessions[session_name]
            except Exception as e:
                print(f"Warning: Failed to cleanup session {session_name}: {str(e)}")

    async def _execute_raw_command(self, command: str) -> Dict[str, Any]:
        """Execute a raw command directly in the sandbox."""
        # Ensure session exists for raw commands
        session_id = await self._ensure_session("raw_commands")

        # Execute command in session
        from daytona_sdk import SessionExecuteRequest
        req = SessionExecuteRequest(
            command=command,
            var_async=False,
            cwd=self.workspace_path
        )

        response = await self.sandbox.process.execute_session_command(
            session_id=session_id,
            req=req,
            timeout=30  # Short timeout for utility commands
        )

        logs = await self.sandbox.process.get_session_command_logs(
            session_id=session_id,
            command_id=response.cmd_id
        )

        return {
            "output": logs,
            "exit_code": response.exit_code
        }

    async def cleanup(self):
        """Clean up all sessions."""
        for session_name in list(self._sessions.keys()):
            await self._cleanup_session(session_name)

        # Also clean up any tmux sessions
        try:
            await self._execute_raw_command("tmux kill-server 2>/dev/null || true")
        except:
            pass

    async def execute_command(
            self,
            command: str,
            folder: Optional[str] = None,
            session_name: Optional[str] = None,
            blocking: bool = False,
            timeout: int = 60
    ) -> XGAToolResult:
        try:
            # Ensure sandbox is initialized
            # await self._ensure_sandbox()

            # Set up working directory
            cwd = self.workspace_path
            if folder:
                folder = folder.strip('/')
                cwd = f"{self.workspace_path}/{folder}"

            # Generate a session name if not provided
            if not session_name:
                session_name = f"session_{str(uuid4())[:8]}"

            # Check if tmux session already exists
            check_session = await self._execute_raw_command(
                f"tmux has-session -t {session_name} 2>/dev/null || echo 'not_exists'")
            session_exists = "not_exists" not in check_session.get("output", "")

            if not session_exists:
                # Create a new tmux session
                await self._execute_raw_command(f"tmux new-session -d -s {session_name}")

            # Ensure we're in the correct directory and send command to tmux
            full_command = f"cd {cwd} && {command}"
            wrapped_command = full_command.replace('"', '\\"')  # Escape double quotes

            if blocking:
                # For blocking execution, use a more reliable approach
                # Add a unique marker to detect command completion
                marker = f"COMMAND_DONE_{str(uuid4())[:8]}"
                completion_command = f"{command} ; echo {marker}"
                wrapped_completion_command = completion_command.replace('"', '\\"')

                # Send the command with completion marker
                await self._execute_raw_command(
                    f'tmux send-keys -t {session_name} "cd {cwd} && {wrapped_completion_command}" Enter')

                start_time = time.time()
                final_output = ""

                while (time.time() - start_time) < timeout:
                    # Wait a shorter interval for more responsive checking
                    await asyncio.sleep(0.5)

                    # Check if session still exists (command might have exited)
                    check_result = await self._execute_raw_command(
                        f"tmux has-session -t {session_name} 2>/dev/null || echo 'ended'")
                    if "ended" in check_result.get("output", ""):
                        break

                    # Get current output and check for our completion marker
                    output_result = await self._execute_raw_command(f"tmux capture-pane -t {session_name} -p -S - -E -")
                    current_output = output_result.get("output", "")

                    if marker in current_output:
                        final_output = current_output
                        break

                # If we didn't get the marker, capture whatever output we have
                if not final_output:
                    output_result = await self._execute_raw_command(f"tmux capture-pane -t {session_name} -p -S - -E -")
                    final_output = output_result.get("output", "")

                # Kill the session after capture
                await self._execute_raw_command(f"tmux kill-session -t {session_name}")

                return XGAToolResult(
                    success=True,
                    output=json.dumps({
                    "output": final_output,
                    "session_name": session_name,
                    "cwd": cwd,
                    "completed": True
                    }))
            else:
                # Send command to tmux session for non-blocking execution
                await self._execute_raw_command(f'tmux send-keys -t {session_name} "{wrapped_command}" Enter')

                # For non-blocking, just return immediately
                return XGAToolResult(
                    success=True,
                    output=json.dumps({
                    "session_name": session_name,
                    "cwd": cwd,
                    "message": f"Command sent to tmux session '{session_name}'. Use check_command_output to view results.",
                    "completed": False
                    }))

        except Exception as e:
            # Attempt to clean up session in case of error
            if session_name:
                try:
                    await self._execute_raw_command(f"tmux kill-session -t {session_name}")
                except:
                    pass
            return  XGAToolResult(
                success=False,
                output=f"Error executing command: {str(e)}")

    async def check_command_output(
            self,
            session_name: str,
            kill_session: bool = False
    ) -> XGAToolResult:
        try:
            # Check if session exists
            check_result = await self._execute_raw_command(
                f"tmux has-session -t {session_name} 2>/dev/null || echo 'not_exists'")
            if "not_exists" in check_result.get("output", ""):
                return XGAToolResult(
                success=False,
                output=f"Tmux session '{session_name}' does not exist.")

            # Get output from tmux pane
            output_result = await self._execute_raw_command(f"tmux capture-pane -t {session_name} -p -S - -E -")
            output = output_result.get("output", "")

            # Kill session if requested
            if kill_session:
                await self._execute_raw_command(f"tmux kill-session -t {session_name}")
                termination_status = "Session terminated."
            else:
                termination_status = "Session still running."

            return XGAToolResult(
                success=True,
                output=json.dumps({
                "output": output,
                "session_name": session_name,
                "status": termination_status
            }))

        except Exception as e:
            return XGAToolResult(
                success=False,
                output=f"Error checking command output: {str(e)}")

    async def terminate_command(
            self,
            session_name: str
    ) -> XGAToolResult:
        try:

            # Check if session exists
            check_result = await self._execute_raw_command(
                f"tmux has-session -t {session_name} 2>/dev/null || echo 'not_exists'")
            if "not_exists" in check_result.get("output", ""):
                return XGAToolResult(
                    success=False,
                    output=f"Tmux session '{session_name}' does not exist.")

            # Kill the session
            await self._execute_raw_command(f"tmux kill-session -t {session_name}")

            return XGAToolResult(
                success=True,
                output=json.dumps({
                    "message": f"Tmux session '{session_name}' terminated successfully."
                }))

        except Exception as e:
            return XGAToolResult(
                success=False,
                output=f"Error terminating command: {str(e)}")

    async def list_commands(self) -> XGAToolResult:
        try:
            # List all tmux sessions
            result = await self._execute_raw_command("tmux list-sessions 2>/dev/null || echo 'No sessions'")
            output = result.get("output", "")

            if "No sessions" in output or not output.strip():
                return XGAToolResult(
                success=True,
                output="No active tmux sessions found.")

            # Parse session list
            sessions = []
            for line in output.split('\n'):
                if line.strip():
                    parts = line.split(':')
                    if parts:
                        session_name = parts[0].strip()
                        sessions.append(session_name)

            return XGAToolResult(
                success=True,
                output=json.dumps({
                    "message": f"Found {len(sessions)} active sessions.",
                    "sessions": sessions
                })
            )

        except Exception as e:
            return XGAToolResult(
                success=False,
                output=f"Error listing commands: {str(e)}"
            )