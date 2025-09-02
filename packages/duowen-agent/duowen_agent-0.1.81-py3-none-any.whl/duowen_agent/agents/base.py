from abc import ABC, abstractmethod
from typing import Callable, Optional
from typing import Union

from duowen_agent.llm import MessagesSet
from duowen_agent.llm.chat_model import OpenAIChat
from duowen_agent.llm.embedding_model import OpenAIEmbedding, EmbeddingCache
from duowen_agent.llm.rerank_model import GeneralRerank
from duowen_agent.rag.retrieval.base import BaseVector
from duowen_agent.tools.base import BaseToolResult
from duowen_agent.utils.concurrency import make_async


class BaseAgent(ABC):

    def __init__(
        self,
        llm: OpenAIChat = None,
        retrieval_instance: BaseVector = None,
        embedding_instance: Union[EmbeddingCache, OpenAIEmbedding] = None,
        rerank_model: GeneralRerank = None,
        start_hook: Optional[Callable] = None,
        end_hook: Optional[Callable] = None,
        **kwargs,
    ):
        self.llm = llm
        self.retrieval_instance = retrieval_instance
        self.embedding_instance = embedding_instance
        self.rerank_model = rerank_model
        self.start_hook = start_hook
        self.end_hook = end_hook

    @abstractmethod
    def _run(
        self, instruction: str | MessagesSet, *args, **kwargs
    ) -> BaseToolResult | str | int | float:
        raise NotImplementedError()

    async def _arun(
        self, instruction: str | MessagesSet, *args, **kwargs
    ) -> BaseToolResult | str | int | float:
        return await make_async(self._run, instruction, *args, **kwargs)

    def run(
        self,
        instruction: str | MessagesSet,
        *args,
        **kwargs,
    ) -> BaseToolResult | str | int | float:
        result = self._run(instruction, *args, **kwargs)
        return result

    async def arun(
        self,
        instruction: str | MessagesSet,
        *args,
        **kwargs,
    ) -> BaseToolResult | str | int | float:
        result = await self._arun(instruction, *args, **kwargs)
        return result
