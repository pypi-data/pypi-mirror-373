import math
from typing import List, Optional, Any

from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.error import ObserverException
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.core_utils import retrying
from duowen_agent.utils.string_template import StringTemplate


class Keywords(BaseModel):
    keywords: List[str] = Field(description="重要的关键词/短语")


class ChunkKeywordsExtract(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        return GeneralPromptBuilder(
            instruction="""角色：你是一个文本分析器
任务：提取给定文本内容中最重要的关键词/短语""",
            output_format=Keywords,
            sample="""```json
{
  "questions": [
    "关键词/短语1", 
    "关键词/短语2",
    "关键词/短语3",
    ...
  ]
}
```""",
            note=StringTemplate(
                """- 对文本内容进行总结，并给出前{topn}个最重要的关键词/短语
- 关键词/短语必须使用原文的语言"""
            ),
        )

    async def arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def run(
        self, chunk: str, top_n=3, title: str = None, summary: str = None
    ) -> Keywords:
        _question = ""
        if title:
            _question += f"- 文章标题: {title}\n\n"
        if summary:
            _question += f"- 文章摘要: {summary}\n\n"
        _question += f"- 文章片段内容: {chunk}\n\n"
        _question += f"---------------------\n\n"
        _question += "文章标题和文章摘要只是用来帮助你理解文章片段内容，请提取关于文章片段内容最重要的{topn}个关键词/短语"
        _prompt = self.build_prompt().get_instruction(
            user_input=_question, temp_vars={"topn": top_n}
        )
        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        _res = json_observation(_res, Keywords)
        return _res


class Questions(BaseModel):
    questions: List[str] = Field(
        ..., description="propose questions about text content"
    )


class ChunkQuestionsExtract(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        return GeneralPromptBuilder(
            instruction=StringTemplate(
                """Role: 你是一个文本分析器
Task: 针对给定的文本内容，提出{topn}个相关问题

## 约束条件（重要！）
- 必须基于文本内容直接生成
- 问题应具有明确答案指向性
- 需覆盖文本的不同方面
- 禁止生成假设性、重复或相似问题

## 处理流程
1. 【文本解析】分段处理内容，识别关键实体和核心概念
2. 【问题生成】基于信息密度选择最佳提问点
3. 【质量检查】确保：
   - 问题答案可在原文中找到依据
   - 标签与问题内容强相关
   - 无格式错误
"""
            ),
            output_format=Questions,
            sample="""```json
{
  "questions": [
    "问题1", 
    "问题2",
    "问题3",
    ...
  ]
}
```""",
            note=StringTemplate(
                """- 理解并总结文本内容后，提出最重要的{topn}个核心问题
- 问题必须聚焦文本的关键信息点
- 问题间应形成逻辑递进关系
- 须使用文本原语言进行提问
- 提出的问题不要和材料本身相关，例如禁止出现作者、章节、目录等相关问题
- 提出的问题中不得出现 ' 文章中 / 文章片段中 / 报告中 ' 等任何引用性表述
- """
            ),
        )

    # - 禁止出现"这些"、"它"、"该"、"本文"、"报告中"、"文章中"、"文献中"、"表格中"、"文章片段中"等类似指代性表述

    async def arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def run(
        self, chunk: str, top_n=3, title: str = None, summary: str = None
    ) -> Questions:
        _question = ""
        if title:
            _question += f"- 文章标题: {title}\n\n"
        if summary:
            _question += f"- 文章摘要: {summary}\n\n"
        _question += f"- 文章片段内容: {chunk}\n\n"
        _question += f"---------------------\n\n"
        _question += "文章标题和文章摘要只是用来帮助你理解文章片段内容，请提取关于文章片段内容最重要的{topn}个核心问题\n\n"
        _prompt = self.build_prompt().get_instruction(
            user_input=_question, temp_vars={"topn": top_n}
        )
        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        _res = json_observation(_res, Questions)
        return _res


class TitleSummary(BaseModel):
    title: str = Field(description="一个精准的标题（不超过15字）")
    summary: str = Field(description="一段凝练的摘要（80-120字）")


class SummaryExtract(BaseComponent):
    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        return GeneralPromptBuilder(
            instruction="""请基于提供的文章片段，生成一个精准的标题（不超过15字）和一段凝练的摘要（80-120字），要求：
1. 标题需突出核心观点/发现/冲突
2. 摘要需包含三个关键要素：
   - 研究/事件的背景/目标
   - 使用的方法/核心论据
   - 主要结论/社会影响/争议点
3. 遵循学术/新闻规范（二选一）
""",
            output_format=TitleSummary,
            sample='''"""```json
{
  "title": "一个精准的标题（不超过15字）",
  "summary": "一段凝练的摘要（80-120字）"
}
```"""''',
            note="""- 若原文含数据/专有名词，必须保留关键数值和术语
- 不添加解释性内容，不采用"本文""本研究"等主观表述""",
        )

    def run(self, content: str) -> TitleSummary:
        _content = tokenizer.truncate_chat(
            content, int(self.llm_instance.token_limit / 2)
        )
        _prompt = self.build_prompt().get_instruction(
            user_input=f"文章片段:\n\n{_content}"
        )
        _res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        _res = json_observation(_res, TitleSummary)
        return _res

    async def arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class ChunkExtendList(BaseModel):
    index: int
    data: Optional[List[str]]


class ChunkExtendSchema(BaseModel):
    title: Optional[str]
    summary: Optional[str]
    chunk_keywords: Optional[List[ChunkExtendList]]
    chunk_questions: Optional[List[ChunkExtendList]]


class ChunkExtend(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    async def arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def run(
        self,
        content: str,
        chunks: List[str],
        keywords_dividend: int = 120,
        questions_dividend: int = 180,
        title: str = None,
        is_summary: bool = True,
    ) -> ChunkExtendSchema:
        _title = title
        _summary = None
        if is_summary:
            try:
                _res = retrying(
                    func=SummaryExtract(self.llm_instance).run,
                    func_params=dict(content=content),
                )
                if not _title:
                    _title = _res.title
                _summary = _res.summary
            except ObserverException:
                pass

        _chunk_keywords = []
        if keywords_dividend:
            for _index, _chunk in enumerate(chunks):
                _keywords_topn = math.floor(len(_chunk) / keywords_dividend)
                if _keywords_topn >= 1:
                    try:
                        _res = retrying(
                            func=ChunkKeywordsExtract(self.llm_instance).run,
                            func_params=dict(
                                chunk=_chunk,
                                top_n=_keywords_topn,
                                title=_title,
                                summary=_summary,
                            ),
                        )
                        _chunk_keywords.append(
                            {"index": _index, "data": _res.keywords[:_keywords_topn]}
                        )
                    except ObserverException:
                        _chunk_keywords.append({"index": _index, "data": []})
                else:
                    _chunk_keywords.append({"index": _index, "data": []})

        _chunk_questions = []
        if questions_dividend:
            for _index, _chunk in enumerate(chunks):
                _questions_topn = math.floor(len(_chunk) / questions_dividend)
                if _questions_topn >= 1:
                    try:
                        _res = retrying(
                            func=ChunkQuestionsExtract(self.llm_instance).run,
                            func_params=dict(
                                chunk=_chunk,
                                top_n=_questions_topn,
                                title=_title,
                                summary=_summary,
                            ),
                        )
                        _chunk_questions.append(
                            {"index": _index, "data": _res.questions[:_questions_topn]}
                        )
                    except ObserverException:
                        _chunk_questions.append({"index": _index, "data": []})
                else:
                    _chunk_questions.append({"index": _index, "data": []})

        return ChunkExtendSchema(
            title=_title,
            summary=_summary,
            chunk_keywords=_chunk_keywords,
            chunk_questions=_chunk_questions,
        )
