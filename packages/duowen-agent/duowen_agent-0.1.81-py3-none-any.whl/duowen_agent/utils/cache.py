from abc import ABC, abstractmethod
from time import time, sleep
from typing import Any, Optional, List


class Cache(ABC):
    """
    缓存抽象类，定义了缓存操作的基本接口。
    """

    @abstractmethod
    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """
        设置缓存项。

        :param key: 缓存键
        :param value: 缓存值
        :param expire: 缓存过期时间（秒）
        """
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存项。

        :param key: 缓存键
        :return: 缓存值，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """
        批量获取缓存项。

        :param keys: 缓存键列表
        :return: 缓存值列表，如果不存在则值为 None
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        删除缓存项。

        :param key: 缓存键
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        清空所有缓存项。
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        检查缓存项是否存在。

        :param key: 缓存键
        :return: 如果存在则返回 True，否则返回 False
        """
        pass

    @abstractmethod
    async def aset(self, key: str, value: Any, expire: int = 3600) -> None:
        """
        设置缓存项。

        :param key: 缓存键
        :param value: 缓存值
        :param expire: 缓存过期时间（秒）
        """
        pass

    @abstractmethod
    async def aget(self, key: str) -> Optional[Any]:
        """
        获取缓存项。

        :param key: 缓存键
        :return: 缓存值，如果不存在则返回 None
        """
        pass

    @abstractmethod
    async def amget(self, keys: List[str]) -> List[Optional[Any]]:
        """
        批量获取缓存项。

        :param keys: 缓存键列表
        :return: 缓存值列表，如果不存在则值为 None
        """
        pass

    @abstractmethod
    async def adelete(self, key: str) -> None:
        """
        删除缓存项。

        :param key: 缓存键
        """
        pass

    @abstractmethod
    async def aclear(self) -> None:
        """
        清空所有缓存项。
        """
        pass

    @abstractmethod
    async def aexists(self, key: str) -> bool:
        """
        检查缓存项是否存在。

        :param key: 缓存键
        :return: 如果存在则返回 True，否则返回 False
        """
        pass


class InMemoryCache(Cache):
    def __init__(self):
        self._cache = {}

    def set(self, key: str, value: Any, expire: int = None) -> None:
        self._cache[key] = {
            "value": value,
            "expire_at": time() + expire if expire else None,
        }

    def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if item is None:
            return None
        if item["expire_at"] is not None and time() > item["expire_at"]:
            del self._cache[key]
            return None
        return item["value"]

    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        results = []
        for key in keys:
            results.append(self.get(key))
        return results

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    def exists(self, key: str) -> bool:
        return key in self._cache

    async def aset(self, key: str, value: Any, expire: int = 3600) -> None:
        self.set(key, value, expire)

    async def aget(self, key: str) -> Optional[Any]:
        return self.get(key)

    async def amget(self, keys: List[str]) -> List[Optional[Any]]:
        return self.mget(keys)

    async def adelete(self, key: str) -> None:
        self.delete(key)

    async def aclear(self) -> None:
        self.clear()

    async def aexists(self, key: str) -> bool:
        """异步检查缓存项是否存在"""
        return self.exists(key)


if __name__ == "__main__":
    # 示例使用
    import time

    cache = InMemoryCache()
    cache.set("key1", "value1", expire=10)  # 设置缓存，10秒后过期
    cache.set("key2", "value2")  # 设置缓存，永不过期
    print(cache.get("key1"))  # 输出: value1
    print(cache.get("key2"))  # 输出: value2

    sleep(11)
    print(cache.get("key1"))  # 输出: None，因为缓存已过期
    print(cache.get("key2"))  # 输出: value2

    print(cache.mget(["key1", "key2", "key3"]))  # 输出: [None, 'value2', None]

    cache.delete("key2")
    print(cache.exists("key2"))  # 输出: False

    cache.clear()
    print(cache.exists("key1"))  # 输出: False
    print(cache.exists("key2"))  # 输出: False
