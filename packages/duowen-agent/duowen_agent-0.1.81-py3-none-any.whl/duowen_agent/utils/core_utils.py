import logging
import random
import re
import string
import time
from functools import wraps
from importlib import import_module
from typing import Callable, Iterator
from typing import Coroutine, Dict, List, Optional, Type

import json5
import xmltodict
from duowen_agent.error import ObserverException
from pydantic import ValidationError, BaseModel

logger = logging.getLogger(__name__)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Args:
        dotted_path: eg promptulate.schema.MessageSet

    Returns:
        Class corresponding to dotted path.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


def listdict_to_string(
    data: List[Dict],
    prefix: Optional[str] = "",
    suffix: Optional[str] = "\n",
    item_prefix: Optional[str] = "",
    item_suffix: Optional[str] = ";\n\n",
    is_wrap: bool = True,
) -> str:
    """Convert List[Dict] type data to string type"""
    wrap_ch = "\n" if is_wrap else ""
    result = f"{prefix}"
    for item in data:
        temp_list = ["{}:{} {}".format(k, v, wrap_ch) for k, v in item.items()]
        result += f"{item_prefix}".join(temp_list) + f"{item_suffix}"
    result += suffix
    return result[:-2]


def generate_unique_id(prefix: str = "dw") -> str:
    timestamp = int(time.time() * 1000)
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    unique_id = f"{prefix}-{timestamp}-{random_string}"
    return unique_id


def convert_backslashes(path: str):
    """Convert all \\ to / of file path."""
    return path.replace("\\", "/")


def hint(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ret = fn(*args, **kwargs)
        logger.debug(f"function {fn.__name__} is running now")
        return ret

    return wrapper


def remove_think(content: str):
    # 优先尝试匹配完整的 <think>...</think> 模式
    full_pattern = r"<think>.*?</think>"
    full_match = re.search(full_pattern, content, flags=re.DOTALL)
    if full_match:
        # 找到完整模式，移除第一个匹配项
        return re.sub(full_pattern, "", content, count=1, flags=re.DOTALL).strip()

    # 没有完整模式时，匹配从开头到第一个 </think>
    partial_pattern = r"^.*?</think>"
    partial_match = re.search(partial_pattern, content, flags=re.DOTALL)
    if partial_match:
        # 移除匹配的部分
        return re.sub(partial_pattern, "", content, count=1, flags=re.DOTALL).strip()

    # 两种情况都不存在时返回原内容
    return content.strip()


def extract_think(content: str):
    # 优先尝试匹配完整的 <think>...</think> 模式
    full_pattern = r"<think>(.*?)</think>"
    full_match = re.search(full_pattern, content, flags=re.DOTALL)
    if full_match:
        return full_match.group(1).strip()

    # 没有完整模式时，匹配从开头到第一个 </think> 之前的内容
    partial_pattern = r"^(.*?)</think>"
    partial_match = re.search(partial_pattern, content, flags=re.DOTALL)
    if partial_match:
        return partial_match.group(1).strip()

    # 两种情况都不存在时返回None
    return None


def separate_reasoning_and_response(content: str):
    return {
        "content": remove_think(content),
        "content_reasoning": extract_think(content),
    }


def record_time():
    def decorator(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Callable:
            start_time = time.time()
            ret = fn(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"[duowen-agent timer] <{fn.__name__}> run {duration}s")
            return ret

        return wrapper

    return decorator


def async_record_time():
    """异步函数设计的执行时间记录装饰器
    @async_record_time()
    async def async_operation():
        await asyncio.sleep(1.5)
        # 模拟异步操作
        return "result"
    """

    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Coroutine:
            start_time = time.time()
            try:
                # 注意这里需要使用 await 来等待异步函数执行
                return await fn(*args, **kwargs)
            finally:
                # 使用高精度时间计算
                duration = time.time() - start_time
                logger.debug(
                    f"[duowen-agent async-timer] <{fn.__name__}> run {duration:.4f}s"
                )

        # # 类型检查确保装饰的是协程函数
        # if not asyncio.iscoroutinefunction(fn):
        #     raise TypeError(
        #         "async_record_time decorator can only be applied to async functions"
        #     )

        return async_wrapper

    return decorator


def retrying(
    func,
    func_params: dict = None,
    max_retries=3,
    exception_types=(ObserverException,),
    time_sleep=0.1,
):
    for attempt in range(max_retries):
        try:
            if func_params:
                return func(**func_params)
            else:
                return func()
        except exception_types:
            if attempt == max_retries - 1:
                raise
            else:
                time.sleep(time_sleep)
                continue
        except Exception as e:
            raise


def parse_xml_markdown(xml_string: str) -> dict:
    """
    从包含 XML 的字符串中提取 XML 内容并解析为字典
    支持多种 XML 代码块标记格式

    参数:
        xml_string: 可能包含 XML 代码块标记的字符串

    返回:
        解析后的字典对象

    异常:
        如果无法提取有效的 XML 内容则抛出异常
    """
    # 清理输入字符串
    xml_string = xml_string.strip()

    # 定义可能的 XML 代码块起始和结束标记
    start_markers = [
        r"```xml",  # Markdown 代码块标记
        r"```",  # 通用代码块标记
        r"``",  # 短代码块标记
        r"`",  # 内联代码标记
        r"<\?xml",  # XML 声明
        r"<",  # 普通 XML 起始
    ]

    # 尝试匹配起始标记
    start_index = -1
    start_marker = None

    for marker in start_markers:
        match = re.search(marker, xml_string, re.IGNORECASE)
        if match:
            start_index = match.start()
            start_marker = marker
            break

    # 如果没有找到起始标记，尝试直接解析整个字符串
    if start_index == -1:
        try:
            return xmltodict.parse(xml_string)
        except Exception as e:
            logging.error(f"Failed to parse XML: {e}\nContent: {xml_string}")
            raise Exception("Could not find XML block or parse content as XML")

    # 计算 XML 内容实际起始位置
    content_start = start_index
    if start_marker not in ["<", r"<\?xml"]:
        content_start += len(start_marker)

    # 提取 XML 结束位置（查找对称的结束标记）
    end_index = -1
    end_marker = None

    # 对称结束标记映射
    end_marker_map = {
        r"```xml": "```",
        r"```": "```",
        r"``": "``",
        r"`": "`",
        r"<\?xml": ">",  # XML 声明结束
        r"<": ">",  # XML 标签结束
    }

    # 特殊处理：完整的 XML 文档应包含根元素结束标记
    if start_marker in ["<", r"<\?xml"]:
        # 查找根元素的结束位置
        try:
            # 尝试解析整个字符串中 start_index 之后的内容
            parsed = xmltodict.parse(xml_string[content_start:])
            # 如果解析成功，则整个片段都是 XML
            return parsed
        except Exception:
            # 如果失败，则继续查找结束标记
            pass

    # 获取对应的结束标记
    target_end_marker = end_marker_map.get(start_marker, None)

    if target_end_marker:
        # 查找结束标记
        end_index = xml_string.find(target_end_marker, content_start)
        if end_index == -1:
            # 如果找不到对称结束标记，尝试查找最近的结束标记
            possible_ends = list(set(end_marker_map.values()))
            for marker in possible_ends:
                pos = xml_string.find(marker, content_start)
                if pos != -1 and (end_index == -1 or pos < end_index):
                    end_index = pos
                    end_marker = marker

    # 如果找到结束标记
    if end_index != -1:
        # 调整结束位置（包含结束标记的长度）
        content_end = end_index
        if end_marker and end_marker not in [">"]:
            content_end += len(end_marker)

        # 提取 XML 内容
        xml_content = xml_string[content_start:content_end].strip()

        try:
            # 使用 xmltodict 解析 XML
            return xmltodict.parse(xml_content)
        except Exception as e:
            logging.error(f"XML parsing failed: {e}\nExtracted content: {xml_content}")
            raise Exception("Failed to parse extracted XML content")

    # 所有尝试都失败
    logging.error(f"Could not extract XML block from content: {xml_string}")
    raise Exception("Could not find complete XML block in the output")


def xml_observation(content: str, pydantic_obj: Type[BaseModel]):
    try:
        _content = remove_think(content)
        _data1 = parse_xml_markdown(_content)
        if len(_data1) == 1:
            _data1 = next(iter(_data1.values()))

    except ValueError as e:
        raise ObserverException(
            predict_value=remove_think(content),
            expect_value="valid XML format",
            err_msg=f"XML extraction failed: {str(e)}",
        )
    try:
        return pydantic_obj(**_data1)
    except ValidationError as e:
        raise ObserverException(
            predict_value=str(_data1),
            expect_value=str(pydantic_obj.model_json_schema()),
            err_msg=f"Pydantic validation failed: {str(e)}",
        )


def parse_json_markdown(json_string: str) -> dict:
    # Get json from the backticks/braces
    json_string = json_string.strip()
    starts = ["```json", "```", "``", "`", "{"]
    ends = ["```", "``", "`", "}"]
    end_index = -1
    for s in starts:
        start_index = json_string.find(s)
        if start_index != -1:
            if json_string[start_index] != "{":
                start_index += len(s)
            break
    if start_index != -1:
        for e in ends:
            end_index = json_string.rfind(e, start_index)
            if end_index != -1:
                if json_string[end_index] == "}":
                    end_index += 1
                break
    if start_index != -1 and end_index != -1 and start_index < end_index:
        extracted_content = json_string[start_index:end_index].strip()
        parsed = json5.loads(extracted_content)
    else:
        logging.error(f"parse_json_markdown content: {json_string}")
        raise Exception("Could not find JSON block in the output.")

    return parsed


def json_observation(content: str, pydantic_obj: Type[BaseModel]):
    try:
        _content = remove_think(content)
        _data1 = parse_json_markdown(_content)
    except ValueError as e:
        raise ObserverException(
            predict_value=remove_think(content),
            expect_value="json format data",
            err_msg=f"observation error jsonload, msg: {str(e)}",
        )
    try:
        return pydantic_obj(**_data1)
    except ValidationError as e:
        raise ObserverException(
            predict_value=_content,
            expect_value=str(pydantic_obj.model_json_schema()),
            err_msg=f"observation error ValidationError, msg: {str(e)}",
        )


def stream_to_string(stream: Iterator[str]) -> str:
    response = ""
    for chunk in stream:
        response += chunk
    return response
