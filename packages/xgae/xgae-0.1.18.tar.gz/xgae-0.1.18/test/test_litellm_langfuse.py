import os
import litellm
import asyncio

from dotenv import load_dotenv
from litellm import acompletion, completion

load_dotenv()

env_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
env_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
env_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
print(f"Langfuse: env_public_key: {env_public_key}, env_secret_key: {env_secret_key}, env_host: {env_host}")

env_llm_model = os.getenv("LLM_MODEL", "openai/qwen3-235b-a22b")
env_llm_api_key = os.getenv("LLM_API_KEY")
env_llm_api_base = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
print(f"LLM: env_llm_model: {env_llm_model}, env_llm_api_key: {env_llm_api_key}, env_llm_api_base: {env_llm_api_base}")

if env_public_key and env_secret_key:
    litellm.success_callback = ["langfuse"]
    litellm.failure_callback = ["langfuse"]

    response = completion(
        model=env_llm_model,
        api_key=env_llm_api_key,
        api_base=env_llm_api_base,
        enable_thinking=False,
        stream=False,
        messages=[
            {"role": "user", "content": "2+3="}
        ],
        metadata={
            "generation_name": "litellm-completion-test",  # set langfuse generation name
        }
    )

    print("completion:" + response.choices[0].message.content)

async def llm_acompletion():
    response = await acompletion(
        model=env_llm_model,
        api_key=env_llm_api_key,
        api_base=env_llm_api_base,
        enable_thinking=False,
        stream=False,
        messages=[
            {"role": "user", "content": "4+5="}
        ],
        metadata={
            "generation_name": "litellm-acompletion-test",  # set langfuse generation name
        }
    )

    print("acompletion:"  + response.choices[0].message.content)


asyncio.run(llm_acompletion())