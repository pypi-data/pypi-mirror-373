import logging

from typing import List, Dict, Any, Optional, AsyncGenerator, override

from xgae.utils import log_trace
from xgae.utils.json_helpers import format_for_yield
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
        accumulated_content = continuous_state.get('accumulated_content', "")
        auto_continue_count = continuous_state.get('auto_continue_count', 0)
        can_auto_continue = continuous_state.get("auto_continue", False)
        use_assistant_chunk_msg = self.response_context.get("use_assistant_chunk_msg")
        
        finish_reason = None
        should_auto_continue = False
        sequence = continuous_state.get('assistant_msg_sequence', 0)
        
        try:
            async for llm_chunk in llm_response:
                if hasattr(llm_chunk, 'choices') and llm_chunk.choices and hasattr(llm_chunk.choices[0], 'finish_reason'):
                    if llm_chunk.choices[0].finish_reason:
                        finish_reason = llm_chunk.choices[0].finish_reason
                        logging.info(f"StreamResp：LLM chunk response finish_reason={finish_reason}")

                if hasattr(llm_chunk, 'choices') and llm_chunk.choices:
                    llm_chunk_msg = llm_chunk.choices[0].delta if hasattr(llm_chunk.choices[0], 'delta') else None

                    if llm_chunk_msg and hasattr(llm_chunk_msg, 'content') and llm_chunk_msg.content:
                        chunk_content = llm_chunk_msg.content
                        accumulated_content += chunk_content

                        xml_tool_call_count = len(self._extract_xml_chunks(accumulated_content))
                        if self.max_xml_tool_calls <= 0 or xml_tool_call_count < self.max_xml_tool_calls:
                            if use_assistant_chunk_msg:
                                message_data = {"role": "assistant", "content": chunk_content}
                                metadata = {"sequence": sequence}
                                assistant_chunk_msg = self.create_response_message(type="assistant_chunk", content=message_data,
                                                                                   is_llm_message=True, metadata=metadata)
                                yield assistant_chunk_msg

                            sequence += 1
                        else:
                            finish_reason = "xml_tool_limit_reached"
                            break

            if  len(accumulated_content) == 0:
                logging.warning(f"StreamResp: LLM response_message content is empty")

            if finish_reason == "xml_tool_limit_reached":
                xml_chunks = self._extract_xml_chunks(accumulated_content)
                if len(xml_chunks) > self.max_xml_tool_calls:
                    limited_chunks = xml_chunks[:self.max_xml_tool_calls]
                    if limited_chunks:
                        last_chunk = limited_chunks[-1]
                        last_chunk_pos = accumulated_content.find(last_chunk) + len(last_chunk)
                        accumulated_content = accumulated_content[:last_chunk_pos]
            parsed_xml_data = self._parse_xml_tool_calls(accumulated_content)

            should_auto_continue = (can_auto_continue and finish_reason == 'length')

            self.root_span.event(name=f"stream_processor_start[{self.task_no}]({auto_continue_count})",level="DEFAULT",
                                 status_message=f"finish_reason={finish_reason}, tool_exec_strategy={self.tool_execution_strategy}, "
                                                f"parsed_xml_data_len={len(parsed_xml_data)}, accumulated_content={len(accumulated_content)}, "
                                                f"should_auto_continue={should_auto_continue}")

            assistant_msg = None
            if accumulated_content and not should_auto_continue:
                message_data = {"role": "assistant", "content": accumulated_content}
                assistant_msg = self.add_response_message(type="assistant", content=message_data,
                                                          is_llm_message=True)
                yield assistant_msg

            tool_calls_to_execute = [item['tool_call'] for item in parsed_xml_data]
            if len(tool_calls_to_execute) > 0:
                tool_results = await self._execute_tools(tool_calls_to_execute, self.tool_execution_strategy)

                tool_index = 0
                for i, (returned_tool_call, tool_result) in enumerate(tool_results):
                    parsed_xml_item = parsed_xml_data[i]
                    tool_call = parsed_xml_item['tool_call']
                    parsing_details = parsed_xml_item['parsing_details']
                    assistant_msg_id = assistant_msg['message_id'] if assistant_msg else None

                    tool_context = self._create_tool_context(tool_call, tool_index, assistant_msg_id, parsing_details)
                    tool_context.result = tool_result

                    tool_start_msg = self._add_tool_start_message(tool_context)
                    yield format_for_yield(tool_start_msg)

                    tool_message = self._add_tool_messsage(tool_call, tool_result, self.xml_adding_strategy, assistant_msg_id, parsing_details)

                    tool_completed_msg = self._add_tool_completed_message(tool_context, tool_message['message_id'])
                    yield format_for_yield(tool_completed_msg)

                    yield format_for_yield(tool_message)

                    if tool_completed_msg["metadata"].get("agent_should_terminate") == "true":
                        finish_reason = "completed"
                        break

                    tool_index += 1
            else:
                finish_reason = "non_tool_call"
                logging.warning(f"StreamResp: tool_calls is empty, No Tool need to call !")

            if finish_reason:
                finish_content = {"status_type": "finish", "finish_reason": finish_reason}
                finish_msg = self.add_response_message(type="status", content=finish_content, is_llm_message=False)
                yield format_for_yield(finish_msg)
        except Exception as e:
            trace = log_trace(e, f"StreamResp: Process response accumulated_content:\n {accumulated_content}")
            self.root_span.event(name="stream_response_process_error", level="ERROR",
                                 status_message=f"Process streaming response error: {e}",
                                 metadata={"content": accumulated_content, "trace": trace})

            content = {"role": "system", "status_type": "error", "message": f"Process streaming response error: {e}"}
            error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
            yield format_for_yield(error_msg)

            raise  # Use bare 'raise' to preserve the original exception with its traceback
        finally:
            if should_auto_continue:
                continuous_state['accumulated_content'] = accumulated_content
                continuous_state['assistant_msg_sequence'] = sequence
                logging.warning(f"StreamResp: Updated continuous state for auto-continue with {len(accumulated_content)} chars")
