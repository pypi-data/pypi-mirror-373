from typing import Optional

import networkx as nx
from duowen_agent.llm import OpenAIChat
from duowen_agent.rag.graph.community_reports import CommunityReportsExtractor
from duowen_agent.rag.graph.merge_graph import MergeGraph
from duowen_agent.rag.graph.prompt import GRAPH_FIELD_SEP
from duowen_agent.rag.graph.query import LocalQuery
from duowen_agent.rag.graph.utils import load_json_graph, dump_graph, get_from_to
from duowen_agent.rag.splitter.base import BaseChunk

from .base import BaseKVStorage, GraphChange, BaseVectorStorage, QueryParam
from .extractor import Extractor
from .query import GlobalQuery
from .storage.kv_json import JsonKVStorage
from .utils import (
    print_call_back,
    is_interrupt,
    tidy_graph,
    compute_args_hash,
)

DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event", "category"]


class Graph:
    def __init__(
        self,
        llm_instance: OpenAIChat,
        chunk_func: BaseChunk,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        language: str = "Chinese",
        entity_types: list[str] = None,
        max_gleanings: int = 2,
        extractor_concurrent_num: int = 1,
        community_concurrent_num: int = 1,
        init_graph: nx.Graph = None,
        llm_cache: BaseKVStorage = JsonKVStorage("llm_cache"),
        full_docs: BaseKVStorage = JsonKVStorage("full_docs"),
        text_chunks: BaseKVStorage = JsonKVStorage("text_chunks"),
        knowledge_graph_inst: BaseKVStorage = JsonKVStorage("graph"),
        entity_vdb: BaseVectorStorage = None,
        community_vdb: BaseVectorStorage = None,
        graph_name: str = "duowen_graph",
    ):
        self.llm = llm_instance
        self.language = language
        self.chunk_func = chunk_func
        self.init_graph = init_graph

        # storage
        self.llm_cache = llm_cache
        self.full_docs = full_docs
        self.text_chunks = text_chunks
        self.entity_vdb = entity_vdb
        self.knowledge_graph_inst = knowledge_graph_inst
        self.graph_name = graph_name

        # entity_extractor
        self.entity_types = entity_types or DEFAULT_ENTITY_TYPES
        self.max_gleanings = max_gleanings
        self.extractor_concurrent_num = extractor_concurrent_num

        self.community_concurrent_num = community_concurrent_num
        self.community_report_length = 1500
        self.community_vdb = community_vdb

        # callback interrupt
        self.call_back_func = call_back_func
        self.interrupt_func = interrupt_func

    def get_graph(self) -> Optional[nx.Graph]:
        _data = self.knowledge_graph_inst.get_by_id(self.graph_name)
        if _data:
            return load_json_graph(self.knowledge_graph_inst.get_by_id(self.graph_name))
        else:
            return None

    def _chunk(self, docs: dict[str, str]) -> dict[str, str]:
        _data = {}
        for k, v in docs.items():
            _chunk_data = [i.page_content for i in self.chunk_func.chunk(v)]
            _chunk_id = [f"{k}_{compute_args_hash(i)}" for i in _chunk_data]
            _data.update(dict(zip(_chunk_id, _chunk_data)))

        _data = {k: v for k, v in _data.items() if not self.text_chunks.get_by_id(k)}
        self.text_chunks.upsert(_data)
        return _data

    def insert(self, docs: dict[str, str]):
        for i in [
            self.full_docs,
            self.text_chunks,
            self.entity_vdb,
            self.knowledge_graph_inst,
        ]:
            i.index_start_callback()

        _docs = {k: v for k, v in docs.items() if not self.full_docs.get_by_id(k)}
        if not _docs:
            self.call_back_func("没有需要处理的文件")
            return

        subgraph = self.generate_subgraph(_docs)
        if subgraph:
            self.merge_subgraph(subgraph)

        for i in [
            self.full_docs,
            self.text_chunks,
            self.entity_vdb,
            self.knowledge_graph_inst,
        ]:
            i.index_done_callback()

    def query(self, query: str, param: QueryParam = QueryParam()):

        if param.mode == "local":
            local_query = LocalQuery(
                llm_instance=self.llm,
                community_vdb=self.community_vdb,
                graph=self.get_graph(),
                text_chunks=self.text_chunks,
                entity_vdb=self.entity_vdb,
                call_back_func=self.call_back_func,
                interrupt_func=self.interrupt_func,
                query_param=param,
            )
            return local_query.query(query)

        elif param.mode == "global":
            global_query = GlobalQuery(
                llm_instance=self.llm,
                community_vdb=self.community_vdb,
                call_back_func=self.call_back_func,
                interrupt_func=self.interrupt_func,
                query_param=param,
            )
            return global_query.query(query)

    def build_community(self):
        for i in [self.community_vdb, self.knowledge_graph_inst]:
            i.index_start_callback()

        _graph = self.get_graph()
        for i in _graph.nodes:
            _graph.nodes[i]["clusters"] = []

        cr = CommunityReportsExtractor(
            llm_instance=self.llm,
            llm_cache=self.llm_cache,
            concurrent_num=self.community_concurrent_num,
            call_back_func=self.call_back_func,
            interrupt_func=self.interrupt_func,
            max_report_length=self.community_report_length,
        ).extract(_graph)

        _community_structure = cr.structured_output
        _community_reports = cr.output
        _community_vdata = {
            stru["index"]: (rep, stru)
            for stru, rep in zip(_community_structure, _community_reports)
        }
        self.community_vdb.drop()
        self.community_vdb.upsert(_community_vdata)
        self.knowledge_graph_inst.upsert({self.graph_name: dump_graph(_graph)})

        for i in [self.community_vdb, self.knowledge_graph_inst]:
            i.index_done_callback()

    def generate_subgraph(
        self,
        docs: dict[str, str],
    ) -> Optional[nx.Graph]:
        self.full_docs.upsert(docs)
        chunks = self._chunk(docs)

        if not chunks:
            self.call_back_func("没有要处理的文本块")
            return

        ents, rels = Extractor(
            llm_instance=self.llm,
            language=self.language,
            entity_types=self.entity_types,
            max_gleanings=self.max_gleanings,
            llm_cache=self.llm_cache,
            concurrent_num=self.extractor_concurrent_num,
            call_back_func=self.call_back_func,
            interrupt_func=self.interrupt_func,
        ).extract(chunks)

        subgraph = nx.Graph()
        for ent in ents:
            assert "description" in ent, f"entity {ent} does not have description"
            subgraph.add_node(ent["entity_name"], **ent)

        ignored_rels = 0
        for rel in rels:
            assert "description" in rel, f"relation {rel} does not have description"
            if not subgraph.has_node(rel["src_id"]) or not subgraph.has_node(
                rel["tgt_id"]
            ):
                ignored_rels += 1
                continue
            subgraph.add_edge(
                rel["src_id"],
                rel["tgt_id"],
                **rel,
            )
        if ignored_rels:
            self.call_back_func(f"由于缺少实体而忽略了 {ignored_rels} 关系")
        tidy_graph(subgraph, self.call_back_func, check_attribute=False)
        return subgraph

    def merge_subgraph(
        self,
        subgraph: nx.Graph,
    ):
        MergeGraph(
            graph_name=self.graph_name,
            llm_instance=self.llm,
            knowledge_graph_inst=self.knowledge_graph_inst,
            entity_vdb=self.entity_vdb,
            call_back_func=self.call_back_func,
            interrupt_func=self.interrupt_func,
            concurrent_num=self.extractor_concurrent_num,
            llm_cache=self.llm_cache,
        ).merge(subgraph)
