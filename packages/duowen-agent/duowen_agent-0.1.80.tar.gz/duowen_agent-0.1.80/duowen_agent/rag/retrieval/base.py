from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
from duowen_agent.llm import OpenAIEmbedding
from duowen_agent.rag.nlp import LexSynth

from ..models import Document, SearchResult


class BaseVector(ABC):
    def __init__(self, lex_synth: LexSynth, llm_embeddings_instance: OpenAIEmbedding):
        self.lex_synth = lex_synth
        self.llm_embeddings_instance = llm_embeddings_instance

    @abstractmethod
    def get_backend_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = 0.0,
        query_embedding: np.ndarray | List[float] = None,
        **kwargs
    ) -> list[SearchResult]:
        raise NotImplementedError

    @abstractmethod
    def full_text_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = 0.0,
        **kwargs
    ) -> list[SearchResult]:
        raise NotImplementedError

    @abstractmethod
    def add_document(self, document: Document, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def batch_add_document(self, documents: list[Document], batch_num: int, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_documents_by_ids(self, ids: list[str], **kwargs) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def delete_documents_by_ids(self, ids: list[str], **kwargs):
        raise NotImplementedError

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = 0.0,
        query_embedding: np.ndarray | List[float] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        **kwargs
    ) -> list[SearchResult]:

        if not query_embedding:
            query_embedding = self.llm_embeddings_instance.get_embedding(query)[0]

        full_text_data = self.full_text_search(query, top_k=top_k, **kwargs)
        semantic_data = self.semantic_search(
            query, top_k=top_k, query_embedding=query_embedding, **kwargs
        )

        _data: List[Document] = list(
            set([i.result for i in full_text_data] + [i.result for i in semantic_data])
        )

        hybrid_data = self.lex_synth.hybrid_similarity(
            question=query,
            question_vector=query_embedding,
            docs_vector=[i.vector for i in _data],
            docs_sm=[
                (
                    i.page_content_split
                    if i.page_content_split
                    else self.lex_synth.content_cut(i.page_content)
                )
                for i in _data
            ],
            tkweight=keyword_weight,
            vtweight=vector_weight,
        )

        hybrid_data_index = [(index, score) for index, score in enumerate(hybrid_data)]

        hybrid_data_index = sorted(hybrid_data_index, key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        return [
            SearchResult(result=_data[i[0]], rerank_similarity_score=i[1])
            for i in hybrid_data_index
            if i[1] >= score_threshold
        ]
