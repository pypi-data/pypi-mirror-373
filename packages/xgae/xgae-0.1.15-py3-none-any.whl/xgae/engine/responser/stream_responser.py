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

        pending_tool_executions = []
        yielded_tool_indices = set()  # Track which tool statuses have been yielded
        tool_results_buffer = []  # Store (tool_call, result, tool_index, context)
        tool_index = 0
        
        current_xml_content = accumulated_content  # Track XML content for streaming detection

        logging.info(f"=== StreamResp：tool_exec_on_stream={self.tool_exec_on_stream}, auto_continue_count={auto_continue_count}, "
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
                        current_xml_content += chunk_content  #Track streaming XML content

                        xml_tool_call_count = len(self._extract_xml_chunks(accumulated_content))
                        if self.max_xml_tool_calls <= 0 or xml_tool_call_count < self.max_xml_tool_calls:
                            if use_assistant_chunk_msg:
                                message_data = {"role": "assistant", "content": chunk_content}
                                metadata = {"sequence": msg_sequence}
                                assistant_chunk_msg = self.create_response_message(type="assistant_chunk",
                                                                                   content=message_data,
                                                                                   is_llm_message=True,
                                                                                   metadata=metadata)
                                yield assistant_chunk_msg
                                msg_sequence += 1

                            #Process XML tool calls during streaming
                            if self.tool_exec_on_stream:
                                xml_chunks = self._extract_xml_chunks(current_xml_content)
                                for xml_chunk in xml_chunks:
                                    current_xml_content = current_xml_content.replace(xml_chunk, "", 1)
                                    result = self._parse_xml_tool_call(xml_chunk)
                                    if result:
                                        tool_call, parsing_details = result

                                        # Create tool context for streaming execution
                                        tool_context = self._create_tool_context(tool_call, tool_index, None, parsing_details)

                                        # Yield tool start status immediately
                                        tool_start_msg = self._add_tool_start_message(tool_context)
                                        yield tool_start_msg
                                        yielded_tool_indices.add(tool_index)

                                        # Create async execution task
                                        execution_task = asyncio.create_task(self._execute_tool(tool_call))
                                        pending_tool_executions.append({'task': execution_task,
                                                                        'tool_call': tool_call,
                                                                        'tool_index': tool_index,
                                                                        'tool_context': tool_context,
                                                                        'parsing_details': parsing_details})
                                        tool_index += 1
                        else:
                            finish_reason = "xml_tool_limit_reached"
                            logging.warning(f"StreamResp: Over XML Tool Limit, finish_reason='xml_tool_limit_reached', "
                                            f"xml_tool_call_count={xml_tool_call_count}")
                            break
            # for chunk is end

            if len(accumulated_content) == 0:
                logging.warning(f"StreamResp: LLM response_message content is empty")

            # Wait for pending tool executions from streaming phase
            if pending_tool_executions:
                logging.info(f"StreamResp: Waiting for {len(pending_tool_executions)} pending streamed tool executions")

                pending_tasks = [execution['task'] for execution in pending_tool_executions]
                done, _ = await asyncio.wait(pending_tasks)

                for pend_tool_exec in pending_tool_executions:
                    pend_tool_index = pend_tool_exec['tool_index']
                    pend_tool_context = pend_tool_exec['tool_context']

                    try:
                        if pend_tool_exec["task"].done():
                            result = pend_tool_exec['task'].result()
                            pend_tool_context.result = result
                            tool_results_buffer.append((pend_tool_exec["tool_call"], result, pend_tool_index, pend_tool_context))
                        else:
                            logging.warning(f"StreamResp: Task for tool index {pend_tool_index} is not done after wait.")
                    except Exception as e:
                        logging.error(f"StreamResp: Error getting result for pending tool execution {pend_tool_index}: {str(e)}")
                        pend_tool_context.error = e

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

            self.root_span.event(name=f"stream_processor_start[{self.task_no}]({auto_continue_count})", level="DEFAULT",
                                 status_message=f"finish_reason={finish_reason}, tool_exec_strategy={self.tool_exec_strategy}, "
                                                f"parsed_xml_data_len={len(parsed_xml_data)}, accumulated_content_len={len(accumulated_content)}, "
                                                f"should_auto_continue={should_auto_continue}, pending_executions_len={len(pending_tool_executions)}")

            assistant_msg = None
            if accumulated_content and not should_auto_continue:
                message_data = {"role": "assistant", "content": accumulated_content}
                assistant_msg = self.add_response_message(type="assistant", content=message_data, is_llm_message=True)
                yield assistant_msg

            # Process results from both streaming and non-streaming executions
            tool_calls_to_execute = [item['tool_call'] for item in parsed_xml_data]

            # Update assistant_message_id for streaming tool contexts
            assistant_msg_id = assistant_msg['message_id'] if assistant_msg else None
            for pend_tool_exec in pending_tool_executions:
                if not pend_tool_exec["tool_context"].assistant_message_id:
                    pend_tool_exec["tool_context"].assistant_message_id = assistant_msg_id

            if len(tool_calls_to_execute) > 0:
                if self.tool_exec_on_stream:
                    # Handle results from streaming executions + any remaining tools
                    remaining_tools = []
                    streamed_tool_indices = set()

                    # Identify which tools were already executed during streaming by index
                    for pend_tool_exec in pending_tool_executions:
                        streamed_tool_indices.add(pend_tool_exec["tool_index"])

                    # Find remaining tools that weren't executed during streaming
                    for i, parsed_item in enumerate(parsed_xml_data):
                        tool_call = parsed_item['tool_call']
                        tool_identifier = (tool_call.get('function_name', ''), str(tool_call.get('arguments', {})))

                        # Check if this tool was already executed during streaming
                        already_executed = False
                        for pend_tool_exec in pending_tool_executions:
                            exec_tool_call = pend_tool_exec["tool_call"]
                            exec_identifier = (exec_tool_call.get('function_name', ''),str(exec_tool_call.get('arguments', {})))
                            if tool_identifier == exec_identifier:
                                already_executed = True
                                break

                        if not already_executed:
                            remaining_tools.append((parsed_item['tool_call'], parsed_item['parsing_details'], tool_index))
                            tool_index += 1

                    # Execute remaining tools if any
                    if remaining_tools:
                        for tool_call, parsing_details, t_idx in remaining_tools:
                            tool_context = self._create_tool_context(tool_call, t_idx, assistant_msg_id,parsing_details)

                            tool_start_msg = self._add_tool_start_message(tool_context)
                            yield tool_start_msg

                            result = await self._execute_tool(tool_call)
                            tool_context.result = result
                            tool_results_buffer.append((tool_call, result, t_idx, tool_context))

                    # Process all tool results
                    for tool_call, result, t_idx, pend_tool_context in tool_results_buffer:
                        tool_message = self._add_tool_messsage(tool_call, result, self.xml_adding_strategy,assistant_msg_id,
                                                               getattr(pend_tool_context, 'parsing_details', None))

                        tool_completed_msg = self._add_tool_completed_message(pend_tool_context,tool_message['message_id'] if tool_message else None)
                        yield tool_completed_msg

                        yield tool_message

                        if pend_tool_context.function_name in ['ask', 'complete']:
                            finish_reason = "completed"
                            break
                else: # non-streaming execution
                    tool_results = await self._execute_tools(tool_calls_to_execute, self.tool_exec_strategy)
                    tool_index = 0
                    for i, (returned_tool_call, tool_result) in enumerate(tool_results):
                        parsed_xml_item = parsed_xml_data[i]
                        tool_call = parsed_xml_item['tool_call']
                        parsing_details = parsed_xml_item['parsing_details']

                        tool_context = self._create_tool_context(tool_call, tool_index, assistant_msg_id,parsing_details, tool_result)

                        tool_start_msg = self._add_tool_start_message(tool_context)
                        yield tool_start_msg

                        tool_message = self._add_tool_messsage(tool_call, tool_result, self.xml_adding_strategy,assistant_msg_id, parsing_details)

                        tool_completed_msg = self._add_tool_completed_message(tool_context, tool_message['message_id'])
                        yield tool_completed_msg

                        yield tool_message

                        if tool_context.function_name in ['ask', 'complete']:
                            finish_reason = "completed"
                            break

                        tool_index += 1
            else:
                finish_reason = "non_tool_call"
                logging.warning(f"StreamResp: tool_calls is empty, No Tool need to call !")

            if finish_reason:
                finish_content = {"status_type": "finish", "finish_reason": finish_reason}
                finish_msg = self.add_response_message(type="status", content=finish_content, is_llm_message=False)
                yield finish_msg
        except Exception as e:
            trace = log_trace(e, f"StreamResp: Process response accumulated_content:\n {accumulated_content}")
            self.root_span.event(name="stream_response_process_error", level="ERROR",
                                 status_message=f"Process streaming response error: {e}",
                                 metadata={"content": accumulated_content, "trace": trace})

            content = {"role": "system", "status_type": "error", "message": f"Process streaming response error: {e}"}
            error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
            yield error_msg

            raise  # Use bare 'raise' to preserve the original exception with its traceback
        finally:
            if should_auto_continue:
                continuous_state['accumulated_content'] = accumulated_content
                continuous_state['assistant_msg_sequence'] = msg_sequence
                logging.warning(f"StreamResp: Updated continuous state for auto-continue with {len(accumulated_content)} chars")