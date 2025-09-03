import asyncio
import json
import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union, Literal, Callable, TypedDict, AsyncGenerator

from xgae.utils import log_trace
from xgae.utils.json_helpers import safe_json_parse
from xgae.utils.xml_tool_parser import XMLToolParser

from xgae.engine.engine_base import XGAToolResult, XGAToolBox
from xgae.engine.task_langfuse import XGATaskLangFuse


# Type alias for XML result adding strategy
XmlAddingStrategy = Literal["user_message", "assistant_message", "inline_edit"]

# Type alias for tool execution strategy
ToolExecutionStrategy = Literal["sequential", "parallel"]

class TaskResponserContext(TypedDict, total=False):
    is_stream: bool
    task_id: str
    task_run_id: str
    task_no: int
    model_name: str
    max_xml_tool_calls: int             # LLM generate max_xml_tool limit, 0 is no limit
    use_assistant_chunk_msg: bool
    tool_exec_strategy: ToolExecutionStrategy
    xml_adding_strategy: XmlAddingStrategy
    add_response_msg_func: Callable
    create_response_msg_func: Callable
    tool_box: XGAToolBox
    task_langfuse: XGATaskLangFuse


class TaskRunContinuousState(TypedDict, total=False):
    accumulated_content: str
    auto_continue_count: int
    auto_continue: bool
    assistant_msg_sequence: int


@dataclass
class ToolExecutionContext:
    """Context for a tool execution including call details, result, and display info."""
    tool_call: Dict[str, Any]
    tool_index: int
    function_name: str
    xml_tag_name: str
    result: Optional[XGAToolResult] = None
    error: Optional[Exception] = None
    assistant_message_id: Optional[str] = None
    parsing_details: Optional[Dict[str, Any]] = None


class TaskResponseProcessor(ABC):
    def __init__(self, response_context: TaskResponserContext):
        self.response_context = response_context

        self.task_id                = response_context['task_id']
        self.task_run_id            = response_context['task_run_id']
        self.task_no                = response_context['task_no']
        self.tool_exec_strategy     = response_context['tool_exec_strategy']
        self.xml_adding_strategy    = response_context['xml_adding_strategy']
        self.max_xml_tool_calls     = response_context['max_xml_tool_calls']

        self.add_response_message       = response_context['add_response_msg_func']
        self.create_response_message    = response_context['create_response_msg_func']
        self.tool_box                   = response_context['tool_box']

        task_langfuse = response_context['task_langfuse']
        self.root_span = task_langfuse.root_span

        self.xml_parser                 = XMLToolParser()



    @abstractmethod
    async def process_response(self,
                               llm_response: AsyncGenerator,
                               prompt_messages: List[Dict[str, Any]],
                               continuous_state: TaskRunContinuousState
                               ) -> AsyncGenerator[Dict[str, Any], None]:
        pass


    def _extract_xml_chunks(self, content: str) -> List[str]:
        """Extract complete XML chunks using start and end pattern matching."""
        chunks = []
        pos = 0

        try:
            # First, look for new format <function_calls> blocks
            start_pattern = '<function_calls>'
            end_pattern = '</function_calls>'

            while pos < len(content):
                # Find the next function_calls block
                start_pos = content.find(start_pattern, pos)
                if start_pos == -1:
                    break

                # Find the matching end tag
                end_pos = content.find(end_pattern, start_pos)
                if end_pos == -1:
                    break

                # Extract the complete block including tags
                chunk_end = end_pos + len(end_pattern)
                chunk = content[start_pos:chunk_end]
                chunks.append(chunk)

                # Move position past this chunk
                pos = chunk_end

            # If no new format found, fall back to old format for backwards compatibility
            if not chunks:
                pos = 0
                while pos < len(content):
                    # Find the next tool tag
                    next_tag_start = -1
                    current_tag = None

                    # Find the earliest occurrence of any registered tool function name
                    # Check for available function names
                    available_func_names = self.tool_box.get_task_tool_names(self.task_id)
                    for func_name in available_func_names:
                        # Convert function name to potential tag name (underscore to dash)
                        tag_name = func_name.replace('_', '-')
                        start_pattern = f'<{tag_name}'
                        tag_pos = content.find(start_pattern, pos)

                        if tag_pos != -1 and (next_tag_start == -1 or tag_pos < next_tag_start):
                            next_tag_start = tag_pos
                            current_tag = tag_name

                    if next_tag_start == -1 or not current_tag:
                        break

                    # Find the matching end tag
                    end_pattern = f'</{current_tag}>'
                    tag_stack = []
                    chunk_start = next_tag_start
                    current_pos = next_tag_start

                    while current_pos < len(content):
                        # Look for next start or end tag of the same type
                        next_start = content.find(f'<{current_tag}', current_pos + 1)
                        next_end = content.find(end_pattern, current_pos)

                        if next_end == -1:  # No closing tag found
                            break

                        if next_start != -1 and next_start < next_end:
                            # Found nested start tag
                            tag_stack.append(next_start)
                            current_pos = next_start + 1
                        else:
                            # Found end tag
                            if not tag_stack:  # This is our matching end tag
                                chunk_end = next_end + len(end_pattern)
                                chunk = content[chunk_start:chunk_end]
                                chunks.append(chunk)
                                pos = chunk_end
                                break
                            else:
                                # Pop nested tag
                                tag_stack.pop()
                                current_pos = next_end + 1

                    if current_pos >= len(content):  # Reached end without finding closing tag
                        break

                    pos = max(pos + 1, current_pos)
        except Exception as e:
            trace = log_trace(e, f"TaskProcessor extract_xml_chunks: Error extracting XML chunks: {content}")
            self.root_span.event(name="task_process_extract_xml_chunk_error", level="ERROR",
                                 status_message=f"Error extracting XML chunks: {e}",
                                 metadata={"content": content, "trace": trace})

        return chunks

    def _parse_xml_tool_call(self, xml_chunk: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Parse XML chunk into tool call format and return parsing details.

        Returns:
            Tuple of (tool_call, parsing_details) or None if parsing fails.
            - tool_call: Dict with 'function_name', 'xml_tag_name', 'arguments'
            - parsing_details: Dict with 'attributes', 'elements', 'text_content', 'root_content'
        """
        try:
            # Check if this is the new format (contains <function_calls>)
            if '<function_calls>' in xml_chunk and '<invoke' in xml_chunk:
                # Use the new XML parser
                parsed_calls = self.xml_parser.parse_content(xml_chunk)

                if not parsed_calls:
                    logging.error(f"TaskProcessor parse_xml_tool_call: No tool calls found in XML chunk: {xml_chunk}")
                    return None

                # Take the first tool call (should only be one per chunk)
                xml_tool_call = parsed_calls[0]
                if not xml_tool_call.function_name:
                    logging.error(f"TaskProcessor parse_xml_tool_call: xml_tool_call function name is empty: {xml_tool_call}")
                    return None

                # Convert to the expected format
                tool_call = {
                    'function_name' : xml_tool_call.function_name,
                    'xml_tag_name'  : xml_tool_call.function_name.replace("_", "-"),  # For backwards compatibility
                    'arguments'     : xml_tool_call.parameters
                }

                # Include the parsing details
                parsing_details = xml_tool_call.parsing_details
                parsing_details['raw_xml'] = xml_tool_call.raw_xml

                logging.debug(f"TaskProcessor parse_xml_tool_call: Parsed new format tool call: {tool_call}")
                return tool_call, parsing_details

            # If not the expected <function_calls><invoke> format, return None
            logging.error(f"TaskProcessor parse_xml_tool_call: XML chunk does not contain expected <function_calls><invoke> format: {xml_chunk}")
        except Exception as e:
            trace = log_trace(e, f"TaskProcessor parse_xml_tool_call: Error parsing XML chunk: {xml_chunk}")
            self.root_span.event(name="task_process_parsing_xml_chunk_error", level="ERROR",
                                 status_message=f"Error parsing XML chunk: {e}",
                                 metadata={"xml_chunk": xml_chunk, "trace": trace})
            return None

    def _parse_xml_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse XML tool calls from content string.

        Returns:
            List of dictionaries, each containing {'tool_call': ..., 'parsing_details': ...}
        """
        parsed_data = []
        xml_chunk = None
        try:
            xml_chunks = self._extract_xml_chunks(content)

            for xml_chunk in xml_chunks:
                result = self._parse_xml_tool_call(xml_chunk)
                if result:
                    tool_call, parsing_details = result
                    parsed_data.append({
                        "tool_call": tool_call,
                        "parsing_details": parsing_details
                    })
        except Exception as e:
            trace = log_trace(e, f"TaskProcessor parse_xml_tool_calls: Error parsing XML tool calls, xml_chunk: {xml_chunk}")
            self.root_span.event(name="task_process_parse_xml_tool_calls_error", level="ERROR",
                             status_message=f"Error parsing XML tool calls: {e}",
                                 metadata={"content": xml_chunk, "trace": trace})

        return parsed_data


    async def _execute_tool(self, tool_call: Dict[str, Any]) -> XGAToolResult:
        """Execute a single tool call and return the result."""
        function_name = tool_call['function_name']
        exec_tool_span = self.root_span.span(name=f"execute_tool.{function_name}", input=tool_call["arguments"])
        try:
            arguments = tool_call.get('arguments', {})
            if isinstance(arguments, str):
                try:
                    arguments = safe_json_parse(arguments)
                except json.JSONDecodeError:
                    logging.warning(f"TaskProcessor execute_tool: Tool '{function_name}' arguments is not dict type, args={arguments}")
                    arguments = {"text": arguments}  # useless

            result = None
            available_tool_names = self.tool_box.get_task_tool_names(self.task_id)
            if function_name in available_tool_names:
                logging.info(f"TaskProcessor execute_tool: Tool '{function_name}' executing, args={arguments}")
                result = await self.tool_box.call_tool(self.task_id, function_name, arguments)
            else:
                logging.error(f"TaskProcessor execute_tool: Tool function '{function_name}' not found in toolbox")
                result = XGAToolResult(success=False, output=f"Tool function '{function_name}' not found")

            logging.info(f"TaskProcessor execute_tool: Tool '{function_name}' execution complete, result: {result}")
            exec_tool_span.update(status_message="tool_executed", output=result)

            return result
        except Exception as e:
            trace = log_trace(e, f"TaskProcessor execute_tool: Executing tool {function_name}")

            exec_tool_span.update(status_message="task_process_tool_exec_error", level="ERROR",
                                  output=f"Error executing tool {function_name}, error: {str(e)}",
                                  metadata={"trace": trace})

            return XGAToolResult(success=False, output=f"Executing tool {function_name}, error: {str(e)}")


    async def _execute_tools(self, tool_calls: List[Dict[str, Any]],
                             execution_strategy: ToolExecutionStrategy = "sequential"
                             ) -> List[Tuple[Dict[str, Any], XGAToolResult]]:
        if execution_strategy == "sequential":
            return await self._execute_tools_sequentially(tool_calls)
        elif execution_strategy == "parallel":
            return await self._execute_tools_in_parallel(tool_calls)
        else:
            logging.warning(f"TaskProcessor execute_tools: Unknown execution strategy '{execution_strategy}', use sequential")
            return await self._execute_tools_sequentially(tool_calls)


    async def _execute_tools_sequentially(self, tool_calls: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], XGAToolResult]]:
        """Execute tool calls sequentially and return results.

        This method executes tool calls one after another, waiting for each tool to complete
        before starting the next one. This is useful when tools have dependencies on each other.

        Returns:
            List of tuples containing the original tool call and its result
        """
        if not tool_calls:
            logging.warning("TaskProcessor execute_tools_sequentially: tool_calls is empty")
            return []

        tool_names = [tc['function_name'] for tc in tool_calls]
        tool_num = len(tool_calls)
        if tool_num > 1:
            logging.info(f"TaskProcessor execute_tools_sequentially: Executing {tool_num} tools sequentially: {tool_names}")
            self.root_span.event(name="task_process_execute_tools_sequentially", level="DEFAULT",
                                  status_message=f"Executing {len(tool_calls)} tools sequentially: {tool_names}")

        results = []
        for index, tool_call in enumerate(tool_calls):
            tool_name = tool_call['function_name']
            logging.info(f"TaskProcessor execute_tools_sequentially: Executing tool '{tool_name}', sequence={index + 1}/{tool_num}")
            result = await self._execute_tool(tool_call)
            results.append((tool_call, result))

            # Check if this is a terminating tool (ask or complete)
            if tool_name in ["ask", "complete"]:
                if len(results) < tool_num:
                    logging.info(f"TaskProcessor execute_tools_sequentially: Terminating tool '{tool_name}' executed, Stopping further tool execution.")
                    self.root_span.event(name="task_process_terminate_tool_executed", level="DEFAULT",
                                         status_message=f"Terminating tool '{tool_name}' executed, Stopping further tool execution.")
                break

        logging.info(f"TaskProcessor execute_tools_sequentially: Execution completed for {len(results)} tools, total {tool_num} tools)")
        return results


    async def _execute_tools_in_parallel(self, tool_calls: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], XGAToolResult]]:
        """Execute tool calls in parallel and return results.

        This method executes all tool calls simultaneously using asyncio.gather, which
        can significantly improve performance when executing multiple independent tools.

        Returns:
            List of tuples containing the original tool call and its result
        """
        if not tool_calls:
            logging.warning("TaskProcessor execute_tools_in_parallel: tool_calls is empty")
            return []

        tool_names = [tc['function_name'] for tc in tool_calls]
        tool_num = len(tool_calls)
        if tool_num > 1:
            logging.info(f"TaskProcessor execute_tools_in_parallel: Executing {tool_num} tools sequentially: {tool_names}")
            self.root_span.event(name="task_process_execute_tools_parallel", level="DEFAULT",
                                  status_message=f"Executing {len(tool_calls)} tools parallelly: {tool_names}")

        # Execute all tasks concurrently with error handling
        tasks = [self._execute_tool(tool_call) for tool_call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, (tool_call, result) in enumerate(zip(tool_calls, results)):
            processed_results.append((tool_call, result))

        logging.info(f"TaskProcessor execute_tools_in_parallel: Execution completed for {len(results)} tools, total {tool_num} tools)")
        return processed_results

    def _create_tool_context(self,
                             tool_call: Dict[str, Any],
                             tool_index: int,
                             assistant_message_id: Optional[str] = None,
                             parsing_details: Optional[Dict[str, Any]] = None,
                             result: Optional[XGAToolResult] = None,
                             ) -> ToolExecutionContext:
        """Create a tool execution context with display name and parsing details populated."""
        return ToolExecutionContext(
            tool_call               = tool_call,
            tool_index              = tool_index,
            function_name           = tool_call['function_name'],
            xml_tag_name            = tool_call['xml_tag_name'],
            assistant_message_id    = assistant_message_id,
            parsing_details         = parsing_details,
            result                  = result
        )


    def _add_tool_messsage(self,context:ToolExecutionContext, strategy: XmlAddingStrategy) -> Optional[Dict[str, Any]]:  # Return the full message object
        # Create two versions of the structured result
        # Rich version for the frontend
        result_for_frontend = self._create_structured_tool_result(context.tool_call, context.result, context.parsing_details, for_llm=False)
        # Concise version for the LLM
        result_for_llm = self._create_structured_tool_result(context.tool_call, context.result, context.parsing_details, for_llm=True)

        # Add the message with the appropriate role to the conversation history
        # This allows the LLM to see the tool result in subsequent interactions
        role = "user" if strategy == "user_message" else "assistant"
        content = {
            'role': role,
            'content': json.dumps(result_for_llm)
        }

        metadata = {}
        if context.assistant_message_id:
            metadata['assistant_message_id'] = context.assistant_message_id

        if context.parsing_details:
            metadata['parsing_details'] = context.parsing_details

        metadata['frontend_content'] = result_for_frontend

        tool_message =  self.add_response_message(type="tool", content=content, is_llm_message=True, metadata=metadata)

        # Let's result_for_frontend the message for yielding.
        yield_message = tool_message.copy()
        yield_message['content'] = result_for_frontend

        return yield_message


    def _create_structured_tool_result(self,
                                       tool_call: Dict[str, Any],
                                       result: XGAToolResult,
                                       parsing_details: Optional[Dict[str, Any]] = None,
                                       for_llm: bool = False) -> Dict[str, Any]:
        function_name = tool_call['function_name']
        xml_tag_name = tool_call['xml_tag_name']
        arguments = tool_call.get('arguments', {})

        # Process the output - if it's a JSON string, parse it back to an object
        output = result.output
        parsed_output = safe_json_parse(output)
        if isinstance(parsed_output, (dict, list)):
            output = parsed_output

        output_to_use = output
        # If this is for the LLM and it's an edit_file tool, create a concise output
        if for_llm and function_name == 'edit_file' and isinstance(output, dict):
            # The frontend needs original_content and updated_content to render diffs.
            # The concise version for the LLM was causing issues.
            # @todo We will now pass the full output, and rely on the ContextManager to truncate if needed.
            output_to_use = output

        structured_result = {
            'tool_execution': {
                'function_name' : function_name,
                'xml_tag_name'  : xml_tag_name,
                'arguments'     : arguments,
                'result'      : {
                    'success' : result.success,
                    'output'  : output_to_use,
                    'error'   : None if result.success else result.output
                },
            }
        }

        return structured_result


    def _add_tool_start_message(self, context: ToolExecutionContext) -> Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool started status message."""
        content = {
            'status_type'       : "tool_started",
            'role'              : "assistant",
            'function_name'     : context.function_name,
            'xml_tag_name'      : context.xml_tag_name,
            'message'           : f"Starting execution of {context.function_name}",
            'tool_index'        : context.tool_index
        }

        return  self.add_response_message(type="status", content=content, is_llm_message=False)

    def _add_tool_completed_message(self, context: ToolExecutionContext, tool_message_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool completed/failed status message."""
        if not context.result:
            return  self._add_tool_error_message(context)

        status_type = "tool_completed" if context.result.success else "tool_failed"
        message_text = f"Tool {context.function_name} {'completed successfully' if context.result.success else 'failed'}"

        content = {
            'status_type'       : status_type,
            'role'              : "assistant",
            'function_name'     : context.function_name,
            'xml_tag_name'      : context.xml_tag_name,
            'message'           : message_text,
            'tool_index'        : context.tool_index
        }

        metadata = {}
        if tool_message_id:
            metadata['tool_result_message_id'] = tool_message_id

        return  self.add_response_message(type="status", content=content, is_llm_message=False, metadata=metadata)

    def _add_tool_error_message(self, context: ToolExecutionContext) -> Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool error status message."""
        error_msg = str(context.error) if context.error else "Tool execution unknown exception"
        content = {
            'status_type'       : "tool_error",
            'role'              : "assistant",
            'function_name'     : context.function_name,
            'xml_tag_name'      : context.xml_tag_name,
            'message'           : f"Executing tool {context.function_name} exception: {error_msg}",
            'tool_index'        : context.tool_index
        }

        return  self.add_response_message(type="status", content=content, is_llm_message=False)

