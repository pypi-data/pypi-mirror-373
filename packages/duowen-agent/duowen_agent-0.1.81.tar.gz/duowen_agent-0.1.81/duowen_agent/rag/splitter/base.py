from abc import ABC, abstractmethod
from typing import List, Literal

from duowen_agent.llm import tokenizer
from duowen_agent.rag.models import Document
from duowen_agent.utils.concurrency import make_async


class BaseChunk(ABC):
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 0,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
        **kwargs
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.token_count_type = token_count_type

    def token_len(self, text: str) -> int:
        if self.token_count_type == "o200k":
            return tokenizer.chat_len(text)
        elif self.token_count_type == "cl100k":
            return tokenizer.emb_len(text)
        else:
            raise ValueError("token_count_type must be o200k or cl100k")

    @abstractmethod
    def chunk(self, text: str) -> List[Document]:
        raise NotImplementedError

    async def achunk(self, text: str) -> List[Document]:
        result = await make_async(self.chunk, text)  # 折中方案，建议继承重写
        return result
