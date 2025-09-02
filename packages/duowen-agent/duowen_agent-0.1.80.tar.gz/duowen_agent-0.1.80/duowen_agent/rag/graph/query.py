import logging
from collections import Counter
from typing import Optional

import networkx as nx
from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.rag.graph.base import (
    BaseLLM,
    BaseVectorStorage,
    BaseKVStorage,
    QueryParam,
)
from duowen_agent.rag.graph.prompt import (
    GLOBAL_MAP_RAG_POINTS,
    FAIL_RESPONSE,
    GLOBAL_REDUCE_RAG_RESPONSE,
    LOCAL_RAG_RESPONSE,
)
from duowen_agent.utils.concurrency import concurrent_execute

from .utils import (
    print_call_back,
    is_interrupt,
    convert_response_to_json,
    truncate_list_by_token_size,
    list_of_list_to_csv,
    NetworkXUtils,
)


class LocalQuery(BaseLLM):

    def __init__(
        self,
        llm_instance: OpenAIChat,
        community_vdb: BaseVectorStorage,
        graph: nx.Graph,
        text_chunks: BaseKVStorage,
        entity_vdb: BaseVectorStorage,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        retry_cnt: int = 3,
        retry_sleep: int = 1,
        query_param: QueryParam = QueryParam(mode="naive"),
    ):
        super().__init__(
            llm_instance, call_back_func, interrupt_func, retry_cnt, retry_sleep
        )
        self.community_vdb = community_vdb
        self.text_chunks = text_chunks
        self.entity_vdb = entity_vdb
        self.graph_utils = NetworkXUtils(graph)
        self.query_param = query_param

    def query(self, query: str):
        context = self._build_local_query_context(query)

        if self.query_param.only_need_context:
            return context
        if context is None:
            return FAIL_RESPONSE

        _prompt = MessagesSet()
        _prompt.add_system(
            LOCAL_RAG_RESPONSE.format(
                context_data=context, response_type=self.query_param.response_type
            )
        )
        _prompt.add_user(query)
        response = self._chat(_prompt)
        return response

    def _build_local_query_context(self, query: str):
        results = self.entity_vdb.query(query=query, top_k=self.query_param.top_k)
        if not len(results):
            return None

        node_datas = self.graph_utils.get_nodes_batch(
            [r["entity_name"] for r in results]
        )

        node_degrees = self.graph_utils.node_degrees_batch(
            [r["entity_name"] for r in results]
        )

        node_datas = [
            {**n, "entity_name": k["entity_name"], "rank": d}
            for k, n, d in zip(results, node_datas, node_degrees)
            if n is not None
        ]

        if self.community_vdb:
            use_communities = self._find_most_related_community_from_entities(
                node_datas
            )
        else:
            use_communities = []

        use_text_units = self._find_most_related_text_unit_from_entities(node_datas)
        # print(use_text_units)

        use_relations = self._find_most_related_edges_from_entities(node_datas)

        self._call_back_func(
            f"使用 {len(node_datas)} 实体, {len(use_communities)} 社区, {len(use_relations)} 关系, {len(use_text_units)} 文本单元"
        )
        entites_section_list = [["id", "entity", "type", "description", "rank"]]
        for i, n in enumerate(node_datas):
            entites_section_list.append(
                [
                    i,
                    n["entity_name"],
                    n.get("entity_type", "UNKNOWN"),
                    n.get("description", "UNKNOWN"),
                    n["rank"],
                ]
            )
        entities_context = list_of_list_to_csv(entites_section_list)

        relations_section_list = [
            ["id", "source", "target", "description", "weight", "rank"]
        ]
        for i, e in enumerate(use_relations):
            relations_section_list.append(
                [
                    i,
                    e["src_tgt"][0],
                    e["src_tgt"][1],
                    e["description"],
                    e["weight"],
                    e["rank"],
                ]
            )
        relations_context = list_of_list_to_csv(relations_section_list)

        communities_section_list = [["id", "content"]]
        for i, c in enumerate(use_communities):
            communities_section_list.append([i, c["report"]])
        communities_context = list_of_list_to_csv(communities_section_list)

        text_units_section_list = [["id", "content"]]
        for i, t in enumerate(use_text_units):
            text_units_section_list.append([i, t])
        text_units_context = list_of_list_to_csv(text_units_section_list)
        return f"""-----Reports-----
```csv
{communities_context}
```
-----Entities-----
```csv
{entities_context}
```
-----Relationships-----
```csv
{relations_context}
```
-----Sources-----
```csv
{text_units_context}
```
"""

    def _find_most_related_edges_from_entities(
        self,
        node_datas: list[dict],
    ):
        all_related_edges = self.graph_utils.get_nodes_edges_batch(
            [dp["entity_name"] for dp in node_datas]
        )

        all_edges = []
        seen = set()

        for this_edges in all_related_edges:
            for e in this_edges:
                sorted_edge = tuple(sorted(e))
                if sorted_edge not in seen:
                    seen.add(sorted_edge)
                    all_edges.append(sorted_edge)

        all_edges_pack = self.graph_utils.get_edges_batch(all_edges)
        all_edges_degree = self.graph_utils.edge_degrees_batch(all_edges)
        all_edges_data = [
            {"src_tgt": k, "rank": d, **v}
            for k, v, d in zip(all_edges, all_edges_pack, all_edges_degree)
            if v is not None
        ]
        all_edges_data = sorted(
            all_edges_data, key=lambda x: (x["rank"], x["weight"]), reverse=True
        )
        all_edges_data = truncate_list_by_token_size(
            all_edges_data,
            key=lambda x: x["description"],
            max_token_size=self.query_param.local_max_token_for_local_context,
        )
        return all_edges_data

    def _find_most_related_text_unit_from_entities(self, node_datas):
        text_units = [dp["source_id"] for dp in node_datas]
        edges = self.graph_utils.get_nodes_edges_batch(
            [dp["entity_name"] for dp in node_datas]
        )

        all_one_hop_nodes = set()
        for this_edges in edges:
            if not this_edges:
                continue
            all_one_hop_nodes.update([e[1] for e in this_edges])
        all_one_hop_nodes = list(all_one_hop_nodes)
        all_one_hop_nodes_data = self.graph_utils.get_nodes_batch(all_one_hop_nodes)

        all_one_hop_text_units_lookup = {
            k: v["source_id"]
            for k, v in zip(all_one_hop_nodes, all_one_hop_nodes_data)
            if v is not None
        }
        all_text_units_lookup = {}
        for index, (this_text_units, this_edges) in enumerate(zip(text_units, edges)):
            for c_id in this_text_units:
                if c_id in all_text_units_lookup:
                    continue
                relation_counts = 0
                for e in this_edges:
                    if (
                        e[1] in all_one_hop_text_units_lookup
                        and c_id in all_one_hop_text_units_lookup[e[1]]
                    ):
                        relation_counts += 1
                all_text_units_lookup[c_id] = {
                    "data": self.text_chunks.get_by_id(c_id),
                    "order": index,
                    "relation_counts": relation_counts,
                }
        if any([v is None for v in all_text_units_lookup.values()]):
            logging.warning("Text chunks are missing, maybe the storage is damaged")
        all_text_units = [
            {"id": k, **v} for k, v in all_text_units_lookup.items() if v is not None
        ]
        # for i in all_text_units: print(i)
        all_text_units = sorted(
            all_text_units, key=lambda x: (x["order"], -x["relation_counts"])
        )
        all_text_units = truncate_list_by_token_size(
            all_text_units,
            key=lambda x: x["data"],
            max_token_size=self.query_param.local_max_token_for_text_unit,
        )
        all_text_units = [t["data"] for t in all_text_units]
        return all_text_units

    def _find_most_related_community_from_entities(
        self,
        node_datas: list[dict],
    ):
        related_communities = []
        for node_d in node_datas:
            if "clusters" not in node_d:
                continue
            related_communities.extend(node_d["clusters"])

        # print(related_communities)
        related_community_dup_keys = [
            str(dp["communities"])
            for dp in related_communities
            if dp["level"] <= self.query_param.level
        ]
        related_community_keys_counts = dict(Counter(related_community_dup_keys))
        # print(related_community_keys_counts)

        _related_community_datas = [
            self.community_vdb.get_by_id(k)
            for k in related_community_keys_counts.keys()
        ]
        # print(_related_community_datas)

        related_community_datas = {
            k: v
            for k, v in zip(
                related_community_keys_counts.keys(), _related_community_datas
            )
            if v is not None
        }
        related_community_keys = sorted(
            related_community_keys_counts.keys(),
            key=lambda k: (
                related_community_keys_counts[k],
                related_community_datas[k].get("rating", -1),
            ),
            reverse=True,
        )
        sorted_community_datas = [
            related_community_datas[k] for k in related_community_keys
        ]

        use_community_reports = truncate_list_by_token_size(
            sorted_community_datas,
            key=lambda x: x["report"],
            max_token_size=self.query_param.local_max_token_for_community_report,
        )

        if self.query_param.local_community_single_one:
            use_community_reports = use_community_reports[:1]
        return use_community_reports


class GlobalQuery(BaseLLM):
    def __init__(
        self,
        llm_instance: OpenAIChat,
        community_vdb: BaseVectorStorage,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        retry_cnt: int = 3,
        retry_sleep: int = 1,
        query_param: QueryParam = QueryParam(mode="global"),
    ):
        super().__init__(
            llm_instance,
            call_back_func,
            interrupt_func,
            retry_cnt,
            retry_sleep,
            query_param.global_concurrent_num,
            None,
        )
        self.community_vdb = community_vdb
        self.query_param = query_param

    def query(self, query: str):
        data = self._community_retrieval(query)
        points_context = self._map_global_communities(query, data)

        if self.query_param.only_need_context:
            return points_context

        elif points_context == FAIL_RESPONSE:
            return points_context
        else:
            _prompt = MessagesSet()
            _prompt.add_system(
                GLOBAL_REDUCE_RAG_RESPONSE.format(
                    report_data=points_context,
                    response_type=self.query_param.response_type,
                )
            )
            return self._chat(_prompt)

    def _community_retrieval(
        self,
        query: Optional[str] = None,
        entities: Optional[list[str]] = None,
    ):
        data = self.community_vdb.query(
            query, top_k=self.query_param.global_max_consider_community * 10
        )

        data = [
            i
            for i in data
            if i.get("rating", 0) >= self.query_param.global_min_community_rating
        ]
        if entities:
            data = [i for i in data if bool(set(i["entities"]) & set(entities))]

        if self.query_param.level:
            data = [i for i in data if i["level"] <= self.query_param.level]

        data = sorted(
            data, key=lambda x: (x["occurrence"], x.get("rating", 0)), reverse=True
        )[: self.query_param.global_max_consider_community]
        return data

    def _map_global_communities(
        self,
        query: str,
        communities_data: list[dict],
    ):
        community_groups = []
        while len(communities_data):

            this_group = truncate_list_by_token_size(
                communities_data,
                key=lambda x: x["report"],
                max_token_size=self.query_param.global_max_token_for_community_report,
            )
            community_groups.append(this_group)
            communities_data = communities_data[len(this_group) :]

        def _process(community_truncated_datas: list[dict]) -> list[dict]:
            communities_section_list = [["id", "content", "rating", "importance"]]
            for i, c in enumerate(community_truncated_datas):
                communities_section_list.append(
                    [
                        i,
                        c["report"],
                        c.get("rating", 0),
                        c["occurrence"],
                    ]
                )
            community_context = list_of_list_to_csv(communities_section_list)
            sys_prompt_temp = GLOBAL_MAP_RAG_POINTS
            sys_prompt = sys_prompt_temp.format(context_data=community_context)

            _prompt = MessagesSet()
            _prompt.add_system(sys_prompt)
            _prompt.add_user(query)

            response = self._chat(_prompt)

            _data = convert_response_to_json(response)
            return _data.get("points", [])

        logging.info(f"分组到 {len(community_groups)} 组以进行全局搜索")

        map_communities_points = concurrent_execute(
            _process,
            [{"community_truncated_datas": i} for i in community_groups],
            work_num=self.concurrent_num,
        )

        final_support_points = []

        for i, mc in enumerate(map_communities_points):
            for point in mc:
                if "description" not in point:
                    continue
                final_support_points.append(
                    {
                        "analyst": i,
                        "answer": point["description"],
                        "score": point.get("score", 1),
                    }
                )
        final_support_points = [p for p in final_support_points if p["score"] > 0]
        if not len(final_support_points):
            return FAIL_RESPONSE

        final_support_points = sorted(
            final_support_points, key=lambda x: x["score"], reverse=True
        )
        final_support_points = truncate_list_by_token_size(
            final_support_points,
            key=lambda x: x["answer"],
            max_token_size=self.query_param.global_max_token_for_community_report,
        )
        points_context = []
        for dp in final_support_points:
            points_context.append(
                f"""----Analyst {dp['analyst']}----
Importance Score: {dp['score']}
{dp['answer']}
"""
            )
        points_context = "\n".join(points_context)
        return points_context
