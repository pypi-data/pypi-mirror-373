import json
from typing import List, Optional, Union

from duowen_agent.agents.base import BaseToolResult
from duowen_agent.error import ToolError
from duowen_agent.tools.base import BaseTool


class ToolManager:
    """ToolManager helps Agent to manage tools"""

    def __init__(self, tools: List[BaseTool], filter_function_list: List[str] = None):
        self.tools: List[BaseTool] = tools
        self.filter_function_list = filter_function_list

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Find specified tool by tool name.
        Args:
            tool_name(str): The name of the tool.

        Returns:
            Optional[BaseTool]: The specified tool or None if not found.
        """
        return next((tool for tool in self.tools if tool.name == tool_name), None)

    def run_tool(
        self, tool_name: str, parameters: Union[str, dict]
    ) -> BaseToolResult | str | int | float:
        """Run tool by input tool name and data inputs

        Args:
            tool_name(str): The name of the tool.
            parameters(Union[str, dict]): The parameters for the tool.

        Returns:
            str: The result of the tool.
            Any: 结构化数据用于页面展示
        """
        tool = self.get_tool(tool_name)

        if tool is None:
            return (
                f"{tool_name} has not been provided yet, please use the provided tool."
            )

        if isinstance(parameters, dict):
            data = tool.run(**parameters)
        else:
            data = tool.run(parameters)

        if data:
            return data
        else:
            raise ToolError(f"Tool {tool_name} has no return value.")

    @property
    def tool_names(self) -> str:
        """Get all tool names."""
        tool_names = ""
        for tool in self.tools:
            tool_names += f"{tool.name}, "
        return tool_names[:-2]

    @property
    def tool_classifiers(self) -> dict[str, str]:
        _classifiers = {}
        if self.filter_function_list:
            for tool in self.tools:
                if tool.name in self.filter_function_list:
                    _classifiers[tool.name] = tool.description
        else:
            for tool in self.tools:
                _classifiers[tool.name] = tool.description
        return _classifiers

    @property
    def tool_descriptions(self) -> str:
        """Get all tool descriptions, including the schema if available."""
        tool_descriptions = ""
        if self.filter_function_list:
            for tool in self.tools:
                if tool.name in self.filter_function_list:
                    tool_descriptions += (
                        json.dumps(
                            tool.to_schema(),
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        else:
            for tool in self.tools:
                tool_descriptions += (
                    json.dumps(
                        tool.to_schema(),
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return tool_descriptions
