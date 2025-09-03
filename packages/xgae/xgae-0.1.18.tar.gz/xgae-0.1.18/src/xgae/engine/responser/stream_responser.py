import logging
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator, override

from xgae.utils import log_trace

from xgae.engine.responser.responser_base import TaskResponseProcessor, TaskResponserContext, TaskRunContinuousState


class StreamTaskResponser(TaskResponseProcessor):
    def __init__(self, response_context: TaskResponserContext):
        super().__init__(response_context)

    @override
    async def process_response(self,
                               llm_response: AsyncGenerator,
                               prompt_messages: List[Dict[str, Any]],
                               continuous_state: TaskRunContinuousState
                               ) -> AsyncGenerator[Dict[str, Any], None]:
        accumulated_content = continuous_state['accumulated_content']
        auto_continue_count = continuous_state['auto_continue_count']
        can_auto_continue   = continuous_state['auto_continue']
        msg_sequence        = continuous_state['assistant_msg_sequence']

        use_assistant_chunk_msg = self.response_context["use_assistant_chunk_msg"]

        finish_reason = None
        should_auto_continue = False

        logging.info(f"=== StreamResp：Start Process Response, assistant_msg_sequence={msg_sequence}, "
                     f"accumulated_content_len={len(accumulated_content)}")
        try:
            async for llm_chunk in llm_response:
                if hasattr(llm_chunk, 'choices') and llm_chunk.choices and hasattr(llm_chunk.choices[0],'finish_reason'):
                    if llm_chunk.choices[0].finish_reason:
                        finish_reason = llm_chunk.choices[0].finish_reason # LLM finish reason: ‘stop' , 'length'
                        logging.info(f"StreamResp：LLM chunk response finish_reason={finish_reason}")

                if hasattr(llm_chunk, 'choices') and llm_chunk.choices:
                    llm_chunk_msg = llm_chunk.choices[0].delta if hasattr(llm_chunk.choices[0], 'delta') else None

                    if llm_chunk_msg and hasattr(llm_chunk_msg, 'content') and llm_chunk_msg.content:
                        chunk_content = llm_chunk_msg.content
                        accumulated_content += chunk_content

                        xml_tool_chunks = self._extract_xml_chunks(accumulated_content)
                        xml_tool_chunk_len = len(xml_tool_chunks)
                        if self.max_xml_tool_calls <= 0 or xml_tool_chunk_len <= self.max_xml_tool_calls:
                            if use_assistant_chunk_msg:
                                message_data = {"role": "assistant", "content": chunk_content}
                                metadata = {"sequence": msg_sequence}
                                assistant_chunk_msg = self.create_response_message(type="assistant_chunk",
                                                                                   content=message_data,
                                                                                   is_llm_message=True,
                                                                                   metadata=metadata)
                                yield assistant_chunk_msg
                                msg_sequence += 1
                        else:
                            finish_reason = "xml_tool_limit_reached"
                            logging.warning(f"StreamResp: Over XML Tool Limit, finish_reason='xml_tool_limit_reached', "
                                            f"xml_tool_chunk_len={xml_tool_chunk_len}")
                            break

            parsed_xml_data = self._parse_xml_tool_calls(accumulated_content)
            if finish_reason == "xml_tool_limit_reached":
                parsed_xml_data = parsed_xml_data[:self.max_xml_tool_calls]

            should_auto_continue = (can_auto_continue and finish_reason == 'length')

            self.root_span.event(name=f"stream_processor_start[{self.task_no}]({auto_continue_count})", level="DEFAULT",
                                 status_message=f"finish_reason={finish_reason}, tool_exec_strategy={self.tool_exec_strategy}, "
                                                f"parsed_xml_data_len={len(parsed_xml_data)}, accumulated_content_len={len(accumulated_content)}, "
                                                f"should_auto_continue={should_auto_continue}")

            assistant_msg_id = None
            if accumulated_content and not should_auto_continue:
                message_data = {"role": "assistant", "content": accumulated_content}
                assistant_msg = self.add_response_message(type="assistant", content=message_data, is_llm_message=True)
                yield assistant_msg
                assistant_msg_id = assistant_msg['message_id']

            tool_calls_to_execute = [item['tool_call'] for item in parsed_xml_data]
            if len(tool_calls_to_execute) > 0 and not should_auto_continue:
                tool_results = await self._execute_tools(tool_calls_to_execute, self.tool_exec_strategy)
                tool_index = 0
                for i, (returned_tool_call, tool_result) in enumerate(tool_results):
                    parsed_xml_item = parsed_xml_data[i]
                    tool_call = parsed_xml_item['tool_call']
                    parsing_details = parsed_xml_item['parsing_details']

                    tool_context = self._create_tool_context(tool_call, tool_index, assistant_msg_id, parsing_details, tool_result)

                    tool_start_msg = self._add_tool_start_message(tool_context)
                    yield tool_start_msg

                    tool_message = self._add_tool_messsage(tool_context, self.xml_adding_strategy)

                    tool_completed_msg = self._add_tool_completed_message(tool_context, tool_message['message_id'])
                    yield tool_completed_msg

                    yield tool_message

                    if tool_context.function_name in ['ask', 'complete']:
                        finish_reason = "completed"
                        break

                    tool_index += 1
            else:
                finish_reason = "non_tool_call"
                logging.warning(f"StreamResp: finish_reason='non_tool_call', No Tool need to call !")

            if finish_reason:
                finish_content = {'status_type': "finish", 'finish_reason': finish_reason}
                finish_msg = self.add_response_message(type="status", content=finish_content, is_llm_message=False)
                yield finish_msg
        except Exception as e:
            trace = log_trace(e, f"StreamResp: Process response accumulated_content:\n {accumulated_content}")
            self.root_span.event(name="stream_response_process_error", level="ERROR",
                                 status_message=f"Process streaming response error: {e}",
                                 metadata={"content": accumulated_content, "trace": trace})

            content = {'role': "system", 'status_type': "error", 'message': f"Process streaming response error: {e}"}
            error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
            yield error_msg

            raise  # Use bare 'raise' to preserve the original exception with its traceback
        finally:
            if should_auto_continue:
                continuous_state['accumulated_content'] = accumulated_content
                continuous_state['assistant_msg_sequence'] = msg_sequence
                logging.warning(f"StreamResp: Updated continuous state for auto-continue with {len(accumulated_content)} chars")