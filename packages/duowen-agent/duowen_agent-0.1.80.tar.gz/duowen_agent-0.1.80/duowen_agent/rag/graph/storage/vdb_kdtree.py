import os

from duowen_agent.llm import OpenAIEmbedding
from duowen_agent.rag.graph.base import BaseVectorStorage
from duowen_agent.rag.graph.utils import create_file_dir
from duowen_agent.rag.models import Document
from duowen_agent.rag.nlp import LexSynth
from duowen_agent.rag.retrieval.kdtree import KDTreeVector


class KdTreeVectorStorage(BaseVectorStorage):

    def __init__(
        self,
        namespace: str,
        embedding: OpenAIEmbedding,
        lex_synth: LexSynth,
        working_dir: str = "./duowen_graph_data",
        cosine_better_than_threshold: float = 0.3,
    ):
        super().__init__(namespace=namespace)
        self._client_file_name = os.path.join(working_dir, f"vdb_{self.namespace}.svdb")
        self._embedding = embedding
        self._lex_synth = lex_synth
        create_file_dir(self._client_file_name)
        self._client = KDTreeVector(
            db_file=self._client_file_name,
            lex_synth=self._lex_synth,
            llm_embeddings_instance=self._embedding,
        )
        self._cosine_better_than_threshold = cosine_better_than_threshold

    def query_done_callback(self):
        pass

    def index_done_callback(self):
        self._client.save_to_disk()

    def index_start_callback(self):
        pass

    def upsert(self, data: dict[str, tuple[str, dict]]):
        docs = [
            Document(
                id=k,
                page_content=v[0],
                metadata=v[1],
            )
            for k, v in data.items()
        ]
        self._client.batch_add_document(docs)

    def delete_by_ids(self, ids: list[str]):
        self._client.delete_documents_by_ids(ids)

    def drop(self):
        self._client.init_vector()

    def query(self, query: str, top_k: int) -> list[dict]:
        data = self._client.semantic_search(
            query,
            top_k=top_k,
        )
        data = [
            i
            for i in data
            if i.vector_similarity_score > self._cosine_better_than_threshold
        ]

        return [
            {
                **i.result.metadata,
                "id": i.result.id,
                "distance": i.vector_similarity_score,
            }
            for i in data
        ]

    def get_by_id(self, id: str):
        data = self._client.get_documents_by_ids([id])
        if data:
            return {
                **data[0].metadata,
                "id": data[0].id,
            }
        else:
            return None

    def get_by_ids(self, ids: list[str]):
        data = self._client.get_documents_by_ids(ids)
        if data:
            return [
                {
                    **i.metadata,
                    "id": i.id,
                }
                for i in data
            ]
        else:
            return None
