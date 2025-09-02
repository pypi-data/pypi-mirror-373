import math
import re
from typing import List, Literal, Optional

from duowen_agent.rag.models import Document
from .base import BaseChunk

BULLET_PATTERN = {
    # 英文法律条款（PART/Chapter/Section等）
    "english_legal": [
        r"\*{0,2}?PART (ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)",
        r"\*{0,2}?Chapter (I+V?|VI*|XI|IX|X)",
        r"\*{0,2}?Section [0-9]+",
        r"\*{0,2}?Article [0-9]+",
    ],
    # 中文法律条款结构（编/章/节/条 + 括号条款）
    "chinese_legal": [
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+(分?编|部分)",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+篇",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+章",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+节",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+条",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+款",
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+项",
        r"^\*{0,2}?[$（][零一二三四五六七八九十百]+[$）]",
        r"^\*{0,2}?[零一二三四五六七八九十百]+[ 、]",
        # r"^\*{0,2}?[0-9]{1,2}[\. 、]",
        # r"^\*{0,2}?[0-9]{1,2}\.[0-9]{1,2}[^a-zA-Z/%~-]",
        # r"^\*{0,2}?[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}",
        # r"^\*{0,2}?[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}",
        # r"^\*{0,2}?[$（][0-9]{1,2}[$）]",
    ],
    "official_document": [
        # 1. 顶层结构（较少见，多用于大型公文）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+编",  # 如“第一编 总则”
        # 2. 章（公文核心层级）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+章",  # 如“第一章 总体要求”
        # 3. 节（章下细分）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+节",  # 如“第一节 主要目标”
        # 4. 条（节下基础单位）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+条",  # 如“第一条 指导思想”
        # 5. 款（条下细分，通常无编号，若明确标注则包含）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+款",  # 如“第一款 适用范围”
        # 6. 项（款下细分，公文常用中文序号）
        r"^\*{0,2}?第[零一二三四五六七八九十百0-9]+项",  # 如“第一项 具体措施”
        r"^\*{0,2}?[一二三四五六七八九十百]+[、．]",  # 如“一、”“二．”（中文一级序号）
        r"^\*{0,2}?[（(][一二三四五六七八九十百]+[）)]",  # 如“（一）”“(二)”（中文二级序号）
        # 7. 目（项的进一步细分，常用阿拉伯数字）
        r"^\*{0,2}?[0-9]+[、．]",  # 如“1、”“2．”（阿拉伯数字一级）
        r"^\*{0,2}?[（(][0-9]+[）)]",  # 如“（1）”“(2)”（阿拉伯数字二级）
        r"^\*{0,2}?[①②③④⑤⑥⑦⑧⑨⑩]",  # 如“①”“②”（圈码序号）
    ],
}


def not_bullet(line):
    patt = [r"\*{0,2}?0", r"\*{0,2}?[0-9]+ +[0-9~个只-]", r"\*{0,2}?[0-9]+\.{2,}"]
    return any([re.match(r, line) for r in patt])


def is_bullet_document(text):
    """
    判断文档是否属于条款类结构
    :param text: 输入文本
    :param threshold: 匹配比例阈值（默认5%）
    :return: True/False 及匹配详情
    """
    total_lines = len(text.split("\n"))

    # 动态阈值规则（基于行数的简单分段）
    if total_lines <= 5:
        min_lines = 2  # 5行以内至少2行匹配
    elif total_lines <= 20:
        min_lines = max(2, math.ceil(total_lines * 0.3))  # 20行以内30%
    else:
        min_lines = max(3, math.ceil(total_lines * 0.05))  # 长文档5%

    def _structured(bullet_type, text):
        match_count = 0

        # 合并所有正则模式
        all_patterns = [re.compile(p) for p in BULLET_PATTERN[bullet_type]]

        # 逐行检测
        for line in text.split("\n"):
            stripped_line = "".join(filter(str.isprintable, line)).strip()
            if not stripped_line:
                continue

            # 判断是否匹配条款模式
            for pattern in all_patterns:
                if pattern.match(stripped_line) and not not_bullet(stripped_line):
                    match_count += 1
                    break  # 避免重复计数

        return {
            "bullet_type": bullet_type,
            "matched_lines": match_count,
            "total_lines": total_lines,
        }

    data_list = []
    for i in BULLET_PATTERN:
        data_list.append(_structured(i, text))

    data = {}
    for x in data_list:
        if x["matched_lines"] > min_lines:
            data = x
            break

    if not data:
        data = max(data_list, key=lambda x: x["matched_lines"])

    data["is_structured"] = data["matched_lines"] > min_lines

    return data


def split_bullet_text(text: str, pattern: str) -> List[str]:
    """
    Markdown目录分割
    输入: 内容；目录级别
    输出: List[[分割后的内容(不包含当前标题), 当前级别标题]]
    - 自动包含第一个匹配标题前的所有内容
    - 正确处理代码块中的伪标题
    """
    lines = text.split("\n")
    result = []
    current_content = []

    re_pattern = re.compile(pattern)

    for line in lines:
        stripped_for_check = "".join(filter(str.isprintable, line.strip()))

        if re_pattern.match(stripped_for_check):
            result.append("\n".join(current_content))
            current_content = [line]
            continue
        else:
            current_content.append(line)

    if current_content:
        result.append("\n".join(current_content))

    return result


class BulletChunker(BaseChunk):
    def __init__(
        self,
        chunk_size: int = 512,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
        bullet_pattern_type: Optional[
            Literal["english_legal", "chinese_legal", "official_document"]
        ] = None,
        **kwargs
    ):
        super().__init__(token_count_type=token_count_type)
        self.chunk_size = chunk_size
        self.bullet_pattern_type = bullet_pattern_type

    def chunk(self, text: str) -> List[Document]:

        if self.bullet_pattern_type is None:
            _chk = is_bullet_document(text)

            if _chk["is_structured"] is False:
                return [
                    Document(
                        page_content=text,
                        metadata=dict(
                            token_count=self.token_len(text),
                            chunk_index=0,
                            is_structured=False,
                        ),
                    )
                ]
            rule_pattern = BULLET_PATTERN[_chk["bullet_type"]]
        else:
            rule_pattern = BULLET_PATTERN[self.bullet_pattern_type]

        _doc = []

        def _chunk(text, level):
            _data = split_bullet_text(text, rule_pattern[level])

            if len(_data) == 1:
                if (level + 1) < len(rule_pattern):
                    _chunk(text, level + 1)
                else:
                    _doc.append(text)
                return

            _current_doc = []

            for i in _data:

                if self.token_len(i) > self.chunk_size:

                    if _current_doc:
                        _doc.append("\n\n".join(_current_doc))
                        _current_doc = []

                    if (level + 1) < len(rule_pattern):

                        _chunk(i, level + 1)
                    else:
                        _doc.append(i)
                else:
                    _merge_str = "\n\n".join(_current_doc + [i])
                    if self.token_len(_merge_str) <= self.chunk_size:
                        _current_doc.append(i)
                    else:
                        _doc.append("\n\n".join(_current_doc))
                        _current_doc = [i]

            if _current_doc:
                _doc.append("\n\n".join(_current_doc))
                _current_doc = []

        _chunk(text, 0)

        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(_doc)
            if len(i.strip()) > 0
        ]
