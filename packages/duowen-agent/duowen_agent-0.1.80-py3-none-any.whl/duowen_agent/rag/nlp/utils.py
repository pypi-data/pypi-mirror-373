import re
from typing import Optional, List

import chardet
from hanziconv import HanziConv
from pydantic import BaseModel, Field


def traditional_to_simplified(text: str) -> str:
    """将繁体中文文本转换为简体中文"""
    return HanziConv.toSimplified(text)


def fullwidth_to_halfwidth(text: str) -> str:
    """将全角字符转换为半角字符"""
    converted = []
    for char in text:
        code_point = ord(char)
        if code_point == 0x3000:  # 处理全角空格
            converted.append(0x0020)
        else:
            converted.append(code_point - 0xFEE0)

        # 处理非可转换范围的字符
        if not (0x0020 <= converted[-1] <= 0x7E):
            converted[-1] = code_point

    return "".join(chr(c) for c in converted)


CHINESE_CHAR_PATTERN = re.compile("[一-龥]")


def check_chinese_char(text):
    if text == "":
        return False

    if CHINESE_CHAR_PATTERN.search(text):
        return True

    return False


def is_english(texts):
    if not texts:
        return False

    pattern = re.compile(r"[`a-zA-Z0-9\s.,':;/\"?<>!\(\)\-]")

    if isinstance(texts, str):
        texts = list(texts)
    elif isinstance(texts, list):
        texts = [t for t in texts if isinstance(t, str) and t.strip()]
    else:
        return False

    if not texts:
        return False

    eng = sum(1 for t in texts if pattern.fullmatch(t.strip()))
    return (eng / len(texts)) > 0.8


def is_chinese(text):
    if not text:
        return False
    chinese = 0
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            chinese += 1
    if chinese / len(text) > 0.2:
        return True
    return False


def is_number(s):
    if s >= "\u0030" and s <= "\u0039":
        return True
    else:
        return False


def is_alphabet(s):
    if (s >= "\u0041" and s <= "\u005a") or (s >= "\u0061" and s <= "\u007a"):
        return True
    else:
        return False


PATTERN_ENDS_WITH_LETTER = re.compile(r".*[a-zA-Z]$")


def naive_tokenize(text: str) -> list[str]:
    """简单的分词函数，对连续字母单词插入空格分隔"""
    tokens = []
    for word in text.split():
        if (
            tokens  # 非空
            and PATTERN_ENDS_WITH_LETTER.match(tokens[-1])  # 前一个单词以字母结尾
            and PATTERN_ENDS_WITH_LETTER.match(word)  # 当前单词以字母结尾
        ):
            tokens.append(" ")
        tokens.append(word)
    return tokens


class ExtractionResult(BaseModel):
    """正则抽取结果的Pydantic模型"""

    text: str = Field(..., alias="s", description="匹配到的文本内容")
    span: tuple[int, int] = Field(
        ..., alias="o", description="文本在原文中的位置范围（起始，结束）"
    )
    type: Optional[str] = Field(None, alias="t", description="匹配结果的类型标识")

    class Config:
        populate_by_name = True
        json_schema_extra = {"example": {"s": "2023", "o": (5, 9), "t": "year"}}


class Extractor(object):
    """规则抽取器"""

    def __init__(self):
        self.email_pattern = re.compile(
            r"(?<=[^0-9a-zA-Z.\-])"
            r"([a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+(?:\.[a-zA-Z0-9_.-]+)*\.[a-zA-Z0-9]{2,6})"
            r"(?=[^0-9a-zA-Z.\-])"
        )

        self.url_pattern = re.compile(
            r"(?<=[^.])((?:(?:https?|ftp|file)://|(?<![a-zA-Z\-\.])www\.)"
            r"[\-A-Za-z0-9\+&@\(\)#/%\?=\~_|!:\,\.\;]+[\-A-Za-z0-9\+&@#/%=\~_\|])"
            r"(?=[<\u4E00-\u9FA5￥，。；！？、“”‘’>（）—《》…● \t\n])"
        )

        ip_single = r"(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)"
        self.ip_address_pattern = re.compile(
            "".join(
                [
                    r"(?<=[^0-9])(",
                    ip_single,
                    r"\.",
                    ip_single,
                    r"\.",
                    ip_single,
                    r"\.",
                    ip_single,
                    ")(?=[^0-9])",
                ]
            )
        )

        self.id_card_pattern = re.compile(
            r"(?<=[^0-9a-zA-Z])"
            r"((1[1-5]|2[1-3]|3[1-7]|4[1-6]|5[0-4]|6[1-5]|71|81|82|91)"
            r"(0[0-9]|1[0-9]|2[0-9]|3[0-4]|4[0-3]|5[1-3]|90)"
            r"(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-3]|5[1-7]|6[1-4]|7[1-4]|8[1-7])"
            r"(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])"
            r"\d{3}[0-9xX])"
            r"(?=[^0-9a-zA-Z])"
        )

        self.cell_phone_pattern = re.compile(
            r"(?<=[^\d])(((\+86)?([- ])?)?((1[3-9][0-9]))([- ])?\d{4}([- ])?\d{4})(?=[^\d])"
        )
        self.landline_phone_pattern = re.compile(
            r"(?<=[^\d])(([\(（])?0\d{2,3}[\)） —-]{1,2}\d{7,8}|\d{3,4}[ -]\d{3,4}[ -]\d{4})(?=[^\d])"
        )

    @staticmethod
    def _extract_base(pattern, text, typing, with_type=True) -> List[ExtractionResult]:
        """正则抽取器的基础函数

        Args:
            pattern(re.compile): 正则表达式对象
            text(str): 字符串文本
            type(str): 抽取的字段类型

        Returns:
            list: 返回结果

        """
        # `s` is short for text string,
        # `o` is short for offset
        # `t` is short for type
        if with_type:
            return [
                ExtractionResult(
                    **{
                        "s": item.group(1),
                        "o": (item.span()[0] - 1, item.span()[1] - 1),
                        "t": typing,
                    }
                )
                for item in pattern.finditer(text)
            ]
        else:
            return [
                ExtractionResult(
                    **{
                        "s": item.group(1),
                        "o": (item.span()[0] - 1, item.span()[1] - 1),
                    }
                )
                for item in pattern.finditer(text)
            ]

    def extract_email(self, text, with_type=True) -> List[ExtractionResult]:
        """提取文本中的 E-mail

        Args:
            text(str): 字符串文本

        Returns:
            list: email列表

        """
        return self._extract_base(
            self.email_pattern, text, typing="email", with_type=with_type
        )

    def extract_id_card(self, text, with_type=True) -> List[ExtractionResult]:
        """提取文本中的 ID 身份证号

        Args:
            text(str): 字符串文本

        Returns:
            list: 身份证信息列表

        """
        return self._extract_base(
            self.id_card_pattern, text, typing="id", with_type=with_type
        )

    def extract_ip_address(self, text, with_type=True) -> List[ExtractionResult]:
        """提取文本中的 IP 地址

        Args:
            text(str): 字符串文本

        Returns:
            list: IP 地址列表

        """
        return self._extract_base(
            self.ip_address_pattern, text, typing="ip", with_type=with_type
        )

    def extract_phone_number(self, text, with_type=True) -> List[ExtractionResult]:
        """从文本中抽取出电话号码

        Args:
            text(str): 字符串文本

        Returns:
            list: 电话号码列表

        """
        cell_results = self._extract_base(
            self.cell_phone_pattern, text, typing="tel", with_type=with_type
        )
        landline_results = self._extract_base(
            self.landline_phone_pattern, text, typing="tel", with_type=with_type
        )

        return cell_results + landline_results

    def extract_url(self, text, with_type=True) -> List[ExtractionResult]:
        """提取文本中的url链接

        Args:
            text(str): 字符串文本

        Returns:
            list: url列表

        """
        return self._extract_base(
            self.url_pattern, text, typing="url", with_type=with_type
        )

    def extract_info(self, text, with_type=True) -> List[ExtractionResult]:
        text = "".join(["￥", text, "￥"])  # 因 # 可能出现在 url 中

        results_list = list()

        results_list.extend(
            self._extract_base(
                self.url_pattern, text, typing="url", with_type=with_type
            )
        )
        results_list.extend(
            self._extract_base(
                self.email_pattern, text, typing="email", with_type=with_type
            )
        )
        results_list.extend(
            self._extract_base(
                self.id_card_pattern, text, typing="id", with_type=with_type
            )
        )
        results_list.extend(
            self._extract_base(
                self.ip_address_pattern, text, typing="ip", with_type=with_type
            )
        )
        results_list.extend(self.extract_phone_number(text, with_type=with_type))

        return results_list


all_codecs = [
    "utf-8",
    "gb2312",
    "gbk",
    "utf_16",
    "ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp273",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "windows-1250",
    "windows-1251",
    "windows-1252",
    "windows-1253",
    "windows-1254",
    "windows-1255",
    "windows-1256",
    "windows-1257",
    "windows-1258",
    "latin-2",
]


def find_codec(blob):
    """检测二进制数据的编码格式"""
    detected = chardet.detect(blob[:1024])
    if detected["confidence"] > 0.5:
        if detected["encoding"] == "ascii":
            return "utf-8"

    for c in all_codecs:
        try:
            blob[:1024].decode(c)
            return c
        except Exception:
            pass
        try:
            blob.decode(c)
            return c
        except Exception:
            pass

    return "utf-8"
