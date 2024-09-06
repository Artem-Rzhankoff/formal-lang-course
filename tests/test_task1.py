import cfpq_data as cd
import networkx as nx
from project.task1 import *
import pytest

available_graphs = cd.DATASET

@pytest.mark.parametrize("graph_name", available_graphs[:5])
def test_get_graph_summary_on_archieve_graphs(graph_name):
    graph = cd.graph_from_csv(cd.download(graph_name))
    expected_graph_summary = GraphSummary(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        edge_labels = set(d['label'] for _, _, d in graph.edges(data=True))
    )

    actual_graph_summary = get_graph_summary(graph_name)

    assert actual_graph_summary == expected_graph_summary

def test_get_graph_with_error_graphname():
    with pytest.raises(Exception):
        get_graph_summary("wrong name")

expected_graph_1_1 = nx.DiGraph(
        [
            (0, 1, dict(label="x")),
            (1, 0, dict(label="x")),
            (0, 2, dict(label="y")),
            (2, 0, dict(label="y"))
        ]
    )

expected_graph_1_2 = nx.DiGraph(
        [
            (0, 1, dict(label="x")),
            (1, 0, dict(label="x")),
            (0, 2, dict(label="y")),
            (2, 3, dict(label="y")),
            (3, 0, dict(label="y"))
        ]
    )

@pytest.mark.parametrize("expected_graph, cycle_node_count1, cycle_node_count2", [
    (expected_graph_1_1, 1, 1),
    (expected_graph_1_2, 1, 2)
])
def test_create_two_cycles_graph(tmp_path, expected_graph, cycle_node_count1, cycle_node_count2):
    path_to_actual_save = tmp_path / "graph.dot"
    create_two_cycles_graph(cycle_node_count1, cycle_node_count2, ("x", "y"), path_to_actual_save)

    actual_graph = nx.DiGraph(nx.drawing.nx_pydot.read_dot(path_to_actual_save))

    node_match = nx.algorithms.isomorphism.categorical_node_match('label', None)
    edge_match = nx.algorithms.isomorphism.categorical_edge_match('weight', None)

    assert nx.is_isomorphic(
        actual_graph, expected_graph, node_match=node_match, edge_match=edge_match
    )


def test_create_two_cycles_graph_with_one_zero_length_cycle(tmp_path):
    path_to_actual_save = tmp_path / "graph.dot"

    with pytest.raises(Exception):
        create_two_cycles_graph(1, 0, ("x", "y", path_to_actual_save))
