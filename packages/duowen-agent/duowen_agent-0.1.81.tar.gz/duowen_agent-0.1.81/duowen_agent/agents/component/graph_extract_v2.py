import json
from typing import List, Optional
from typing import Literal, Type

from pydantic import BaseModel, Field, conint
from pydantic import create_model

from duowen_agent.agents.component.base import BaseLLMComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import (
    stream_to_string,
)
from duowen_agent.utils.string_template import StringTemplate

DEFAULT_ENTITY_TYPES_CONFIG = {
    "Person": "真实或虚构的人物，包括历史人物、现代人物、文学角色等",
    "Organization": "公司、政府机构、团队、学校等组织实体",
    "Location": "地理位置、地标、国家、城市等",
    "Date": "日期、时间段、年代等时间相关信息",
    "Event": "事件、会议、节日、历史事件等",
    "Work": "书籍、电影、音乐、艺术作品等创作内容",
    "Product": "商品、服务、品牌等商业产品",
    "Resource": "自然资源、信息资源、工具等",
    "Concept": "抽象概念、思想、理论等",
    "Category": "分类、类别、领域等",
    "Operation": "操作、动作、方法、过程等",
}


class Entity(BaseModel):
    entity_type: str = Field(description="实体类型")
    entity_name: str = Field(description="实体名称")
    entity_description: str = Field(description="实体描述")


class Entities(BaseModel):
    entities: Optional[List[Entity]] = Field(description="从文本中识别出的所有实体列表")

    def add_entity(self, entity: Entity):
        _entities_name = [i.entity_name for i in self.entities]
        if entity.entity_name not in _entities_name:
            self.entities.append(entity)


def create_dynamic_entity_model(entity_config: dict[str, str]) -> Type[BaseModel]:
    entity_type_keys = list(entity_config.keys())
    entity_types_literal = Literal[tuple(entity_type_keys)]
    entity_type_descriptions = "\n".join(
        [f"- `{key}`: {desc}" for key, desc in entity_config.items()]
    )
    entity_type_field_description = (
        f"实体的类型。必须是以下之一：\n{entity_type_descriptions}"
    )

    _DynamicEntity = create_model(
        "Entity",
        entity_type=(
            entity_types_literal,
            Field(description=entity_type_field_description),
        ),
        entity_name=(str, Field(description="实体的唯一名称")),
        entity_description=(str, Field(description="对这个具体实体的详细描述")),
    )

    _DynamicEntities = create_model(
        "Entities",
        entities=(
            List[_DynamicEntity],
            Field(description="从文本中识别出的所有实体列表"),
        ),
    )

    return _DynamicEntities


class EntityExtract(BaseLLMComponent):

    def __init__(
        self,
        llm_instance: BaseAIChat,
        entity_config: dict[str, str] = None,
        max_gleanings: int = 2,
        retry_cnt: int = 3,
        retry_sleep: int = 3,
        *args,
        **kwargs,
    ):
        super().__init__(llm_instance, retry_cnt, retry_sleep, *args, **kwargs)
        self.max_gleanings = max_gleanings
        self.entity_config = entity_config or DEFAULT_ENTITY_TYPES_CONFIG
        self.entities = Entities(entities=[])
        self.continue_prompt = "MANY entities were missed in the last extraction.  Add them below using the same format:\n"
        self.if_loop_prompt = "It appears some entities may have still been missed. Answer Y if there are still entities that need to be added, or N if there are none. Please answer with a single letter Y or N.\n"

    def build_prompt(self) -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """用户提供的文本中，提取所有符合以下实体类型的实体：
EntityTypes: [{{EntityTypes}}]

## 实体提取规则
{{EntityList}}""",
                template_format="jinja2",
            ),
            step="""1. 仔细阅读文本，识别可能的实体
2. 对每个识别到的实体，确定其最适合的实体类型（必须从EntityTypes中选择）
3. 为每个实体创建包含以下字段的JSON对象：
   - title: 实体的标准名称，不包含修饰词，如引号等
   - type: 从EntityTypes中选择的实体类型
   - description: 对该实体的简明中文描述，应基于文本内容
4. 验证每个实体的所有字段是否正确且格式化恰当
5. 将所有实体对象合并为一个JSON数组
6. 检查最终JSON是否有效并符合要求""",
            output_format=create_dynamic_entity_model(self.entity_config),
            sample="""[输入]
EntityTypes: [Person, Organization, Location, Product, Event, Date, Work, Concept, Resource, Category, Operation]
文本： 《红楼梦》，又名《石头记》，是清代作家曹雪芹创作的中国古典四大名著之一，被誉为中国封建社会的百科全书。该书前80回由曹雪芹所著，后40回一般认为是高鹗所续。小说以贾、史、王、薛四大家族的兴衰为背景，以贾宝玉、林黛玉和薛宝钗的爱情悲剧为主线，刻画了以贾宝玉和金陵十二钗为中心的正邪两赋、贤愚并出的高度复杂的人物群像。成书于乾隆年间（1743年前后），是中国文学史上现实主义的高峰，对后世影响深远。

[输出]
```json
{
    "entities": [
        {
            "entity_name": "红楼梦",
            "entity_type": "Work",
            "entity_description": "红楼梦是清代作家曹雪芹创作的中国古典四大名著之一，被誉为中国封建社会的百科全书",
        },
        {
            "entity_name": "石头记", 
            "entity_type": "Work", 
            "entity_description": "石头记是红楼梦的别名"
        },
        {
            "entity_name": "曹雪芹",
            "entity_type": "Person",
            "entity_description": "曹雪芹是清代作家，红楼梦的作者，创作了前80回",
        },
        {
            "entity_name": "高鹗",
            "entity_type": "Person",
            "entity_description": "高鹗是红楼梦后40回的续作者",
        },
        {
            "entity_name": "贾宝玉",
            "entity_type": "Person",
            "entity_description": "贾宝玉是红楼梦中的主要角色，爱情悲剧的主角之一",
        },
        {
            "entity_name": "林黛玉",
            "entity_type": "Person",
            "entity_description": "林黛玉是红楼梦中的主要角色，爱情悲剧的主角之一",
        },
        {
            "entity_name": "薛宝钗",
            "entity_type": "Person",
            "entity_description": "薛宝钗是红楼梦中的主要角色，爱情悲剧的主角之一",
        },
        {
            "entity_name": "金陵十二钗",
            "entity_type": "Concept",
            "entity_description": "金陵十二钗是红楼梦中以贾宝玉为中心的十二位主要女性角色",
        },
        {
            "entity_name": "乾隆年间",
            "entity_type": "Date",
            "entity_description": "乾隆年间指的是红楼梦成书的时间，约1743年前后",
        },
        {
            "entity_name": "四大家族",
            "entity_type": "Concept",
            "entity_description": "四大家族是红楼梦中的贾、史、王、薛四个家族，是小说的背景",
        },
        {
            "entity_name": "中国文学史",
            "entity_type": "Category",
            "entity_description": "红楼梦被视为中国文学史中现实主义的高峰之作",
        },
    ]
}
```
""",
            note="""
1. 提取结果必须以JSON数组格式输出
2. 每个实体必须包含 title 和 type 字段，description 字段可选但强烈建议提供
3. 确保 type 字段的值必须严格从 EntityTypes 列表中选择，不得创建新类型
4. 如果无法确定实体类型，不要强行归类，宁可不提取该实体
5. 不要输出任何解释或额外内容，只输出JSON数组
6. 所有字段值不能包含HTML标签或其他代码
7. 如果实体有歧义，需在description中说明具体指代
8. 若没有找到任何实体，返回空数组 []""",
        )

    def _tidy_entity(self, _entities: Entities) -> Entities:
        valid_entity_types = set(self.entity_config.keys())
        if _entities.entities:
            # 过滤掉类型不在配置中的实体
            _entities.entities = [
                entity
                for entity in _entities.entities
                if entity.entity_type in valid_entity_types
            ]
        return _entities

    def _merge_entity(self, new_entities: Entities) -> Entities:
        for i in new_entities.entities:
            self.entities.add_entity(i)
        return self.entities

    def run(self, input: str) -> Entities:
        _EntityTypes = ", ".join(list(self.entity_config.keys()))
        _EntityList = "\n".join([f"- {k}: {v}" for k, v in self.entity_config.items()])
        _prompt = self.build_prompt().get_instruction(
            f"EntityTypes: [{_EntityTypes}]\n文本: {input}",
            temp_vars={
                "EntityTypes": _EntityTypes,
                "EntityList": _EntityList,
            },
        )
        _entities = self._extract(_prompt, Entities, temperature=0.3)
        _entities = self._tidy_entity(_entities)
        _entities = self._merge_entity(_entities)
        _prompt.add_assistant(
            f"```json\n{json.dumps(_entities.model_dump(), indent=2, ensure_ascii=False)}\n```"
        )

        for i in range(self.max_gleanings):
            if i >= self.max_gleanings - 1:
                break
            _prompt.add_user(self.if_loop_prompt)
            continuation = stream_to_string(
                self.llm_instance.chat_for_stream(_prompt, temperature=0.8)
            )
            if continuation.strip() != "Y":
                break
            _prompt.add_assistant("Y")

            _prompt.add_user(self.continue_prompt)
            _res = self._extract(_prompt, Entities, temperature=0.3)
            _res = self._tidy_entity(_res)
            self._merge_entity(_res)
            _prompt.add_assistant(
                f"```json\n{json.dumps(_res.model_dump(), indent=2, ensure_ascii=False)}\n```"
            )

        return self.entities


class Edge(BaseModel):
    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    strength: conint(ge=5, le=10) = Field(
        description="关系强度，取值范围为5到10之间的正整数"
    )
    description: str = Field(description="关系描述")


class Edges(BaseModel):
    edges: List[Edge] = Field(description="从文本中识别出的所有关系列表")


class EdgeExtract(BaseLLMComponent):

    def __init__(
        self,
        llm_instance: BaseAIChat,
        max_gleanings: int = 2,
        retry_cnt: int = 3,
        retry_sleep: int = 3,
        *args,
        **kwargs,
    ):
        super().__init__(llm_instance, retry_cnt, retry_sleep, *args, **kwargs)
        self.max_gleanings = max_gleanings
        self.edges = Edges(edges=[])
        self.continue_prompt = "MANY edges were missed in the last extraction.  Add them below using the same format:\n"
        self.if_loop_prompt = "It appears some edges may have still been missed. Answer Y if there are still edges that need to be added, or N if there are none. Please answer with a single letter Y or N.\n"

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""从用户提供的实体数组中，提取实体之间存在的明确关系，形成结构化的关系网络。

## 关系提取规则
- 只有在文本中明确体现的关系才应被提取
- 源实体(source)和目标实体(target)必须是实体数组中已有的实体
- 关系描述(description)应简明扼要地说明两个实体间的具体关系
- 关系强度(strength)应根据以下标准确定：
  * 10分：直接创造/从属关系（如作者与作品、发明者与发明、母公司与子公司）
  * 9分：同一实体的不同表现形式（如别名、曾用名）
  * 8分：紧密相关且互相影响的关系（如密切合作伙伴、家庭成员）
  * 7分：明确但非直接的关系（如作品中的角色、组织中的成员）
  * 6分：间接关联且有明确联系（如同事关系、相似产品）
  * 5分：存在关联但较为松散（如同一领域的不同概念）""",
            step="""1. 仔细分析文本内容，确定哪些实体之间存在明确关系
2. 只考虑文本中明确提及的关系，不要臆测
3. 对每个找到的关系，确定：
   - source: 关系的源实体标题（必须是实体列表中已有的实体）
   - target: 关系的目标实体标题（必须是实体列表中已有的实体）
   - description: 简明准确的关系描述（用中文表述）
   - strength: 基于上述标准的关系强度（5-10之间的整数）
4. 检查每个关系是否双向：
   - 如果关系是双向的（如"A是B的朋友"意味着"B也是A的朋友"），考虑是否需要创建反向关系
   - 如果关系是单向的（如"A创作了B"），则只保留单向关系
5. 验证所有关系的一致性和合理性：
   - 确保没有矛盾的关系（如A同时是B的父亲和兄弟）
   - 确保关系描述与关系强度匹配
6. 将所有有效关系组织为JSON数组""",
            output_format=Edges,
            sample="""[输入]
实体： [
  {
    "entity_name": "红楼梦",
    "entity_type": "Work",
    "entity_description": "红楼梦是清代作家曹雪芹创作的中国古典四大名著之一，被誉为中国封建社会的百科全书"
  },
  {
    "entity_name": "石头记",
    "entity_type": "Work",
    "entity_description": "石头记是红楼梦的别名"
  },
  {
    "entity_name": "曹雪芹",
    "entity_type": "Person",
    "entity_description": "曹雪芹是清代作家，红楼梦的作者，创作了前80回"
  },
  {
    "entity_name": "高鹗",
    "entity_type": "Person",
    "entity_description": "高鹗是红楼梦后40回的续作者"
  },
  {
    "entity_name": "贾宝玉",
    "entity_type": "Person",
    "entity_description": "贾宝玉是红楼梦中的主要角色，爱情悲剧的主角之一"
  },
  {
    "entity_name": "林黛玉",
    "entity_type": "Person",
    "entity_description": "林黛玉是红楼梦中的主要角色，爱情悲剧的主角之一"
  },
  {
    "entity_name": "薛宝钗",
    "entity_type": "Person",
    "entity_description": "薛宝钗是红楼梦中的主要角色，爱情悲剧的主角之一"
  },
  {
    "entity_name": "四大家族",
    "entity_type": "Concept",
    "entity_description": "四大家族是红楼梦中的贾、史、王、薛四个家族，是小说的背景"
  },
  {
    "entity_name": "金陵十二钗",
    "entity_type": "Concept",
    "entity_description": "金陵十二钗是红楼梦中以贾宝玉为中心的十二位主要女性角色"
  },
  {
    "entity_name": "乾隆年间",
    "entity_type": "Date",
    "entity_description": "乾隆年间指的是红楼梦成书的时间，约1743年前后"
  },
  {
    "entity_name": "中国文学史",
    "entity_type": "Category",
    "entity_description": "红楼梦被视为中国文学史中现实主义的高峰之作"
  }
]

文本： 《红楼梦》，又名《石头记》，是清代作家曹雪芹创作的中国古典四大名著之一，被誉为中国封建社会的百科全书。该书前80回由曹雪芹所著，后40回一般认为是高鹗所续。小说以贾、史、王、薛四大家族的兴衰为背景，以贾宝玉、林黛玉和薛宝钗的爱情悲剧为主线，刻画了以贾宝玉和金陵十二钗为中心的正邪两赋、贤愚并出的高度复杂的人物群像。成书于乾隆年间（1743年前后），是中国文学史上现实主义的高峰，对后世影响深远。

[输出]
```json
{
    "edges": [
        {
            "source": "曹雪芹",
            "target": "红楼梦",
            "description": "曹雪芹是红楼梦的主要作者，创作了前80回",
            "strength": 10,
        },
        {
            "source": "高鹗",
            "target": "红楼梦",
            "description": "高鹗是红楼梦后40回的续作者",
            "strength": 10,
        },
        {
            "source": "红楼梦",
            "target": "石头记",
            "description": "石头记是红楼梦的别名",
            "strength": 9,
        },
        {
            "source": "红楼梦",
            "target": "中国文学史",
            "description": "红楼梦被视为中国文学史中现实主义的高峰之作",
            "strength": 7,
        },
        {
            "source": "贾宝玉",
            "target": "林黛玉",
            "description": "贾宝玉与林黛玉有深厚的爱情关系，是小说主线之一",
            "strength": 8,
        },
        {
            "source": "贾宝玉",
            "target": "薛宝钗",
            "description": "贾宝玉与薛宝钗的关系是小说爱情悲剧主线的一部分",
            "strength": 8,
        },
        {
            "source": "贾宝玉",
            "target": "金陵十二钗",
            "description": "贾宝玉是金陵十二钗故事的中心人物",
            "strength": 8,
        },
        {
            "source": "红楼梦",
            "target": "贾宝玉",
            "description": "贾宝玉是红楼梦中的主要角色",
            "strength": 7,
        },
        {
            "source": "红楼梦",
            "target": "林黛玉",
            "description": "林黛玉是红楼梦中的主要角色",
            "strength": 7,
        },
        {
            "source": "红楼梦",
            "target": "薛宝钗",
            "description": "薛宝钗是红楼梦中的主要角色",
            "strength": 7,
        },
        {
            "source": "红楼梦",
            "target": "四大家族",
            "description": "四大家族是红楼梦的背景设定",
            "strength": 7,
        },
        {
            "source": "红楼梦",
            "target": "金陵十二钗",
            "description": "金陵十二钗是红楼梦中的重要概念",
            "strength": 7,
        },
        {
            "source": "红楼梦",
            "target": "乾隆年间",
            "description": "红楼梦成书于乾隆年间，约1743年前后",
            "strength": 6,
        },
    ]
}
```
""",
            note="""1. 关系提取必须基于提供的文本内容，不得臆测不存在的关系
2. 结果必须以JSON数组格式输出，每个关系为数组中的一个对象
3. 每个关系对象必须包含 source, target, description 和 strength 字段
4. 不要输出任何解释或额外内容，只输出JSON数组
5. 若没有找到任何关系，返回空数组 []""",
        )

    def _tidy_edge(self, _edges: Edges, entities: Entities) -> Edges:
        """验证和清理边数据，确保源实体和目标实体都存在于实体列表中"""
        if _edges.edges:
            entity_names = {entity.entity_name for entity in entities.entities}
            # 过滤掉源实体或目标实体不在实体列表中的边
            _edges.edges = [
                edge
                for edge in _edges.edges
                if edge.source in entity_names and edge.target in entity_names
            ]
        return _edges

    def _merge_edge(self, new_edges: Edges) -> Edges:
        """合并新的边到现有边集合中"""
        for edge in new_edges.edges:
            # 检查是否已存在相同的边（相同的源和目标）
            existing_edge = None
            for existing in self.edges.edges:
                if existing.source == edge.source and existing.target == edge.target:
                    existing_edge = existing
                    break

            if existing_edge:
                # 如果存在相同的边，更新强度为较高值
                if edge.strength > existing_edge.strength:
                    existing_edge.strength = edge.strength
                    existing_edge.description = edge.description
            else:
                # 如果不存在，添加新边
                self.edges.edges.append(edge)
        return self.edges

    def run(self, input: str, entities: Entities) -> Edges:
        """提取实体间的关系"""
        entities_json = json.dumps(
            [entity.model_dump() for entity in entities.entities],
            indent=2,
            ensure_ascii=False,
        )

        _prompt = self.build_prompt().get_instruction(
            f"实体： {entities_json}\n\n文本： {input}"
        )

        _edges = self._extract(_prompt, Edges, temperature=0.3)
        _edges = self._tidy_edge(_edges, entities)
        _edges = self._merge_edge(_edges)
        _prompt.add_assistant(
            f"```json\n{json.dumps(_edges.model_dump(), indent=2, ensure_ascii=False)}\n```"
        )

        for i in range(self.max_gleanings):
            if i >= self.max_gleanings - 1:
                break
            _prompt.add_user(self.if_loop_prompt)
            continuation = stream_to_string(
                self.llm_instance.chat_for_stream(_prompt, temperature=0.8)
            )
            if continuation.strip() != "Y":
                break
            _prompt.add_assistant("Y")

            _prompt.add_user(self.continue_prompt)
            _res = self._extract(_prompt, Edges, temperature=0.3)
            _res = self._tidy_edge(_res, entities)
            self._merge_edge(_res)
            _prompt.add_assistant(
                f"```json\n{json.dumps(_res.model_dump(), indent=2, ensure_ascii=False)}\n```"
            )

        return self.edges


class GraphModel(BaseModel):
    entities: Optional[List[Entity]] = Field(description="实体列表")
    edges: Optional[List[Edge]] = Field(description="边列表")


class GraphExtract(BaseLLMComponent):

    def __init__(
        self,
        llm_instance: BaseAIChat,
        entity_config: dict[str, str] = None,
        entity_max_gleanings: int = 2,
        edge_max_gleanings: int = 2,
        retry_cnt: int = 3,
        retry_sleep: int = 3,
        *args,
        **kwargs,
    ):
        super().__init__(llm_instance, retry_cnt, retry_sleep, *args, **kwargs)
        self.entity_max_gleanings = entity_max_gleanings
        self.edge_max_gleanings = edge_max_gleanings
        self.entity_config = entity_config or DEFAULT_ENTITY_TYPES_CONFIG

    def run(self, input: str) -> GraphModel:
        """
        执行图谱提取，先提取实体，再提取关系

        Args:
            input: 输入文本

        Returns:
            GraphModel: 包含实体和边的图谱模型
        """
        # 1. 使用 EntityExtract 提取实体
        entity_extractor = EntityExtract(
            llm_instance=self.llm_instance,
            entity_config=self.entity_config,
            max_gleanings=self.entity_max_gleanings,
            retry_cnt=self.retry_cnt,
            retry_sleep=self.retry_sleep,
        )
        entities = entity_extractor.run(input)

        # 2. 使用 EdgeExtract 提取关系
        edge_extractor = EdgeExtract(
            llm_instance=self.llm_instance,
            max_gleanings=self.edge_max_gleanings,
            retry_cnt=self.retry_cnt,
            retry_sleep=self.retry_sleep,
        )
        edges = edge_extractor.run(input, entities)

        # 3. 构建并返回图谱模型
        return GraphModel(entities=entities.entities, edges=edges.edges)
