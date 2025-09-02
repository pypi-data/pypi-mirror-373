from typing import List

from pydantic import BaseModel, Field

from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.tokenizer import tokenizer
from .base import BaseComponent
from ...prompt.prompt_build import GeneralPromptBuilder
from ...utils.core_utils import json_observation, stream_to_string


class Ranker(BaseComponent):
    """通过语言模型实现 rerank能力 不支持分值，只能排序"""

    # query: str, documents
    def __init__(self, llm: BaseAIChat):
        super().__init__()
        self.llm = llm
        self.content_tokens_limit = None
        self.documents = None
        self.question_tokens = None
        self.prompt_tokens = 1000
        self.rank_limit = 5
        self.query = None

    def init_data(self, query: str, documents: List[str], rank_limit=5):
        self.query = query
        self.rank_limit = rank_limit
        self.question_tokens = tokenizer.chat_len(query)
        self.documents = documents
        self.content_tokens_limit = (
            self.llm.token_limit - self.prompt_tokens - self.question_tokens
        )

    def cut_passages(self):
        _content_tokens = self.content_tokens_limit
        _passages = []
        for _chunk in self.documents:
            _curr_token = tokenizer.chat_len(_chunk)
            _content_tokens = _content_tokens - _curr_token
            if _content_tokens > 0:
                _passages.append(_chunk)
            else:
                break
        self.documents = _passages

    def chk_passages_tokens_limit(self):
        if tokenizer.chat_len("".join(self.documents)) > self.content_tokens_limit:
            return False
        else:
            return True

    def get_prefix_prompt(self, num):
        return [
            {
                "role": "system",
                "content": "You are RankGPT, an intelligent assistant that can rank passages based on their relevancy to the query.",
            },
            {
                "role": "user",
                "content": f"I will provide you with {num} passages, each indicated by number identifier []. \nRank the passages based on their relevance to query: {self.query}.",
            },
            {"role": "assistant", "content": "Okay, please provide the passages."},
        ]

    def get_post_prompt(self, num):
        return f"Search Query: {self.query}. \nRank the {num} passages above based on their relevance to the search query. The passages should be listed in descending order using identifiers. The most relevant passages should be listed first. The output format should be [] > [], e.g., [1] > [2]. Only response the ranking results, do not say any word or explain."

    def create_permutation_instruction(self):
        if not self.chk_passages_tokens_limit():
            raise ValueError(
                f"Agent Ranker token passages overly long, model tokens limit number {self.llm.token_limit}."
            )
        num = len(self.documents)
        messages = self.get_prefix_prompt(num)
        rank = 0
        for hit in self.documents:
            rank += 1
            content = hit
            content = content.replace("Title: Content: ", "")
            content = content.strip()
            messages.append({"role": "user", "content": f"[{rank}] {content}"})
            messages.append(
                {"role": "assistant", "content": f"Received passage [{rank}]."}
            )
        messages.append({"role": "user", "content": self.get_post_prompt(num)})
        return messages

    def run_llm(self, messages):
        response = stream_to_string(
            self.llm.chat_for_stream(messages=messages, temperature=0)
        )
        return response

    async def arun_llm(self, messages):
        response = await self.llm.achat(messages=messages, temperature=0)
        return response

    @staticmethod
    def clean_response(response: str):
        new_response = ""
        for c in response:
            if not c.isdigit():
                new_response += " "
            else:
                new_response += c
        new_response = new_response.strip()
        return new_response

    @staticmethod
    def remove_duplicate(response):
        new_response = []
        for c in response:
            if c not in new_response:
                new_response.append(c)
        return new_response

    def receive_permutation(self, permutation):
        _passages = []
        response = self.clean_response(permutation)
        response = [int(x) - 1 for x in response.split()]
        response = self.remove_duplicate(response)
        original_rank = [tt for tt in range(len(self.documents))]
        response = [ss for ss in response if ss in original_rank]
        response = response + [tt for tt in original_rank if tt not in response]
        for x in response[: self.rank_limit]:
            _passages.append(self.documents[x])
        return _passages

    def run(self, query: str, documents: List[str], rank_limit=5) -> List[str]:
        self.init_data(query, documents, rank_limit)
        if self.rank_limit < len(self.documents):
            messages = self.create_permutation_instruction()
            permutation = self.run_llm(messages)
            item = self.receive_permutation(permutation)
            return item
        else:
            return self.documents

    async def arun(self, query: str, documents: List[str], rank_limit=5) -> List[str]:
        self.init_data(query, documents, rank_limit)
        if self.rank_limit < len(self.documents):
            messages = self.create_permutation_instruction()
            permutation = await self.arun_llm(messages)
            item = self.receive_permutation(permutation)
            return item
        else:
            return self.documents


class RelevanceScore(BaseModel):
    reasoning: str = Field(..., description="推理过程(50字以内)")
    relevance_score: int = Field(..., ge=0, le=10, description="相关性分数")


class RankerScore(BaseComponent):
    """通过语言模型实现 对文档进行相关性打分"""

    def __init__(self, llm: BaseAIChat):
        super().__init__()
        self.llm = llm

    def build_prompt(self) -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""根据文档片段与用户问题的相关性进行1-10分的评分，并严格遵守评分标准。确保所有结论基于详细的分析推理得出，推理过程必须出现在最终评分之前。

### 评分标准
对每个评分级别定义具体要求，需严格遵循：
1. **完全不相关** (1分)：文档与问题主题毫无关联
2. **极弱相关** (2分)：仅有个别非关键单词相同
3. **微弱相关** (3分)：涉及相同领域但无实质信息
4. **部分相关** (4分)：解决次要问题或提供间接信息
5. **基本相关** (5分)：能回应部分核心问题但存在重大缺失
6. **中等相关** (6分)：覆盖主要问题但需用户自行补充
7. **良好相关** (7分)：直接回答核心问题但有轻微遗漏
8. **高度相关** (8分)：精确解答主要问题并有额外支持
9. **极强相关** (9分)：完全解决问题并给出深度洞察
10. **完美相关** (10分)：精准确认所有细节并预判延伸需求
""",
            step="""1. **识别关键要素**
   - 提取问题核心需求：[主要查询点]
   - 标记文档核心信息：[关键知识点]
2. **对比分析**
   - 主题匹配度：[领域/场景重合度]
   - 信息完整度：[问题需求覆盖比例]
   - 细节精确度：[数据/术语准确率]
3. **缺失项检测**
   - 未覆盖的需求点：[列出具体遗漏]
   - 矛盾信息：[存在冲突的陈述]
4. **推理结论**
   - 说明评分依据与标准条款对应关系""",
            output_format=RelevanceScore,
            sample="""**输入组合：**
用户问题："网站显示500错误怎么办？"
文档片段："HTTP状态码200表示请求成功，404表示资源未找到"

**输出：**
```json
{
  "reasoning": "由于提供的回答内容完全未触及用户核心问题——服务器500错误的原因或解决方案，且相关文档仅涵盖200/404状态码而明确缺失对5xx错误的说明，依据关键主题匹配度（0%）与核心需求覆盖度（0%）的分析结果，根据评分标准第1条：属于完全无关主题。",
  "score": 1
}
```

**(实际案例中，文档与问题应存在部分关联时，推理段落需更详细展开具体匹配点分析)**""",
            note="""- 当问题包含多子需求时，逐点分析关联性
- 对专业术语需验证使用一致性
- 文档隐含信息（如推论结论）不计入评分依据
- 分值必须精确对应评分标准条目""",
        )

    def run(self, query: str, document: str) -> int:

        _prompt = self.build_prompt().get_instruction(
            f"用户问题：{query}\n\n文档片段：\n{document}"
        )

        resp = stream_to_string(self.llm.chat_for_stream(_prompt))

        resp = json_observation(resp, RelevanceScore)

        return resp.relevance_score

    async def arun(self, query: str, document: str) -> int:
        _prompt = self.build_prompt().get_instruction(
            f"用户问题：{query}\n\n文档片段：\n{document}"
        )
        resp = await self.llm.achat(_prompt)
        resp: RelevanceScore = json_observation(resp, RelevanceScore)
        return resp.relevance_score
