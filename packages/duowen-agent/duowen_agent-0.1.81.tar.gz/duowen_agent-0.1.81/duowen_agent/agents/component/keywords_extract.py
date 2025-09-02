from typing import List

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class Keywords(BaseModel):
    keywords: List[str] = Field(description="提取的中/英文关键词列表")


class KeywordExtract(BaseComponent):
    """
    关键词抽取，用于提升全文或向量检索的泛化能力
    """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="根据问题内容提取中/英文关键词，结合资料库语言习惯扩展相关概念，用于文本匹配检索",
            step=StringTemplate(
                """1. 分析句子核心语义，识别关键实体、行为、属性和关联对象
2. 拆分复合词为独立语义单元（如环境污染控制→环境污染/控制）
3. 补充专业术语、同义词、具体实例等关联概念
4. 英文内容优先保留原词，必要情况增加缩写形式
5. 人工概念判断优先于机械分词，保留完整术语
6. 5-{{num}}个精准关键词（宁缺毋滥）""",
                template_format="jinja2",
            ),
            output_format=Keywords,
            sample="""输入：如何评估企业数字化转型对员工生产力的影响

输出:
```json
{
    "keywords": ["数字化转型","生产力分析","组织变革","办公效率","员工培训","数字化工具","KPI评估","远程办公","流程自动化","人机协作",...]
}
```

""",
            note="""- 名词词组控制在4字以内，动词词组3字以内
- 人名机构名保持完整（如世界卫生组织不拆分）
- 数字组合保留原格式（5G/30%减排）
- 排除助词、介词等非实义词
- 带注音专业词汇保持完整（CRISPR-Cas9/F22战机）
""",
        )

    def run(self, question: str, num: int = 10) -> List[str]:

        _prompt = self.build_prompt().get_instruction(
            user_input=f"输入: {question}",
            temp_vars={"num": num},
        )
        res1 = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        res: Keywords = json_observation(res1, Keywords)
        return res.keywords

    async def arun(self, question: str, num: int = 10) -> List[str]:

        _prompt = self.build_prompt().get_instruction(
            user_input=f"输入: {question}",
            temp_vars={"num": num},
        )
        res1 = await self.llm_instance.achat(_prompt)
        res: Keywords = json_observation(res1, Keywords)
        return res.keywords


class CentralWord(BaseModel):
    analysis: str = Field(..., description="50字内简要说明选择依据")
    core_term: List[str] = Field(description="提取的中心词")
    backup_options: List[str] = Field(description="候选词")


class CentralWordExtract(BaseComponent):
    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="根据输入的文本内容，精准识别并提取最核心的中心词。中心词应为能够概括文本主旨或关键信息的单个词语或短语，要求简洁、准确且具有代表性。",
            step="""1. **解析语义意图**：分析文本的核心表达意向和情感倾向
2. **识别关键元素**：
   - 定位高频重复的关键概念
   - 识别文本结构中的主干成分（主语/谓语/核心宾语）
   - 捕捉强调句式中的重点对象
3. **关系网络建模**：
   - 构建词项间的语义关联图谱
   - 计算节点中心度（介数中心性/接近中心性）
4. **跨维度验证**：
   - 核对主题一致性
   - 验证信息覆盖率
   - 确保可脱离语境独立表意""",
            output_format=CentralWord,
            sample="""输入："量子计算正在引发新一轮科技革命，其超强算力将重塑人工智能、药物研发等多个领域的发展格局"

输出：
```json
{
  "analysis": "文本围绕量子计算的技术特性及其行业影响展开，其他候选词均为该核心术语的衍生属性或应用场景"
  "core_term": ["量子计算"],
  "backup_options": ["科技革命", "超强算力"]
  
}
```""",
            note="""1. 专业术语场景需保持原词完整性（如"区块链"优于"链式技术"）
2. 隐喻性表达需还原本体（如"数字黄金"应转换为"比特币"）
3. 多中心场景按顺序优先原则标注（主要中心词+逗号分隔的次要中心词）""",
        )

    def run(self, question: str) -> CentralWord:
        _prompt = self.build_prompt().get_instruction(question)
        res1: str = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        res: CentralWord = json_observation(res1, CentralWord)
        return res

    async def arun(self, question: str) -> CentralWord:
        _prompt = self.build_prompt().get_instruction(question)
        res1 = await self.llm_instance.achat(_prompt)
        res: CentralWord = json_observation(res1, CentralWord)
        return res
