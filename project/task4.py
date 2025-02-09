import numpy as np
from typing import Type
from networkx import MultiDiGraph
from pyformlang.finite_automaton import Symbol
from functools import reduce
import scipy.sparse as sp
from project.task2 import regex_to_dfa, graph_to_nfa
from project.task3 import AdjacencyMatrixFA


def _initial_front(
    dfa: AdjacencyMatrixFA, dfa_start_state: int, nfa: AdjacencyMatrixFA, sparse_format: Type[sp.spmatrix] = sp.csr_matrix
):
    nfa_st_states_count = len(nfa.start_states)
    data = np.ones(nfa_st_states_count, dtype=bool)
    rows = [dfa_start_state + dfa.states_count * i for i in range(nfa_st_states_count)]
    columns = [st_state for st_state in nfa.start_states]

    return sparse_format(
        (data, (rows, columns)),
        shape=(dfa.states_count * nfa_st_states_count, nfa.states_count),
        dtype=bool,
    )


def ms_bfs_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int], sparse_format: Type[sp.spmatrix] = sp.csr_matrix
) -> set[tuple[int, int]]:
    adj_matrix_dfa = AdjacencyMatrixFA(regex_to_dfa(regex), sparse_format)
    adj_matrix_nfa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes), sparse_format)

    transposed_matricies: dict[Symbol, Type[sp.spmatrix]] = {}
    for symbol, matrix in adj_matrix_dfa.matricies.items():
        transposed_matricies[symbol] = matrix.transpose()

    dfa_states_count = adj_matrix_dfa.states_count
    dfa_start_state = list(adj_matrix_dfa.start_states)[0]

    nfa_start_states = adj_matrix_nfa.start_states

    front = _initial_front(adj_matrix_dfa, dfa_start_state, adj_matrix_nfa, sparse_format)
    visited = front

    symbols = adj_matrix_dfa.matricies.keys() & adj_matrix_nfa.matricies.keys()

    while front.count_nonzero() > 0:
        next_fronts: dict[Symbol, Type[sp.spmatrix]] = {}
        for s in symbols:
            next_fronts[s] = front @ adj_matrix_nfa.matricies[s]

            for i in range(len(nfa_start_states)):
                next_fronts[s][i * dfa_states_count : (i + 1) * dfa_states_count] = (
                    transposed_matricies[s]
                    @ next_fronts[s][dfa_states_count * i : dfa_states_count * (i + 1)]
                )

        front = reduce(lambda x, y: x + y, next_fronts.values(), front)
        front = front > visited
        visited += front

    result = set()
    reversed_nfa_states = {value: key for key, value in adj_matrix_nfa.states.items()}

    for dfa_fn_state in adj_matrix_dfa.final_states:
        for i, nfa_start_state in enumerate(nfa_start_states):
            for nfa_reached in visited.getrow(
                dfa_states_count * i + dfa_fn_state
            ).indices:
                if nfa_reached in adj_matrix_nfa.final_states:
                    result.add(
                        (
                            reversed_nfa_states[nfa_start_state],
                            reversed_nfa_states[nfa_reached],
                        )
                    )

    return result
