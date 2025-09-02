import logging
import os
import pickle
from typing import List, Tuple, Dict, Any, Union, Optional

import numpy as np
from scipy.spatial import cKDTree

from duowen_agent.llm import OpenAIEmbedding
from duowen_agent.rag.models import Document, SearchResult
from .base import BaseVector
from ..nlp import LexSynth


class KDTreeVector(BaseVector):
    vectors: np.ndarray
    metadata: List[Dict[str, Any]]
    index: Union[cKDTree, None]
    next_id: int

    def __init__(
        self,
        llm_embeddings_instance: OpenAIEmbedding,
        lex_synth: LexSynth,
        db_file: str = "./local.svdb",
    ):

        super().__init__(lex_synth, llm_embeddings_instance)
        self.db_file = db_file
        self.init_vector()
        if self.db_file and os.path.exists(self.db_file):
            self.load_from_disk()
        else:
            self.init_vector()

    def init_vector(self):
        self.vectors: np.ndarray = np.array([])
        self.metadata: List[Dict[str, Any]] = []
        self.index: Union[cKDTree, None] = None
        self.next_id: int = 1

    def get_backend_type(self) -> str:
        raise "KDTree"

    def load_from_disk(
        self,
    ) -> None:
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, "rb") as file:
                    self.vectors, self.metadata = pickle.load(file)
            else:
                raise FileNotFoundError(f"File not found: {self.db_file}")
            self.__build_index()

            if self.metadata:
                self.next_id = max(meta["id"] for meta in self.metadata) + 1
            else:
                self.next_id = 1
        except Exception as e:
            print(f"Error loading from disk: {e}")

    def save_to_disk(self) -> None:
        try:
            with open(self.db_file, "wb") as file:
                pickle.dump((self.vectors, self.metadata), file)
        except Exception as e:
            print(f"Error saving to disk: {e}")

    def delete_to_disk(self) -> None:
        if self.db_file and os.path.exists(self.db_file):
            os.remove(self.db_file)

    def __build_index(self) -> None:
        if len(self.vectors) > 0:
            self.index = cKDTree(self.vectors)

    @staticmethod
    def normalize_vector(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def pretreated(self, document: Document) -> Document:
        if not document.vector:
            document.vector = self.llm_embeddings_instance.get_embedding(
                document.vector_content or document.page_content
            )[0]

        if not document.page_content_split:
            document.page_content_split = self.lex_synth.content_cut(
                document.page_content
            )

        return document

    def batch_pretreated(self, documents: list[Document]) -> list[Document]:
        if not documents[0].page_content_split:
            for document in documents:
                document.page_content_split = self.lex_synth.content_cut(
                    document.page_content
                )

        if not documents[0].vector:
            vectors = self.llm_embeddings_instance.get_embedding(
                [
                    document.vector_content or document.page_content
                    for document in documents
                ]
            )
            for document, vector in zip(documents, vectors):
                document.vector = vector

        return documents

    def add_document(self, document: Document, **kwargs) -> int:
        document = self.pretreated(document)

        embedding = document.vector

        embedding = self.normalize_vector(np.array(embedding))

        if self.vectors.size == 0:
            self.vectors = np.array([embedding])
        else:
            self.vectors = np.vstack([self.vectors, embedding])

        record_id = self.next_id
        self.next_id += 1  # Increment the next available ID

        if not document.id:
            document.id = str(record_id)

        record = {
            "id": record_id,
            "document": document.model_dump(),
        }

        self.metadata.append(record)
        self.__build_index()

        return record_id

    def batch_add_document(self, documents: list[Document], **kwargs) -> None:

        documents = self.batch_pretreated(documents)

        vectors = []
        for document in documents:
            vector = np.array(document.vector)
            vector = self.normalize_vector(vector)
            vectors.append(vector)
            if not document.id:
                document.id = str(self.next_id)
            metadata = {
                "id": self.next_id,
                "document": document.model_dump(),
            }
            self.next_id += 1
            self.metadata.append(metadata)

        if self.vectors.size == 0:
            self.vectors = np.array(vectors)
        else:
            self.vectors = np.vstack([self.vectors] + vectors)
        self.__build_index()

    def get_documents_by_ids(self, ids: list[str], **kwargs) -> List[Document]:
        _docs = [i for i in self.metadata if i["document"]["id"] in ids]
        return [Document(**i["document"]) for i in _docs]

    def delete_documents_by_ids(self, ids: list[str], **kwargs):
        indices_to_delete = [
            index
            for index, meta in enumerate(self.metadata)
            if meta["document"]["id"] in ids
        ]

        for index in sorted(indices_to_delete, reverse=True):
            self.vectors = np.delete(self.vectors, index, axis=0)
            del self.metadata[index]
        self.__build_index()

    def top_cosine_similarity(
        self, target_vector: np.ndarray, top_n: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        try:
            if self.index is None or len(self.vectors) == 0:
                print("The database is empty.")
                return []

            target_vector = self.normalize_vector(target_vector)

            # Adjust top_n if it's greater than the number of vectors
            top_n = min(top_n, len(self.vectors))

            distances, indices = self.index.query(target_vector.reshape(1, -1), k=top_n)

            # Ensure distances and indices are 1D
            distances = distances.flatten()
            indices = indices.flatten()

            similarities = 1 - distances**2 / 2

            return [(self.metadata[i], float(s)) for i, s in zip(indices, similarities)]
        except Exception as e:
            print(f"An error occurred during similarity search: {e}")
            return []

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = 0.0,
        query_embedding: np.ndarray | List[float] = None,
        **kwargs,
    ) -> list[SearchResult]:
        if len(self.vectors) == 0:
            logging.warning("The database is empty.")
            return []

        if not query_embedding:
            query_embedding = self.llm_embeddings_instance.get_embedding(query)[0]

        initial_results = self.top_cosine_similarity(query_embedding, top_k)

        return [
            SearchResult(
                result=Document(**result["document"]),
                vector_similarity_score=similarity,
            )
            for result, similarity in initial_results
            if similarity >= score_threshold
        ]

    def full_text_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = 0.0,
        **kwargs,
    ) -> list[SearchResult]:
        doc_sm = [i["document"]["page_content_split"] for i in self.metadata]
        text_similarity_data = self.lex_synth.text_similarity(
            question=query, docs_sm=doc_sm, qa=True
        )
        text_similarity_data = [
            (index, score) for index, score in enumerate(text_similarity_data)
        ]

        text_similarity_top_k = sorted(
            text_similarity_data, key=lambda x: x[1], reverse=True
        )[:top_k]

        return [
            SearchResult(
                result=self.metadata[i[0]]["document"], token_similarity_score=i[1]
            )
            for i in text_similarity_top_k
            if i[1] >= score_threshold
        ]
