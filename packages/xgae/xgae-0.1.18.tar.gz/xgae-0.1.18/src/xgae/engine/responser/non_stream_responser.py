import logging

from typing import List, Dict, Any, AsyncGenerator, override,Optional

from xgae.utils import log_trace


from xgae.engine.responser.responser_base import TaskResponseProcessor, TaskResponserContext, TaskRunContinuousState


class NonStreamTaskResponser(TaskResponseProcessor):
    def __init__(self, response_context: TaskResponserContext):
        super().__init__(response_context)

    @override
    async def process_response(self,
                               llm_response: Any,prompt_messages: List[Dict[str, Any]],
                               continuous_state: TaskRunContinuousState
                               ) -> AsyncGenerator[Dict[str, Any], None]:
        llm_content = ""
        parsed_xml_data = []
        finish_reason = None
        auto_continue_count = continuous_state['auto_continue_count']

        try:
            if hasattr(llm_response, 'choices') and llm_response.choices:
                if hasattr(llm_response.choices[0], 'finish_reason'):
                    finish_reason = llm_response.choices[0].finish_reason # LLM finish reason: ‘stop' , 'length'
                    logging.info(f"NonStreamResp: LLM response finish_reason={finish_reason}")

                response_message = llm_response.choices[0].message if hasattr(llm_response.choices[0], 'message') else None
                if response_message:
                    if hasattr(response_message, 'content') and response_message.content:
                        llm_content = response_message.content
                        
                        parsed_xml_data = self._parse_xml_tool_calls(llm_content)
                        if self.max_xml_tool_calls > 0 and len(parsed_xml_data) > self.max_xml_tool_calls:
                            logging.warning(f"NonStreamResp: Over XML Tool Limit, finish_reason='xml_tool_limit_reached', "
                                            f"parsed_xml_data_len={len(parsed_xml_data)}")
                            parsed_xml_data = parsed_xml_data[:self.max_xml_tool_calls]
                            finish_reason = "xml_tool_limit_reached"

            self.root_span.event(name=f"non_stream_processor_start[{self.task_no}]({auto_continue_count})", level="DEFAULT",
                             status_message=f"finish_reason={finish_reason}, tool_exec_strategy={self.tool_exec_strategy}, "
                                            f"parsed_xml_data_len={len(parsed_xml_data)}, llm_content_len={len(llm_content)}")

            message_data = {"role": "assistant", "content": llm_content}
            assistant_msg = self.add_response_message(type="assistant", content=message_data, is_llm_message=True)
            yield assistant_msg

            tool_calls_to_execute = [item['tool_call'] for item in parsed_xml_data]
            if  len(tool_calls_to_execute) > 0:
                tool_results = await self._execute_tools(tool_calls_to_execute, self.tool_exec_strategy)

                tool_index = 0
                for i, (returned_tool_call, tool_result) in enumerate(tool_results):
                    parsed_xml_item = parsed_xml_data[i]
                    tool_call = parsed_xml_item['tool_call']
                    parsing_details = parsed_xml_item['parsing_details']
                    assistant_msg_id = assistant_msg['message_id'] if assistant_msg else None

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
                logging.warning(f"NonStreamResp: finish_reason='non_tool_call', No Tool need to call !")

            if finish_reason:
                finish_content = {'status_type': "finish", 'finish_reason': finish_reason}
                finish_msg = self.add_response_message(type="status", content=finish_content, is_llm_message=False)
                yield finish_msg
        except Exception as e:
            trace = log_trace(e, f"NonStreamResp: Process response llm_content:\n {llm_content}")
            self.root_span.event(name="non_stream_process_response_error", level="ERROR",
                                 status_message=f"Process non-streaming response error: {e}",
                                 metadata={"content": llm_content, "trace": trace})

            content = {'role': "system", 'status_type': "error", 'message': f"Process non-streaming response error: {e}"}
            error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
            yield error_msg

            raise  # Use bare 'raise' to preserve the original exception with its traceback



