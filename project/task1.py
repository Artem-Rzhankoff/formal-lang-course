import cfpq_data as cd
import networkx as nx
from typing import Tuple, Set
from dataclasses import dataclass


@dataclass
class GraphSummary:
    vertex_count: int
    edge_count: int
    edge_labels: Set[any]


def load_graph(graph_name):
    path = cd.download(graph_name)
    graph = cd.graph_from_csv(path)

    return graph


def save_graph_to_dot(graph: nx.MultiDiGraph, dot_filepath: str):
    dot_data = nx.drawing.nx_pydot.to_pydot(graph).to_string()
    with open(dot_filepath, "w") as f:
        f.write(dot_data)


def get_graph_summary(graph_name):
    graph = load_graph(graph_name)

    vertex_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    edge_labels = set(cd.get_sorted_labels(graph))

    return GraphSummary(vertex_count, edge_count, edge_labels)


def create_two_cycles_graph(
    first_cycle_vertex_count: int,
    second_cycle_vertex_count: int,
    labels: Tuple[str],
    output_path,
):
    if first_cycle_vertex_count < 1 or second_cycle_vertex_count < 1:
        raise ValueError("The number of vertices in cycle is less than 2")

    graph: nx.MultiDiGraph = cd.labeled_two_cycles_graph(
        first_cycle_vertex_count, second_cycle_vertex_count, labels=labels
    )
    save_graph_to_dot(graph, output_path)
