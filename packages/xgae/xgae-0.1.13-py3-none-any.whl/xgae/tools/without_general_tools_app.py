from typing import Annotated, Optional
from pydantic import Field

from mcp.server.fastmcp import FastMCP

from xgae.engine.engine_base import  XGAToolResult

mcp = FastMCP(name="XGAE Message Tools")

@mcp.tool(
    description="""A special tool to indicate you have completed all tasks and are about to enter complete state. Use ONLY when: 1) All tasks in todo.md are marked complete [x], 2) The user's original request has been fully addressed, 3) There are no pending actions or follow-ups required, 4) You've delivered all final outputs and results to the user. IMPORTANT: This is the ONLY way to properly terminate execution. Never use this tool unless ALL tasks are complete and verified. Always ensure you've provided all necessary outputs and references before using this tool. Include relevant attachments when the completion relates to specific files or resources."""
)
async def complete(task_id: str,
                   text: Annotated[Optional[str], Field(default=None,
                       description="Completion summary. Include: 1) Task summary 2) Key deliverables 3) Next steps 4) Impact achieved")],
                   attachments: Annotated[Optional[str], Field(default=None,
                       description="Comma-separated list of final outputs. Use when: 1) Completion relates to files 2) User needs to review outputs 3) Deliverables in files")]
                   ):
    print(f"<XGAETools-complete>: task_id={task_id}, text={text}, attachments={attachments}")
    return XGAToolResult(success=True, output=str({"status": "complete"}))


@mcp.tool(
    description="""Ask user a question and wait for response. Use for: 1) Requesting clarification on ambiguous requirements, 2) Seeking confirmation before proceeding with high-impact changes, 3) Gathering additional information needed to complete a task, 4) Offering options and requesting user preference, 5) Validating assumptions when critical to task success, 6) When encountering unclear or ambiguous results during task execution, 7) When tool results don't match expectations, 8) For natural conversation and follow-up questions, 9) When research reveals multiple entities with the same name, 10) When user requirements are unclear or could be interpreted differently. IMPORTANT: Use this tool when user input is essential to proceed. Always provide clear context and options when applicable. Use natural, conversational language that feels like talking with a helpful friend. Include relevant attachments when the question relates to specific files or resources. CRITICAL: When you discover ambiguity (like multiple people with the same name), immediately stop and ask for clarification rather than making assumptions."""
)
async def ask(task_id: str,
              text: Annotated[str, Field(
                  description="Question text to present to user. Include: 1) Clear question/request 2) Context why input is needed 3) Available options 4) Impact of choices 5) Relevant constraints")],
              attachments: Annotated[Optional[str], Field(default=None,
                  description="Comma-separated list of files/URLs to attach. Use when: 1) Question relates to files/configs 2) User needs to review content 3) Options documented in files 4) Supporting evidence needed")]
              ):
    print(f"<XGAETools-ask>: task_id={task_id}, text={text}, attachments={attachments}")
    return XGAToolResult(success=True, output=str({"status": "Awaiting user response..."}))

@mcp.tool(
    description="end task, destroy sandbox"
)
async def end_task(task_id: str) :
    print(f"<XGAETools-end_task> task_id: {task_id}")



def main():
    print("="*20 + "   XGAE Message Tools Sever Started in Stdio mode   " + "="*20)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()