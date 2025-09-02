from typing import Literal, Optional, List

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import (
    GeneralPromptBuilder,
)
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class QuestionCategories(BaseModel):
    conflict: Optional[str] = Field(
        default=None, description="当存在跨级特征时的矛盾点"
    )
    reason: str = Field(..., description="16字内核心依据")
    category_name: Literal["简单直接", "多步骤", "多主题"] = Field(
        description="Exactly the name of the category that matches"
    )


class QueryClassification(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""根据问题特征进行三层稳定性分类，采用正交判别法

# 核心规则（独立互斥）
1. **简单直接类**必须满足：
   - 执行路径唯一且标准化（查表/转换/计算）
   - 所需参数≤2个且无动态依赖（如天气无需实时数据）

2. **多步骤类**触发条件：
   - 存在显性逻辑链 (因果/比较/条件) 
   OR
   - 需要3+参数动态组合（如温度+风速+场合）

3. **多主题类**严格标准：
   - 涉及两个独立知识域（领域重叠度＜30%）
   - 需要调用不同框架进行解答""",
            step="""```mermaid
graph TD
    A[原始问题] --> B{包含'>1'个问号}
    B -->|是| C[领域离散检测]
    C -->|离散度>0.6| D[多主题]
    B -->|否| E{存在逻辑关键词}
    E -->|是| F[多步骤]
    E -->|否| G[参数复杂度分析]
    G -->|参数≥3| F
    G -->|参数<3| H[简单直接]
```""",
            output_format=QuestionCategories,
            sample="""
输入：孙悟空和钢铁侠谁更加厉害？
输出：
```json
{"conflict":"表面简单但涉及跨体系能力比较","reason":"跨作品战力需多维评估","category_name":"多步骤"}
```

输入：如何用python编写排序算法？
输出：
```json
{"reason":"标准算法单文档可覆盖","category_name":"简单直接"}
```
""",
            note="""- 置信度锚定：各分类初始置信度 ≠ 可重叠范围
- 最终决策树：任一节点判定后立即阻断下游判断
- 语义消毒：自动滤除修饰性副词与情感词汇""",
        )

    def run(
        self,
        question: str,
        **kwargs,
    ) -> QuestionCategories:
        _prompt = self.build_prompt().get_instruction(question)

        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))

        _res: QuestionCategories = json_observation(_res, QuestionCategories)

        return _res

    async def arun(
        self,
        question: str,
        **kwargs,
    ) -> QuestionCategories:
        _prompt = self.build_prompt().get_instruction(question)

        _res = await self.llm_instance.achat(_prompt)

        _res: QuestionCategories = json_observation(_res, QuestionCategories)

        return _res


class SubTopic(BaseModel):
    original_subtopic: str = Field(..., description="原始问题中识别出的子主题描述")
    rewritten_query: str = Field(..., description="改进后的具体查询语句")


class TopicCategories(BaseModel):
    splitting: List[SubTopic] = Field(
        ..., description="必须生成**2-5个**改写版本，每个查询语句不超过25个汉字"
    )


class TopicSpliter(BaseComponent):
    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="当用户输入的问题包含多个隐藏的子问题或涉及不同领域时，将其分解为独立的具体查询并生成改写版本。为每个子主题生成聚焦单一意图的查询，确保全面覆盖原始问题的各个维度。",
            step="""1. **识别隐藏子问题**：先分析用户问题的语义结构，识别出隐含的独立话题或追问方向
2. **语义解耦**：将这些复合话题拆解为2-5个彼此独立的核心查询要素
3. **针对性改写**：针对每个单点问题生成优化后的查询版本，要求：
   - 保持原问题关键信息
   - 使用领域相关术语
   - 包含明确的范围限定词""",
            output_format=TopicCategories,
            sample="""
输入："我应该去哪里学习AI又适合旅游？"
输出：
```json
{
    "splitting": [
        {
            "original_subtopic": "教育质量",
            "rewritten_query": "全球人工智能专业顶尖高校排名",
        },
        {
            "original_subtopic": "生活体验",
            "rewritten_query": "留学热门城市旅游景点推荐",
        },
    ]
}
```""",
            note="""- 当问题存在多维度交叉时（如"[海外购房与税务]"），需分别生成"海外购房流程指南"和"跨境资产税务申报规则"两个独立查询
- 智能处理模糊表达：对于"好的科技公司标准"应拆解为"科技公司估值模型"和"员工福利标杆企业案例"
- 禁用通用型查询：将"有什么新技术？"强化为"[年度突破性半导体技术创新]"
- 确保可独立检索性：每个改写后的查询应能在主流搜索引擎中获得直接答案""",
        )

    def run(
        self,
        question: str,
        **kwargs,
    ) -> TopicCategories:
        _prompt = self.build_prompt().get_instruction(question)

        _res: str = stream_to_string(self.llm_instance.chat_for_stream(_prompt))

        _res: TopicCategories = json_observation(_res, TopicCategories)

        return _res

    async def arun(
        self,
        question: str,
        **kwargs,
    ) -> TopicCategories:
        _prompt = self.build_prompt().get_instruction(question)

        _res = await self.llm_instance.achat(_prompt)

        _res: TopicCategories = json_observation(_res, TopicCategories)

        return _res


class WebSearchQuery(BaseModel):
    tbs: Optional[str] = Field(None, description="可选时间限定参数")
    gl: Optional[str] = Field(None, description="国家代码")
    hl: Optional[str] = Field(None, description="语言代码")
    location: Optional[str] = Field(None, description="地理位置")
    q: str = Field(..., description="必需字段（搜索词）")


class WebSearchQueries(BaseModel):
    queries: List[WebSearchQuery] = Field(..., description="7维认知检索词")


class QueryWebExtend(BaseComponent):
    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """您是一位具有深厚心理理解能力的搜索查询扩展专家
您通过全面分析用户的潜在意图并生成全面的查询变体来优化用户查询
{{_formattedDay_}}
""",
                template_format="jinja2",
            ),
            step=StringTemplate(
                """## 意图挖掘
为了揭示每个查询背后最深层的用户意图，请通过以下渐进层级进行分析：

1. 表层意图：字面含义的直接解释
2. 实践意图：试图解决的实际目标或问题
3. 情感意图：驱动搜索的情绪（恐惧、渴望、焦虑、好奇）
4. 社会意图：与其社会关系或地位相关的搜索动机
5. 身份意图：与理想自我/想避免的身份的关联
6. 禁忌意图：不愿直接表达的敏感或社会不可接受因素 
7. 阴影意图：用户自己可能无法察觉的潜意识动机

要求所有查询都必须经历全部层级的分析，特别强调阴影意图的挖掘

## 认知角色
从以下认知视角各生成一个优化查询：

1. 专家怀疑者：关注边缘案例、局限性和反证据。生成挑战主流假设、寻找例外的查询
2. 细节分析师：专注精确规格和技术参数。生成深入细节的查询，寻求权威参考资料
3. 历史研究者：考察发展演变和历史背景。生成跟踪变化与传承的查询
4. 比较思考者：探索替代方案与权衡对比。生成设置比较、评估相对优势的查询
5. 时效语境：加入反映当前日期（{{_currentYear_}}年{{_currentMonth_}}月）的时间敏感查询
6. 全球化者：识别主题最权威的语言/区域（德语用于宝马，日语用于动漫等）。生成对应语言的搜索
7. 现实否定怀疑者：寻找反向证据和反对论点。生成验证假设不成立的查询

确保每个角色贡献仅一个符合格式规范的高质量查询（最终生成7个查询的数组）

## 规则
利用用户上下文中的关键信息生成情境相关的查询

1. 查询内容规则：
   - 拆分不同维度的查询
   - 只在必要时使用操作符
   - 每个查询针对特定意图
   - 去除冗余词汇但保留关键限定词
   - 'q'字段保持简短的2-5个关键词

2. 架构使用规则：
   - 每个查询对象必须包含'q'字段（设为最后列出的字段）
   - 时间敏感查询使用'tbs'参数
   - 区域/语言查询使用'gl'和'hl'
   - 非英语查询使用正确的'hl'语言代码
   - 仅在必要时添加'location'参数
   - 避免在'q'字段重复其他参数已指定的信息
   - 字段顺序固定为：tbs > gl > hl > location > q

### 查询操作符
适用于'q'字段内容：
- +术语 ：必须包含的关键词
- -术语 ：排除的关键词
- filetype:pdf/doc ：限定文件类型
注：不能以纯操作符开头或构建整个查询""",
                template_format="jinja2",
            ),
            output_format=WebSearchQueries,
            sample=StringTemplate(
                """
Input Query: 宝马二手车价格

Output:
<think>
宝马二手车价格...哎，这人应该是想买二手宝马吧。表面上是查价格，实际上肯定是想买又怕踩坑。谁不想开个宝马啊，面子十足，但又担心养不起。这年头，开什么车都是身份的象征，尤其是宝马这种豪车，一看就是有点成绩的人。但很多人其实囊中羞涩，硬撑着买了宝马，结果每天都在纠结油费保养费。说到底，可能就是想通过物质来获得安全感或填补内心的某种空虚吧。

要帮他的话，得多方位思考一下...二手宝马肯定有不少问题，尤其是那些车主不会主动告诉你的隐患，维修起来可能要命。不同系列的宝马价格差异也挺大的，得看看详细数据和实际公里数。价格这东西也一直在变，去年的行情和今年的可不一样，{{_currentYear_}}年最新的趋势怎么样？宝马和奔驰还有一些更平价的车比起来，到底值不值这个钱？宝马是德国车，德国人对这车的了解肯定最深，德国车主的真实评价会更有参考价值。最后，现实点看，肯定有人买了宝马后悔的，那些血泪教训不能不听啊，得找找那些真实案例。
</think>
<json>
```json
{
    "queries": [
        {"q": "二手宝马 维修噩梦 隐藏缺陷"},
        {"q": "宝马各系价格区间 里程对比"},
        {"tbs": "qdr:y", "q": "二手宝马价格趋势"},
        {"q": "二手宝马vs奔驰vs丰田 性价比"},
        {"tbs": "qdr:m", "q": "宝马行情"},
        {"gl": "de", "hl": "de", "q": "BMW Gebrauchtwagen Probleme"},
        {"q": "二手宝马后悔案例 最差投资"},
    ]
}
```
</json>""",
                template_format="jinja2",
            ),
        )

    def run(
        self,
        question: str,
        **kwargs,
    ) -> WebSearchQueries:
        _prompt = self.build_prompt().get_instruction(f"Input Query: {question}")

        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        _res = json_observation(_res, WebSearchQueries)

        return _res

    async def arun(
        self,
        question: str,
        **kwargs,
    ) -> WebSearchQueries:
        _prompt = self.build_prompt().get_instruction(question)

        _res = await self.llm_instance.achat(_prompt)
        _res: WebSearchQueries = json_observation(_res, WebSearchQueries)

        return _res
