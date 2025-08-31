import asyncio

from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.misc import read_file

from xgae.utils.setup_env import setup_logging

setup_logging(log_level="ERROR")

async def main() -> None:
    # Before Run Exec: uv run example-fault-tools
    tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
    system_prompt = read_file("templates/example/fault_user_prompt.txt")

    engine = XGATaskEngine(tool_box=tool_box,
                           general_tools=[],
                           custom_tools=["*"],
                           system_prompt=system_prompt)

    user_input =  "locate 10.2.3.4 fault and solution"
    chunks = []
    async for chunk in engine.run_task(task_message={"role": "user", "content": user_input}):
        chunks.append(chunk)
        print(chunk)

    final_result = engine.parse_final_result(chunks)
    print(f"\n\nFINAL_RESULT: {final_result}")

asyncio.run(main())