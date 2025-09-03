import json
import logging
import os

from typing import List, Any, Dict, Optional, Literal, override

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from xgae.engine.engine_base import XGAError, XGAToolSchema, XGAToolBox, XGAToolResult, XGAToolType

class XGAMcpToolBox(XGAToolBox):
    GENERAL_MCP_SERVER_NAME = "xga_general"
    AGENT_MCP_SERVER_PREFIX = "_@_"

    def __init__(self,
                 custom_mcp_server_file: Optional[str] = None,
                 custom_mcp_server_config: Optional[Dict[str, Any]] = None
        ):
        general_mcp_server_config = self._load_mcp_servers_config("mcpservers/xga_server.json")
        tool_box_mcp_server_config = general_mcp_server_config.get('mcpServers', {})

        if custom_mcp_server_config:
            tool_box_mcp_server_config.update(custom_mcp_server_config)
        elif custom_mcp_server_file:
            custom_mcp_server_config = self._load_mcp_servers_config(custom_mcp_server_file)
            custom_mcp_server_config = custom_mcp_server_config.get('mcpServers', {})
            tool_box_mcp_server_config.update(custom_mcp_server_config)

        self._mcp_client = MultiServerMCPClient(tool_box_mcp_server_config)

        self.mcp_server_names: List[str] = [server_name for server_name in tool_box_mcp_server_config]
        self.mcp_tool_schemas: Dict[str, List[XGAToolSchema]] = {}
        self.task_tool_schemas: Dict[str, Dict[str,XGAToolSchema]] = {}

        self.is_loaded_tool_schemas = False

    @override
    async def creat_task_tool_box(self, task_id: str, general_tools: List[str], custom_tools: List[str]):
        task_tool_schemas = {}
        general_tool_schemas = self.mcp_tool_schemas.get(self.GENERAL_MCP_SERVER_NAME, {})
        if "*" in general_tools:
            task_tool_schemas = {tool_schema.tool_name: tool_schema for tool_schema in general_tool_schemas}
        else:
            for tool_schema in general_tool_schemas:
                if tool_schema.tool_name in general_tools:
                    task_tool_schemas[tool_schema.tool_name] = tool_schema
        task_tool_schemas.pop("end_task", None)

        if len(custom_tools) == 1 and custom_tools[0] == "*":
            custom_tools = []
            for server_name in self.mcp_server_names:
                if server_name != self.GENERAL_MCP_SERVER_NAME:
                    custom_tools.append(f"{server_name}.*")

        for server_tool_name in custom_tools:
            parts = server_tool_name.split(".")
            if len(parts) != 2:
                continue
            custom_server_name, custom_tool_name = parts
            if (not custom_server_name ) or (not custom_tool_name):
                continue

            custom_tool_schemas = self.mcp_tool_schemas.get(custom_server_name, None)
            if custom_tool_schemas is None:
                continue
            if custom_tool_name == "*":
                custom_tool_schema_dict = {tool_schema.tool_name: tool_schema for tool_schema in custom_tool_schemas}
                task_tool_schemas.update(custom_tool_schema_dict)
            else:
                for tool_schema in custom_tool_schemas:
                    if custom_tool_name == tool_schema.tool_name:
                        task_tool_schemas[custom_tool_name] = tool_schema


        self.task_tool_schemas[task_id] = task_tool_schemas

    @override
    async def destroy_task_tool_box(self, task_id: str):
        tool_schemas = self.get_task_tool_schemas(task_id, "general")
        if len(tool_schemas) > 0:
            await self.call_tool(task_id, "end_task", {'task_id': task_id})
        self.task_tool_schemas.pop(task_id, None)

    @override
    def get_task_tool_names(self, task_id: str) -> List[str]:
        task_tool_schema = self.task_tool_schemas.get(task_id, {})
        task_tool_names =  list(task_tool_schema.keys())
        return task_tool_names

    @override
    def get_task_tool_schemas(self, task_id: str, tool_type: XGAToolType) -> List[XGAToolSchema]:
        task_tool_schemas = []

        all_task_tool_schemas = self.task_tool_schemas.get(task_id, {})
        for tool_schema in all_task_tool_schemas.values():
            if tool_schema.tool_type == tool_type:
                task_tool_schemas.append(tool_schema)

        return task_tool_schemas

    @override
    async def call_tool(self, task_id: str, tool_name: str, args: Optional[Dict[str, Any]] = None) -> XGAToolResult:
        if tool_name == "end_task":
            server_name = self.GENERAL_MCP_SERVER_NAME
        else:
            task_tool_schemas = self.task_tool_schemas.get(task_id, {})
            tool_schema = task_tool_schemas.get(tool_name, None)
            if tool_schema is None:
                raise XGAError(f"MCP tool not found: '{tool_name}'")
            server_name = tool_schema.server_name

        async with self._mcp_client.session(server_name) as session:
            tools = await load_mcp_tools(session)
            mcp_tool = next((t for t in tools if t.name == tool_name), None)

            if mcp_tool:
                tool_args = args or {}
                tool_type = self._get_tool_type(server_name)
                if tool_type == "general" or tool_type == "agent":
                    tool_args = dict({'task_id': task_id}, **tool_args)

                try:
                    tool_result = await mcp_tool.arun(tool_args)
                    if tool_type == "general":
                        tool_result = json.loads(tool_result)
                        result = XGAToolResult(success=tool_result['success'], output=str(tool_result['output']))
                    else:
                        result = XGAToolResult(success=True, output=str(tool_result))
                except Exception as e:
                    error = f"Call mcp tool '{tool_name}' error: {str(e)}"
                    logging.error(f"McpToolBox call_tool: {error}")
                    result = XGAToolResult(success=False, output=error)
            else:
                error = f"No MCP tool found with name: {tool_name}"
                logging.info(f"McpToolBox call_tool: error={error}")
                result =  XGAToolResult(success=False, output=error)

            return result


    async def load_mcp_tools_schema(self)-> None:
        if not self.is_loaded_tool_schemas:
            for server_name in self.mcp_server_names:
                self.mcp_tool_schemas[server_name] = []
                try:
                    mcp_tools = await self._mcp_client.get_tools(server_name=server_name)
                except Exception as e:
                    logging.error(f"### McpToolBox load_mcp_tools_schema: Langchain mcp get_tools failed, "
                                  f"need start mcp server '{server_name}' !")
                    continue

                tool_type = self._get_tool_type(server_name)
                for tool in mcp_tools:
                    input_schema = tool.args_schema
                    if tool_type == "general" or tool_type == "agent":
                        input_schema['properties'].pop("task_id", None)
                        if 'task_id' in input_schema['required']:
                            input_schema['required'].remove('task_id')
                        params_properties = input_schema.get('properties', {})
                        for param_properties in params_properties.values():
                            param_properties.pop('title', None)

                    metadata = tool.metadata or {}
                    tool_schema = XGAToolSchema(tool_name=tool.name,
                                                tool_type=tool_type,
                                                server_name=server_name,
                                                description=tool.description,
                                                input_schema=input_schema,
                                                metadata=metadata)
                    self.mcp_tool_schemas[server_name].append(tool_schema)
            self.is_loaded_tool_schemas = True

    async def reload_mcp_tools_schema(self) -> None:
        self.is_loaded_tool_schemas = False
        await self.load_mcp_tools_schema()


    def _load_mcp_servers_config(self, mcp_config_path: str) -> Dict[str, Any]:
        try:
            if os.path.exists(mcp_config_path):
                with open(mcp_config_path, 'r', encoding="utf-8") as f:
                    server_config = json.load(f)

                    for server_name, server_info in server_config['mcpServers'].items():
                        if "transport" not in server_info:
                            if "url" in server_info:
                                server_info['transport'] = "streamable_http" if "mcp" in server_info['url'] else "sse"
                            else:
                                server_info['transport'] = "stdio"

                    return server_config
            else:
                logging.warning(f"McpToolBox load_mcp_servers_config: MCP servers config file not found at: {mcp_config_path}")
                return {'mcpServers': {}}

        except Exception as e:
            logging.error(f"McpToolBox load_mcp_servers_config: Failed to load MCP servers config: {e}")
            return {'mcpServers': {}}

    def _get_tool_type(self, server_name: str) -> XGAToolType:
        tool_type: XGAToolType = "custom"
        if server_name == self.GENERAL_MCP_SERVER_NAME:
            tool_type = "general"
        elif server_name.startswith(self.AGENT_MCP_SERVER_PREFIX):
            tool_type = "agent"
        return tool_type

if __name__ == "__main__":
    import asyncio
    from dataclasses import asdict
    from xgae.utils.setup_env import setup_logging

    setup_logging()

    async def main():
        ## Before Run Exec: uv run example-fault-tools
        mcp_tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        #mcp_tool_box = XGAMcpToolBox()

        task_id = "task1"
        await mcp_tool_box.load_mcp_tools_schema()
        await mcp_tool_box.creat_task_tool_box(task_id=task_id, general_tools=["*"], custom_tools=["*"])
        tool_schemas = mcp_tool_box.get_task_tool_schemas(task_id, "general")
        print("general_tools_schemas" + "*"*50)
        for tool_schema in tool_schemas:
            print(asdict(tool_schema))
        print()

        tool_schemas = mcp_tool_box.get_task_tool_schemas(task_id, "custom")
        print("custom_tools_schemas" + "*" * 50)
        for tool_schema in tool_schemas:
            print(asdict(tool_schema))
        print()

        result = await mcp_tool_box.call_tool(task_id=task_id, tool_name="complete", args={"task_id": task_id})
        print(f"call complete result: {result}")

        await mcp_tool_box.destroy_task_tool_box(task_id)

    asyncio.run(main())