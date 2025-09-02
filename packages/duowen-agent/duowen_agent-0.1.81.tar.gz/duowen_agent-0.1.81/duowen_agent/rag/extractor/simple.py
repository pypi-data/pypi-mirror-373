import warnings

warnings.filterwarnings(
    "ignore",
    message="builtin type .* has no __module__ attribute",
    category=DeprecationWarning,
)

from pathlib import Path
from typing import List

import mammoth
import pymupdf4llm
from markdownify import markdownify

from duowen_agent.rag.extractor.html_parser import MainContentExtractor
from duowen_agent.rag.extractor.pptx_extractor import PptxExtractor
from duowen_agent.rag.extractor.xls_extractor import XlsExtractor
from duowen_agent.rag.extractor.xlsx_extractor import XlsxExtractor


# from pptx2md import convert


def word2md(file_path: str) -> str:
    def convert_image(image):
        return {"src": ""}

    with open(file_path, "rb") as docx_file:

        html: str = mammoth.convert_to_html(
            fileobj=docx_file,
            convert_image=mammoth.images.img_element(convert_image),
        ).value

    return markdownify(
        html,
        escape_misc=False,
        escape_asterisks=False,
        escape_underscores=False,
    )


def pdf2md(file_path: str) -> str:
    md_text = pymupdf4llm.to_markdown(file_path)
    return md_text


def ppt2md(file_path: str) -> str:
    return PptxExtractor().convert(file_path)


def html2md(content: str) -> str:
    return MainContentExtractor.extract(content, output_format="markdown")


def excel_parser(file_path: str) -> List[str]:
    match _suffix := Path(file_path).suffix.lower():
        case ".xlsx":
            return XlsxExtractor(file_path).extract()
        case ".xls":
            return XlsExtractor(file_path).extract()
        case _:
            raise ValueError(f"无法识别的excel格式:{_suffix}")
