import json
from typing import Literal, List, Union, Dict

from pydantic import BaseModel, Field

from duowen_agent.utils.core_utils import remove_think

openai_params_list = {
    "messages",
    "model",
    "audio",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "max_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "response_format",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
}


class BaseContent(BaseModel):
    """内容基类"""


class TextContent(BaseContent):
    type: Literal["text"] = "text"
    text: str

    def to_dict(self):
        return {"type": self.type, "text": self.text}


class ImageURLContent(BaseContent):
    type: Literal["image_url"] = "image_url"
    image_url: Dict[str, str]

    def to_dict(self):
        return {"type": self.type, "image_url": self.image_url}


ContentUnion = Union[TextContent, ImageURLContent]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: Union[str, List[ContentUnion]]

    def __init__(
        self,
        content: Union[str, List[ContentUnion]],
        role: Literal["system", "user", "assistant"] = "user",
    ):
        super().__init__(content=content, role=role)

    def __getitem__(self, item):
        if item == "content":
            return self.content
        elif item == "role":
            return self.role
        else:
            raise KeyError(f"Message has no key {item}")

    def format_str(self) -> str:
        if isinstance(self.content, str):
            return (
                f"<{self.role}>\n"
                + "\n".join(["  " + j for j in self.content.split("\n")])
                + f"\n</{self.role}>"
            )
        else:
            return (
                f"<{self.role}>\n"
                + "\n".join([f"  {str(j)}" for j in self.content])
                + f"\n</{self.role}>"
            )

    def to_dict(self) -> dict:

        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": [i.to_dict() for i in self.content]}


class SystemMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "system")


class UserMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "user")


class AssistantMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "assistant")


class MessagesSet(BaseModel):
    message_list: List[Message] = []

    def __init__(self, message_list: List[dict] | List[Message] = None):
        if message_list:
            if isinstance(message_list[0], dict):
                message_list = [Message(**i) for i in message_list]
            elif isinstance(message_list[0], Message):
                pass
            else:
                raise ValueError("MessagesSet init message_list type error")
            super().__init__(message_list=message_list)
        else:
            super().__init__()

    def remove_assistant_think(self):
        """推理模型需要剔除think部分"""
        for message in self.message_list:
            if message.role == "assistant":
                message.content = remove_think(message.content)
        return self

    def init_message_list(self, message: List[Dict[str, str]]):
        for i in message:
            if i["role"] == "assistant":
                self.add_assistant(i["content"])
            elif i["role"] == "system":
                self.add_system(i["content"])
            elif i["role"] == "user":
                self.add_user(i["content"])
        return self

    def add_user(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(UserMessage(content))
        return self

    def add_assistant(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(AssistantMessage(content))
        return self

    def add_system(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(SystemMessage(content))
        return self

    def append_messages(
        self, messages_set: Union["MessagesSet", List[UserMessage | AssistantMessage]]
    ):
        if type(messages_set) is MessagesSet:
            self.message_list = self.message_list + messages_set.message_list
        else:
            for message in messages_set:
                if type(message) is Message:
                    self.message_list.append(message)
                else:
                    raise ValueError("MessagesSet append_messages type error")
        return self

    def get_messages(self):
        return [i.to_dict() for i in self.message_list]

    def get_format_messages(self):
        _data = []

        for i in self.message_list:
            _data.append(i.format_str())

        return "\n\n".join(_data)

    def pretty_print(self):
        print(self.get_format_messages())

    def get_last_message(self):
        """Returns the last message if available, otherwise returns None."""
        if not self.message_list:
            return None
        return self.message_list[-1]

    def __add__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __iadd__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __getitem__(self, item):
        return self.message_list[item]

    def __len__(self):
        return len(self.message_list)

    def __bool__(self):
        return bool(self.message_list)

    def __iter__(self):
        for item in self.message_list:
            yield item

    def __repr__(self):
        return f"MessagesSet({self.message_list})"

    def __str__(self):
        return f"MessagesSet({str(self.message_list)[:200]})"


class Tool(BaseModel):
    name: str
    arguments: Dict = Field(default_factory=dict)
    think: str = None

    def __str__(self):
        return json.dumps(
            {"name": self.name, "arguments": self.arguments, "think": self.think},
            ensure_ascii=False,
        )


class ToolsCall(BaseModel):
    think: str = None
    tools: List[Tool] = Field(default_factory=list)

    def __str__(self):
        return json.dumps(
            {"think": self.think, "tools": [i.model_dump() for i in self.tools]},
            ensure_ascii=False,
        )
