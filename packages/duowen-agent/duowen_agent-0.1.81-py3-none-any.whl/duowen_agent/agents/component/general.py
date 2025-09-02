from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string


class SimpleTranslateResult(BaseModel):
    target: str = Field(description="译文")


class SimpleTranslate(BaseComponent):

    def __init__(
        self, llm, original: str = "英文", target: str = "中文", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.llm = llm
        self.original = original
        self.target = target

    def build(self):
        return GeneralPromptBuilder(
            instruction=f"将{self.original}文本准确翻译为{self.target}，并按照指定JSON格式返回结果。",
            output_format=SimpleTranslateResult,
            sample="""
输入：文本原文
输出：
```json
{"target":"译文"}
```
""",
            note="""
- 若输入含换行符，译文保持相同段落结构
- 不翻译编程代码（仅处理自然语言）
- 禁止添加额外解释或说明文字""",
        )

    def run(self, text: str) -> str:
        _prompt = self.build().get_instruction(f"输入：{text}")
        _result = stream_to_string(self.llm.chat_for_stream(_prompt))
        return json_observation(_result, SimpleTranslateResult).target
