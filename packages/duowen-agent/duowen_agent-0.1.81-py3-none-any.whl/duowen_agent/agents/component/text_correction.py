from typing import List, Optional

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string


class Edits(BaseModel):
    pos: int = Field(..., description="起始字符位置")
    src: str = Field(..., description="原字符")
    tgt: str = Field(..., description="修正字符")
    spelling: str = Field(..., description="形态校验结论")


class Correction(BaseModel):
    source: str = Field(default=None, description="原始文本内容")
    edits: Optional[List[Edits]] = Field(..., description="无修改记录保持空数组状态")
    target: str = Field(default=None, description="完整修正文本")


class TextCorrection(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""对文本进行规范化处理并生成标准格式的修正结果

将输入文本进行语法成分分析和错误模式匹配，严格按照技术要求执行多维度文本校验。处理流程包含句法树构建→语义角色标注→错误模式匹配三个阶段，最后输出包含字符级修改记录的标准化数据结构。

处理要求：
1. 断言式错误验证：每个修改需通过词性匹配、词语搭配验证、语义连贯性检测三重校验
2. 采用UTF-16字符编码体系进行精确位置标定
3. 对混淆词进行音形码双重对比（基于拼音首字母与笔画结构相似度）""",
            output_format=Correction,
            sample="""输入文本："今天我门去参观了故宫搏物院"
修正输出：
```json
{
    "source": "今天我门去参观了故宫搏物院",
    "edits": [
        {
            "pos": 3,
            "src": "门",
            "spelling":"形近混淆（缺亻旁）",
            "tgt": "们"
        },
        {
            "pos": 11,
            "src": "搏",
            "spelling":"部首错误（扌→十）",
            "tgt": "博"
        },
    ],
    "target": "今天我们去了参观故宫博物院",
}
```""",
            note="""1. 上下文字段需去除标点后截取有效内容
2. 合并连续修改点时应进行位置偏移量补偿计算
3. 对唐诗宋词等古典文本自动启用文言文处理模式
4. 修正结果必须与原始输入严格字面一致（包括标点符号的保留）""",
        )

    def run(
        self,
        question: str,
        **kwargs,
    ) -> Correction:
        _prompt = self.build_prompt().get_instruction(question)

        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))

        _res: Correction = json_observation(_res, Correction)

        return _res

    async def arun(
        self,
        question: str,
        **kwargs,
    ) -> Correction:
        _prompt = self.build_prompt().get_instruction(question)

        _res = await self.llm_instance.achat(_prompt)

        _res: Correction = json_observation(_res, Correction)

        return _res
