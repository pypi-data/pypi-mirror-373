import click
import logging

from typing import Annotated, Optional, Dict, List, Any, Literal, TypedDict
from pydantic import Field

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Simulate A2A MCP Proxy")

# XGA agent tool must return {type, content, attachments} like XGAAgentResult class
class XGAAgentResult(TypedDict, total=False):
    type: Literal["ask", "answer", "error"]
    content: str
    attachments: Optional[List[str]]


@mcp.tool(
    description="Get Equipment Type Fault Solution and Cause",
)
# XGA agent tool, must have 2 parameter, first parameter must be task_id, second parameter must be str type
def query_equip_fault_cause(task_id:str, input: Annotated[str, Field(description="Fault Code")]):
    logging.info(f"get_equip_fault_cause: task_id={task_id}, faultCode={input}")

    fault_cause:XGAAgentResult = None
    if 'F02' in input:
        fault_cause:XGAAgentResult = {
            'type': "answer",
            'content': "Host Fault, Fault Cause is 'Host Disk is Damaged' ，Solution is 'Change Host Disk'"
        }
    else:
        fault_cause:XGAAgentResult = {
            'type': "ask",
            'content': f"FaultCode '{input}' is not Equipment Type"
        }

    return  fault_cause


@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=21010, help="Port to listen on for SSE")
def main(transport: str, host: str, port: int):
    if transport != "stdio":
        from xgae.utils.setup_env import setup_logging
        setup_logging()
        logging.info("=" * 10 + f"   Simulate A2A MCP Proxy Sever Started   " + "=" * 10)
        logging.info(f"=== transport={transport}, host={host}, port={port}")


    mcp.settings.host = host
    mcp.settings.port = port

    mcp.run(transport=transport)


if __name__ == '__main__':
    main()
