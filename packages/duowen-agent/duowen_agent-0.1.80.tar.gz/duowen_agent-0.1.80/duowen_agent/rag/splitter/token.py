from typing import List, Union, Literal

from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.rag.models import Document

from .base import BaseChunk


class TokenChunker(BaseChunk):

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: Union[int, float] = 128,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if isinstance(chunk_overlap, int) and chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        if isinstance(chunk_overlap, float) and chunk_overlap >= 1:
            raise ValueError("chunk_overlap must be less than 1")

        self.chunk_size = chunk_size
        self.chunk_overlap = (
            chunk_overlap
            if isinstance(chunk_overlap, int)
            else int(chunk_overlap * chunk_size)
        )

    def _encode(self, text):
        if self.token_count_type == "o200k":
            return tokenizer.chat_encode(text)
        elif self.token_count_type == "cl100k":
            return tokenizer.emb_encode(text)
        else:
            raise ValueError("token_count_type must be o200k or cl100k")

    def _decode(self, tokens):
        if self.token_count_type == "o200k":
            return tokenizer.chat_decode(tokens)
        elif self.token_count_type == "cl100k":
            return tokenizer.emb_decode(tokens)
        else:
            raise ValueError("token_count_type must be o200k or cl100k")

    def chunk(self, text: str) -> List[Document]:

        if not text.strip():
            return []

        # Encode full text

        text_tokens = self._encode(text)

        chunks = []

        # Calculate chunk positions
        start_indices = range(0, len(text_tokens), self.chunk_size - self.chunk_overlap)

        for start_idx in start_indices:
            # Get token indices for this chunk
            end_idx = min(start_idx + self.chunk_size, len(text_tokens))

            # Extract and decode tokens for this chunk
            chunk_tokens = text_tokens[start_idx:end_idx]

            chunk_text = self._decode(chunk_tokens)

            chunks.append(
                Document(
                    page_content=chunk_text,
                    metadata=dict(
                        start_index=start_idx,
                        end_index=end_idx,
                        token_count=len(chunk_tokens),
                    ),
                )
            )
            # Break if we've reached the end of the text
            if end_idx == len(text_tokens):
                break

        return chunks

    def __repr__(self) -> str:
        return (
            f"TokenChunker(chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap})"
        )
