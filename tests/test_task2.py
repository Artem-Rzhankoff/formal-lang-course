import cfpq_data as cd
from project.task1 import get_graph_summary
from project.task2 import regex_to_dfa, graph_to_nfa
from test_task1 import available_graphs
import pytest


def test_regex_to_dfa():
    dfa = regex_to_dfa("(a|b)*c")

    assert dfa.accepts("c")
    assert dfa.accepts("abababaaac")
    assert not dfa.accepts("aabb")


@pytest.mark.parametrize("graph_name", available_graphs[:5])
def test_cfpq_graph_to_nfa(graph_name):
    graph = cd.graph_from_csv(cd.download(graph_name))
    graph_summary = get_graph_summary(graph_name)
    nfa = graph_to_nfa(graph, set(), set())

    assert set(nfa.start_states) == set(nfa.final_states) == set(nfa.states)
    assert len(set(nfa.states)) == graph_summary.vertex_count
    assert nfa.symbols == graph_summary.edge_labels
