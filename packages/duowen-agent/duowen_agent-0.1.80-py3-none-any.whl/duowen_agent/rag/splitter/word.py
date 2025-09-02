"""Word-based chunker."""

import warnings
from typing import List, Literal

# 忽略无效转义序列的警告
warnings.filterwarnings(
    "ignore", message=".*invalid escape sequence.*", category=DeprecationWarning
)

# 忽略pkg_resources弃用警告
warnings.filterwarnings(
    "ignore", message=".*pkg_resources is deprecated.*", category=DeprecationWarning
)

import jieba
from duowen_agent.rag.models import Document

from .base import BaseChunk


class WordChunker(BaseChunk):

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 0,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):

        super().__init__(token_count_type=token_count_type)
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        # Assign the values if they make sense
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_into_words(self, text: str) -> List[str]:
        """Split text into words while preserving whitespace."""
        # split_points = [match.end() for match in re.finditer(r"(\s*\S+)", text)]
        words = jieba.tokenize(text)
        split_points = [item[2] for item in words]
        words = []
        prev = 0

        for point in split_points:
            words.append(text[prev:point])
            prev = point

        if prev < len(text):
            words.append(text[prev:])

        return words

    def _create_chunk(
        self,
        words: List[str],
        text: str,
        token_count: int,
        current_index: int = 0,
    ) -> Document:
        """Create a chunk from a list of words.

        Args:
            words: List of words to create chunk from
            text: The original text
            token_count: Number of tokens in the chunk
            current_index: The index of the first token in the chunk

        Returns:
            Tuple of (Chunk object, number of tokens in chunk)

        """
        chunk_text = "".join(words)
        start_index = text.find(chunk_text, current_index)
        return Document(
            page_content=chunk_text,
            metadata=dict(
                start_index=start_index,
                end_index=start_index + len(chunk_text),
                token_count=token_count,
            ),
        )

    def _get_word_list_token_counts(self, words: List[str]) -> List[int]:
        """Get the number of tokens for each word in a list.

        Args:
            words: List of words

        Returns:
            List of token counts for each word

        """
        words = [
            word for word in words if word != ""
        ]  # Add space in the beginning because tokenizers usually split that differently
        return [self.token_len(word) for word in words]

    def chunk(self, text: str) -> List[Document]:
        """Split text into overlapping chunks based on words while respecting token limits.

        Args:
            text: Input text to be chunked

        Returns:
            List of Chunk objects containing the chunked text and metadata

        """
        if not text.strip():
            return []

        words = self._split_into_words(text)
        lengths = self._get_word_list_token_counts(words)
        chunks = []

        # Saving the current chunk
        current_chunk = []
        current_chunk_length = 0

        current_index = 0

        for i, (word, length) in enumerate(zip(words, lengths)):
            if current_chunk_length + length <= self.chunk_size:
                current_chunk.append(word)
                current_chunk_length += length
            else:

                chunk = self._create_chunk(
                    current_chunk,
                    text,
                    current_chunk_length,
                    current_index,
                )
                chunks.append(chunk)

                # update the current_chunk and previous chunk
                previous_chunk_length = current_chunk_length
                current_index = chunk.metadata["end_index"]

                overlap = []
                overlap_length = 0
                # calculate the overlap from the current chunk in reverse
                for j in range(0, previous_chunk_length):
                    cwi = i - 1 - j
                    oword = words[cwi]
                    olength = lengths[cwi]
                    if overlap_length + olength <= self.chunk_overlap:
                        overlap.append(oword)
                        overlap_length += olength
                    else:
                        break

                current_chunk = [w for w in reversed(overlap)]
                current_chunk_length = overlap_length

                current_chunk.append(word)
                current_chunk_length += length

        # Add the final chunk if it has any words
        if current_chunk:
            chunk = self._create_chunk(current_chunk, text, current_chunk_length)
            chunks.append(chunk)

        return [i for i in chunks if len(i.page_content.strip()) > 0]

    def __repr__(self) -> str:
        """Return a string representation of the WordChunker."""
        return f"chunk_size={self.chunk_size}, " f"chunk_overlap={self.chunk_overlap}"
