import json
import traceback
from abc import ABC, abstractmethod
from hashlib import sha1
from typing import List, Dict, Literal, Annotated
from urllib.parse import urlparse
from urllib.request import urlopen

import requests
from pydantic import BaseModel, conlist, Field

from duowen_agent.error import EmbeddingError
from duowen_agent.utils.cache import Cache


class EmbeddingVLInputModel(BaseModel):
    input: conlist(
        Annotated[Dict[Literal["text", "image"], str], Field(min_length=1)],
        min_length=1,
    )


class EmbeddingVL(ABC):
    def __init__(
            self,
            base_url: str,
            model: str = None,
            api_key: str = None,
            timeout: int = 120,
            dimension: int = 512,
            extra_headers: dict = None,
            **kwargs,
    ):
        self.base_url = f"{base_url}/v1/embeddings"
        self.model = model
        self.timeout = timeout
        self.api_key = api_key
        self.dimension = dimension
        self.extra_headers = extra_headers
        self.kwargs = kwargs

    @abstractmethod
    def get_embedding(
            self, input: List[Dict[Literal["text", "image"], str]]
    ) -> List[List[float]]:
        pass


class JinaClipV2Embedding(EmbeddingVL):
    def __init__(
            self,
            base_url: str,
            model: str = None,
            api_key: str = None,
            timeout: int = 120,
            dimension: int = 512,
            extra_headers: dict = None,
            **kwargs,
    ):
        super().__init__(
            base_url, model, api_key, timeout, dimension, extra_headers, **kwargs
        )
        self.model = model or kwargs.get("model_name", "jina-clip-v2")

    def get_embedding(
            self, input: List[Dict[Literal["text", "image"], str]]
    ) -> List[List[float]]:
        try:
            EmbeddingVLInputModel(input=input)

            headers = {"Content-Type": "application/json"}
            if self.extra_headers:
                headers.update(self.extra_headers)
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            data = {
                "model": self.model,
                "dimensions": self.dimension,
                "normalized": self.kwargs.get("normalized", True),
                "embedding_type": self.kwargs.get("embedding_type", "float"),
                "input": input,
            }
            if (embedding_type := self.kwargs.get("task", None)) == "retrieval.query":
                data["task"] = embedding_type

            resp = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(data),
                timeout=self.timeout,
            )
            resp.raise_for_status()
            v_res = resp.json()

            return [item["embedding"] for item in v_res["data"]]
        except:
            raise EmbeddingError(traceback.format_exc(), self.base_url, self.api_key)


class EmbeddingVLCache:
    def __init__(
            self, emb_cache: Cache, model_instance: EmbeddingVL, cache_ttl: int = 3600
    ):
        self.emb_cache = emb_cache
        self.model_instance = model_instance
        self.cache_ttl = cache_ttl
        self.base_url = self.model_instance.base_url
        self.model = self.model_instance.model
        self.timeout = self.model_instance.timeout
        self.api_key = self.model_instance.api_key
        self.dimension = self.model_instance.dimension

    def _generate_key(self, question: str, is_image: bool = False) -> str:
        if not is_image:
            return f"embed::{self.model_instance.model}::{sha1(question.encode()).hexdigest()}"
        else:
            resp = urlopen(urlparse(question)._replace(query=None).geturl())
            if resp.getcode() == 200:
                return f"embed::{self.model_instance.model}::{sha1(resp.read()).hexdigest()}"
            else:
                raise EmbeddingError(
                    traceback.format_exc(), self.base_url, self.api_key
                )

    def get_embedding(
            self, input: List[Dict[Literal["text", "image"], str]], cache_ttl: int = None
    ) -> List[List[float]]:

        EmbeddingVLInputModel(input=input)
        _cache_ttl = cache_ttl or self.cache_ttl or 3600

        embedding_cache = {
            embedding_content: {
                "key": self._generate_key(embedding_content, embedding_type == "image"),
                "embedding_type": embedding_type,
                "embedding": [],
            }
            for item in input
            for embedding_type, embedding_content in item.items()
        }
        cached_embeddings = self.emb_cache.mget(
            [embedding_cache[item]["key"] for item in embedding_cache]
        )
        for i, item in enumerate(embedding_cache):
            if cached_embeddings[i]:
                embedding_cache[item]["embedding"] = json.loads(cached_embeddings[i])

        _input = [
            {embedding_cache[embedding_content]["embedding_type"]: embedding_content}
            for embedding_content in embedding_cache
            if not embedding_cache[embedding_content]["embedding"]
        ]
        cached_embeddings = self.model_instance.get_embedding(_input)
        for i, item in enumerate(embedding_cache):
            if not embedding_cache[item]["embedding"]:
                embedding_cache[item]["embedding"] = cached_embeddings[i]
                self.emb_cache.set(
                    embedding_cache[item]["key"],
                    json.dumps(cached_embeddings[i]),
                    _cache_ttl,
                )

        return [embedding_cache[item]["embedding"] for item in embedding_cache]
