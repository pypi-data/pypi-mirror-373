import json
from typing import Any

import pydantic
from duowen_agent.tools.base import BaseTool
from pydantic import BaseModel, Field

from .base import BaseComponent


class Parameters(BaseModel):
    content: str = Field(..., description="输入内容")


class ComponentToolWrapper(BaseTool):
    """A tool for human feedback"""

    name: str = "ComponentToolWrapper"
    description: str = "ComponentToolWrapper"
    parameters: BaseModel = Parameters

    def __init__(
        self,
        component: BaseComponent,
        name: str,
        description: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.description = description
        self.component = component

    def _run(self, content: Any) -> str:
        data = self.component.run(content)
        if isinstance(data, str):
            return data
        elif isinstance(data, pydantic.BaseModel):
            return json.dumps(data.model_dump(), ensure_ascii=False, indent=2)
        else:
            return str(data)
