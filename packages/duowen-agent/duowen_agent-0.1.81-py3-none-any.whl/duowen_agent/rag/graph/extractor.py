import re
import threading
import time
from collections import defaultdict, Counter
from typing import List

from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.rag.graph.base import BaseLLM
from duowen_agent.utils.concurrency import concurrent_execute

from . import BaseKVStorage
from .prompt import (
    DEFAULT_TUPLE_DELIMITER,
    DEFAULT_RECORD_DELIMITER,
    DEFAULT_COMPLETION_DELIMITER,
    GRAPH_EXTRACTION_PROMPT,
    CONTINUE_PROMPT,
    LOOP_PROMPT,
    SUMMARIZE_DESCRIPTIONS_PROMPT,
    GRAPH_FIELD_SEP,
)
from .utils import (
    print_call_back,
    is_interrupt,
    clean_str,
    is_float_regex,
    flat_uniq_list,
    truncate,
)


class Extractor(BaseLLM):
    def __init__(
        self,
        llm_instance: OpenAIChat,
        language: str = "Chinese",
        entity_types: List[str] = None,
        max_gleanings: int = 2,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        retry_cnt: int = 3,
        retry_sleep: int = 1,
        concurrent_num: int = 1,
        llm_cache: BaseKVStorage = None,
    ):
        super().__init__(
            llm_instance,
            call_back_func,
            interrupt_func,
            retry_cnt,
            retry_sleep,
            concurrent_num,
            llm_cache,
        )

        self._language = language
        self._entity_types = entity_types or [
            "organization",
            "person",
            "geo",
            "event",
            "category",
        ]
        self._call_back_func = call_back_func
        self._interrupt_func = interrupt_func
        self.max_gleanings = max_gleanings
        self.entity_extract_prompt = GRAPH_EXTRACTION_PROMPT
        self.context_base = dict(
            tuple_delimiter=DEFAULT_TUPLE_DELIMITER,
            record_delimiter=DEFAULT_RECORD_DELIMITER,
            completion_delimiter=DEFAULT_COMPLETION_DELIMITER,
            entity_types=", ".join(self._entity_types),
        )
        self.continue_prompt = CONTINUE_PROMPT
        self.if_loop_prompt = LOOP_PROMPT
        self.total_cnt = 0
        self.current_cnt = 0
        self._lock = threading.Lock()

    def extract(self, chunks: dict[str, str]) -> tuple[list, list]:
        _params_lst = [{"chunk_key": k, "chunk_content": v} for k, v in chunks.items()]
        self.total_cnt = len(_params_lst)
        self.current_cnt = 0
        out_results = concurrent_execute(
            self._process_single_content,
            _params_lst,
            work_num=self.concurrent_num,
        )

        maybe_nodes = defaultdict(list)
        maybe_edges = defaultdict(list)
        for i in out_results:
            m_nodes, m_edges = i
            for k, v in m_nodes.items():
                maybe_nodes[k].extend(v)
            for k, v in m_edges.items():
                maybe_edges[tuple(sorted(k))].extend(v)

        self._call_back_func(
            msg=f"实体和关系提取完成, {len(maybe_nodes)} 节点, {len(maybe_edges)} 关系."
        )

        self._call_back_func("开始实体合并")
        all_entities_data = []

        concurrent_execute(
            self._merge_nodes,
            [
                {
                    "entity_name": en_nm,
                    "entities": ents,
                    "all_entities_data": all_entities_data,
                }
                for en_nm, ents in maybe_nodes.items()
            ],
            work_num=self.concurrent_num,
        )

        self._call_back_func("实体合并完成")
        self._call_back_func("开始关系合并")

        all_relationships_data = []
        concurrent_execute(
            self._merge_edges,
            [
                {
                    "src_id": src,
                    "tgt_id": tgt,
                    "edges_data": rels,
                    "all_relationships_data": all_relationships_data,
                }
                for (src, tgt), rels in maybe_edges.items()
            ],
            work_num=self.concurrent_num,
        )

        self._call_back_func("关系合并完成")

        if not len(all_entities_data) and not len(all_relationships_data):
            self._call_back_func("没有提取任何实体和关系，可能是您的语言模型异常")

        if not len(all_entities_data):
            self._call_back_func("没有抽取到任何实体")
        if not len(all_relationships_data):
            self._call_back_func("没有抽取任何关系")

        return all_entities_data, all_relationships_data

    def _process_single_content(
        self, chunk_key: str, chunk_content: str
    ) -> tuple[dict, dict]:
        _prompt = MessagesSet()
        _prompt.add_system(
            self.entity_extract_prompt.format(
                **{**self.context_base, "input_text": chunk_content}
            )
        )
        _prompt.add_user("Output:")
        response = self._chat(_prompt, temperature=0.3)
        results = response or ""
        _prompt.add_assistant(response)
        for i in range(self.max_gleanings):
            _prompt.add_user(self.continue_prompt)
            response = self._chat(_prompt, temperature=0.3)
            results += response or ""

            if i >= self.max_gleanings - 1:
                break

            _prompt.add_assistant(response)
            _prompt.add_user(self.if_loop_prompt)
            # print(_prompt.get_format_messages())
            continuation = self._chat(_prompt, temperature=0.8)
            # print(continuation)
            if continuation.strip() != "Y":
                break
            _prompt.add_assistant("Y")

        records = self._split_string_by_multi_markers(
            results,
            [
                DEFAULT_RECORD_DELIMITER,
                DEFAULT_COMPLETION_DELIMITER,
            ],
        )

        rcds = []
        for record in records:
            record = re.search(r"\((.*)\)", record)
            if record is None:
                continue
            rcds.append(record.group(1))
        records = rcds

        maybe_nodes, maybe_edges = self._entities_and_relations(
            chunk_key, records, DEFAULT_TUPLE_DELIMITER
        )
        with self._lock:
            self.current_cnt += 1

            self._call_back_func(
                msg=f"实体抽取({'、'.join([i for i in maybe_nodes])[:10]}...)，已处理 {self.current_cnt}/{self.total_cnt} 个 chunk"
            )

        return maybe_nodes, maybe_edges

    def _handle_entity_relation_summary(
        self, entity_or_relation_name: str, description: str
    ) -> str:
        summary_max_tokens = 512
        use_description = truncate(description, summary_max_tokens)
        description_list = (use_description.split(GRAPH_FIELD_SEP),)
        if len(description_list) <= 12:
            return use_description
        prompt_template = SUMMARIZE_DESCRIPTIONS_PROMPT
        context_base = dict(
            entity_name=entity_or_relation_name,
            description_list=description_list,
            language=self._language,
        )
        use_prompt = prompt_template.format(**context_base)
        _prompt = MessagesSet()

        _prompt.add_system(use_prompt)
        _prompt.add_user("Output: ")

        self._call_back_func(f"触发摘要: {entity_or_relation_name}")
        summary = self._chat(_prompt, temperature=0.8)
        return summary

    def _merge_nodes(self, entity_name: str, entities: list[dict], all_entities_data):
        if not entities:
            return
        entity_type = sorted(
            Counter([dp["entity_type"] for dp in entities]).items(),
            key=lambda x: x[1],
            reverse=True,
        )[0][0]
        description = GRAPH_FIELD_SEP.join(
            sorted(set([dp["description"] for dp in entities]))
        )
        already_source_ids = flat_uniq_list(entities, "source_id")
        description = self._handle_entity_relation_summary(entity_name, description)
        node_data = dict(
            entity_type=entity_type,
            description=description,
            source_id=already_source_ids,
        )
        node_data["entity_name"] = entity_name
        with self._lock:
            all_entities_data.append(node_data)

    def _merge_edges(
        self,
        src_id: str,
        tgt_id: str,
        edges_data: list[dict],
        all_relationships_data=None,
    ):
        if not edges_data:
            return
        weight = sum([edge["weight"] for edge in edges_data])
        description = GRAPH_FIELD_SEP.join(
            sorted(set([edge["description"] for edge in edges_data]))
        )
        description = self._handle_entity_relation_summary(
            f"{src_id} -> {tgt_id}", description
        )
        source_id = flat_uniq_list(edges_data, "source_id")
        edge_data = dict(
            src_id=src_id,
            tgt_id=tgt_id,
            description=description,
            weight=weight,
            source_id=source_id,
        )
        with self._lock:
            all_relationships_data.append(edge_data)

    @staticmethod
    def _handle_single_relationship_extraction(
        record_attributes: list[str], chunk_key: str
    ):
        if len(record_attributes) < 5 or record_attributes[0] != '"relationship"':
            return None
        # add this record as edge
        source = clean_str(record_attributes[1].upper())
        target = clean_str(record_attributes[2].upper())
        edge_description = clean_str(record_attributes[3])

        edge_source_id = chunk_key
        weight = (
            float(record_attributes[-1])
            if is_float_regex(record_attributes[-1])
            else 1.0
        )
        pair = sorted([source.upper(), target.upper()])
        return dict(
            src_id=pair[0],
            tgt_id=pair[1],
            weight=weight,
            description=edge_description,
            source_id=edge_source_id,
            metadata={"created_at": time.time()},
        )

    @staticmethod
    def _handle_single_entity_extraction(
        record_attributes: list[str],
        chunk_key: str,
    ):
        if len(record_attributes) < 4 or record_attributes[0] != '"entity"':
            return None
        # add this record as a node in the G
        entity_name = clean_str(record_attributes[1].upper())
        if not entity_name.strip():
            return None
        entity_type = clean_str(record_attributes[2].upper())
        entity_description = clean_str(record_attributes[3])
        entity_source_id = chunk_key
        return dict(
            entity_name=entity_name.upper(),
            entity_type=entity_type.upper(),
            description=entity_description,
            source_id=entity_source_id,
        )

    def _entities_and_relations(
        self, chunk_key: str, records: list, tuple_delimiter: str
    ):
        maybe_nodes = defaultdict(list)
        maybe_edges = defaultdict(list)
        ent_types = [t.lower() for t in self._entity_types]
        for record in records:
            record_attributes = self._split_string_by_multi_markers(
                record, [tuple_delimiter]
            )

            if_entities = self._handle_single_entity_extraction(
                record_attributes, chunk_key
            )
            if (
                if_entities is not None
                and if_entities.get("entity_type", "unknown").lower() in ent_types
            ):
                maybe_nodes[if_entities["entity_name"]].append(if_entities)
                continue

            if_relation = self._handle_single_relationship_extraction(
                record_attributes, chunk_key
            )
            if if_relation is not None:
                maybe_edges[(if_relation["src_id"], if_relation["tgt_id"])].append(
                    if_relation
                )
        return dict(maybe_nodes), dict(maybe_edges)

    @staticmethod
    def _split_string_by_multi_markers(content: str, markers: list[str]) -> list[str]:
        """Split a string by multiple markers"""
        if not markers:
            return [content]
        results = re.split("|".join(re.escape(marker) for marker in markers), content)
        return [r.strip() for r in results if r.strip()]
