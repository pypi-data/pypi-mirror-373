import re
from typing import List, Optional, Literal

from duowen_agent.rag.models import Document
from openai import BaseModel
from pydantic import computed_field

from .base import BaseChunk

HEADER_SPLIT_CHR = "\n\n\n\n..._..._..._\n\n\n\n"


class MarkdownProcessor:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text
        self.code_block_pattern = re.compile(r"```.*?```", re.DOTALL)  # 匹配代码块
        self.atx_heading_pattern = re.compile(
            r"^(#{1,6})\s+(.+)$", re.MULTILINE
        )  # # 格式标题
        self.setext_heading_pattern = re.compile(
            r"^(.+)\n=+$|^(.+)\n-+$", re.MULTILINE
        )  # = 和 - 格式标题

    def _is_in_code_block(self, position):
        """检查某个位置是否在代码块中"""
        for match in self.code_block_pattern.finditer(self.markdown_text):
            if match.start() <= position < match.end():
                return True
        return False

    def _is_valid_setext_heading(self, match):
        """检查 = 和 - 格式的标题是否合法"""
        heading_text = match.group(1) or match.group(2)  # 获取标题文本
        underline_line = match.group(0).split("\n")[1]  # 获取 = 或 - 行
        # 检查 = 或 - 的长度是否至少与标题文本长度相同
        return len(underline_line) >= len(heading_text.strip())

    def convert_underline_headings(self):
        """
        将 Markdown 中的 `=` 和 `-` 格式的标题转换为 `#` 格式的标题。
        - `=` 替换为 `#`
        - `-` 替换为 `##`
        - 排除代码块中的内容。
        """

        def replace_heading(match):
            if self._is_in_code_block(match.start()):
                return match.group(0)  # 如果在代码块中，直接返回原内容
            if not self._is_valid_setext_heading(match):
                return match.group(0)  # 如果标题不合法，直接返回原内容
            heading_text = match.group(1) or match.group(2)
            if match.group(0).endswith("="):
                return f"# {heading_text.strip()}"  # 一级标题
            else:
                return f"## {heading_text.strip()}"  # 二级标题

        self.markdown_text = self.setext_heading_pattern.sub(
            replace_heading, self.markdown_text
        )
        return self.markdown_text

    def count_headings(self):
        """统计 Markdown 文档中的标题数量"""
        # 移除代码块
        text_without_code_blocks = self.code_block_pattern.sub("", self.markdown_text)

        # 查找所有匹配的标题（# 格式）
        atx_headings = [
            match.group(0)
            for match in self.atx_heading_pattern.finditer(text_without_code_blocks)
            if not self._is_in_code_block(match.start())
        ]

        # 查找所有匹配的标题（= 和 - 格式），并排除代码块中的内容
        setext_headings = [
            match.group(0)
            for match in self.setext_heading_pattern.finditer(text_without_code_blocks)
            if not self._is_in_code_block(match.start())
            and self._is_valid_setext_heading(match)
        ]

        return len(atx_headings) + len(setext_headings)

    def get_top_level_heading(self):
        """
        获取 Markdown 文档中最顶级的目录是几级标签。
        - 返回最顶级标题的级别（1 表示一级标题，2 表示二级标题，依此类推）。
        - 如果没有标题，返回 None。
        """
        # 移除代码块
        text_without_code_blocks = self.code_block_pattern.sub("", self.markdown_text)

        # 存储所有标题的级别
        heading_levels = []

        # 查找所有匹配的标题（# 格式）
        for match in self.atx_heading_pattern.finditer(text_without_code_blocks):
            if not self._is_in_code_block(match.start()):
                level = len(match.group(1))  # # 的数量
                heading_levels.append(level)

        # 查找所有匹配的标题（= 和 - 格式），并排除代码块中的内容
        for match in self.setext_heading_pattern.finditer(text_without_code_blocks):
            if not self._is_in_code_block(
                match.start()
            ) and self._is_valid_setext_heading(match):
                level = 1 if match.group(0).endswith("=") else 2  # = 为一级，- 为二级
                heading_levels.append(level)

        return min(heading_levels) if heading_levels else None


class MdLevelContent(BaseModel):
    heading: Optional[str] = None
    content: str
    level: int

    @computed_field
    def heading_and_content(self) -> str:
        if self.heading:
            return self.heading + "\n" + self.content
        else:
            return self.content


def check_header_cnt(
    text: str,
    header: List[str] = None,
) -> int:

    if header is None:
        header = ["#", "##", "###", "####", "#####", "######", "#######"]

    lines = text.split("\n")
    result = 0
    in_code_block = False
    opening_fence = ""

    for line in lines:
        stripped_line = line.strip()
        stripped_for_check = "".join(filter(str.isprintable, stripped_line))

        # 代码块检测逻辑
        if not in_code_block:
            if (
                stripped_for_check.startswith("```")
                and stripped_for_check.count("```") == 1
            ):
                in_code_block = True
                opening_fence = "```"
            elif stripped_for_check.startswith("~~~"):
                in_code_block = True
                opening_fence = "~~~"
        else:
            if stripped_for_check.startswith(opening_fence):
                in_code_block = False
                opening_fence = ""

        if not in_code_block and stripped_for_check.startswith(
            tuple(i + " " for i in header)
        ):
            result += 1
            continue

    return result


def split_header_text(text: str, level=1) -> List[MdLevelContent]:
    """
    Markdown目录分割
    输入: 内容；目录级别
    输出: List[[分割后的内容(不包含当前标题), 当前级别标题]]
    - 自动包含第一个匹配标题前的所有内容
    - 正确处理代码块中的伪标题
    """
    header = "#" * level
    lines = text.split("\n")
    result = []
    current_content = []
    current_header = None
    in_code_block = False
    opening_fence = ""

    for line in lines:
        stripped_line = line.strip()
        stripped_for_check = "".join(filter(str.isprintable, stripped_line))

        # 代码块检测逻辑
        if not in_code_block:
            if (
                stripped_for_check.startswith("```")
                and stripped_for_check.count("```") == 1
            ):
                in_code_block = True
                opening_fence = "```"
            elif stripped_for_check.startswith("~~~"):
                in_code_block = True
                opening_fence = "~~~"
        else:
            if stripped_for_check.startswith(opening_fence):
                in_code_block = False
                opening_fence = ""

        if not in_code_block and stripped_for_check.startswith(header + " "):
            result.append(
                MdLevelContent(
                    content="\n".join(current_content),
                    heading=current_header,
                    level=level,
                )
            )
            current_header = stripped_for_check.strip()
            current_content = []
            continue
        else:
            current_content.append(line)

    result.append(
        MdLevelContent(
            content="\n".join(current_content),
            heading=current_header,
            level=level,
        )
    )
    return result


class MarkdownHeaderChunker(BaseChunk):
    def __init__(
        self,
        chunk_size: int = 512,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[Document]:

        if MarkdownProcessor(text).count_headings() > 1:
            text = MarkdownProcessor(text).convert_underline_headings()

        else:
            return [
                Document(
                    page_content=text,
                    metadata=dict(token_count=self.token_len(text), chunk_index=0),
                )
            ]

        _doc = []

        def _chunk(text, level, parent_header=None):

            if parent_header is None:
                parent_header = []
            _parent_header = parent_header.copy()

            _header_str = "\n".join([i for i in _parent_header if i and i.strip()])

            if check_header_cnt(text, [level * "#"]) == 0:
                if (level + 1) <= 7:
                    _chunk(text, level + 1, _parent_header)
                else:
                    _doc.append(_header_str + HEADER_SPLIT_CHR + text)
                return

            _data = split_header_text(text, level)

            _current_doc = []

            for i in _data:

                if self.token_len(i.heading_and_content) > self.chunk_size:

                    if _current_doc:
                        _doc.append(_header_str + "\n\n".join(_current_doc))
                        _current_doc = []

                    if (level + 1) <= 7:
                        _chunk(i.content, level + 1, _parent_header + [i.heading])
                    else:
                        _header2 = _parent_header + [i.heading]
                        _header_str2 = "\n".join(
                            [i for i in _header2 if i and i.strip()]
                        )
                        _doc.append(_header_str2 + HEADER_SPLIT_CHR + text)
                else:
                    _merge_str = "\n\n".join(_current_doc + [i.heading_and_content])
                    if self.token_len(_merge_str) <= self.chunk_size:
                        _current_doc.append(i.heading_and_content)
                    else:
                        _doc.append(_header_str + "\n\n".join(_current_doc))
                        _current_doc = [i.heading_and_content]

            _doc.append(_header_str + "\n\n".join(_current_doc))
            _current_doc = []

        _chunk(text, 1)

        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(_doc)
            if len(i.strip()) > 0
        ]
