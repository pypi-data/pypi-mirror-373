import logging
import json
import os

from typing import List, Any, Dict, Optional, AsyncGenerator, Union, Literal
from uuid import uuid4

from xgae.utils import log_trace, to_bool
from xgae.utils.llm_client import LLMClient, LLMConfig


from xgae.engine.engine_base import XGAResponseMsgType, XGAResponseMessage, XGAToolBox, XGATaskResult
from xgae.engine.task_langfuse import XGATaskLangFuse
from xgae.engine.prompt_builder import XGAPromptBuilder
from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.engine.responser.responser_base import TaskResponserContext, TaskResponseProcessor, TaskRunContinuousState

class XGATaskEngine:
    def __init__(self,
                 session_id: Optional[str] = None,
                 task_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 general_tools: Optional[List[str]] = None,
                 custom_tools: Optional[List[str]] = None,
                 system_prompt: Optional[str] = None,
                 max_auto_run: Optional[int] = None,
                 tool_exec_parallel: Optional[bool] = None,
                 llm_config: Optional[LLMConfig] = None,
                 prompt_builder: Optional[XGAPromptBuilder] = None,
                 tool_box: Optional[XGAToolBox] = None):
        self.task_id    = task_id if task_id else f"xga_task_{uuid4()}"
        self.agent_id   = agent_id
        self.session_id = session_id

        self.llm_client = LLMClient(llm_config)
        self.model_name = self.llm_client.model_name
        self.is_stream  = self.llm_client.is_stream

        self.prompt_builder                 = prompt_builder or XGAPromptBuilder(system_prompt)
        self.tool_box: XGAToolBox           = tool_box or XGAMcpToolBox()

        self.general_tools:List[str] = general_tools
        self.custom_tools:List[str]  = custom_tools

        max_auto_run = max_auto_run if max_auto_run  else int(os.getenv('MAX_AUTO_RUN', 15))
        self.max_auto_run: int = 1 if max_auto_run <= 1 else max_auto_run

        self.use_assistant_chunk_msg = to_bool(os.getenv('USE_ASSISTANT_CHUNK_MSG', False))
        self.tool_exec_parallel = True if tool_exec_parallel is None else tool_exec_parallel

        self.task_no = -1
        self.task_run_id :str = None
        self.task_prompt :str = None
        self.task_langfuse: XGATaskLangFuse = None

        self.task_response_msgs: List[XGAResponseMessage] = []

    async def run_task_with_final_answer(self,
                                         task_message: Dict[str, Any],
                                         trace_id: Optional[str] = None) -> XGATaskResult:
        final_result:XGATaskResult = None
        try:
            await self._init_task()

            self.task_langfuse.start_root_span("run_task_with_final_answer", task_message, trace_id)

            chunks = []
            async for chunk in self.run_task(task_message=task_message, trace_id=trace_id):
                chunks.append(chunk)

            if len(chunks) > 0:
                final_result = self.parse_final_result(chunks)
            else:
                final_result = XGATaskResult(type="error", content="LLM Answer is Empty")

            return final_result
        finally:
            self.task_langfuse.end_root_span("run_task_with_final_answer", final_result)


    async def run_task(self,
                       task_message: Dict[str, Any],
                       trace_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._init_task()

            self.task_langfuse.start_root_span("run_task", task_message, trace_id)

            self.add_response_message(type="user", content=task_message, is_llm_message=True)

            async for chunk in self._run_task_auto():
                yield chunk
        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)
            self.task_langfuse.end_root_span("run_task")
            self.task_run_id = None

    async def _init_task(self) -> None:
        if self.task_run_id is None:
            self.task_no = self.task_no + 1
            self.task_run_id = f"{self.task_id}[{self.task_no}]"

            self.task_langfuse =self._create_task_langfuse()

            general_tools = self.general_tools or ["complete", "ask"]
            if "*" not in general_tools:
                if "complete" not in general_tools:
                    general_tools.append("complete")
                elif "ask" not in general_tools:
                    general_tools.append("ask")

            custom_tools = self.custom_tools or []
            if isinstance(self.tool_box, XGAMcpToolBox):
                await  self.tool_box.load_mcp_tools_schema()

            await self.tool_box.creat_task_tool_box(self.task_id, general_tools, custom_tools)
            general_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "general")
            custom_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "custom")
            agent_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "agent")

            self.task_prompt = self.prompt_builder.build_task_prompt(self.model_name,
                                                                     general_tool_schemas,
                                                                     custom_tool_schemas,
                                                                     agent_tool_schemas)

            logging.info("*" * 10 + f"   XGATaskEngine Task'{self.task_id}' Initialized   " + "*" * 10)
            logging.info(f"model_name={self.model_name}, is_stream={self.is_stream}")
            logging.info(f"general_tools={general_tools}, custom_tools={custom_tools}")


    async def _run_task_auto(self) -> AsyncGenerator[Dict[str, Any], None]:
        continuous_state: TaskRunContinuousState = {
            'accumulated_content'   : "",
            'auto_continue_count'   : 0,
            'auto_continue'         : False if self.max_auto_run <= 1 else True,
            'assistant_msg_sequence': 0
        }

        def update_continuous_state(_auto_continue_count,  _auto_continue):
            continuous_state['auto_continue_count'] = _auto_continue_count
            continuous_state['auto_continue'] = _auto_continue

        auto_continue_count = 0
        auto_continue = True
        while auto_continue and auto_continue_count < self.max_auto_run:
            auto_continue = False

            try:
                async for chunk in self._run_task_once(continuous_state):
                    yield chunk
                    try:
                        if chunk['type'] == "status":
                            status_content = chunk['content']
                            status_type = status_content['status_type']
                            if status_type == "error":
                                logging.error(f"TaskEngine run_task_auto: task_response error: {chunk.get('message')}")
                                auto_continue = False
                                break
                            elif status_type == "finish":
                                finish_reason = status_content['finish_reason']
                                if finish_reason == "completed":
                                    logging.info(f"TaskEngine run_task_auto: Detected finish_reason='completed', TASK_COMPLETE Success !")
                                    auto_continue = False
                                    break
                                elif finish_reason == "xml_tool_limit_reached":
                                    logging.warning(f"TaskEngine run_task_auto: Detected finish_reason='xml_tool_limit_reached', stop auto-continue")
                                    auto_continue = False
                                    break
                                elif finish_reason == "non_tool_call":
                                    logging.warning(f"TaskEngine run_task_auto: Detected finish_reason='non_tool_call', stop auto-continue")
                                    auto_continue = False
                                    break
                                elif finish_reason in ["stop", "length"]: # 'length'  occur on some LLM
                                    auto_continue_count += 1
                                    auto_continue = True if auto_continue_count < self.max_auto_run else False
                                    update_continuous_state(auto_continue_count, auto_continue)
                                    logging.info(f"TaskEngine run_task_auto: Detected finish_reason='{finish_reason}', auto-continuing ({auto_continue_count}/{self.max_auto_run})")
                    except Exception as parse_error:
                        trace = log_trace(parse_error,f"TaskEngine run_task_auto: Parse chunk error, chunk: {chunk}")
                        self.task_langfuse.root_span.event(name="engine_parse_chunk_error", level="ERROR",
                                             status_message=f"Task Engine parse chunk error: {parse_error}",
                                             metadata={"content": chunk, "trace": trace})

                        status_content = {'status_type': "error", 'role': "system", 'message': "Parse response chunk Error"}
                        error_msg = self.add_response_message(type="status", content=status_content, is_llm_message=False)
                        yield error_msg
            except Exception as run_error:
                trace = log_trace(run_error, "TaskEngine run_task_auto: Call task_run_once")
                self.task_langfuse.root_span.event(name="engine_task_run_once_error", level="ERROR",
                                                   status_message=f"Call task_run_once error: {run_error}",
                                                   metadata={"trace": trace})

                status_content = {'status_type': "error", 'role': "system", 'message': "Call run_task_once error"}
                error_msg = self.add_response_message(type="status", content=status_content, is_llm_message=False)
                yield error_msg


    async def _run_task_once(self, continuous_state: TaskRunContinuousState) -> AsyncGenerator[Dict[str, Any], None]:
        llm_messages = [{"role": "system", "content": self.task_prompt}]
        cxt_llm_contents = self.get_history_llm_messages()
        llm_messages.extend(cxt_llm_contents)

        partial_content = continuous_state.get('accumulated_content', '')
        if partial_content:
            temp_assistant_message = {
                "role": "assistant",
                "content": partial_content
            }
            llm_messages.append(temp_assistant_message)

        auto_count = continuous_state.get("auto_continue_count")
        langfuse_metadata = self.task_langfuse.create_llm_langfuse_meta(auto_count)

        llm_response = await self.llm_client.create_completion(llm_messages, langfuse_metadata)
        response_processor = self._create_response_processer()

        async for chunk in response_processor.process_response(llm_response, llm_messages, continuous_state):
            self._logging_reponse_chunk(chunk, auto_count)
            yield chunk

    def parse_final_result(self, chunks: List[Dict[str, Any]]) -> XGATaskResult:
        final_result: XGATaskResult = None
        reverse_chunks = reversed(chunks)
        chunk = None
        try:
            finish_reason = ''
            for chunk in reverse_chunks:
                chunk_type = chunk['type']
                if chunk_type == "status":
                    status_content = chunk['content']
                    status_type = status_content['status_type']
                    if status_type == "error":
                        error = status_content['message']
                        final_result = XGATaskResult(type="error", content=error)
                    elif status_type == "finish":
                        finish_reason = status_content['finish_reason']
                elif chunk_type == "tool" and finish_reason in ['completed', 'stop', 'xml_tool_limit_reached', 'length']:
                    tool_content= chunk['content']
                    tool_execution = tool_content.get('tool_execution')
                    tool_name = tool_execution.get('function_name')
                    if tool_name == "complete":
                        result_content = tool_execution['arguments'].get('text', "Task completed with no answer")
                        attachments = tool_execution['arguments'].get('attachments', None)
                        final_result = XGATaskResult(type="answer", content=result_content, attachments=attachments)
                    elif tool_name == "ask":
                        result_content = tool_execution["arguments"].get("text", "Task ask for more info")
                        attachments = tool_execution["arguments"].get("attachments", None)
                        final_result = XGATaskResult(type="ask", content=result_content, attachments=attachments)
                    else:
                        # finish reason 1) 'stop': auto run reach max_auto_run limit 2) 'xml_tool_limit_reached' 3) 'length': occur on some LLM
                        tool_result = tool_execution.get("result", None)
                        if tool_result is not None:
                            success = tool_result['success']
                            output = tool_result.get('output', '')
                            result_type = "answer" if success else "error"
                            result_content = output
                            final_result = XGATaskResult(type=result_type, content=result_content)
                elif chunk_type == "assistant" and finish_reason == "non_tool_call":
                    assis_content = chunk['content']
                    result_content = assis_content.get('content', "LLM output is empty")
                    final_result = XGATaskResult(type="answer", content=result_content)

                if final_result:
                    break

            if final_result and (finish_reason == "completed" or finish_reason == "non_tool_call"):
                logging.info(f"✅ FINAL_RESULT: finish_reason={finish_reason}, final_result={final_result}")
            elif final_result is not None:
                logging.warning(f"⚠️ FINAL_RESULT: finish_reason={finish_reason}, final_result={final_result}")
            else:
                logging.warning(f"❌ FINAL_RESULT: LLM Result is EMPTY, finish_reason={finish_reason}")
                final_result = XGATaskResult(type="error", content="LLM has no answer")
        except Exception as e:
            trace = log_trace(e, f"TaskEngine parse_final_result: Parse message chunk error, chunk: {chunk}")
            self.task_langfuse.root_span.event(name="engine_parse_final_result_error", level="ERROR",
                                               status_message=f"Task Engine parse final result error: {e}",
                                               metadata={"content": chunk, "trace": trace})

            final_result = XGATaskResult(type="error", content="Parse final result failed!")

        return final_result

    def create_response_message(self, type: XGAResponseMsgType,
                             content: Union[Dict[str, Any], List[Any], str],
                             is_llm_message: bool,
                             metadata: Optional[Dict[str, Any]]=None)-> XGAResponseMessage:
        metadata = metadata or {}
        metadata["task_id"]     = self.task_id
        metadata["task_run_id"] = self.task_run_id
        metadata["trace_id"]    = self.task_langfuse.trace_id
        metadata["session_id"]  = self.session_id
        metadata["agent_id"]    = self.agent_id

        message = XGAResponseMessage(
            message_id      = f"xga_msg_{uuid4()}",
            type            = type,
            is_llm_message  = is_llm_message,
            content         = content,
            metadata        = metadata
        )

        return message

    def add_response_message(self, type: XGAResponseMsgType,
                             content: Union[Dict[str, Any], List[Any], str],
                             is_llm_message: bool,
                             metadata: Optional[Dict[str, Any]]=None)-> XGAResponseMessage:
        message = self.create_response_message(type, content, is_llm_message, metadata)
        self.task_response_msgs.append(message)
        return message

    def get_history_llm_messages (self) -> List[Dict[str, Any]]:
        llm_messages = []
        for message in self.task_response_msgs:
            if message['is_llm_message']:
                llm_messages.append(message)

        response_llm_contents = []
        for llm_message in llm_messages:
            content = llm_message['content']
            if isinstance(content, str):
                try:
                    _content = json.loads(content)
                    response_llm_contents.append(_content)
                except json.JSONDecodeError as e:
                    pass
            else:
                response_llm_contents.append(content)

        return response_llm_contents

    def _create_response_processer(self) -> TaskResponseProcessor:
        response_context = self._create_response_context()
        is_stream = response_context['is_stream']
        if is_stream:
            from xgae.engine.responser.stream_responser import StreamTaskResponser
            return StreamTaskResponser(response_context)
        else:
            from xgae.engine.responser.non_stream_responser import NonStreamTaskResponser
            return NonStreamTaskResponser(response_context)

    def _create_response_context(self) -> TaskResponserContext:
        response_context: TaskResponserContext = {
            'is_stream'                 : self.is_stream,
            'task_id'                   : self.task_id,
            'task_run_id'               : self.task_run_id,
            'task_no'                   : self.task_no,
            'model_name'                : self.model_name,
            'max_xml_tool_calls'        : 0,
            'use_assistant_chunk_msg'   : self.use_assistant_chunk_msg,
            'tool_exec_strategy'        : "parallel" if self.tool_exec_parallel else "sequential",
            'xml_adding_strategy'       : "assistant_message", # user_message
            'add_response_msg_func'     : self.add_response_message,
            'create_response_msg_func'  : self.create_response_message,
            'tool_box'                  : self.tool_box,
            'task_langfuse'             : self.task_langfuse,
        }
        return response_context


    def _create_task_langfuse(self)-> XGATaskLangFuse:
        return XGATaskLangFuse(self.session_id, self.task_id, self.task_run_id, self.task_no, self.agent_id)


    def _logging_reponse_chunk(self, chunk, auto_count: int)-> None:
        try:
            chunk_type = chunk['type']
            prefix = ""
            if chunk_type == "status":
                status_content = chunk['content']
                status_type = status_content.get('status_type', "empty")
                if status_type in ["tool_started", "tool_completed"]:
                    return
                prefix = "-" + status_type
            elif chunk_type == "tool":
                tool_content = chunk['content']
                tool_execution = tool_content.get('tool_execution')
                tool_name = tool_execution.get('function_name')
                prefix = "-" + tool_name

            status_content = chunk['content']
            pretty_content = status_content
            if isinstance(status_content, dict):
                pretty_content = json.dumps(status_content, ensure_ascii=False, indent=2)

            if chunk_type == "assistant_chunk":
                logging.debug(f"TASK_RESP_CHUNK[{auto_count}]<{chunk_type}{prefix}> content: {pretty_content}")
            else:
                logging.info(f"TASK_RESP_CHUNK[{auto_count}]<{chunk_type}{prefix}> content: {pretty_content}")
        except Exception as e:
            logging.error(f"TaskEngine logging_reponse_chunk: Decorate chunk={chunk}, error: {e}")



if __name__ == "__main__":
    import asyncio
    from xgae.utils.misc import read_file
    from xgae.utils.setup_env import setup_logging

    setup_logging()

    async def main():
        # Before Run Exec: uv run example-fault-tools
        tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        system_prompt = read_file("templates/example/fault_user_prompt.txt")
        engine =  XGATaskEngine(tool_box=tool_box,
                                custom_tools=["*"],
                                system_prompt=system_prompt,
                                session_id="session_1",
                                agent_id="agent_1"
                                )
        user_input = "locate 10.0.0.1 fault and solution"
        final_result = await engine.run_task_with_final_answer(task_message={'role': "user", 'content': user_input})
        print(f"FINAL RESULT:{final_result}")


    asyncio.run(main())