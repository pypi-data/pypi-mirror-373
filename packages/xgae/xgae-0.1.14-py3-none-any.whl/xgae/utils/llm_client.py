import asyncio
import json
import os
import logging
import litellm

from typing import Union, Dict, Any, Optional, List, TypedDict
from openai import OpenAIError
from litellm.utils import ModelResponse, CustomStreamWrapper

from xgae.utils import to_bool
from xgae.utils.setup_env import setup_langfuse

class LLMConfig(TypedDict, total=False):
    model: str              # Optional Name of the model to use , Override .env LLM_MODEL
    model_name: str         # Optional Name of the model to use , use model if empty
    model_id: str           # Optional ARN for Bedrock inference profiles, default is None
    api_key: str            # Optional  API key, Override .env LLM_API_KEY or OS env variable
    api_base: str           # Optional API base URL, Override .env LLM_API_BASE
    temperature: float      # temperature: Optional Sampling temperature (0-1), Override .env LLM_TEMPERATURE
    max_tokens: int         # max_tokens: Optional Maximum tokens in the response, Override .env LLM_MAX_TOKENS
    stream: bool            # stream: Optional whether to stream the response, Override .env LLM_STREAM
    enable_thinking: bool   # Optional whether to enable thinking, Override .env LLM_ENABLE_THINKING
    reasoning_effort: str   # Optional level of reasoning effort, default is  ‘low’
    response_format: str    # response_format: Optional desired format for the response, default is  None
    top_p: int              # Optional Top-p sampling parameter, default is None


class LangfuseMetadata(TypedDict, total=False):
    generation_name: str
    generation_id: str
    existing_trace_id: str
    session_id: str


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass

class LLMClient:
    RATE_LIMIT_DELAY = 30
    RETRY_DELAY = 0.1

    langfuse_inited = False
    langfuse_enabled = False

    def __init__(self, llm_config: LLMConfig=None):
        litellm.modify_params = True
        litellm.drop_params = True

        self._init_langfuse()

        llm_config = llm_config or LLMConfig()
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", 1))

        env_llm_model = os.getenv("LLM_MODEL", "openai/qwen3-235b-a22b")
        env_llm_api_key = os.getenv("LLM_API_KEY")
        env_llm_api_base = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        env_llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", 16384))
        env_llm_temperature = float(os.getenv("LLM_TEMPERATURE", 0.7))
        env_llm_stream = to_bool(os.getenv("LLM_STREAM", False))
        env_llm_enable_thinking = to_bool(os.getenv("LLM_ENABLE_THINKING", False))

        llm_config_params = {
            "model":            llm_config.get("model", env_llm_model),
            "model_name":       llm_config.get("model_name", env_llm_model),
            "model_id":         llm_config.get("model_id", None),
            "api_key":          llm_config.get("api_key", env_llm_api_key),
            "api_base":         llm_config.get("api_base", env_llm_api_base),
            "temperature":      llm_config.get("temperature", env_llm_temperature),
            "max_tokens":       llm_config.get("max_tokens", env_llm_max_tokens),
            "stream":           llm_config.get("stream", env_llm_stream),
            "enable_thinking":  llm_config.get("enable_thinking", env_llm_enable_thinking),
            "reasoning_effort": llm_config.get("reasoning_effort", 'low'),
            "response_format":  llm_config.get("response_format", None),
            "top_p":            llm_config.get("top_p", None),
            "tools":            None,
            "tool_choice":      "none",
        }

        self.model_name = llm_config_params["model_name"]
        self.is_stream = llm_config_params['stream']

        self.lite_llm_params = self._prepare_llm_params(llm_config_params)
        logging.info(f"=== LLMClient initialed : model={self.model_name}, is_stream={self.is_stream}, enable thinking={self.lite_llm_params['enable_thinking']}")

    @staticmethod
    def _init_langfuse():
        if not LLMClient.langfuse_inited:
            LLMClient.langfuse_inited =True

            env_llm_langfuse_enable = to_bool(os.getenv("LLM_LANGFUSE_ENABLE", False))
            if env_llm_langfuse_enable:
                env_langfuse = setup_langfuse()
                if env_langfuse and env_langfuse.enabled:
                    litellm.success_callback = ["langfuse"]
                    litellm.failure_callback = ["langfuse"]
                    LLMClient.langfuse_enabled = True
                    logging.info("🛠️ LiteLLM Langfuse is enable !")
                else:
                    LLMClient.langfuse_enabled = False
                    logging.warning("🛠️ LiteLLM Langfuse is disable, langfuse.enabled=false !")
            else:
                LLMClient.langfuse_enabled = False
                logging.warning("🛠️ LiteLLM Langfuse is disable, LLM_LANGFUSE_ENABLE=False !")

    def _prepare_llm_params(self, llm_config_params: Dict[str, Any]) -> Dict[str, Any]:
        prepared_llm_params = llm_config_params.copy()

        model_name = llm_config_params.get("model_name")
        max_tokens = llm_config_params.get("max_tokens")
        model_id = llm_config_params.get("model_id")

        # Handle token limits
        if max_tokens is not None:
            # For Claude 3.7 in Bedrock, do not set max_tokens or max_tokens_to_sample
            # as it causes errors with inference profiles
            if model_name.startswith("bedrock/") and "claude-3-7" in model_name:
                prepared_llm_params.pop("max_tokens")
                logging.debug(f"LLMClient prepare_llm_params: Remove 'max_tokens' param for model: {model_name}")
            else:
                is_openai_o_series = 'o1' in model_name
                is_openai_gpt5 = 'gpt-5' in model_name
                param_name = "max_completion_tokens" if (is_openai_o_series or is_openai_gpt5) else "max_tokens"
                if param_name == "max_completion_tokens":
                    prepared_llm_params[param_name] = max_tokens
                    logging.debug(f"LLMClient prepare_llm_params: Add 'max_completion_tokens' param for model: {model_name}")

        # # Add Claude-specific headers
        if "claude" in model_name.lower() or "anthropic" in model_name.lower():
            prepared_llm_params["extra_headers"] = {
                "anthropic-beta": "output-128k-2025-02-19"
            }
            logging.debug(f"LLMClient prepare_llm_params: Add 'extra_headers' param for model: {model_name}")

        # Add Bedrock-specific parameters
        if model_name.startswith("bedrock/"):
            if not model_id and "anthropic.claude-3-7-sonnet" in model_name:
                prepared_llm_params["model_id"] = "arn:aws:bedrock:us-west-2:935064898258:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                logging.debug(f"LLMClient prepare_llm_params: Must Set 'model_id' param for model: {model_name}")

        # Apply Anthropic prompt caching (minimal implementation)
        effective_model_name = llm_config_params.get("model", model_name)

        # OpenAI GPT-5: drop unsupported temperature param (only default 1 allowed)
        if "gpt-5" in effective_model_name and "temperature" in llm_config_params and llm_config_params["temperature"] != 1:
            prepared_llm_params.pop("temperature", None)
            logging.debug(f"LLMClient prepare_llm_params: Remove 'temperature' param for model: {model_name}")

        # OpenAI GPT-5: request priority service tier when calling OpenAI directly
        # Pass via both top-level and extra_body for LiteLLM compatibility
        if "gpt-5" in effective_model_name and not effective_model_name.startswith("openrouter/"):
            prepared_llm_params["service_tier"] = "priority"
            prepared_llm_params["extra_body"] = {"service_tier": "priority"}
            logging.debug(f"LLMClient prepare_llm_params: Add 'service_tier' and 'extra_body' param for model: {model_name}")

        # Add reasoning_effort for Anthropic models if enabled
        enable_thinking = llm_config_params.get("enable_thinking")
        use_thinking = enable_thinking if enable_thinking is not None else False

        is_anthropic = "anthropic" in effective_model_name.lower() or "claude" in effective_model_name.lower()
        is_kimi_k2 = "kimi-k2" in effective_model_name.lower() or model_name.startswith("moonshotai/kimi-k2")

        if is_kimi_k2:
            prepared_llm_params["provider"] = {
                "order": ["together/fp8", "novita/fp8", "baseten/fp8", "moonshotai", "groq"]
            }
            logging.debug(f"LLMClient prepare_llm_params: Add 'provider' param for model: {model_name}")

        reasoning_effort = llm_config_params.get("reasoning_effort")
        if is_anthropic and use_thinking:
            effort_level = reasoning_effort if reasoning_effort else 'low'
            prepared_llm_params["reasoning_effort"] = effort_level
            prepared_llm_params["temperature"] = 1.0  # Required by Anthropic when reasoning_effort is used
            logging.debug(f"LLMClient prepare_llm_params: Set 'temperature'=1.0 param for model: {model_name}")

        return prepared_llm_params


    def _prepare_complete_params(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare parameters for the API call."""
        complete_params = self.lite_llm_params.copy()
        complete_params["messages"] = messages

        model_name = self.lite_llm_params["model_name"]
        effective_model_name = complete_params.get("model", model_name)

        # Apply cache control to the first 4 text blocks across all messages , for anthropic and claude model
        if "claude" in effective_model_name.lower() or "anthropic" in effective_model_name.lower():
            messages = complete_params["messages"]

            if not isinstance(messages, list):
                return complete_params

            cache_control_count = 0
            max_cache_control_blocks = 3

            for message in messages:
                if cache_control_count >= max_cache_control_blocks:
                    break

                content = message.get("content")

                if isinstance(content, str):
                    message["content"] = [
                        {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                    ]
                    cache_control_count += 1
                    logging.debug(f"LLMClient prepare_complete_params: Add 'cache_control' in message content, for model: {model_name}")
                elif isinstance(content, list):
                    for item in content:
                        if cache_control_count >= max_cache_control_blocks:
                            break
                        if isinstance(item, dict) and item.get("type") == "text" and "cache_control" not in item:
                            item["cache_control"] = {"type": "ephemeral"}
                            cache_control_count += 1
                            logging.debug(f"LLMClient prepare_complete_params: Add 'cache_control' in message content list, for model: {model_name}")

        return complete_params

    async def _handle_llm_error(self, error: Exception, attempt: int) -> None:
        """Handle API errors with appropriate delays and logging."""
        if (attempt + 1) < self.max_retries:
            delay = LLMClient.RATE_LIMIT_DELAY if isinstance(error, litellm.exceptions.RateLimitError) else LLMClient.RETRY_DELAY
            logging.warning(f"LLMClient: Error on llm completion, retry={attempt + 1}/{self.max_retries}: {error}")
            logging.debug(f"LLMClient: Waiting {delay} seconds before retry llm completion...")
            await asyncio.sleep(delay)

    async def create_completion(self, messages: List[Dict[str, Any]], langfuse_metadata: Optional[LangfuseMetadata]=None) -> Union[ModelResponse, CustomStreamWrapper]:
        complete_params = self._prepare_complete_params(messages)
        if LLMClient.langfuse_enabled and langfuse_metadata:
            complete_params["metadata"] = langfuse_metadata

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logging.info(f"*** LLMClient create_completion: LLM '{self.model_name}' completion attempt {attempt + 1}/{self.max_retries}")
                response = await litellm.acompletion(**complete_params)
                return response
            except (litellm.exceptions.RateLimitError, OpenAIError, json.JSONDecodeError) as e:
                last_error = e
                await self._handle_llm_error(e, attempt)
            except Exception as e:
                logging.error(f"LLMClient create_completion: Unexpected error during LLM completion: {str(e)}", exc_info=True)
                raise LLMError(f"LLMClient create completion failed: {e}")

        logging.error(f"LLMClient create_completion: LLM completion failed after {self.max_retries} attempts: {last_error}", exc_info=True)
        raise LLMError(f"LLMClient create completion failed after {self.max_retries} attempts !")

if __name__ == "__main__":
    from xgae.utils.setup_env import setup_logging

    setup_logging()
    langfuse = setup_langfuse()

    async def main():
        llm_client = LLMClient(LLMConfig(stream=False))

        messages = [{"role": "user", "content": "1+1="}]
        trace_id = langfuse.trace(name = "xgae_litellm_test").trace_id
        await asyncio.sleep(1)

        meta = LangfuseMetadata(
                generation_name="llm_completion_test",
                generation_id="generation_id_0",
                existing_trace_id=trace_id,
                session_id="session_0",
        )

        response = await llm_client.create_completion(messages, meta)
        if llm_client.is_stream:
            async for chunk in response:
                choices = chunk.get("choices", [{}])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    print(content, end="", flush=True)
        else:
            print(response.choices[0].message.content)

    asyncio.run(main())


