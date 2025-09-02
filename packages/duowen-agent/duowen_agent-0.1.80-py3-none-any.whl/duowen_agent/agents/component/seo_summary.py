from typing import List

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class Abstract(BaseModel):
    title: str = Field(..., description="文章标题")
    keywords: List[str] = Field(
        ..., description='["关键词1", "关键词2", "同义词1", "相关短语1",...]'
    )
    entity: List[str] = Field(
        ...,
        description='["人名","组织名","地点","时间表达式","产品","事件",...]',
    )
    abstract: str = Field(..., description="150-200字的摘要，逻辑清晰，简明扼要")


class SeoSummary(BaseComponent):
    """
    备选

    为搜索引擎优化撰写结构化摘要，完整涵盖语义要素与实体信息，严格遵循输出格式要求

    根据文章内容执行以下处理流程：
    1. 主题精炼：解析文本构建三级主题框架（核心论点>支撑证据>补充说明）
    2. 语义解构：
       - 关键词库：包含基础术语+长尾变体+领域黑话（数量8-12个）
       - 实体图谱：区分实体类型并标注权重（人物/机构[★] > 事件/产品[★★] > 概念/技术[★★★]）
    3. 摘要生成：
       - 前导段落必须包含核心实体与加权关键词
       - 语义链长度控制在3-4个SVO结构（主谓宾）
       - 文末设置语义锚点呼应主题框架

    # 输出格式
    {
      "abstract": "首句包含[核心实体]与[★★级关键词]，采用「现象陈述→成因分析→影响预测」结构。第二句嵌入[长尾变体]与[★级实体]。末尾设置[语义锚点]呼应主题，190±5字符",
      "entity": {
        "Person/Org": ["[首席执行官]", "[创新实验室]"],
        "Event/Product": ["[产品发布会]", "[智能终端]"],
        "Concept/Tech": ["[神经网络]", "[分布式计算]"]
      },
      "keywords": {
        "Core": ["语义搜索", "检索优化"],
        "Extension": ["SEO策略", "搜索可见性提升"]
      },
      "title": "核心实体+最高频关键词+动态动词结构（例：《[智能终端]如何通过[神经网络]重构[搜索可见性]新范式》）"
    }

    # 示例参考
    输入文章：
    "Meta近日公布神经搜索框架NSP的最新进展，该技术融合图神经网络与语义矢量化模型，可提升长尾query匹配精度..."

    输出：
    {
      "abstract": "Meta神经搜索框架NSP通过融合图神经网络与语义矢量化模型，显著提升长尾查询匹配精度。该框架在电商搜索场景实现30%的相关性提升，由FAIR实验室联合沃尔玛技术团队共同验证。此项突破标志着语义检索正式进入动态表征时代。",
      "entity": {
        "Person/Org": ["Meta", "FAIR实验室", "沃尔玛技术团队"],
        "Event/Product": ["神经搜索框架NSP"],
        "Concept/Tech": ["图神经网络", "语义矢量化模型", "动态表征"]
      },
      "keywords": {
        "Core": ["神经搜索", "长尾查询"],
        "Extension": ["语义检索优化", "动态表征技术"]
      },
      "title": "神经搜索框架NSP如何重塑电商语义检索新标准"
    }

    # 注意事项
    1. 实体权重判定原则：直接影响业务收益的实体标★，技术组件标★★，行业概念标★★★
    2. 关键词变异规则：对核心术语进行「技术黑话+学术命名+通俗表述」三维拓展
    3. 严格禁止：JSON输出不得包含```代码块标记，实体分类错误视为重大缺陷
    4. 语义锚点要求：必须使用「标志着」「意味着」「引发」等转折连词承接影响分析
    """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="围绕文章内容高效生成符合SEO规范的摘要文本。通过主题提炼、关键词嵌入和语义扩展技术优化搜索引擎可见性，确保信息准确性与可读性平衡。",
            step="""1. 主题分析： 阅读文章，确定主题和核心信息，将其总结为一句简洁描述。
2. 关键词提取： 仔细阅读文章，提取最重要的关键词。
3. 实体提取: 仔细阅读文章，提取最重要的关键实体，如人名、组织名、地点、时间表达式、产品、事件等。
4. 初稿编写： 基于关键词、实体和核心信息，编写150-200字的初稿摘要。
5. 关键词和实体融入： 确保摘要包含所有重要关键词和实体，保持自然流畅，避免堆砌。
6. 语义扩展： 使用同义词或相关短语替代部分关键词，提升语义覆盖面。""",
            output_format=Abstract,
            sample="""
```json
{
  "title": "文章标题 or 自行总结",
  "entity": ["人名","组织名","地点","时间表达式","产品","事件",...],
  "keywords": ["关键词1", "关键词2", "同义词1", "相关短语1",...],
  "abstract": "150-200字的摘要，逻辑清晰，简明扼要"
}
```
""",
        )

    def run(
        self,
        question: str,
        **kwargs,
    ) -> Abstract:
        _prompt = self.build_prompt().get_instruction(question)

        _res: str = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        _res: Abstract = json_observation(_res, Abstract)

        return _res

    async def arun(
        self,
        question: str,
        **kwargs,
    ) -> Abstract:
        _prompt = self.build_prompt().get_instruction(question)

        _res = await self.llm_instance.achat(_prompt)
        _res: Abstract = json_observation(_res, Abstract)

        return _res


class Questions(BaseModel):
    questions: List[str] = Field(..., description="问题列表")


class QuestionsExtract(BaseComponent):
    """
    面向搜索引擎的文章摘要
    """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """根据提供的文本知识，列举能够被准确回答的{topn}个问题，确保完全覆盖知识内容且每个问题的答案都能在知识中找到对应信息。问题需要具体明确，形式应为问句，并以JSON数组格式输出。"""
            ),
            step="""- 仔细分析知识中的每个要点，包括但不限于概念定义、特征、分类、步骤、因果关系等
- 每个问题应针对知识点中的独立信息块
- 避免重复或语义近似的问题
- 问题表述应采用自然的口语化问法
""",
            output_format=Questions,
            sample="""```json
{
  "questions": [
    "什么是[核心概念]？", 
    "[具体步骤]包含哪些阶段？",
    "[特定方法]的优缺点有哪些？",
    "[概念A]与[概念B]有什么区别？"
    ...
  ]
}
```""",
            note=StringTemplate(
                """- 字段值必须严格使用问答形式的中文疑问句
- 禁止包含知识中未提及的内容
- 禁止问题间存在前后逻辑依赖或术语省略
- JSON必须合法可直接解析，不使用换行符
- 若知识包含专业术语，需确保生成对应的问题术语与原词完全一致
- 时间序列要素须保留原始顺序表述
- 量词需与知识原文中的数量描述精确对应
- 禁止出现"这些"、"它"、"该"等指代性表述
- 总数量严格限制为{topn}个"""
            ),
        )

    def run(
        self,
        question: str,
        top_n: int = 3,
        **kwargs,
    ) -> List[str]:
        _prompt = self.build_prompt().get_instruction(
            question,
            temp_vars={"topn": top_n},
        )

        _res: str = stream_to_string(self.llm_instance.chat_for_stream(_prompt))

        _res: Questions = json_observation(_res, Questions)

        return _res.questions

    async def arun(
        self,
        question: str,
        top_n: int = 3,
        **kwargs,
    ) -> List[str]:
        _prompt = self.build_prompt().get_instruction(
            question,
            temp_vars={"topn": top_n},
        )

        _res = await self.llm_instance.achat(_prompt)

        _res: Questions = json_observation(_res, Questions)

        return _res.questions


if __name__ == "__main__":
    SeoSummary.build_prompt()
    QuestionsExtract.build_prompt()
