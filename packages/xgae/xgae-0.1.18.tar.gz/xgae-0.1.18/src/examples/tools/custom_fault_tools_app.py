import click
import logging

from typing import Annotated, Dict, Any
from pydantic import Field

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Fault Location Tools")
alarm_type = 0

@mcp.tool(
    description="Get Alarm Object",
)
def get_alarm(ip: Annotated[str, Field(description="Alarm Object IP Address")]) -> Dict[str, str]:
    logging.info(f"get_alarm: ip={ip}")
    return {"alarmId":"alm0123", "objId": "obj567"}


@mcp.tool(
    description="Get alarm type, return result enum: 1: Business Type Alarm; 2: Equipment Type Alarm; 3: Middleware Type Alarm",
)
def get_alarm_type(alarm_id: Annotated[str, Field(description="Alarm Object Id")]) -> str:
    logging.info(f"get_alarm_type: alarm_id={alarm_id}, alarm_type={alarm_type}")
    return f"{alarm_type}"


@mcp.tool(
    description="Locate Business Type Fault",
)
def get_busi_fault(obj_id: Annotated[str, Field(description="Alarm Object Id")]) -> Dict[str, Any]:
    logging.info(f"get_busi_fault: obj_id={obj_id}")
    return {"fault_code": "F01", "fault_desc": "Business Recharge Fault"}


@mcp.tool(
    description="Locate Equipment Type Fault",
)
def get_equip_fault(obj_id: Annotated[str, Field(description="Alarm Object Id")]) -> Dict[str, Any]:
    logging.info(f"get_equip_fault: obj_id={obj_id}")
    return {"fault_code": "F02", "fault_desc": "Host Disk Fault"}


@mcp.tool(
    description="Locate Middleware Type Fault",
)
def get_middle_fault(obj_id: Annotated[str, Field(description="Alarm Object Id")]) -> Dict[str, Any]:
    logging.info(f"get_middle_fault: obj_id={obj_id}")
    return {"fault_code": "F03", "fault_desc": "Redis Fault"}


@mcp.tool(
    description="Get Business Type Fault Solution and Cause",
)
async def get_busi_fault_cause(fault_code: Annotated[str, Field(description="Fault Code")]) -> str:
    logging.info(f"get_busi_fault_cause: faultCode={fault_code}")

    fault_cause = ""
    if (fault_code == 'F01'):
        fault_cause = "Business Recharge Fault, Fault Cause is 'Phone Recharge Application Crash' ，Solution is 'Restart Phone Recharge Application'"
    else:
        fault_cause = f"FaultCode '{fault_code}' is not Business Type"

    return  fault_cause


# @mcp.tool(
#     description="Get Equipment Type Fault Solution and Cause",
# )
# async def query_equip_fault_cause(fault_code: Annotated[str, Field(description="Fault Code")]) -> str:
#     logging.info(f"get_equip_fault_cause: faultCode={fault_code}")
#
#     fault_cause = ""
#     if (fault_code == 'F02'):
#         fault_cause = "Host Fault, Fault Cause is 'Host Disk is Damaged' ，Solution is 'Change Host Disk'"
#     else:
#         fault_cause = f"FaultCode '{fault_code}' is not Equipment Type"
#
#     return  fault_cause


@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=17070, help="Port to listen on for SSE")
@click.option("--alarmtype", default=1, help="AlarmType Set")
def main(transport: str, host: str, port: int, alarmtype:int):
    if transport != "stdio":
        from xgae.utils.setup_env import setup_logging
        setup_logging()
        logging.info("=" * 10 + f"   Example Fault Tools Sever Started   " + "=" * 10)
        logging.info(f"=== transport={transport}, host={host}, port={port}, alarmtype={alarmtype}")

    global alarm_type
    alarm_type = alarmtype

    mcp.settings.host = host
    mcp.settings.port = port

    mcp.run(transport=transport)


if __name__ == '__main__':
    main()
