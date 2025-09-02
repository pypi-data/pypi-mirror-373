from typing import List, Literal

from .entity import Message, MessagesSet, UserMessage, SystemMessage
from .tokenizer import tokenizer


def format_messages(
    message: str | List[dict] | List[Message] | MessagesSet, is_reasoning=False
) -> MessagesSet:
    if isinstance(message, str):
        if is_reasoning:
            return MessagesSet(
                message_list=[
                    UserMessage(message),
                ]
            )
        else:
            return MessagesSet(
                [
                    SystemMessage("You are a helpful assistant"),
                    UserMessage(message),
                ]
            )
    elif type(message) is MessagesSet:
        return message
    elif isinstance(message, List) and all(isinstance(i, Message) for i in message):
        return MessagesSet(message)
    elif isinstance(message, List) and all(isinstance(i, dict) for i in message):
        return MessagesSet().init_message_list(message)
    else:
        raise ValueError(f"message 格式非法:{str(message)}")


def message_fit_in(
    msg: str | List[dict] | List[Message] | MessagesSet,
    max_length=4000,
    encoding: Literal["o200k", "cl100k"] = "o200k",
) -> MessagesSet:
    """
    对消息进行截断，使其不超过max_length
    :param msg: 消息列表
    :param max_length: 最大长度
    :param encoding: 编码方式
    """
    _msg = format_messages(msg)
    _lst_msg = _msg.get_messages()

    if encoding == "o200k":
        num_tokens_from_string = tokenizer.chat_len
        truncate = tokenizer.truncate_chat
    else:
        num_tokens_from_string = tokenizer.emb_len
        truncate = tokenizer.truncate_emb

    def count():
        nonlocal _lst_msg
        tks_cnts = []
        for m in _lst_msg:
            tks_cnts.append(
                {"role": m["role"], "count": num_tokens_from_string(m["content"])}
            )
        total = 0
        for m in tks_cnts:
            total += m["count"]
        return total

    c = count()
    if c < max_length:
        return MessagesSet(_lst_msg)

    msg_ = [m for m in _lst_msg if m["role"] == "system"]
    if len(_lst_msg) > 1:
        msg_.append(_lst_msg[-1])
    _lst_msg = msg_
    c = count()
    if c < max_length:
        return MessagesSet(_lst_msg)

    ll = num_tokens_from_string(msg_[0]["content"])
    ll2 = num_tokens_from_string(msg_[-1]["content"])
    if ll / (ll + ll2) > 0.8:
        m = msg_[0]["content"]
        m = truncate(m, max_length - ll2)
        _lst_msg[0]["content"] = m
        return MessagesSet(_lst_msg)

    m = msg_[-1]["content"]
    m = truncate(m, max_length - ll2)
    _lst_msg[-1]["content"] = m
    return MessagesSet(_lst_msg)
