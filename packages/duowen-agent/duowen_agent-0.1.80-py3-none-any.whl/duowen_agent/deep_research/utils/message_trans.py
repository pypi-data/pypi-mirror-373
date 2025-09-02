from duowen_agent.llm import MessagesSet
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


def langchain_to_messageset(
    langchain_messages: list[BaseMessage | dict],
) -> MessagesSet:
    """将 LangChain 消息列表转换为 OpenAI 标准消息列表"""
    role_map = {
        HumanMessage: "user",
        AIMessage: "assistant",
        SystemMessage: "system",  # 补充系统消息的转换
    }
    _prompt = MessagesSet()
    for msg in langchain_messages:
        if isinstance(msg, SystemMessage):
            _prompt.add_system(msg.content)
        elif isinstance(msg, HumanMessage):
            _prompt.add_user(msg.content)
        elif isinstance(msg, AIMessage):
            _prompt.add_assistant(msg.content)
        elif isinstance(msg, dict):
            if msg.get("role") == "system":
                _prompt.add_system(msg.get("content"))
            elif msg.get("role") == "user":
                _prompt.add_user(msg.get("content"))
            elif msg.get("role") == "assistant":
                _prompt.add_assistant(msg.get("content"))
            else:
                raise ValueError(f"不支持的消息类型: {msg.get('role')}")
        else:
            raise ValueError(f"不支持的消息类型: {type(msg)}")
    return _prompt
