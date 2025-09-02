import os
from typing import List, Optional

import httpx
import requests
from requests import RequestException
from tiktoken import Encoding

from duowen_agent.error import RerankError
from duowen_agent.utils.core_utils import async_record_time, record_time


class GeneralRerank:
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        api_key: Optional[str] = None,
        query_col_name: str = "query",
        documents_col_name: str = "documents",
        encoding: Encoding = None,
        extra_headers: dict = None,
        **kwargs,
    ):
        """
        初始化通用重新排序对象。

        参数:
        - model: 指定使用的模型，例如 "bge-reranker-base"。
        - base_url: API的基础URL，例如 "http://localhost:9997/v1/rerank"。
        - api_key: API密钥，可选参数，默认为None。
        - query_col_name: 查询列名，默认为"query"。
        - documents_col_name: 文档列名，默认为"documents"。
        - encoding: 文本编码方式，可选参数，默认为None。
        - **kwargs: 其他额外参数。
        """
        self.base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", None
        )  # 需要完整路径
        self.model = model or kwargs.get("model_name", None) or "bge-reranker-base"
        self.api_key = api_key
        self.query_col_name = query_col_name
        self.documents_col_name = documents_col_name
        self.encoding = encoding
        self.extra_headers = extra_headers

    def _len_tokens(self, text) -> int:
        if self.encoding:
            tokens = self.encoding.encode(text, disallowed_special=())
            return len(tokens)
        else:
            return len(text)

    def _split_documents(
        self,
        query: str,
        documents: List[str],
        max_chunks_per_doc: int,
        overlap_tokens: int,
    ):
        _document_mapping = {}
        _query_tokens_num = self._len_tokens(query)
        for _index, _chunk in enumerate(documents):
            _chunk_tokens_num = self._len_tokens(_chunk)
            if max_chunks_per_doc < (_query_tokens_num + _chunk_tokens_num):
                _chunks_num = max_chunks_per_doc - _query_tokens_num
                if _chunks_num <= overlap_tokens:
                    raise RerankError(
                        "(max_chunks_per_doc-len(query)) < overlap_tokens"
                    )
                _split_chunks = self._split_text(_chunk, _chunks_num, overlap_tokens)
                for j in _split_chunks:
                    _document_mapping[j] = _index
            else:
                _document_mapping[_chunk] = _index
        return _document_mapping

    def _split_text(
        self, text: str, max_chunks_per_doc: int = 1000, overlap_tokens: int = 80
    ) -> list[str]:
        if self.encoding:
            tokens = self.encoding.encode(text)  # 将文本编码为标记
            total_tokens = len(tokens)  # 总标记数
        else:
            total_tokens = len(text)  # 直接使用字符串长度
            tokens = None

        if total_tokens <= max_chunks_per_doc:
            return [text]

        chunks = []
        start_token = 0

        while start_token < total_tokens:
            end_token = min(start_token + max_chunks_per_doc, total_tokens)
            if self.encoding:
                chunk_tokens = tokens[start_token:end_token]
                chunks.append(self.encoding.decode(chunk_tokens))
            else:
                chunks.append(text[start_token:end_token])

            if end_token == total_tokens:
                break

            start_token = max(end_token - overlap_tokens, 0)

        return chunks

    @staticmethod
    def mapping_documents(documents_mapping, documents, data) -> List[dict]:
        _score = {}
        for i in data:
            _index = documents_mapping[documents[i["index"]]]

            if _index in _score:
                _last_score = _score[_index]
                if i["relevance_score"] > _last_score:
                    _score[_index] = i["relevance_score"]
            else:
                _score[_index] = i["relevance_score"]

        _res = [
            {"index": _index, "relevance_score": _relevance_score}
            for _index, _relevance_score in _score.items()
        ]

        sorted_res = sorted(_res, key=lambda x: x["relevance_score"], reverse=True)

        return sorted_res

    def build_param(
        self,
        query: str,
        documents: List[str] = None,
        max_chunks_per_doc: int = 1000,
        overlap_tokens: int = 80,
        **kwargs,
    ):

        # 兼容历史代码
        if documents:
            _ori_documents = documents
        else:
            _ori_documents = kwargs.get("passages", [])

        if not _ori_documents:
            raise RerankError(
                "documents or passages 为空",
                base_url=self.base_url,
                model_name=self.model,
            )

        headers = {"accept": "application/json", "Content-Type": "application/json"}

        if self.extra_headers:
            headers.update(self.extra_headers)

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if max_chunks_per_doc:
            _split_documents = True
        else:
            _split_documents = False

        if _split_documents:
            # 切分文档
            _document_mapping = self._split_documents(
                query, _ori_documents, max_chunks_per_doc, overlap_tokens
            )
            _documents = list(_document_mapping.keys())
        else:
            _document_mapping = {}
            _documents = _ori_documents

        params = {
            "model": self.model,
            self.query_col_name: query,
            self.documents_col_name: _documents,
        }

        return params, headers, _split_documents, _document_mapping, _documents

    def merge_result(
        self,
        _split_documents,
        _document_mapping,
        _documents,
        res,
        threshold_score,
        top_n,
    ):
        # 合并切分文档
        if _split_documents:
            res = self.mapping_documents(_document_mapping, _documents, res)

        if threshold_score:
            res = [i for i in res if i["relevance_score"] >= threshold_score]

        if top_n:
            res = res[0:top_n]

        return res

    @record_time()
    def rerank(
        self,
        query: str,
        documents: List[str] = None,
        max_chunks_per_doc: int = 1000,
        overlap_tokens: int = 80,
        top_n=None,
        threshold_score=None,
        timeout=10,
        max_retries: int = 3,
        **kwargs,
    ) -> List[dict]:
        """
        对查询和文档进行重新排序，以提供与查询最相关的文档列表。

        该方法首先会将文档分割成块，然后使用特定的模型评估每块与查询的相关性，
        最后根据相关性得分对文档进行重新排序。

        参数:
        - query (str): 用户的查询字符串。
        - documents (List[str]): 需要重新排序的文档列表，每个文档是一个字符串。
        - max_chunks_per_doc (int): 每个文档最大分割块数。如果为0，则不限制分割块数。
        - overlap_tokens (int): 文档分割时，相邻块之间的重叠令牌数。用于保证上下文连贯性。
        - top_n (int, 可选): 返回的文档数量。如果未指定，则返回所有文档。
        - threshold_score (float, 可选): 相关性分数的阈值。只有文档的相关性分数达到或超过此值时才会被返回。
        - timeout (int): 请求的超时时间（秒）。
        - max_retries (int): 请求失败时的最大重试次数。

        返回:
        - List[dict]: 重新排序后的文档列表，每个文档以字典形式提供详细信息。
        """

        params, headers, _split_documents, _document_mapping, _documents = (
            self.build_param(query, documents, max_chunks_per_doc, overlap_tokens)
        )

        res = []
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url, headers=headers, json=params, timeout=timeout
                )
                response.raise_for_status()  # Raise an exception for HTTP errors
                res = response.json()["results"]
                break
            except RequestException as e:
                if attempt == max_retries - 1:
                    raise RerankError(str(e), self.base_url, self.model)
                else:
                    continue
            except Exception as e:
                raise RerankError(str(e), self.base_url, self.model)

        return self.merge_result(
            _split_documents, _document_mapping, _documents, res, threshold_score, top_n
        )

    @async_record_time()
    async def arerank(
        self,
        query: str,
        documents: List[str] = None,
        max_chunks_per_doc: int = 1000,
        overlap_tokens: int = 80,
        top_n=None,
        threshold_score=None,
        timeout=10,
        max_retries: int = 3,
        **kwargs,
    ) -> List[dict]:
        """
        对查询和文档进行重新排序，以提供与查询最相关的文档列表。

        该方法首先会将文档分割成块，然后使用特定的模型评估每块与查询的相关性，
        最后根据相关性得分对文档进行重新排序。

        参数:
        - query (str): 用户的查询字符串。
        - documents (List[str]): 需要重新排序的文档列表，每个文档是一个字符串。
        - max_chunks_per_doc (int): 每个文档最大分割块数。如果为0，则不限制分割块数。
        - overlap_tokens (int): 文档分割时，相邻块之间的重叠令牌数。用于保证上下文连贯性。
        - top_n (int, 可选): 返回的文档数量。如果未指定，则返回所有文档。
        - threshold_score (float, 可选): 相关性分数的阈值。只有文档的相关性分数达到或超过此值时才会被返回。
        - timeout (int): 请求的超时时间（秒）。
        - max_retries (int): 请求失败时的最大重试次数。

        返回:
        - List[dict]: 重新排序后的文档列表，每个文档以字典形式提供详细信息。
        """

        params, headers, _split_documents, _document_mapping, _documents = (
            self.build_param(query, documents, max_chunks_per_doc, overlap_tokens)
        )

        retry_count = 0
        async with httpx.AsyncClient() as client:
            while retry_count < max_retries:
                try:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=params,
                        timeout=httpx.Timeout(timeout),
                    )
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    res = response.json()["results"]
                    break
                except RequestException as e:
                    if retry_count == max_retries - 1:
                        raise RerankError(str(e), self.base_url, self.model)
                    else:
                        continue
                except Exception as e:
                    raise RerankError(str(e), self.base_url, self.model)
                finally:
                    retry_count += 1

        return self.merge_result(
            _split_documents, _document_mapping, _documents, res, threshold_score, top_n
        )
