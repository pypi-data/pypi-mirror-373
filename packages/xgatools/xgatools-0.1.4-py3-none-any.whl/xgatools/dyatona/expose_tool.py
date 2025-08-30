from xgatools.tool_base import XGASandBoxTool,XGAToolResult
from daytona_sdk import AsyncSandbox

class ExposeTool(XGASandBoxTool):
    """Tool for exposing and retrieving preview URLs for sandbox ports."""

    def __init__(self, sandbox: AsyncSandbox):
        super().__init__(sandbox)
        self.sandbox = sandbox

    async def expose_port(self, port: int) -> XGAToolResult:
        try:
            # Convert port to integer if it's a string
            port = int(port)

            # Validate port number
            if not 1 <= port <= 65535:
                return XGAToolResult(success=False, output=f"Invalid port number: {port}. Must be between 1 and 65535.")

            # Check if something is actually listening on the port (for custom ports)
            if port not in [6080, 8080, 8003]:  # Skip check for known sandbox ports
                try:
                    port_check = await self.sandbox.process.exec(f"netstat -tlnp | grep :{port}", timeout=5)
                    if port_check.exit_code != 0:
                        return XGAToolResult(success=False, output=
                            f"No service is currently listening on port {port}. Please start a service on this port first.")
                except Exception:
                    # If we can't check, proceed anyway - the user might be starting a service
                    pass

            # Get the preview link for the specified port
            preview_link = await self.sandbox.get_preview_link(port)

            # Extract the actual URL from the preview link object
            url = preview_link.url if hasattr(preview_link, 'url') else str(preview_link)

            return XGAToolResult(success=True, output=f"Successfully exposed port {port} to the public. Users can now access this service at: {url}")

        except ValueError:
            return XGAToolResult(success=False, output=f"Invalid port number: {port}. Must be a valid integer between 1 and 65535.")
        except Exception as e:
            return XGAToolResult(success=False, output=f"Error exposing port {port}: {str(e)}")
