from typing import Optional
from daytona_sdk import AsyncSandbox
from mcp.types import ToolAnnotations
from dataclasses import dataclass


class XGATool:
    pass

class XGASandBoxTool(XGATool):
    def __init__(self,  sandbox: AsyncSandbox):
        pass

@dataclass
class XGAToolResult:
    success: bool
    output: str

class XGAToolNote(ToolAnnotations):
    example: Optional[str] = None