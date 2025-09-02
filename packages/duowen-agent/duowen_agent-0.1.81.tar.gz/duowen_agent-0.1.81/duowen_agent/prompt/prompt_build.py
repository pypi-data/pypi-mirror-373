import datetime
import json
import logging
import os
from typing import Optional, Union, Any, List, Type, Literal

import yaml
from pydantic import BaseModel

from duowen_agent.llm.entity import (
    MessagesSet,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    Message,
)
from duowen_agent.utils.string_template import StringTemplate


def current_date(time_format: str = "%Y年%m月%d日") -> str:
    return datetime.date.today().strftime(time_format)


def prompt_now_day(lang: Literal["cn", "en"] = "cn") -> str:
    # 获取当前日期
    current_date = datetime.date.today()

    # 获取星期几
    weekday = current_date.strftime("%A")

    # 中文星期几
    weekday_zh = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日",
    }

    if lang == "cn":
        # 格式化日期为中文格式
        formatted_date = (
            current_date.strftime("今天是%Y年%m月%d日，") + weekday_zh[weekday] + "。"
        )
    elif lang == "en":
        # 格式化日期为英文格式
        formatted_date = current_date.strftime("Today is %B %d, %Y, %A.")
    else:
        raise ValueError("Unsupported language. Supported languages are 'zh' and 'en'.")

    return formatted_date


OUTPUT_JSON_FORMAT = """The output should be formatted as a JSON instance that conforms to the JSON schema below. JSON only, no explanation.

As an example, for the schema {{"properties": {{"foo": {{"description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{schema}
```"""


OUTPUT_XML_FORMAT = """The output should be formatted as a VALID XML document that conforms to the XSD schema provided below. Return XML only, no explanation or additional text.

As an example, for the XSD schema:
```xsd
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="items" minOccurs="0" maxOccurs="unbounded">
          <xs:complexType>
            <xs:sequence>
              <xs:element type="xs:string" name="value"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```
the following XML would be valid:
```xml
<root>
  <items>
    <value>valid string</value>
  </items>
</root>
```

Here is the output XSD schema:
```xsd
{schema}
```"""

practice_dir = os.path.dirname(os.path.abspath(__file__)) + "/practice/"


class GeneralPromptBuilder:
    """
    instruction 描述任务的简明说明
    plan 步骤 [可选]
    background 背景参考 [可选]
    output_format 输出格式 [可选]
    sample 样例 [可选]
    note 注意事项 [可选]
    """

    def __init__(
        self,
        instruction: Union[StringTemplate, str],
        step: Optional[Union[StringTemplate, str]] = None,
        background: Optional[Union[StringTemplate, str]] = None,
        output_format: Optional[
            Union[Type[BaseModel], StringTemplate, dict, str]
        ] = None,
        sample: Optional[Union[BaseModel, StringTemplate, str]] = None,
        note: Optional[Union[StringTemplate, str]] = None,
        conversation: Optional[List[UserMessage | AssistantMessage]] = None,
        user_input: Optional[StringTemplate] = None,
    ):
        self.instruction = instruction
        self.step = step
        self.background = background
        self.output_format = output_format
        self.sample = sample
        self.note = note
        if user_input:
            if "user_input" in user_input.variables:
                self.user_input = user_input
            else:
                raise ValueError(
                    "GeneralPromptBuilder user_input Template must be {user_input} variables"
                )
        else:
            self.user_input = None

        self.conversation = conversation

    def _build(self, temp_vars: dict) -> str:
        _prompt = ""
        if isinstance(self.instruction, StringTemplate):
            _prompt = f"# Instructions\n{self.instruction.format(**temp_vars)}"
        else:
            _prompt = f"# Instructions\n{self.instruction}"

        if self.step:
            if isinstance(self.step, StringTemplate):
                _prompt += f"\n\n# Steps\n{self.step.format(**temp_vars)}"
            else:
                _prompt += f"\n\n# Steps\n{self.step}"

        if self.background:
            if isinstance(self.background, StringTemplate):
                _prompt += f"\n\n# Background\n{self.background.format(**temp_vars)}"
            else:
                _prompt += f"\n\n# Background\n{self.background}"

        if self.output_format:

            if isinstance(self.output_format, StringTemplate):
                _prompt += (
                    f"\n\n# Output Format\n{self.output_format.format(**temp_vars)}"
                )
            elif isinstance(self.output_format, dict):
                _prompt += f"\n\n# Output Format\n{OUTPUT_JSON_FORMAT.format(schema=json.dumps(self.output_format, ensure_ascii=False))}"
            elif isinstance(self.output_format, str):
                _output_format = self.output_format.strip()
                if _output_format.startswith("<") and _output_format.endswith(">"):
                    _prompt += f"\n\n# Output Format\n{OUTPUT_XML_FORMAT.format(schema=_output_format)}"
                else:
                    _prompt += f"\n\n# Output Format\n{_output_format}"
            elif issubclass(self.output_format, BaseModel):
                _prompt += f"\n\n# Output Format\n{OUTPUT_JSON_FORMAT.format(schema=json.dumps(self.output_format.model_json_schema(), ensure_ascii=False))}"
            else:
                raise ValueError(
                    f"GeneralPromptBuilder output_format type error {str(self.output_format)}"
                )

        if self.sample:
            if isinstance(self.sample, StringTemplate):
                _prompt += f"\n\n# Examples\n{self.sample.format(**temp_vars)}"
            elif isinstance(self.sample, dict):
                _prompt += f"\n\n# Examples\n{json.dumps(self.sample, ensure_ascii=False, indent=4)}"
            else:
                _prompt += f"\n\n# Examples\n{self.sample}"

        if self.note:
            if isinstance(self.note, StringTemplate):
                _prompt += f"\n\n# Notes\n{self.note.format(**temp_vars)}"
            else:
                _prompt += f"\n\n# Notes\n{self.note}"

        return _prompt

    def add_conversation(self, conversation: List[UserMessage | AssistantMessage]):
        if self.conversation is None:
            self.conversation = conversation
        else:
            self.conversation.extend(conversation)

    def get_user_prompt(
        self,
        temp_vars: dict[str, Any] = None,
    ) -> MessagesSet:
        if temp_vars:
            _temp_vars = temp_vars
        else:
            _temp_vars = {}
        _instruction = self._build(temp_vars=_temp_vars)
        return MessagesSet().add_user(_instruction)

    def get_systen_prompt(
        self,
        temp_vars: dict[str, Any] = None,
    ) -> MessagesSet:
        if temp_vars:
            _temp_vars = temp_vars
        else:
            _temp_vars = {}
        _instruction = self._build(temp_vars=_temp_vars)
        return MessagesSet().add_system(_instruction)

    def get_instruction(
        self,
        user_input: Union[MessagesSet, str],
        temp_vars: dict[str, Any] = None,
    ) -> MessagesSet:

        if temp_vars:
            _temp_vars = temp_vars
        else:
            _temp_vars = {}

        if isinstance(user_input, str):
            _user_input = user_input
        elif type(user_input) is MessagesSet and user_input[-1].role == "user":
            _user_input = user_input[-1].content
        else:
            raise ValueError(
                f"GeneralPromptBuilder get_instruction user_input error {str(user_input)}"
            )

        _history = []
        if (
            type(user_input) is MessagesSet
            and len(user_input) == 2
            and user_input[0].role == "system"
        ):
            _history = []
        elif type(user_input) is MessagesSet and len(user_input) >= 2:
            for item in user_input[:-1]:
                _history.append(item)

        # 提取指令
        _instruction = self._build(temp_vars=_temp_vars)

        if not _history:
            _prompt = MessagesSet([SystemMessage(_instruction)])
            if self.conversation:
                _prompt.append_messages(self.conversation)
            if self.user_input:
                _prompt.add_user(
                    self.user_input.format(
                        **dict(_temp_vars, **{"user_input": _user_input})
                    )
                )
            else:
                _prompt.add_user(_user_input)
            return _prompt

        else:
            _prompt = MessagesSet(_history)
            if self.conversation:
                logging.warning("历史对话输入不支持追加对话样本")

            if self.user_input:
                _instruction += f'\n\n# User Input\n{self.user_input.format(**dict(temp_vars, **{"user_input": _user_input}))}'
            else:
                _instruction += f"\n\n# User Input\n{_user_input}"

            _prompt.add_user(_instruction)

            return _prompt

    def _extract(self):
        _dct: dict[str, Any] = {"prompt_type": "General"}
        if isinstance(self.instruction, StringTemplate):
            _dct["instruction"] = {
                "format": self.instruction.template_format,
                "value": self.instruction.template,
            }
        else:
            _dct["instruction"] = {"format": "str", "value": self.instruction}

        if self.step:
            if isinstance(self.step, StringTemplate):
                _dct["step"] = {
                    "format": self.step.template_format,
                    "value": self.step.template,
                }
            else:
                _dct["step"] = {"format": "str", "value": self.step}

        if self.background:
            if isinstance(self.step, StringTemplate):
                _dct["background"] = {
                    "format": self.background.template_format,
                    "value": self.background.template,
                }
            else:
                _dct["background"] = {"format": "str", "value": self.background}

        if self.output_format:
            if isinstance(self.output_format, StringTemplate):
                _dct["output_format"] = {
                    "format": self.output_format.template_format,
                    "value": self.output_format.template,
                }
            elif isinstance(self.output_format, dict):
                _dct["output_format"] = {"format": "dict", "value": self.output_format}
            elif isinstance(self.output_format, str):
                _dct["output_format"] = {"format": "str", "value": self.output_format}
            elif issubclass(self.output_format, BaseModel):
                _dct["output_format"] = {
                    "format": "dict",
                    "value": self.output_format.model_json_schema(),
                }
            else:
                raise ValueError(
                    f"GeneralPromptBuilder output_format type error {str(self.output_format)}"
                )

        if self.sample:
            if isinstance(self.sample, StringTemplate):
                _dct["sample"] = {
                    "format": self.sample.template_format,
                    "value": self.sample.template,
                }
            elif isinstance(self.sample, dict):
                _dct["sample"] = {
                    "format": "str",
                    "value": json.dumps(self.sample, ensure_ascii=False, indent=4),
                }
            else:
                _dct["sample"] = {"format": "str", "value": self.sample}

        if self.note:
            if isinstance(self.note, StringTemplate):
                _dct["note"] = {
                    "format": self.note.template_format,
                    "value": self.note.template,
                }
            else:
                _dct["note"] = {"format": "str", "value": self.note}

        if self.conversation:
            _dct["conversation"] = {
                "format": "list",
                "value": [i.to_dict() for i in self.conversation],
            }

        if self.user_input:
            if isinstance(self.user_input, StringTemplate):
                _dct["user_input"] = {
                    "format": self.user_input.template_format,
                    "value": self.user_input.template,
                }
            else:
                _dct["user_input"] = {"format": "str", "value": self.user_input}

        return _dct

    def human_print(self):
        for k, v in self._extract().items():
            if k == "prompt_type":
                continue
            if v["format"] == "str":
                print(f"{k}:\n{v['value']}")
            elif v["format"] in ("f-string", "jinja2"):
                print(f"{k}:\n{v['value']}")
            elif v["format"] == "dict":
                print(f"{k}:\n{json.dumps(v['value'], ensure_ascii=False, indent=4)}")
            elif v["format"] == "list":
                _d = "\n".join([str(Message(**i).to_dict()) for i in v["value"]])
                print(f"{k}:\n{_d}")
            print("\n\n")

    def export_yaml(self, path: str = None) -> str:
        _yaml = "\n".join(
            [
                yaml.dump(i, allow_unicode=True, default_flow_style=False)
                for i in [{k: v} for k, v in self._extract().items()]
            ]
        )

        if path:
            with open(path, "w") as f:
                f.write(_yaml)
        else:
            return _yaml

    @classmethod
    def load_dict(cls, data: dict) -> "GeneralPromptBuilder":

        _params = {}
        for k, v in data.items():
            if k == "prompt_type":
                if v != "General":
                    raise ValueError(f"GeneralPromptBuilder 不支持 type {str(v)}")
                else:
                    continue

            if v["format"] == "str":
                _params[k] = v["value"]
            elif v["format"] in ("f-string", "jinja2"):
                _params[k] = StringTemplate(
                    template=v["value"], template_format=v["format"]
                )
            elif v["format"] == "dict":
                if k != "output_format":
                    raise ValueError(
                        f"GeneralPromptBuilder load_yaml type error {str(k)}"
                    )
                # 导入的结构可以使用 datamodel-codegen  --input test.json --input-file-type jsonschema --output test.py 进行反序列化BaseModel结构
                # pip install datamodel-code-generator
                _params[k] = v["value"]
            elif v["format"] == "list":
                if k != "conversation":
                    raise ValueError(
                        f"GeneralPromptBuilder load_yaml type error {str(k)}"
                    )
                _params[k] = [Message(**i) for i in v["value"]]

        return cls(**_params)

    @classmethod
    def load(cls, name: str = None) -> "GeneralPromptBuilder":

        if os.path.exists(f"{practice_dir}{name}.yaml"):
            with open(f"{practice_dir}{name}.yaml", "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                return cls.load_dict(data)
        else:
            raise FileNotFoundError(
                f"GeneralPromptBuilder load Built-in [{name}] not found"
            )

    @classmethod
    def load_yaml(cls, path_name: str) -> "GeneralPromptBuilder":

        if os.path.exists(path_name):
            with open(path_name, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                return cls.load_dict(data)
        else:
            raise FileNotFoundError(
                f"GeneralPromptBuilder load [{path_name}] not found"
            )
