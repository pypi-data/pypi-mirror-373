import json
import logging
import re
from typing import Any, Dict, List

from xgae.utils.misc import read_file
from xgae.utils.llm_client import LLMClient, LangfuseMetadata

class FinalResultAgent:
    def __init__(self):
        self.model_client = LLMClient()
        self.prompt_template: str = read_file("templates/example/final_result_template.txt")


    async def final_result(self, user_request: str, task_results: str, langfuse_metadata:LangfuseMetadata=None)-> Dict[str, Any]:
        prompt = self.prompt_template.replace("{user_request}", user_request)
        prompt = prompt.replace("{task_results}", task_results)

        messages = [{"role": "user", "content": prompt}]

        response_text: str = ""
        response = await self.model_client.create_completion(
            messages,
            langfuse_metadata
        )
        if self.model_client.is_stream:
            async for chunk in response:
                choices = chunk.get("choices", [{}])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    response_text += content
        else:
            response_text = response.choices[0].message.content

        cleaned_text = re.sub(r'^\s*```json|```\s*$', '', response_text, flags=re.MULTILINE).strip()
        final_result = json.loads(cleaned_text)
        return final_result


if __name__ == "__main__":
    import asyncio
    from xgae.utils.setup_env import setup_logging
    setup_logging()

    async def main():
        final_result_agent = FinalResultAgent()

        user_input = "locate 10.2.3.4 fault and solution"
        answer = ("Task Summary: The fault for IP 10.2.3.4 was identified as a Business Recharge Fault (Code: F01), "
                  "caused by a Phone Recharge Application Crash. The solution applied was to restart the application. "
                  "Key Deliverables: Fault diagnosis and resolution steps. Impact Achieved: Service restored.")
        return await final_result_agent.final_result(user_input, answer)


    final_result = asyncio.run(main())
    print(f"FINAL_RESULT：   {final_result} ")