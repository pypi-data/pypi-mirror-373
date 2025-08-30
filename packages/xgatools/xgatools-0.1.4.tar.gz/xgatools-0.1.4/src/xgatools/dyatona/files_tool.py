from daytona_sdk import AsyncSandbox
from xgatools.tool_base import XGASandBoxTool,XGAToolResult
from xgatools.utils.files_utils import should_exclude_file, clean_path
import json
import logging

class FilesTool(XGASandBoxTool):
    """Tool for executing file system operations in a Daytona sandbox. All operations are performed relative to the /workspace directory."""

    def __init__(self, sandbox: AsyncSandbox):  # 修改初始化参数
        super().__init__(sandbox)
        self.sandbox = sandbox
        self.SNIPPET_LINES = 4
        self.workspace_path = "/workspace"

    def clean_path(self, path: str) -> str:
        """Clean and normalize a path to be relative to /workspace"""
        return clean_path(path, self.workspace_path)

    def _should_exclude_file(self, rel_path: str) -> bool:
        """Check if a file should be excluded based on path, name, or extension"""
        return should_exclude_file(rel_path)

    async def _file_exists(self, path: str) -> bool:
        """Check if a file exists in the sandbox"""
        try:
            await self.sandbox.fs.get_file_info(path)
            return True
        except Exception:
            return False

    async def get_workspace_state(self) -> dict:
        """Get the current workspace state by reading all files"""
        files_state = {}
        try:
            files = await self.sandbox.fs.list_files(self.workspace_path)
            for file_info in files:
                rel_path = file_info.name

                # Skip excluded files and directories
                if self._should_exclude_file(rel_path) or file_info.is_dir:
                    continue

                try:
                    full_path = f"{self.workspace_path}/{rel_path}"
                    content = (await self.sandbox.fs.download_file(full_path)).decode()
                    files_state[rel_path] = {
                        "content": content,
                        "is_dir": file_info.is_dir,
                        "size": file_info.size,
                        "modified": file_info.mod_time
                    }
                except Exception as e:
                    print(f"Error reading file {rel_path}: {e}")
                except UnicodeDecodeError:
                    print(f"Skipping binary file: {rel_path}")

            return files_state

        except Exception as e:
            print(f"Error getting workspace state: {str(e)}")
            return {}

    async def create_file(self, file_path: str, file_contents: str, permissions: str = "644") -> XGAToolResult:
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"
            if await self._file_exists(full_path):
                return XGAToolResult(
                    success=False,
                    output=f"File '{file_path}' already exists. Use update_file to modify existing files.")

            # Create parent directories if needed
            parent_dir = '/'.join(full_path.split('/')[:-1])
            if parent_dir:
                await self.sandbox.fs.create_folder(parent_dir, "755")

            # convert to json string if file_contents is a dict
            if isinstance(file_contents, dict):
                file_contents = json.dumps(file_contents, indent=4)

            # Write the file content
            await self.sandbox.fs.upload_file(file_contents.encode(), full_path)
            await self.sandbox.fs.set_file_permissions(full_path, permissions)

            message = f"File '{file_path}' created successfully."

            # Check if index.html was created and add 8080 server info (only in root workspace)
            if file_path.lower() == 'index.html':
                try:
                    website_link = await self.sandbox.get_preview_link(8080)
                    website_url = website_link.url if hasattr(website_link, 'url') else \
                    str(website_link).split("url='")[1].split("'")[0]
                    message += f"\n\n[Auto-detected index.html - HTTP server available at: {website_url}]"
                    message += "\n[Note: Use the provided HTTP server URL above instead of starting a new server]"
                except Exception as e:
                    logging.warning(f"Failed to get website URL for index.html: {str(e)}")

            return XGAToolResult(
                    success=True,
                    output=message)
        except Exception as e:
            return XGAToolResult(
                    success=False,
                    output=f"Error creating file: {str(e)}")

    async def str_replace(self, file_path: str, old_str: str, new_str: str) -> XGAToolResult:
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"
            if not await self._file_exists(full_path):
                return XGAToolResult(
                    success=False,
                    output=f"File '{file_path}' does not exist")

            content = (await self.sandbox.fs.download_file(full_path)).decode()
            old_str = old_str.expandtabs()
            new_str = new_str.expandtabs()

            occurrences = content.count(old_str)
            if occurrences == 0:
                return XGAToolResult(
                    success=False,
                    output=f"String '{old_str}' not found in file")
            if occurrences > 1:
                lines = [i + 1 for i, line in enumerate(content.split('\n')) if old_str in line]
                return XGAToolResult(
                    success=False,
                    output=f"Multiple occurrences found in lines {lines}. Please ensure string is unique")

            # Perform replacement
            new_content = content.replace(old_str, new_str)
            await self.sandbox.fs.upload_file(new_content.encode(), full_path)

            # Show snippet around the edit
            replacement_line = content.split(old_str)[0].count('\n')
            start_line = max(0, replacement_line - self.SNIPPET_LINES)
            end_line = replacement_line + self.SNIPPET_LINES + new_str.count('\n')
            snippet = '\n'.join(new_content.split('\n')[start_line:end_line + 1])

            # Get preview URL if it's an HTML file
            message = f"Replacement successful."

            return XGAToolResult(
                    success=True,
                    output=message)

        except Exception as e:
            return XGAToolResult(
                    success=False,
                    output=f"Error replacing string: {str(e)}")

    async def full_file_rewrite(self, file_path: str, file_contents: str, permissions: str = "644") -> XGAToolResult:
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"
            if not await self._file_exists(full_path):
                return XGAToolResult(
                    success=False,
                    output=f"File '{file_path}' does not exist. Use create_file to create a new file.")

            await self.sandbox.fs.upload_file(file_contents.encode(), full_path)
            await self.sandbox.fs.set_file_permissions(full_path, permissions)

            message = f"File '{file_path}' completely rewritten successfully."

            # Check if index.html was rewritten and add 8080 server info (only in root workspace)
            if file_path.lower() == 'index.html':
                try:
                    website_link = await self.sandbox.get_preview_link(8080)
                    website_url = website_link.url if hasattr(website_link, 'url') else \
                    str(website_link).split("url='")[1].split("'")[0]
                    message += f"\n\n[Auto-detected index.html - HTTP server available at: {website_url}]"
                    message += "\n[Note: Use the provided HTTP server URL above instead of starting a new server]"
                except Exception as e:
                    logging.warning(f"Failed to get website URL for index.html: {str(e)}")

            return XGAToolResult(
                    success=True,
                    output=message)
        except Exception as e:
            return XGAToolResult(
                    success=False,
                    output=f"Error rewriting file: {str(e)}")

    async def delete_file(self, file_path: str) -> XGAToolResult:
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"
            if not await self._file_exists(full_path):
                return XGAToolResult(
                    success=False,
                    output=f"File '{file_path}' does not exist")

            await self.sandbox.fs.delete_file(full_path)
            return XGAToolResult(
                    success=True,
                    output=f"File '{file_path}' deleted successfully.")
        except Exception as e:
            return XGAToolResult(
                    success=False,
                    output=f"Error deleting file: {str(e)}")

    # 在 FilesTool 类中添加以下方法
    async def upload_file(self, file_path: str, file_contents: str, encoding: str = "utf-8") -> XGAToolResult:
        """Upload file content to the sandbox"""
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"

            # Create parent directories if needed
            parent_dir = '/'.join(full_path.split('/')[:-1])
            if parent_dir:
                await self.sandbox.fs.create_folder(parent_dir, "755")

            # Decode base64 if needed
            if encoding == "base64":
                import base64
                file_data = base64.b64decode(file_contents)
            else:
                file_data = file_contents.encode(encoding)

            # Upload file
            await self.sandbox.fs.upload_file(file_data, full_path)

            return XGAToolResult(
                success=True,
                output=f"File '{file_path}' uploaded successfully. Size: {len(file_data)} bytes"
            )
        except Exception as e:
            return XGAToolResult(
                success=False,
                output=f"Error uploading file: {str(e)}"
            )

    async def download_file(self, file_path: str, encoding: str = "utf-8") -> XGAToolResult:
        """Download file content from the sandbox"""
        try:
            file_path = self.clean_path(file_path)
            full_path = f"{self.workspace_path}/{file_path}"

            if not await self._file_exists(full_path):
                return XGAToolResult(
                    success=False,
                    output=f"File '{file_path}' does not exist"
                )

            # Download file
            file_data = await self.sandbox.fs.download_file(full_path)

            # Encode content
            if encoding == "base64":
                import base64
                content = base64.b64encode(file_data).decode()
            else:
                content = file_data.decode(encoding)

            return XGAToolResult(
                success=True,
                output=f"File content of '{file_path}': "+content+" file_path"+file_path.split("/")[-1],
            )
        except UnicodeDecodeError:
            return XGAToolResult(
                success=False,
                output=f"File '{file_path}' appears to be binary. Use encoding='base64' for binary files"
            )
        except Exception as e:
            return XGAToolResult(
                success=False,
                output=f"Error downloading file: {str(e)}"
            )

