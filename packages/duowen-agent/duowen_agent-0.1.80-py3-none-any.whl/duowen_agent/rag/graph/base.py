from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import sleep
from typing import Set, Tuple, Literal
from typing import Union, TypeVar

from duowen_agent.error import LengthLimitExceededError, MaxTokenExceededError, LLMError
from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.utils.core_utils import remove_think
from pydantic import BaseModel

from .utils import print_call_back, is_interrupt, compute_args_hash


@dataclass
class QueryParam:
    mode: Literal["local", "global", "naive"] = "global"
    only_need_context: bool = False
    response_type: str = "Multiple Paragraphs"
    level: int = 2
    top_k: int = 20
    # naive search
    naive_max_token_for_text_unit = 12000
    # local search
    local_max_token_for_text_unit: int = 4000  # 12000 * 0.33
    local_max_token_for_local_context: int = 4800  # 12000 * 0.4
    local_max_token_for_community_report: int = 3200  # 12000 * 0.27
    local_community_single_one: bool = False
    # global search
    global_concurrent_num: int = 4
    global_min_community_rating: float = 0
    global_max_consider_community: int = 512
    global_max_token_for_community_report: int = 16384
    global_special_community_map_llm_kwargs: dict = field(
        default_factory=lambda: {"response_format": {"type": "json_object"}}
    )


T = TypeVar("T")


class GraphChange(BaseModel):
    removed_nodes: Set[str] = set()
    added_updated_nodes: Set[str] = set()
    removed_edges: Set[Tuple[str, str]] = set()
    added_updated_edges: Set[Tuple[str, str]] = set()


class StorageNameSpace(BaseModel, ABC):
    namespace: str

    @abstractmethod
    def index_start_callback(self):
        """commit the storage operations after indexing"""
        pass

    @abstractmethod
    def index_done_callback(self):
        """commit the storage operations after indexing"""
        pass

    @abstractmethod
    def query_done_callback(self):
        """commit the storage operations after querying"""
        pass


class BaseKVStorage(StorageNameSpace):

    @abstractmethod
    def all_keys(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Union[T, None]:
        raise NotImplementedError

    @abstractmethod
    def get_by_ids(
        self, ids: list[str], fields: Union[set[str], None] = None
    ) -> list[Union[T, None]]:
        raise NotImplementedError

    @abstractmethod
    def filter_keys(self, data: list[str]) -> set[str]:
        """return un-exist keys"""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, data: dict[str, T]):
        raise NotImplementedError

    @abstractmethod
    def drop(self):
        raise NotImplementedError

    @abstractmethod
    def delete_by_ids(self, ids: list[str]):
        raise NotImplementedError


class BaseVectorStorage(StorageNameSpace):

    @abstractmethod
    def query(self, query: str, top_k: int) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, data: dict[str, tuple[str, dict]]):
        raise NotImplementedError

    @abstractmethod
    def delete_by_ids(self, ids: list[str]):
        raise NotImplementedError

    @abstractmethod
    def drop(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_ids(self, ids: list[str]):
        raise NotImplementedError


class BaseLLM:
    def __init__(
        self,
        llm_instance: OpenAIChat,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        retry_cnt: int = 3,
        retry_sleep: int = 1,
        concurrent_num: int = 1,
        llm_cache: BaseKVStorage = None,
    ):
        self.llm_instance = llm_instance
        self.llm_cache = llm_cache
        self._call_back_func = call_back_func
        self._interrupt_func = interrupt_func
        self.concurrent_num = concurrent_num
        self.retry_cnt = retry_cnt
        self.retry_sleep = retry_sleep

    def _chat(self, prompt: MessagesSet, **kwargs):

        # print(prompt.get_format_messages())
        # print("-" * 100)
        if self._interrupt_func():
            raise InterruptedError("用户终止")

        args_hash = compute_args_hash(
            self.llm_instance.model, prompt.get_format_messages()
        )
        if self.llm_cache is not None:
            if_cache_return = self.llm_cache.get_by_id(args_hash)
            if if_cache_return is not None:
                return if_cache_return["return"]

        _res = ""
        for i in range(self.retry_cnt):
            try:
                for chunk in self.llm_instance.chat_for_stream(
                    messages=prompt, **kwargs
                ):
                    _res += chunk
                break
            except LengthLimitExceededError as e:
                _res = (
                    e.content
                    + "······\n由于大模型的上下文窗口大小限制，回答已经被大模型截断。"
                )
                break
            except MaxTokenExceededError as e:
                break
            except (Exception, LLMError) as e:
                if i == self.retry_cnt - 1:
                    raise e
                else:
                    _res = ""
                    sleep(self.retry_sleep)

        _res = remove_think(_res)

        if self.llm_cache is not None:
            self.llm_cache.upsert(
                {
                    args_hash: {
                        "input": prompt.model_dump()["message_list"],
                        "return": _res,
                        "model": self.llm_instance.model,
                    }
                }
            )
            self.llm_cache.index_done_callback()

        # print(_res)
        # print("=" * 100)
        return _res
