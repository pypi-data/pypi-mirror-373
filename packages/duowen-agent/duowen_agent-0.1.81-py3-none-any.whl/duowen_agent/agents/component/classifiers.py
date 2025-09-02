from typing import List, Tuple

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.error import ObserverException
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class CategoriesOne(BaseModel):
    category_name: str = Field(
        description="Exactly the name of the category that matches"
    )


class CategoriesMulti(BaseModel):
    category_names: List[str] = Field(
        description="Select one or more applicable categories"
    )


class ClassifiersOne(BaseComponent):
    """
    单选分类器
    """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """Your task is to assign one categories ONLY to the input text and only one category may be assigned returned in the output.

The categories are:
{% for key, value in categories.items() %}
- {{key}}: {{value}}
{% endfor %}""",
                "jinja2",
            ),
            output_format=CategoriesOne,
            note="""- the selection must be singular .
- Respond with JSON code only without any explanations and comments. -- just the JSON code.""",
        )

    def get_prompt(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ):
        _prompt = self.build_prompt()
        if sample:
            _sample = []
            for i in sample:
                _q = i[0]
                _a = f"```json\n{CategoriesOne(category_name=i[1]).model_dump(mode='json')}\n```\n"
                _sample.append((_q, _a))

            _prompt.sample = "\n".join(
                [
                    f"## sample_{i + 1}\ninput:\n{d[0]}\n\noutput:\n{d[1]}"
                    for i, d in enumerate(_sample)
                ]
            )

        _prompt = _prompt.get_instruction(
            user_input=question,
            temp_vars={
                "categories": categories,
            },
        )

        return _prompt

    def observer(self, res, categories):
        _res: CategoriesOne = json_observation(res, CategoriesOne)
        if _res.category_name in categories:
            return _res.category_name
        else:
            raise ObserverException(
                predict_value=_res.category_name,
                expect_value=str(categories.keys()),
                err_msg="observation error values",
            )

    def run(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ) -> str:
        _prompt = self.get_prompt(question, categories, sample, **kwargs)
        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        return self.observer(_res, categories)

    async def arun(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ) -> str:
        _prompt = self.get_prompt(question, categories, sample, **kwargs)
        _res = await self.llm_instance.achat(_prompt)
        return self.observer(_res, categories)


class ClassifiersMulti(BaseComponent):
    """
    多选分类器
    """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """Your task is to assign one or more categories to the input text and the output may include one or more categories.

The categories are:
{% for key, value in categories.items() %}
- {{key}}: {{value}}
{% endfor %}""",
                "jinja2",
            ),
            output_format=CategoriesMulti,
            note="""Respond with JSON code only without any explanations and comments. -- just the JSON code.""",
        )

    def get_prompt(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ):
        _prompt = GeneralPromptBuilder.load("classifiers_multi")
        if sample:
            _sample = []
            for i in sample:
                _q = i[0]
                _a = f"```json\n{CategoriesMulti(category_names=[i[1]] if isinstance(i[1], str) else i[1]).model_dump(mode='json')}\n```\n"
                _sample.append((_q, _a))

            _prompt.sample = "\n".join(
                [
                    f"## sample_{i + 1}\ninput:\n{d[0]}\n\noutput:\n{d[1]}"
                    for i, d in enumerate(_sample)
                ]
            )

        _prompt = _prompt.get_instruction(
            user_input=question,
            temp_vars={
                "categories": categories,
            },
        )

        return _prompt

    def observer(self, res, categories):

        _res: CategoriesMulti = json_observation(res, CategoriesMulti)

        for i in _res.category_names:
            if i not in categories:
                raise ObserverException(
                    predict_value=i,
                    expect_value=str(categories.keys()),
                    err_msg="observation error values",
                )
        return _res.category_names

    def run(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ) -> List[str]:

        _prompt = self.get_prompt(question, categories, sample, **kwargs)
        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        return self.observer(_res, categories)

    async def arun(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ) -> List[str]:

        _prompt = self.get_prompt(question, categories, sample, **kwargs)
        _res = await self.llm_instance.achat(_prompt)
        return self.observer(_res, categories)


class GeneralClassification:
    news_events = {
        "人事.提名": "指对某个职位或角色的候选人提出任命建议的行为。",
        "联系.电话/书面沟通": "通过电话或书面形式进行的信息交流或沟通行为。",
        "商业.宣告破产": "企业或机构因资不抵债，正式宣布无力偿还债务并终止运营。",
        "司法.批准假释": "允许符合条件的囚犯在刑期未满时提前释放，需遵守特定条件。",
        "司法.引渡": "将犯罪嫌疑人或罪犯从一国移送至另一国接受审判或服刑。",
        "人事.就职": "个人正式接受某一职位并开始履行职责。",
        "司法.罚款": "因违法行为对个人或组织施加的经济处罚。",
        "交易.转账": "通过银行或金融机构进行的资金转移行为。",
        "人事.离职": "个人主动或被动结束某一职位或职务。",
        "司法.宣判无罪": "法庭裁定被告在指控中不承担法律责任。",
        "生活.受伤": "因事故、暴力等导致身体受到伤害的事件。",
        "冲突.攻击": "通过武力或威胁手段对目标造成物理或心理伤害的行为。",
        "司法.逮捕-监禁": "强制限制个人自由，通常伴随拘留或监禁措施。",
        "司法.赦免": "政府或司法机关撤销或减轻对罪犯的刑罚。",
        "司法.控告-起诉": "正式向法院提出对某人违法行为的指控并启动法律程序。",
        "冲突.示威": "集体公开表达诉求或抗议的聚集行为。",
        "联系.会面": "多方或双方进行的正式或非正式面对面交流活动。",
        "商业.解散机构": "企业或组织终止运营并解除法律实体的行为。",
        "生活.出生": "新生儿的诞生及相关法律登记行为。",
        "人事.选举": "通过投票或其他方式选任特定职位或代表的程序。",
        "司法.庭审": "法庭对案件进行审理和听证的正式程序。",
        "生活.离婚": "通过法律程序解除婚姻关系。",
        "司法.诉讼": "向法院提出争议并寻求法律裁决的民事程序。",
        "司法.上诉": "对法院判决不满并请求上级法院重新审理的行为。",
        "商业.机构合并": "两个或多个组织通过协议整合为单一实体。",
        "生活.死亡": "个人生命的终结及相关法律记录处理。",
        "商业.创立机构": "新企业或组织的注册和正式成立行为。",
        "司法.定罪": "法庭在审判后确认被告有罪的最终裁决。",
        "物流.运输": "将货物或人员通过特定方式从一个地点移至另一个地点。",
        "生活.结婚": "双方通过法律程序建立婚姻关系的仪式或登记。",
        "司法.判刑": "法庭根据罪名对罪犯作出刑期或惩罚的决定。",
        "司法.处决": "对死刑犯执行死刑的行为。",
        "交易.产权转移": "财产或资产的所有权在法律意义上的变更。",
    }

    sentiment = {
        "抱怨": "客户对服务或产品表达不满或失望",
        "愤怒": "用户在交流中表现出强烈的怒气或急躁情绪",
        "厌恶": "对话中透露出对某些服务或行为的反感或排斥",
        "悲伤": "用户情绪低落，可能隐含挫败感或无力感",
        "投诉": "客户明确提出服务/产品的质量或流程问题",
        "惊讶": "用户对信息或结果表现出意外反应",
        "恐惧": "对方透露出担忧或不安的心理状态（如怀疑欺诈风险）",
        "喜好": "客户对产品、服务或沟通方式表现出的正面偏好或兴趣",
        "高兴": "对话中包含赞赏、满意等正向快乐情绪",
        "认可": "用户对解决方案或服务人员的专业性表示明确赞同",
        "感谢": "客户通过致谢展现出对服务的整体满意度",
    }


if __name__ == "__main__":
    ClassifiersOne.build_prompt()
    ClassifiersMulti.build_prompt()
