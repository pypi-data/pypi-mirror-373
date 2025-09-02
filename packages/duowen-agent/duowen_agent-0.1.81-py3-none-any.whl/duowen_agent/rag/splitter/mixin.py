import logging
from typing import Union, List, Literal

from duowen_agent.rag.models import Document
from .base import BaseChunk
from .bullet import BulletChunker, is_bullet_document
from .markdown import MarkdownHeaderChunker, check_header_cnt, HEADER_SPLIT_CHR
from .recursive import RecursiveChunker
from .regex import JinaTextChunker
from .separator import SeparatorChunker
from .word import WordChunker
from ..extractor.table import markdown_table_to_kv_list


class FastMixinChunker(BaseChunk):

    def __init__(
        self,
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

    @staticmethod
    def table_to_list(text):
        try:
            return markdown_table_to_kv_list(text)
        except Exception as e:
            logging.warning(f"markdown_table_to_kv_list 识别异常: {text[:100]}...")
            return text

    def chunk(self, text: str) -> List[Document]:
        """
        1. markdown表格转 kvlist
        2. markdown切割
        3. 规范文书类切割=>regex切割(实验性质) 失败 降级=> 换行符切割
        4. 递归切割
        5. word切割（chunk_overlap 生效）
        """

        markdown_chk = check_header_cnt(text)
        bullet_chk = is_bullet_document(text)

        slices = []

        try:
            # print(
            #     len(text.split("\n")),
            #     markdown_chk,
            #     bullet_chk["matched_lines"],
            #     bullet_chk["is_structured"],
            # )
            if (
                bullet_chk["is_structured"]
                and bullet_chk["matched_lines"] >= markdown_chk
            ):

                data1 = BulletChunker(
                    chunk_size=self.chunk_size, token_count_type=self.token_count_type
                ).chunk(text)
            else:
                data1 = MarkdownHeaderChunker(
                    chunk_size=self.chunk_size, token_count_type=self.token_count_type
                ).chunk(text)
        except Exception as e:
            logging.warning(
                f"BulletChunker or MarkdownHeaderChunker error {str(e)},data: {text[:100]}..."
            )
            data1 = [Document(page_content=text)]

        for _d1 in data1:

            if _d1.metadata.get("token_count") > self.chunk_size:

                # 提取 markdown分割得到的的表头， 后续切分需要加上该表头
                if HEADER_SPLIT_CHR in _d1.page_content:
                    _ddd = _d1.page_content.strip(HEADER_SPLIT_CHR)
                    _header = _ddd[0].strip() + "\n\n"
                    _text = _ddd[1:].strip()
                else:
                    _header = ""
                    _text = _d1.page_content

                _text = self.table_to_list(_d1.page_content)
                try:
                    data2 = JinaTextChunker(
                        chunk_size=self.chunk_size,
                        token_count_type=self.token_count_type,
                    ).chunk(_text)
                except Exception as e:
                    data2 = SeparatorChunker(
                        chunk_size=self.chunk_size,
                        chunk_overlap=0,
                        token_count_type=self.token_count_type,
                    ).chunk(_text)

                for _d2 in data2:
                    if _d2.metadata.get("token_count") > self.chunk_size:
                        data3 = RecursiveChunker(
                            chunk_size=self.chunk_size,
                            token_count_type=self.token_count_type,
                        ).chunk(_d2.page_content)
                        for _d3 in data3:
                            if _d3.metadata.get("token_count") > self.chunk_size:
                                data4 = WordChunker(
                                    chunk_size=self.chunk_size,
                                    chunk_overlap=self.chunk_overlap,
                                    token_count_type=self.token_count_type,
                                ).chunk(_d3.page_content)
                                for _d4 in data4:
                                    _d4.metadata = {**_d1.metadata, **_d4.metadata}
                                    slices.append(_header + _d4.page_content)
                            else:
                                _d3.metadata = {**_d1.metadata, **_d3.metadata}
                                slices.append(_header + _d3.page_content)
                    else:
                        _d2.metadata = {**_d1.metadata, **_d2.metadata}
                        slices.append(_header + _d2.page_content)
            else:
                slices.append(_d1.page_content)

        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(slices)
            if len(i.strip()) > 0
        ]

    def __repr__(self) -> str:
        return (
            f"FastMixinChunker("
            f"chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
