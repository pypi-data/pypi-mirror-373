import logging
import re
import time
import traceback
from copy import deepcopy
from typing import Union, Optional, List, TypeVar, Iterable, Type, Callable

from duowen_agent.llm import MessagesSet
from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.tools.base import BaseTool
from duowen_agent.tools.manager import ToolManager
from duowen_agent.tools.mcp_client import McpClient
from duowen_agent.utils.core_utils import stream_to_string
from duowen_agent.utils.string_template import StringTemplate
from duowen_agent.utils.xml_tool_parser import parse_xml_tool_calls
from lxml import etree
from pydantic import BaseModel

from .base import BaseAgent
from .state import Resources
from ..error import ObserverException
from ..llm.chat_model import BaseAIChat
from ..utils.core_utils import generate_unique_id, remove_think

REACT_SYSTEM_PROMPT_TEMPLATE = StringTemplate(
    template_format="jinja2",
    template="""作为勤勉的任务代理，你的目标是尽可能高效地完成提供的任务或问题。

## Tools
你可以使用以下工具，工具信息通过以下结构描述提供：
{{tool_descriptions}}

## Output Format
请使用以下XML格式回答问题。仅返回XML，不要有解释。否则将会受到惩罚。
输出必须符合以下XML格式规范。仅返回XML，不要解释。

```xml
<response>
  <analysis>当前操作思路及原因分析</analysis>
  <function_calls>
    <invoke name="工具名称">
      <parameter name="参数名1">参数值1</parameter>
      <parameter name="参数名2">["参数值1","参数值2"]</parameter> 
    </invoke>
  </function_calls>
</response>
```

如果使用此格式，用户将按以下格式回应：

<function_calls_result>
  <name>工具名称</name>
  <result>调用结果</result>
</function_calls_result>


你应持续重复上述格式，同时每次Observation进行反思，直到获得足够信息无需继续使用工具即可回答问题。此时必须改用以下两种格式之一：

- 若能回答问题：

```xml
<response>
  <analysis>最终判断依据及结论</analysis>
  <function_calls>
    <invoke name="final_answer">
      <parameter name="content">你的答案</parameter>
    </invoke>
  </function_calls>
</response>
```

- 若当前上下文无法回答问题：

```xml
<response>
  <analysis>无法解决的原因分析</analysis>
  <function_calls>
    <invoke name="final_answer">
      <parameter name="content">抱歉，我无法回答您的问题，因为（总结所有步骤并说明原因）</parameter>
    </invoke>
  </function_calls>
</response>
```

## Attention
- 仅返回XML格式，不要有解释
- 每一步只能选择一个工具
- 最终答案语言需与用户提问语言一致
- 动作参数的格式（XML或字符串）取决于工具定义
""",  # noqa: E501
)


class ActionResponseArgs(BaseModel):
    name: str
    args: Union[dict, str]


class ActionResponse(BaseModel):
    analysis: str
    action: ActionResponseArgs


class ReactActionParameters(BaseModel):
    analysis: Optional[str] = None
    action_name: str
    action_parameters: Optional[dict] = None


class ReactAction(BaseModel):
    action: ReactActionParameters
    cell_id: str
    call_id: str


T = TypeVar("T")


class ReactObservationResult(BaseModel):
    result: str
    view: Optional[T] = None


class ReactObservation(BaseModel):
    observation: ReactObservationResult
    action: ReactActionParameters
    exec_status: bool
    cell_id: str
    call_id: str


class ReactResult(BaseModel):
    analysis: str
    result: str | int | float
    cell_id: str


class ReactAgent(BaseAgent):

    def __init__(
        self,
        llm: BaseAIChat,
        tools: List[BaseTool] = None,
        mcp_client: Optional[McpClient] = None,
        prefix_prompt: str = None,
        filter_function_list: List[str] = None,
        history_message: MessagesSet = None,
        react_generate_max_token: int = 40000,
        max_iterations: Optional[int] = 15,
        is_interrupt: Callable[[], bool] = None,  # 外部中断函数
        state_schema: Type[BaseModel] = None,
        resources: Resources = None,
        _from: Optional[str] = None,
        agent_name: Optional[str] = None,
    ):

        super().__init__()
        self.tool_manager = ToolManager(tools, filter_function_list) if tools else None
        self.mcp_client = mcp_client
        self.llm = llm
        self.system_prompt_template: StringTemplate = REACT_SYSTEM_PROMPT_TEMPLATE
        self.function_calls_response_template = StringTemplate(
            """<function_calls_result>
  <name>{{name}}</name>
  <result>{{result}}</result>
</function_calls_result>""",
            template_format="jinja2",
        )
        self.filter_function_list = filter_function_list
        self.max_iterations = max_iterations
        self.max_execution_time: Optional[float] = None
        self.state_schema = state_schema
        self.prefix_prompt = prefix_prompt
        if resources:
            self.resources = resources
        else:
            self.resources = Resources()

        if agent_name:
            self.agent_name = agent_name
        else:
            self.agent_name = generate_unique_id("react_agent")

        self.tools_name = []
        if self.tool_manager:
            for tool in self.tool_manager.tools:
                if self.filter_function_list and tool in self.filter_function_list:
                    self.tools_name.append(tool.name)
                else:
                    self.tools_name.append(tool.name)

        if self.mcp_client:
            for tool_name, _ in self.mcp_client.tools.items():
                if self.filter_function_list and tool_name in self.filter_function_list:
                    self.tools_name.append(tool_name)
                else:
                    self.tools_name.append(tool_name)

        self.history_message = MessagesSet()
        if history_message:
            _history_message = []
            _react_token_limit = self.llm.token_limit - react_generate_max_token
            for i in reversed(history_message.message_list):
                _curr_token_len = tokenizer.chat_len(i.format_str())
                if _curr_token_len <= _react_token_limit:
                    _history_message.append(i)
                    _react_token_limit -= _curr_token_len
                else:
                    break
            if len(_history_message) == 0:
                logging.warning(
                    f"{self.agent_name} 历史消息长度超过设置最大限制{self.llm.token_limit - react_generate_max_token}，已清空历史消息"
                )
            self.history_message = MessagesSet(_history_message[::-1])

        self.curr_message: MessagesSet() = MessagesSet()

        self.is_interrupt = is_interrupt

    def get_llm(self) -> BaseAIChat:
        return self.llm

    def _build_system_prompt(self) -> MessagesSet:
        prefix_prompt = self.prefix_prompt + "\n\n" if self.prefix_prompt else ""

        _func_tool_descriptions = (
            self.tool_manager.tool_descriptions if self.tool_manager else "\n"
        )

        _mpc_tool_descriptions = (
            self.mcp_client.tool_descriptions if self.mcp_client else "\n"
        )

        return MessagesSet().add_system(
            prefix_prompt
            + "\n"
            + self.system_prompt_template.format(
                tool_descriptions=_func_tool_descriptions + _mpc_tool_descriptions
            )
        )

    def retry_llm_call(self, msg: MessagesSet):
        error_msg = ""
        logging.debug(f"react llm call start: {msg.get_format_messages()}")
        # print(msg.get_format_messages())
        for i in range(3):
            try:
                llm_resp = stream_to_string(self.llm.chat_for_stream(messages=msg))
                logging.debug(f"react llm call success: {llm_resp}")
                return llm_resp
            except Exception as e:
                logging.error(f"llm call error: {str(e)}")
                error_msg = str(e)
                time.sleep(1)
        else:
            raise ObserverException(error_msg)

    def _run(
        self,
        instruction: MessagesSet | str,
        verbose=True,
        **kwargs,
    ) -> Iterable[Union[ReactAction, ReactObservation, ReactResult]]:
        _system_prompt = self._build_system_prompt() + self.history_message
        self.curr_message = MessagesSet()
        if isinstance(instruction, str):
            self.curr_message.add_user(instruction)
        else:
            self.curr_message = instruction

        iterations = 0
        used_time = 0.0
        start_time = time.time()

        while self._should_continue(iterations, used_time):
            cell_id = generate_unique_id("react")
            _prompt = deepcopy(_system_prompt) + self.curr_message
            llm_resp = self.retry_llm_call(_prompt)

            self.curr_message.add_assistant(f"{remove_think(llm_resp)}")
            try:
                action_resp: ActionResponse = self._parse_llm_response(llm_resp)
            except ObserverException as e:
                logging.warning(f"ReactAction parse llm response error: {str(e)} ")
                self.curr_message.add_assistant(
                    self.function_calls_response_template.format(
                        name="unknown",
                        result=f"parse llm response error: {str(e)} ;response data : {remove_think(llm_resp)}",
                    )
                )
                continue

            _call_id = generate_unique_id("react")
            if verbose:
                if "final_answer" == action_resp.action.name:
                    pass
                else:
                    yield ReactAction(
                        **{
                            "action": {
                                "analysis": action_resp.analysis,
                                "action_name": action_resp.action.name,
                                "action_parameters": action_resp.action.args,
                            },
                            "cell_id": cell_id,
                            "call_id": _call_id,
                        }
                    )

            if "final_answer" == action_resp.action.name:
                _res = ReactResult(
                    analysis=action_resp.analysis,
                    result=action_resp.action.args["content"],
                    cell_id=cell_id,
                )
                yield _res
                return

            try:
                tool_result = self.run_tool(
                    action_resp.action.name, action_resp.action.args
                )
                tool_exec_status = True
            except ObserverException as e:
                tool_result = f"call error: {str(e)}"
                tool_exec_status = False
            except Exception as e:
                tool_result = f"call error: {str(e)}"
                tool_exec_status = False
                logging.error(f"Tool execution error: {traceback.format_exc()}")

            self.curr_message.add_user(
                self.function_calls_response_template.format(
                    name=action_resp.action.name,
                    result=(
                        tool_result
                        if isinstance(tool_result, (str, int, float))
                        else tool_result.to_str()
                    ),
                )
            )

            if verbose:
                yield ReactObservation(
                    **{
                        "observation": {
                            "result": (
                                tool_result
                                if isinstance(tool_result, (str, int, float))
                                else tool_result.to_str()
                            ),
                            "view": (
                                tool_result
                                if isinstance(tool_result, (str, int, float))
                                else tool_result.to_view()
                            ),
                        },
                        "action": {
                            "analysis": action_resp.analysis,
                            "action_name": action_resp.action.name,
                            "action_parameters": action_resp.action.args,
                        },
                        "exec_status": tool_exec_status,
                        "cell_id": cell_id,
                        "call_id": _call_id,
                    }
                )
            iterations += 1
            used_time += time.time() - start_time

    def run_tool(self, tool_name: str, parameters: Union[str, dict]):

        if tool_name not in self.tools_name:
            return f"未知的工具调用 {tool_name}"

        if self.tool_manager and self.tool_manager.get_tool(tool_name):
            return self.tool_manager.run_tool(tool_name, parameters)
        elif self.mcp_client.get_tool_info(tool_name):
            return self.mcp_client.run_tool(tool_name, parameters)
        else:
            return f"未知的工具调用{tool_name}"

    def _should_continue(self, current_iteration: int, current_time_elapsed) -> bool:
        if self.max_iterations and current_iteration >= self.max_iterations:
            return False
        if self.max_execution_time and current_time_elapsed >= self.max_execution_time:
            return False
        if self.is_interrupt and self.is_interrupt():
            return False
        return True

    @staticmethod
    def _extract_response_block(xml_content: str) -> Optional[str]:
        """
        从XML内容中提取第一个完整的<response>...</response>块

        参数:
            xml_content: 包含可能多个XML块的字符串内容

        返回:
            包含完整<response>块的字符串，如果未找到则返回None
        """
        pattern = r"<response>.*?</response>"
        matches = re.findall(pattern, xml_content, re.DOTALL)

        if matches:
            return matches[0]
        return None

    @staticmethod
    def _extract_analysis(response_block: str) -> Optional[str]:
        """
        从<response>块中提取<analysis>标签的内容

        参数:
            response_block: 完整的<response> XML块字符串

        返回:
            <analysis>标签内的文本内容（如存在），如果未找到则返回None
        """
        try:
            # 方法1：使用lxml解析（推荐，更健壮）
            root = etree.fromstring(response_block)
            analysis = root.find(".//analysis")
            if analysis is not None:
                return analysis.text
            return None
        except:
            # 方法2：正则解析（备选方案）
            pattern = r"<analysis>(.*?)</analysis>"
            match = re.search(pattern, response_block, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None

    @staticmethod
    def _parse_llm_response(llm_resp: str) -> ActionResponse:

        res = ReactAgent._extract_response_block(llm_resp)
        if not res:
            raise ObserverException("未找到完整的<response>...</response>块")

        analysis = ReactAgent._extract_analysis(res)
        if not analysis:
            raise ObserverException("未找到<analysis>...</analysis>标签")

        try:
            actions = parse_xml_tool_calls(res)
            for i in actions:
                if i.function_name == "response":
                    raise ObserverException(f"工具调用格式异常 {res}")
                return ActionResponse(
                    analysis=analysis,
                    action=ActionResponseArgs(
                        name=i.function_name,
                        args=i.parameters,
                    ),
                )
        except Exception as e:
            raise ObserverException(f"解析<response>...</response>块失败: {str(e)}")
