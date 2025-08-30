
from typing import Any, Dict, Optional
from langfuse import Langfuse

from xgae.utils.setup_env import setup_langfuse
from xgae.utils.llm_client import LangfuseMetadata
from xgae.engine.engine_base import XGATaskResult

class XGATaskLangFuse:
    langfuse: Langfuse = None

    def __init__(self,
                 session_id: str,
                 task_id:str,
                 task_run_id: str,
                 task_no: int,
                 agent_id: str) -> None:
        if XGATaskLangFuse.langfuse is None:
            XGATaskLangFuse.langfuse =  setup_langfuse()

        self.session_id = session_id
        self.task_id = task_id
        self.task_run_id = task_run_id
        self.task_no = task_no
        self.agent_id = agent_id

        self.trace_id = None
        self.root_span = None
        self.root_span_name = None


    def start_root_span(self,
                        root_span_name: str,
                        task_message: Dict[str, Any],
                        trace_id: Optional[str] = None):
        if self.root_span is None:
            trace = None
            if trace_id:
                self.trace_id = trace_id
                trace = XGATaskLangFuse.langfuse.trace(id=trace_id)
            else:
                trace = XGATaskLangFuse.langfuse.trace(name="xga_task_engine")
                self.trace_id = trace.id

            metadata = {"task_id": self.task_id, "session_id": self.session_id, "agent_id": self.agent_id}
            self.root_span = trace.span(id=self.task_run_id, name=root_span_name, input=task_message,metadata=metadata)
            self.root_span_name = root_span_name


    def end_root_span(self, root_span_name:str, output: Optional[XGATaskResult]=None):
        if self.root_span and self.root_span_name == root_span_name:
            self.root_span.end(output=output)
            self.root_span = None
            self.root_span_name = None


    def create_llm_langfuse_meta(self, llm_count:int)-> LangfuseMetadata:
        generation_name = f"xga_task_engine_llm_completion[{self.task_no}]({llm_count})"
        generation_id = f"{self.task_run_id}({llm_count})"
        return LangfuseMetadata(
            generation_name=generation_name,
            generation_id=generation_id,
            existing_trace_id=self.trace_id,
            session_id=self.session_id,
        )