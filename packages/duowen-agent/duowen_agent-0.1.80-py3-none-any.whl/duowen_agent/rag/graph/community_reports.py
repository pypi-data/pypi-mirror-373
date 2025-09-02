# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License
"""
Reference:
 - [graphrag](https://github.com/microsoft/graphrag)
"""

import logging
import re
import threading
from dataclasses import dataclass

import networkx as nx
import pandas as pd
from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.rag.graph.base import BaseLLM, BaseKVStorage
from duowen_agent.rag.graph.utils import (
    dict_has_keys_with_types,
    print_call_back,
    is_interrupt,
    convert_response_to_json,
)
from duowen_agent.utils.concurrency import concurrent_execute

from .leiden import add_community_info2graph, run
from .prompt import COMMUNITY_REPORT_PROMPT


@dataclass
class CommunityReportsResult:
    """Community reports result class definition."""

    output: list[str]
    structured_output: list[dict]


class CommunityReportsExtractor(BaseLLM):
    """Community reports extractor class definition."""

    _extraction_prompt: str
    _output_formatter_prompt: str
    _max_report_length: int

    def __init__(
        self,
        llm_instance: OpenAIChat,
        call_back_func: callable = print_call_back,
        interrupt_func: callable = is_interrupt,
        retry_cnt: int = 3,
        retry_sleep: int = 1,
        concurrent_num: int = 1,
        llm_cache: BaseKVStorage = None,
        max_report_length: int | None = None,
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
        self._extraction_prompt = COMMUNITY_REPORT_PROMPT
        self._max_report_length = max_report_length or 1500
        self.list_lock = threading.Lock()

    def extract(self, graph: nx.Graph):
        for node_degree in graph.degree:
            graph.nodes[str(node_degree[0])]["rank"] = int(node_degree[1])

        communities: dict[int, dict[str, dict]] = run(graph, {})

        res_str = []
        res_dict = []
        _community = []

        def _extract_community_report(cm_id, cm, _level, _level_max_chunks_cnt, index):
            nonlocal res_str, res_dict, _community
            weight = cm["weight"]
            ents = cm["nodes"]
            if len(ents) < 2:
                return
            ent_list = [
                {"entity": ent, "description": graph.nodes[ent]["description"]}
                for ent in ents
            ]
            ent_df = pd.DataFrame(ent_list)

            source_id = []
            for ent in ents:
                source_id.extend(graph.nodes[ent]["source_id"])

            _edges = []

            rela_list = []
            k = 0
            for i in range(0, len(ents)):
                if k >= 10000:
                    break
                for j in range(i + 1, len(ents)):
                    if k >= 10000:
                        break
                    edge = graph.get_edge_data(ents[i], ents[j])
                    if edge is None:
                        continue
                    _edges.append((ents[i], ents[j]))
                    rela_list.append(
                        {
                            "source": ents[i],
                            "target": ents[j],
                            "description": edge["description"],
                        }
                    )
                    source_id.extend(edge["source_id"])
                    k += 1
            rela_df = pd.DataFrame(rela_list)

            prompt_variables = {
                "entity_df": ent_df.to_csv(index_label="id"),
                "relation_df": rela_df.to_csv(index_label="id"),
            }
            text = self._extraction_prompt.format(**prompt_variables)

            _prompt = MessagesSet()
            _prompt.add_system(text)
            _prompt.add_system("Output:")

            response = self._chat(_prompt)

            response = re.sub(r"^[^\{]*", "", response)
            response = re.sub(r"[^\}]*$", "", response)
            response = re.sub(r"\{\{", "{", response)
            response = re.sub(r"\}\}", "}", response)
            logging.debug(response)
            response = convert_response_to_json(response)
            if response and not dict_has_keys_with_types(
                response,
                [
                    ("title", str),
                    ("summary", str),
                    ("findings", list),
                    ("rating", float),
                    ("rating_explanation", str),
                ],
            ):
                self._call_back_func(
                    msg=f"社区报告构建({'、'.join([i['entity'] for i in ent_list])[0:10]}...)，解析失败"
                )
                return
            response["weight"] = weight
            response["entities"] = ents
            response["edges"] = _edges
            response["level"] = _level
            response["source_id"] = list(set(source_id))
            response["occurrence"] = len(set(source_id)) / _level_max_chunks_cnt
            response["report"] = self._get_text_output(response)
            response["index"] = str(index)

            with self.list_lock:
                add_community_info2graph(graph, ents, response["index"], _level)
                res_str.append(response["report"])
                res_dict.append(response)
                self._call_back_func(
                    msg=f"社区报告构建({'、'.join([i['entity'] for i in ent_list])[0:10]}...)，已处理 {len(res_str)}/{len(_community)} 个"
                )

        _community = []
        for level, comm in communities.items():
            self._call_back_func(f"社区级别 {level}: 社区个数: {len(comm.keys())}")

            # 计算当前级别社区最大个数
            level_max_chunks_cnt = len(
                set(
                    sum(
                        [
                            graph.nodes[i]["source_id"]
                            for _, v in comm.items()
                            for i in v["nodes"]
                        ],
                        [],
                    )
                )
            )

            _community.extend(
                [
                    list(community) + [level] + [level_max_chunks_cnt] + [index]
                    for index, community in enumerate(comm.items())
                ]
            )

        concurrent_execute(
            _extract_community_report,
            _community,
            work_num=self.concurrent_num,
        )

        self._call_back_func("社区报告提取完成")

        return CommunityReportsResult(
            structured_output=res_dict,
            output=res_str,
        )

    @staticmethod
    def _get_text_output(parsed_output: dict) -> str:
        title = parsed_output.get("title", "Report")
        summary = parsed_output.get("summary", "")
        findings = parsed_output.get("findings", [])

        def finding_summary(finding: dict):
            if isinstance(finding, str):
                return finding
            return finding.get("summary")

        def finding_explanation(finding: dict):
            if isinstance(finding, str):
                return ""
            return finding.get("explanation")

        report_sections = "\n\n".join(
            f"## {finding_summary(f)}\n\n{finding_explanation(f)}" for f in findings
        )
        return f"# {title}\n\n{summary}\n\n{report_sections}"
