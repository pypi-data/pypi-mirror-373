import json
import os
import time
from abc import abstractmethod
from copy import deepcopy
from hashlib import md5
from threading import Lock
from typing import List, Any, Generator, Callable, Optional

import jsonlines
from duowen_agent.error import LengthLimitExceededError, LLMError
from duowen_agent.llm import OpenAIChat, Message, MessagesSet
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.utils import format_messages
from duowen_agent.utils.core_utils import remove_think, stream_to_string


def continue_chat(
    llm: BaseAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    continue_cnt: int = 3,
    **kwargs,
) -> str:
    full_response = ""  # 存储所有轮次完整响应
    ori_msg = format_messages(messages)
    msg = deepcopy(ori_msg)

    for attempt in range(continue_cnt):
        buffer = ""
        try:
            # 流式获取当前轮次响应
            for chunk in llm.chat_for_stream(msg, **kwargs):
                buffer += chunk

            # 成功完成：累积并返回
            full_response += remove_think(buffer)
            return full_response

        except LengthLimitExceededError as e:
            if attempt == continue_cnt - 1:  # 最后一次尝试仍失败
                # print("-" * 50)
                # print(msg.get_format_messages())
                # print("-" * 50)
                raise e

            # 处理当前部分响应
            current_part = remove_think(buffer)
            full_response += current_part  # 累积到完整响应
            msg = deepcopy(ori_msg)
            # 更新消息历史
            msg.add_assistant(full_response)  # 包含所有历史内容
            msg.add_user("continue")

    return full_response  # 理论上不会执行到这里


def retry_chat(
    llm: BaseAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    retry_times: int = 3,
    sleep_time: int = 5,
    **kwargs,
) -> str:
    for i in range(retry_times):
        try:
            res = stream_to_string(llm.chat_for_stream(messages, **kwargs))
            return res
        except LLMError as e:
            if i == retry_times - 1:
                raise e
            else:
                time.sleep(sleep_time)


async def async_continue_chat(
    llm: OpenAIChat,
    messages: str | List[dict] | List[Message] | MessagesSet,
    continue_cnt: int = 3,
    **kwargs,
) -> str:
    full_response = ""  # 存储所有轮次完整响应
    ori_msg = format_messages(messages)
    msg = deepcopy(ori_msg)

    for attempt in range(continue_cnt):
        buffer = ""
        try:
            # 流式获取当前轮次响应
            async for chunk in llm.achat_for_stream(msg, **kwargs):
                buffer += chunk

            # 成功完成：累积并返回
            full_response += remove_think(buffer)
            return full_response

        except LengthLimitExceededError as e:
            if attempt == continue_cnt - 1:  # 最后一次尝试仍失败
                # print("-" * 50)
                # print(msg.get_format_messages())
                # print("-" * 50)
                raise LengthLimitExceededError(content=buffer)

            # 处理当前部分响应
            current_part = remove_think(buffer)
            full_response += current_part  # 累积到完整响应
            msg = deepcopy(ori_msg)
            # 更新消息历史
            msg.add_assistant(full_response)  # 包含所有历史内容
            msg.add_user("continue")

    return full_response


class OpenAIChatBaseCache(BaseAIChat):

    def __init__(
        self,
        llm: OpenAIChat,
        ttl: Optional[int] = 3600,
        lock: Optional[Lock] = None,
        observation_func: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.llm = llm
        self.ttl = ttl
        self.lock = lock or Lock()
        self.observation_func = observation_func or (lambda x: True)
        self.params = [
            "temperature",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "max_tokens",
            "stop",
        ]

    def chat(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        **kwargs,
    ) -> str | Any:
        """
        如果观测失败则不记录缓存，上层应用自行处理
        messages: 消息历史
        """
        messages = format_messages(messages)
        self._chat_start_hook(messages, **kwargs)
        _key = self._compute_key(messages, **kwargs)
        _res_cache = self.get(_key)

        if _res_cache:
            if self.observation_func(_res_cache) is False:
                self.delete(_key)
            return _res_cache

        _resp = self.llm.chat(messages, **kwargs)

        # _resp 有可能返回 tool_call对象 则暂时不缓存
        if isinstance(_resp, str) and self.observation_func(_resp):
            self.upsert(_key, messages, _resp, **kwargs)
        return _resp

    def chat_for_stream(
        self, messages: str | List[dict] | List[Message] | MessagesSet, **kwargs
    ) -> Generator:
        """
        如果观测失败则不记录缓存，上层应用自行处理
        messages: 消息历史
        """
        messages = format_messages(messages)
        self._chat_start_hook(messages, **kwargs)
        _key = self._compute_key(messages, **kwargs)
        _res_cache = self.get(_key)
        if _res_cache:
            if self.observation_func(_res_cache) is False:
                self.delete(_key)

            chunk_size = 4
            for i in range(0, len(_res_cache), chunk_size):
                yield _res_cache[i : i + chunk_size]
            return

        _buffer_resp = ""
        for chunk in self.llm.chat_for_stream(messages, **kwargs):
            _buffer_resp += chunk
            yield chunk

        if self.observation_func(_buffer_resp):
            self.upsert(_key, messages, _buffer_resp, **kwargs)
        return

    def _compute_key(self, messages: MessagesSet, **kwargs):
        param_str = json.dumps(
            {k: v for k, v in kwargs.items() if k in self.params},
            sort_keys=True,
            ensure_ascii=False,
        )
        return md5(
            (messages.get_format_messages() + self.llm.model + param_str).encode()
        ).hexdigest()

    def get(self, key: str):
        with self.lock:
            _res = self._get(key)
            if _res:
                _data = json.loads(_res)
                if _data["expire"] is None or _data["expire"] > time.time():
                    return _data["return"]
                else:
                    self._delete(key)
                    return None
            else:
                return None

    def upsert(self, key: str, prompt: MessagesSet, value: str, **kwargs):
        with self.lock:
            param_str = {k: v for k, v in kwargs.items() if k in self.params}
            return self._upsert(
                key,
                json.dumps(
                    {
                        "input": prompt.model_dump()["message_list"],
                        "return": value,
                        "model": self.llm.model,
                        "expire": int(time.time()) + self.ttl if self.ttl else None,
                        **param_str,
                    },
                    ensure_ascii=False,
                ),
            )

    def delete(self, key: str):
        with self.lock:
            if self._exists(key):
                return self._delete(key)

    def _chat_start_hook(self, messages: MessagesSet, **kwargs):
        pass

    @abstractmethod
    def _get(self, key: str) -> str | None:
        """
        子类实现不应再获取锁
        return: json.dumps({"input": str, "return": str, "model": str, "expire": int or null}
        """
        raise NotImplementedError

    @abstractmethod
    def _upsert(self, key: str, value: str) -> bool:
        """
        子类实现不应再获取锁
        value: json.dumps({"input": str, "return": str, "model": str, "expire": int or null}
        接口可以自行扩展
        """
        raise NotImplementedError

    @abstractmethod
    def _delete(self, key: str) -> bool:
        """
        子类实现不应再获取锁
        """
        raise NotImplementedError

    @abstractmethod
    def _exists(self, key: str) -> bool:
        """
        子类实现不应再获取锁
        """
        raise NotImplementedError


class OpenAIChatJsonlCache(OpenAIChatBaseCache):

    def __init__(
        self,
        llm: OpenAIChat,
        ttl: Optional[int] = None,
        lock: Optional[Lock] = None,
        observation_func: Optional[Callable[[str], bool]] = None,
        file_path: str = "./OpenAIChatJsonlCache.jsonl",
    ):

        super().__init__(llm, ttl, lock, observation_func)
        self.file_path = file_path
        self._cache = {}
        self.init_data()

    def init_data(self):
        if not os.path.exists(self.file_path):
            return
        with jsonlines.open(self.file_path, "r") as f:
            for line in f:
                self._cache[line["key"]] = line["value"]

    def _get(self, key: str) -> str | None:
        return self._cache.get(key)

    def _upsert(self, key: str, value: str) -> bool:
        self._cache[key] = value
        with jsonlines.open(self.file_path, "a") as f:
            f.write({"key": key, "value": value})
        return True

    def _delete(self, key: str) -> bool:
        del self._cache[key]
        return True

    def _exists(self, key: str) -> bool:
        return key in self._cache
