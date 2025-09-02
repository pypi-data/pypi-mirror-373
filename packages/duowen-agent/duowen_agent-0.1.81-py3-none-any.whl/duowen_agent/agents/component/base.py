from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Type

from duowen_agent.error import ObserverException, LLMError, LengthLimitExceededError
from duowen_agent.llm import MessagesSet
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.utils.concurrency import make_async
from duowen_agent.utils.core_utils import (
    stream_to_string,
    remove_think,
    json_observation,
)
from pydantic import BaseModel


class BaseComponent(ABC):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    async def arun(self, *args, **kwargs) -> Any:
        return await make_async(self.run(*args, **kwargs))

    # def run_for_stream(self, *args, **kwargs) -> Any:
    #     yield self.run(*args, **kwargs)
    #
    # async def arun_for_stream(self, *args, **kwargs) -> Any:
    #     raise NotImplementedError


class BaseLLMComponent(BaseComponent):

    def __init__(
        self,
        llm_instance: BaseAIChat,
        retry_cnt: int = 3,
        retry_sleep: int = 3,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.llm_instance = llm_instance
        self.retry_cnt = retry_cnt
        self.retry_sleep = retry_sleep

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def _extract(self, prompt: MessagesSet, model: Type[BaseModel], **kwargs):
        for i in range(self.retry_cnt):
            try:
                # prompt.pretty_print()
                _res = stream_to_string(
                    self.llm_instance.chat_for_stream(messages=prompt, **kwargs)
                )
                _res = remove_think(_res)
                return json_observation(_res, model)
            except (ObserverException, LLMError, LengthLimitExceededError) as e:
                if i == self.retry_cnt - 1:
                    raise e
                else:
                    sleep(self.retry_sleep)
