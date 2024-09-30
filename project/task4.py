from networkx import MultiDiGraph
from pyformlang.finite_automaton import Symbol
from functools import reduce
from scipy.sparse import bsr_matrix, vstack
from project.task2 import regex_to_dfa, graph_to_nfa
from project.task3 import AdjacencyMatrixFA

def ms_bfs_based_rpq(regex: str, graph: MultiDiGraph, start_nodes: set[int],
         final_nodes: set[int]) -> set[tuple[int, int]]:
    
    adj_matrix_dfa = AdjacencyMatrixFA(regex_to_dfa(regex))
    adj_matrix_nfa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))

    transposed_matricies : dict[Symbol, bsr_matrix] = {}
    for symbol, matrix in adj_matrix_dfa.matricies.items():
        transposed_matricies[symbol] = matrix.transpose()
        
    dfa_states_count = adj_matrix_dfa.states_count
    dfa_start_state = list(adj_matrix_dfa.start_states)[0]

    nfa_states_count = adj_matrix_nfa.states_count
    nfa_start_states = adj_matrix_nfa.start_states

    front = vstack([
        bsr_matrix(([True], ([dfa_start_state], [nfa_start_state])), shape=(dfa_states_count, nfa_states_count), dtype=bool)
        for nfa_start_state in nfa_start_states
        ])
    visited = front

    symbols = adj_matrix_dfa.matricies.keys() & adj_matrix_nfa.matricies.keys()
    
    while front.count_nonzero() > 0:
        next_fronts: dict[Symbol, bsr_matrix] = {}
        for s in symbols:
            next_front = front @ adj_matrix_nfa.matricies[s]
            next_fronts[s] = vstack(
                [
                    transposed_matricies[s]
                    @ next_front[dfa_states_count * i : dfa_states_count * (i+1)]
                    for i in range(len(start_nodes))
                ]
            )
        front = reduce(lambda x, y: x + y, next_fronts.values(), front)
        front = front > visited
        visited += front

    result: set[tuple[int, int]] = set()
    reversed_nfa_states = {value: key for key, value in adj_matrix_nfa.states.items()}

    for dfa_final in adj_matrix_dfa.final_states:
        for i, nfa_start in enumerate(nfa_start_states): 

            visited_slice = visited[
                dfa_states_count * i : dfa_states_count * (i + 1)
            ]

            for nfa_reached in visited_slice.getrow(dfa_final).indices:
                if nfa_reached in adj_matrix_nfa.final_states:
                    result.add((reversed_nfa_states[nfa_start], reversed_nfa_states[nfa_reached]))

    return result
