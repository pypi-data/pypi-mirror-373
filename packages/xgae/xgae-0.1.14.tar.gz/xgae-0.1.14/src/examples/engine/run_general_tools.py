import asyncio

from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.setup_env import setup_logging


setup_logging()

async def main() -> None:
    engine = XGATaskEngine(general_tools=["*"])

    user_input =  "This week's gold price"
    final_result = await engine.run_task_with_final_answer(task_message={"role": "user", "content": user_input})
    print("FINAL RESULT:", final_result)

asyncio.run(main())