from typing import List, Optional, Union
from xgatools.tool_base import XGATool,XGAToolResult
import logging

class MessageTool(XGATool):
    """Tool for user communication and interaction."""

    def __init__(self):
        super().__init__()

    async def ask(self, text: str, attachments: Optional[str] = None) -> XGAToolResult:
        """Ask the user a question and wait for a response.

        Args:
            text: The question to present to the user
            attachments: Optional file paths or URLs to attach to the question

        Returns:
            ToolResult indicating the question was successfully sent
        """
        try:
            # Convert attachments to list if provided
            attachment_list = []
            if attachments:
                attachment_list = [a.strip() for a in attachments.split(',') if a.strip()]

            logging.info(f"Asked user question: {text}")
            if attachment_list:
                logging.info(f"Attachments: {', '.join(attachment_list)}")

            return XGAToolResult(
                success=True,
                output="Awaiting user response..."
            )
        except Exception as e:
            logging.error(f"Error asking user: {str(e)}")
            return XGAToolResult(
                success=False,
                output=f"Error asking user: {str(e)}"
            )

    async def web_browser_takeover(self, text: str, attachments: Optional[str] = None) -> XGAToolResult:
        """Request user takeover of browser interaction.

        Args:
            text: Instructions for the user about what actions to take
            attachments: Optional file paths or URLs to attach to the request

        Returns:
            ToolResult indicating the takeover request was successfully sent
        """
        try:
            # Convert attachments to list if provided
            attachment_list = []
            if attachments:
                attachment_list = [a.strip() for a in attachments.split(',') if a.strip()]

            logging.info(f"Requested browser takeover: {text}")
            if attachment_list:
                logging.info(f"Attachments: {', '.join(attachment_list)}")

            return XGAToolResult(
                success=True,
                output="Awaiting user browser takeover..."
            )
        except Exception as e:
            logging.error(f"Error requesting browser takeover: {str(e)}")
            return XGAToolResult(
                success=False,
                output= f"Error requesting browser takeover: {str(e)}"
            )

    async def complete(self, text: Optional[str] = None, attachments: Optional[str] = None) -> XGAToolResult:
        """Indicate that the agent has completed all tasks and is entering complete state.

        Args:
            text: Optional completion message or summary to present to the user
            attachments: Optional file paths or URLs to attach to the completion message

        Returns:
            ToolResult indicating successful transition to complete state
        """
        try:
            # Convert attachments to list if provided
            attachment_list = []
            if attachments:
                attachment_list = [a.strip() for a in attachments.split(',') if a.strip()]

            completion_text = text or "All tasks completed successfully."
            logging.info(f"Completion: {completion_text}")
            if attachment_list:
                logging.info(f"Attachments: {', '.join(attachment_list)}")

            return XGAToolResult(
                success=True,
                output=str({"status": "complete"})
            )
        except Exception as e:
            logging.error(f"Error entering complete state: {str(e)}")
            return XGAToolResult(
                success=False,
                output=f"Error entering complete state: {str(e)}"
            )


if __name__ == "__main__":
    import asyncio


    async def test_message_tool():
        message_tool = MessageTool()

        # Test ask
        ask_result = await message_tool.ask(
            text="Would you like to proceed with the next phase?",
            attachments="summary.pdf"
        )
        print("Ask result:", ask_result)

        # Test web_browser_takeover
        takeover_result = await message_tool.web_browser_takeover(
            text="Please solve the CAPTCHA verification",
            attachments="screenshot.png"
        )
        print("Takeover result:", takeover_result)

        # Test complete
        complete_result = await message_tool.complete(
            text="Project completed successfully",
            attachments="final_report.pdf,project_summary.md"
        )
        print("Complete result:", complete_result)


    asyncio.run(test_message_tool())