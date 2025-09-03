import json
import datetime

from typing import Optional, List

from xgae.engine.engine_base import XGAToolSchema
from xgae.utils.misc import read_file, format_file_with_args


class XGAPromptBuilder():
    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt

    def build_task_prompt(self,
                          model_name: str,
                          general_tool_schemas: List[XGAToolSchema],
                          custom_tool_schemas: List[XGAToolSchema],
                          agent_tool_schemas: List[XGAToolSchema])-> str:
        if self.system_prompt is None:
            self.system_prompt = self._load_default_system_prompt(model_name)

        task_prompt = self.system_prompt

        tool_prompt = self.build_general_tool_prompt(general_tool_schemas)
        task_prompt = task_prompt + "\n" + tool_prompt

        tool_prompt = self.build_custom_tool_prompt(custom_tool_schemas)
        task_prompt = task_prompt + "\n" + tool_prompt

        tool_prompt = self.build_agent_tool_prompt(agent_tool_schemas)
        task_prompt = task_prompt + "\n" + tool_prompt

        return task_prompt

    def build_general_tool_prompt(self, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = ""
        tool_schemas = tool_schemas or []
        if len(tool_schemas) > 0:
            tool_prompt = read_file("templates/general_tool_prompt_template.txt")
            example_prompt = ""
            openai_schemas = []
            for tool_schema in tool_schemas:
                openai_schema = {}
                openai_function = {}
                openai_schema['type'] = "function"
                openai_schema['function'] = openai_function

                openai_function['name'] = tool_schema.tool_name
                openai_function['description'] = tool_schema.description if tool_schema.description else 'No description available'
                openai_parameters = {}
                openai_function['parameters'] = openai_parameters

                input_schema = tool_schema.input_schema
                openai_parameters['type']       = input_schema['type']
                openai_parameters['properties'] = input_schema.get('properties', {})
                openai_parameters['required']   = input_schema['required']

                openai_schemas.append(openai_schema)

                metadata = tool_schema.metadata or {}
                example = metadata.get("example", None)
                if example:
                    example_prompt += f"\n{example}\n"

            schema_prompt = json.dumps(openai_schemas, ensure_ascii=False, indent=2)
            tool_prompt = tool_prompt.format(tool_schemas=schema_prompt, tool_examples=example_prompt)
        return tool_prompt


    def build_custom_tool_prompt(self, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = self.build_mcp_tool_prompt("templates/custom_tool_prompt_template.txt", tool_schemas)
        return tool_prompt

    def build_agent_tool_prompt(self, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = self.build_mcp_tool_prompt("templates/agent_tool_prompt_template.txt", tool_schemas)
        return tool_prompt

    def build_mcp_tool_prompt(self, file_path: str, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = ""
        tool_schemas = tool_schemas or []
        if len(tool_schemas) > 0:
            tool_prompt = read_file(file_path)
            tool_info = ""
            for tool_schema in tool_schemas:
                description = tool_schema.description if tool_schema.description else 'No description available'
                tool_info += f"- **{tool_schema.tool_name}**: {description}\n"
                parameters = tool_schema.input_schema.get('properties', {})
                tool_info += f"  Parameters: {parameters}\n"
            tool_prompt = tool_prompt.replace("{tool_schemas}", tool_info)

        return tool_prompt

    def _load_default_system_prompt(self, model_name) -> Optional[str]:
        if "gemini-2.5-flash" in model_name.lower() and "gemini-2.5-pro" not in model_name.lower():
            system_prompt_template = read_file("templates/gemini_system_prompt_template.txt")
        else:
            system_prompt_template = read_file("templates/system_prompt_template.txt")

        system_prompt = format_file_with_args(system_prompt_template, {"datetime": datetime})

        system_prompt = system_prompt.format(
            current_date=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
            current_time=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),
            current_year=datetime.datetime.now(datetime.timezone.utc).strftime('%Y')
        )

        if "anthropic" not in model_name.lower():
            sample_response = read_file("templates/system_prompt_response_sample.txt")
            system_prompt = system_prompt + "\n\n <sample_assistant_response>" + sample_response + "</sample_assistant_response>"

        return system_prompt


