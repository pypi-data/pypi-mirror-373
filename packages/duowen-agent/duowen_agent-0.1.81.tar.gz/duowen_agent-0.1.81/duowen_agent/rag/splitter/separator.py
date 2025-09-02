import logging
from typing import List, Union, Iterable, Optional, Literal

from duowen_agent.rag.models import Document
from duowen_agent.rag.splitter.comm import split_text_with_regex

from .base import BaseChunk


class SeparatorChunker(BaseChunk):

    def __init__(
        self,
        separator: str = "\n\n",
        keep_separator: bool = True,
        chunk_size: int = 512,
        chunk_overlap: Union[int, float] = 80,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.chunk_size = chunk_size
        self.chunk_overlap = (
            chunk_overlap
            if isinstance(chunk_overlap, int)
            else int(chunk_overlap * chunk_size)
        )
        self._separator = separator
        self._keep_separator = keep_separator

    def _length_function(self, text: str) -> int:
        return self.token_len(text)

    @staticmethod
    def _join_docs(docs: list[str], separator: str) -> Optional[str]:
        text = separator.join(docs)
        text = text.strip()
        if text == "":
            return None
        else:
            return text

    def _merge_splits(
        self, splits: Iterable[str], separator: str, lengths: list[int]
    ) -> list[str]:
        # We now want to combine these smaller pieces into medium size
        # chunks to send to the LLM.
        separator_len = self._length_function(separator)

        docs = []
        current_doc: list[str] = []
        total = 0
        index = 0
        for d in splits:
            _len = lengths[index]
            if (
                total + _len + (separator_len if len(current_doc) > 0 else 0)
                > self.chunk_size
            ):
                if total > self.chunk_size:
                    logging.warning(
                        f"Created a chunk of size {total}, which is longer than the specified {self.chunk_size}"
                    )
                if len(current_doc) > 0:
                    doc = self._join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)
                    # Keep on popping if:
                    # - we have a larger chunk than in the chunk overlap
                    # - or if we still have any chunks and the length is long
                    while total > self.chunk_overlap or (
                        total + _len + (separator_len if len(current_doc) > 0 else 0)
                        > self.chunk_size
                        and total > 0
                    ):
                        total -= self._length_function(current_doc[0]) + (
                            separator_len if len(current_doc) > 1 else 0
                        )
                        current_doc = current_doc[1:]
            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)
            index += 1
        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
        return docs

    def chunk(self, text: str) -> List[Document]:
        splits = split_text_with_regex(text, self._separator, self._keep_separator)
        _separator = "" if self._keep_separator else self._separator
        _good_splits_lengths = []  # cache the lengths of the splits
        for split in splits:
            _good_splits_lengths.append(self._length_function(split))
        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(
                self._merge_splits(splits, _separator, _good_splits_lengths)
            ) if len(i.strip()) > 0
        ]

    def __repr__(self) -> str:
        return (
            f"SeparatorChunker(separator={self._separator}"
            f"chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
