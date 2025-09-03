from typing import Union, Optional, Dict, List, Any, Literal, TypedDict
from dataclasses import dataclass
from abc import ABC, abstractmethod

class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass

XGAMsgStatusType = Literal["error", "finish", "tool_started", "tool_completed", "tool_error", "tool_failed"]
XGAResponseMsgType = Literal["user", "status",  "tool", "assistant", "assistant_chunk"]

class XGAResponseMessage(TypedDict, total=False):
    message_id: str
    type: XGAResponseMsgType
    is_llm_message: bool
    content: Union[Dict[str, Any], str]
    metadata: Dict[str, Any]

class XGATaskResult(TypedDict, total=False):
    type: Literal["ask", "answer", "error"]
    content: str
    attachments: Optional[List[str]]

XGAToolType = Literal["general", "custom",  "agent"]

@dataclass
class XGAToolSchema:
    tool_name: str
    tool_type: XGAToolType
    server_name: str
    description: str
    input_schema: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


@dataclass
class XGAToolResult:
    success: bool
    output: str


class XGAToolBox(ABC):
    @abstractmethod
    async def creat_task_tool_box(self, task_id: str, general_tools: List[str], custom_tools: List[str]):
        pass

    @abstractmethod
    async def destroy_task_tool_box(self, task_id: str):
        pass

    @abstractmethod
    def get_task_tool_schemas(self, task_id: str, type: XGAToolType) -> List[XGAToolSchema]:
        pass

    @abstractmethod
    def get_task_tool_names(self, task_id: str) -> List[str]:
        pass

    @abstractmethod
    async def call_tool(self, task_id: str, tool_name: str, args: Optional[Dict[str, Any]] = None) -> XGAToolResult:
        pass