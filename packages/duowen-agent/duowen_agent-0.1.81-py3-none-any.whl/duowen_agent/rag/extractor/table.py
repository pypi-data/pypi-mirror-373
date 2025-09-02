"""markdown 表格解析"""

import re

import mistune
from bs4 import BeautifulSoup

# 用户提供的正则表达式模式
TABLE_PATTERN = (
    r"^ {0,3}\|(?P<table_head>.+)\|[ \t]*\n"
    r" {0,3}\|(?P<table_align> *[-:]+[-| :]*)\|[ \t]*\n"
    r"(?P<table_body>(?: {0,3}\|.*\|[ \t]*(?:\n|$))*)\n*"
)
NP_TABLE_PATTERN = (
    r"^ {0,3}(?P<nptable_head>\S.*\|.*)\n"
    r" {0,3}(?P<nptable_align>[-:]+ *\|[-| :]*)\n"
    r"(?P<nptable_body>(?:.*\|.*(?:\n|$))*)\n*"
)


def markdown_table_to_kv_list(text):
    # 查找所有表格并记录位置
    tables = []
    seen = set()

    # 匹配标准表格
    for match in re.finditer(TABLE_PATTERN, text, flags=re.MULTILINE):
        start, end = match.span()
        if (start, end) not in seen:
            table_text = match.group(0)
            tables.append((start, end, table_text))
            seen.add((start, end))

    # 匹配非标准表格
    for match in re.finditer(NP_TABLE_PATTERN, text, flags=re.MULTILINE):
        start, end = match.span()
        if (start, end) not in seen:
            table_text = match.group(0)
            tables.append((start, end, table_text))
            seen.add((start, end))

    if not tables:
        return text

    print(tables)

    # 按起始位置逆序排序
    tables_sorted = sorted(tables, key=lambda x: -x[0])

    # 初始化Markdown解析器（确保已安装mistune并启用表格插件）
    md = mistune.create_markdown(escape=True, plugins=["table"])

    # 处理每个表格并构建替换段
    segments = []
    last_end = len(text)
    for start, end, table_text in tables_sorted:
        # 转换为HTML
        html = md(table_text.strip())

        if not (
            html.strip().startswith("<table>") and not html.strip().endswith("</table>")
        ):
            return text

        # 转换为JSONL
        jsonl_str = html_table_to_kv_list(html) + "\n\n"

        # 记录替换段
        if jsonl_str.strip():
            segments.append((start, end, jsonl_str))

    # 构建替换后的文本（从后向前替换）
    new_text = []
    last_pos = len(text)
    for start, end, jsonl_str in sorted(segments, key=lambda x: -x[0]):
        new_text.append(text[end:last_pos])
        new_text.append(jsonl_str)
        last_pos = start
    new_text.append(text[:last_pos])
    new_text.reverse()

    return "".join(new_text)


def html_table_to_kv_list(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return ""

    # 提取表头（处理合并单元格）
    headers = []
    header_row = None

    # 尝试从thead或第一个tr获取表头
    if thead := table.find("thead"):
        header_row = thead.find("tr")
    elif first_tr := table.find("tr"):
        header_row = first_tr

    if header_row:
        for cell in header_row.find_all(["th", "td"]):
            # 处理colspan合并
            colspan = int(cell.get("colspan", 1))
            cell_text = cell.get_text(strip=True)
            headers.extend([cell_text] * colspan)

    # 提取数据行（处理合并单元格）
    rows = []
    tbody = table.find("tbody") or table

    for row in tbody.find_all("tr"):
        # 跳过表头行
        if row == header_row:
            continue

        # 处理单元格合并
        cells = []
        for cell in row.find_all(["td", "th"]):
            # 处理colspan合并
            colspan = int(cell.get("colspan", 1))
            cell_text = cell.get_text(strip=True)
            cells.extend([cell_text] * colspan)

        # 生成键值序列
        if len(cells) == len(headers):
            pairs = [f"{key}:{value}" for key, value in zip(headers, cells)]
            rows.append(";".join(pairs))

    return "\n".join(rows)
