import logging
import re
from typing import Literal, Optional, Iterable, List

from duowen_agent.rag.models import Document

from .base import BaseChunk


def _split_text_with_regex(
    text: str, separator: str, keep_separator: bool
) -> list[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({re.escape(separator)})", text)
            splits = [_splits[i - 1] + _splits[i] for i in range(1, len(_splits), 2)]
            if len(_splits) % 2 != 0:
                splits += _splits[-1:]
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if (s not in {"", "\n"})]


class RecursiveChunker(BaseChunk):

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 0,
        splitter_breaks: list[str] = None,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if splitter_breaks is None:
            # self.splitter_breaks = ["\n\n", "\n", " ", "。", "？", "！", ".", "?", "!"]
            self.splitter_breaks = [
                # Paragraph separators
                "\n\n",
                "\r\n\r\n",
                # Line breaks
                "\n",
                "\r\n",
                # Sentence ending punctuation
                "。",  # Chinese period
                "．",  # Full-width dot
                ".",  # English period
                "！",  # Chinese exclamation mark
                "!",  # English exclamation mark
                "？",  # Chinese question mark
                "?",  # English question mark
                # # Whitespace characters
                # " ",  # Space
                # "\t",  # Tab
                # "\u3000",  # Full-width space
                # # Special characters
                # "\u200b",  # Zero-width space (used in some Asian languages)
            ]

        else:
            self.splitter_breaks = splitter_breaks

    def _length_function(self, text: list[str]) -> list[int]:
        return [self.token_len(i) for i in text]

    @staticmethod
    def _join_docs(docs: list[str], separator: str = "") -> Optional[str]:
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
        separator_len = self._length_function([separator])[0]

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
                        total -= self._length_function([current_doc[0]])[0] + (
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

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, _s in enumerate(separators):
            if _s == "":
                separator = _s
                break
            # 使用re.escape确保特殊字符被正确处理.正则表达式中，? 是一个元字符，表示"0次或1次重复
            pattern = _s if _s.startswith("(?") else re.escape(_s)
            if re.search(pattern, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        splits = _split_text_with_regex(text, separator, True)
        _good_splits = []
        _good_splits_lengths = []  # cache the lengths of the splits
        _separator = ""
        s_lens = self._length_function(splits)
        for s, s_len in zip(splits, s_lens):
            if s_len < self.chunk_size:
                _good_splits.append(s)
                _good_splits_lengths.append(s_len)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(
                        _good_splits, _separator, _good_splits_lengths
                    )
                    final_chunks.extend(merged_text)
                    _good_splits = []
                    _good_splits_lengths = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)

        if _good_splits:
            merged_text = self._merge_splits(
                _good_splits, _separator, _good_splits_lengths
            )
            final_chunks.extend(merged_text)

        return final_chunks

    def chunk(self, text: str) -> List[Document]:
        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(self._split_text(text, self.splitter_breaks))
            if len(i.strip()) > 0
        ]

    def __repr__(self) -> str:
        """Return a string representation of the SentenceChunker."""
        return f"RecursiveChunker(chunk_size={self.chunk_size}, "
