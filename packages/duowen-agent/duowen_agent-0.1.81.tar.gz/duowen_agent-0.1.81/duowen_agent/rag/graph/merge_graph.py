import networkx as nx

from duowen_agent.llm import OpenAIChat
from .base import BaseLLM, GraphChange, BaseVectorStorage, BaseKVStorage
from .prompt import GRAPH_FIELD_SEP
from .utils import (
    print_call_back,
    is_interrupt,
    load_json_graph,
    tidy_graph,
    dump_graph,
    get_from_to,
    NetworkXUtils,
)


class MergeGraph(BaseLLM):
    def __init__(
        self,
        graph_name: str,
        llm_instance: OpenAIChat,
        knowledge_graph_inst: BaseKVStorage,
        entity_vdb: BaseVectorStorage,
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
        self.knowledge_graph_inst = knowledge_graph_inst
        self.entity_vdb = entity_vdb
        self.graph_name = graph_name

    def merge(self, subgraph: nx.Graph) -> tuple[nx.Graph, GraphChange]:
        return self.merge_subgraph(subgraph)

    def merge_subgraph(
        self,
        subgraph: nx.Graph,
    ) -> tuple[nx.Graph, GraphChange]:

        change = GraphChange()
        old_graph = self.knowledge_graph_inst.get_by_id(self.graph_name)
        if old_graph is not None:
            old_graph = load_json_graph(old_graph)
            self._call_back_func("与现有图形进行合并")
            tidy_graph(old_graph, self._call_back_func)
            new_graph = self.graph_merge(old_graph, subgraph, change)
        else:
            new_graph = subgraph
            change.added_updated_nodes = set(new_graph.nodes())
            change.added_updated_edges = set(new_graph.edges())

        new_graph = NetworkXUtils(new_graph).pagerank()

        _entity_data = {}
        for i in change.added_updated_nodes:
            _node_data = new_graph.nodes.get(i)
            _entity_data[_node_data["entity_name"]] = (
                f'{_node_data["entity_name"]}: {_node_data["description"]}',
                _node_data,
            )
        self.entity_vdb.upsert(_entity_data)
        self._call_back_func("完成子图合并到全局图")
        self.knowledge_graph_inst.upsert({self.graph_name: dump_graph(new_graph)})
        return new_graph, change

    @staticmethod
    def graph_merge(g1: nx.Graph, g2: nx.Graph, change: GraphChange):
        """Merge graph g2 into g1 in place."""
        for node_name, attr in g2.nodes(data=True):
            change.added_updated_nodes.add(node_name)
            if not g1.has_node(node_name):
                g1.add_node(node_name, **attr)
                continue
            node = g1.nodes[node_name]
            node["description"] += GRAPH_FIELD_SEP + attr["description"]
            # A node's source_id indicates which chunks it came from.
            node["source_id"] += attr["source_id"]

        for source, target, attr in g2.edges(data=True):
            change.added_updated_edges.add(get_from_to(source, target))
            edge = g1.get_edge_data(source, target)
            if edge is None:
                g1.add_edge(source, target, **attr)
                continue
            edge["weight"] += attr.get("weight", 0)
            edge["description"] += GRAPH_FIELD_SEP + attr["description"]
            # edge["keywords"] += attr["keywords"]
            # A edge's source_id indicates which chunks it came from.
            edge["source_id"] += attr["source_id"]

        for node_degree in g1.degree:
            g1.nodes[str(node_degree[0])]["rank"] = int(node_degree[1])
        # A graph's source_id indicates which documents it came from.
        if "source_id" not in g1.graph:
            g1.graph["source_id"] = []
        g1.graph["source_id"] += g2.graph.get("source_id", [])
        return g1
