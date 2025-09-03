import asyncio
import logging
from typing import Any, Dict, List, Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from xgae.engine.engine_base import XGATaskResult, XGAResponseMessage
from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.utils.setup_env import setup_langfuse, setup_logging
from xgae.utils import log_trace
from xgae.utils.misc import read_file
from xgae.engine.task_engine import XGATaskEngine

class TaskState(TypedDict, total=False):
    """State definition for the agent orchestration graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_input: str
    next_node: str
    agent_context: Dict[str, Any]
    system_prompt: str
    custom_tools: List[str]
    general_tools: List[str]
    task_result: XGATaskResult
    iteration_count: int

langfuse = setup_langfuse()

class XGAReactAgent:
    MAX_TASK_RETRY = 2

    def __init__(self):
        self.tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        self.graph = None

    async def _create_graph(self) -> StateGraph:
        try:
            graph_builder = StateGraph(TaskState)

            # Add nodes
            graph_builder.add_node('supervisor', self._supervisor_node)
            graph_builder.add_node('select_tool', self._select_tool_node)
            graph_builder.add_node('exec_task', self._exec_task_node)
            graph_builder.add_node('final_result', self._final_result_node)

            # Add edges
            graph_builder.add_edge(START, 'supervisor')
            graph_builder.add_conditional_edges(
                'supervisor',
                self._next_condition,
                {
                    'select_tool': 'select_tool',
                    'exec_task': 'exec_task',
                    'end': END
                }
            )

            graph_builder.add_edge('select_tool', 'exec_task')
            graph_builder.add_edge('exec_task', 'final_result')

            graph_builder.add_conditional_edges(
                'final_result',
                self._next_condition,
                {
                    'supervisor': 'supervisor',
                    'end': END
                }
            )
            
            graph = graph_builder.compile(checkpointer=MemorySaver())
            graph.name = "XGARectAgentGraph"

            return graph
        except Exception as e:
            logging.error("Failed to create XGARectAgent Graph: %s", str(e))
            raise

    def _search_system_prompt(self, user_input: str) -> str:
        # You should search RAG use user_input, fetch COT or Prompt for your business
        system_prompt = None if "fault" not in user_input else read_file("templates/example/fault_user_prompt.txt")
        return system_prompt

    async def _supervisor_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        system_prompt = self._search_system_prompt(user_input)

        general_tools = [] if system_prompt else ["*"]
        custom_tools = ["*"] if system_prompt  else []

        next_node = "select_tool" if system_prompt else "exec_task"
        return {
            'system_prompt' : system_prompt,
            'next_node'     : next_node,
            'general_tools' : general_tools,
            'custom_tools'  : custom_tools,
        }

    def _select_custom_tools(self, system_prompt: str) -> list[str]:
        custom_tools = ["*"] if system_prompt  else []
        return custom_tools

    async def _select_tool_node(self, state: TaskState) -> Dict[str, Any]:
        system_prompt = state.get('system_prompt',None)
        general_tools = []
        custom_tools = self._select_custom_tools(system_prompt)
        return {
            'general_tools' : general_tools,
            'custom_tools'  : custom_tools,
        }

    async def _exec_task_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state['user_input']
        system_prompt = state.get('system_prompt',None)
        general_tools = state.get('general_tools',[])
        custom_tools = state.get('custom_tools',[])
        is_system_prompt = True if system_prompt is not None else False
        
        try:
            logging.info(f"🔥 XGATaskEngine: run_task_with_final_answer: user_input={user_input}, general_tools={general_tools}, custom_tools={custom_tools}, is_system_prompt={is_system_prompt}")
            engine = XGATaskEngine(tool_box=self.tool_box,
                                   general_tools=general_tools,
                                   custom_tools=custom_tools,
                                   system_prompt=system_prompt)
            task_result = await engine.run_task_with_final_answer(
                task_message={"role": "user", "content": user_input}
            )
        except Exception as e:
            logging.error("Failed to execute task: %s", str(e))
            task_result = XGATaskResult(type="error", content="Failed to execute task")

        iteration_count = state.get('iteration_count', 0) + 1
        return {
            'task_result' : task_result,
            'iteration_count': iteration_count,
        }

    async def _final_result_node(self, state: TaskState) -> Dict[str, Any]:
        iteration_count = state['iteration_count']
        task_result = state['task_result']
        next_node = "end"
        if iteration_count < self.MAX_TASK_RETRY and task_result["type"] == "error":
            next_node = "supervisor"
            
        return {
            'next_node' : next_node
        }

    def _next_condition(self, state: TaskState) -> str:
        next_node = state['next_node']
        return next_node


    async def generate(self, user_input: str) -> XGATaskResult:
        result = None
        try:
            logging.info("****** Start React Agent for user_input: %s", user_input)

            # Create graph if not already created
            if self.graph is None:
                self.graph = await self._create_graph()

            # Initialize state
            initial_state = {
                'messages'          : [HumanMessage(content=f"information for: {user_input}")],
                'user_input'        : user_input,
                'next_node'         : None,
                'agent_context'     : {},
                'iteration_count'   : 0
            }

            # Run the retrieval graph with proper configuration
            config = {'recursion_limit': 100,
                      'configurable': {
                          'thread_id': "manager_async_generate_thread"
                      }}
            final_state = await self.graph.ainvoke(initial_state, config=config)

            # Parse and return formatted results
            result = final_state["task_result"]

            logging.info("=" * 100)
            logging.info(f"USER QUESTION: {user_input}")
            logging.info(f"LLM ANSWER: {result}")
            logging.info("=" * 100)

            return result
        except Exception as e:
            log_trace(e, f"XReactAgent generate: user_input={user_input}")
            result = XGATaskResult(type="error", content=f"React Agent error: {e}")
            return result


if __name__ == "__main__":
    setup_logging()

    async def main():
        agent = XGAReactAgent()
        user_inputs = [
                        "locate 10.2.3.4 fault and solution",
                        #"5+5",
                    ]
        for user_input in user_inputs:
            result = await agent.generate(user_input)
            await asyncio.sleep(1)
            print(result)

    asyncio.run(main())
