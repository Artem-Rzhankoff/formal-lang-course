import itertools

import scipy as sp
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import State
from pyformlang.rsa import Box, RecursiveAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.cfg import CFG
from project.task2 import graph_to_nfa
from project.task3 import intersect_automata
from project.task3 import AdjacencyMatrixFA
from typing import Iterable

import networkx as nx

__all__ = ["cfg_to_rsm", "ebnf_to_rsm", "tensor_based_cfpq"]


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(cfg.to_text())


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(ebnf)

def get_edges_from_fa(
    fa: NondeterministicFiniteAutomaton,
) -> set[tuple[State, Symbol, State]]:
    edges = set()
    for start_state, links in fa.to_dict().items():
        for label, end_states in links.items():
            if not isinstance(end_states, Iterable):
                edges.add((start_state, label, end_states))
                continue

            for end_state in end_states:
                edges.add((start_state, label, end_state))

    return edges


def rsm_to_nfa(
    rsm: RecursiveAutomaton,
) -> NondeterministicFiniteAutomaton:
    def new_st(mark: Symbol, state: State) -> State:
        return State((mark, state.value))

    boxes: dict[Symbol, Box] = rsm.boxes
    _s = set()
    _f = set()
    _t = []

    for var, box in boxes.items():
        for st1, lbl, st2 in get_edges_from_fa(box.dfa):
            new_st1, new_st2 = new_st(var, st1), new_st(var, st2)
            _t.append((new_st1, lbl, new_st2))

        for start_state in box.start_state:
            new_start = new_st(var, start_state)
            _s.add(new_start)

        for final_state in box.final_states:
            new_final = new_st(var, final_state)
            _f.add(new_final)

    rsm_nfa = NondeterministicFiniteAutomaton(start_state=_s, final_states=_f)
    rsm_nfa.add_transitions(_t)
    return rsm_nfa


def tensor_based_cfpq(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    def _get_g_delta(
        _closure: sp.sparse.csc_matrix,
        _intersection: AdjacencyMatrixFA,
    ) -> dict[Symbol, sp.sparse.csc_matrix]:
        def _unpack_kron_state(kron_state: State) -> tuple[State, State]:
            return State(kron_state[0]), State(kron_state[1])

        def _get_box_label(rsm_state: State) -> Symbol:
            return rsm_state.value.value[0]

        ans: dict[Symbol, sp.sparse.csc_matrix] = {}
        for idx1, idx2 in zip(*_closure.nonzero()):
            kron_st1, kron_st2 = _intersection.idx_by_state[idx1], _intersection.idx_by_state[idx2]
            print(kron_st1[0], kron_st1[1])
            g_st1, rsm_st1 = _unpack_kron_state(kron_st1)
            g_st2, rsm_st2 = _unpack_kron_state(kron_st2)

            g_idx1, g_idx2 = g_matrix.states[g_st1], g_matrix.states[g_st2]

            assert _get_box_label(rsm_st1) == _get_box_label(rsm_st2)

            if not (
                (rsm_matrix.states[rsm_st1] in rsm_matrix.start_states) # инвертируем
                and (rsm_matrix.states[rsm_st2] in rsm_matrix.final_states)
            ):
                continue

            label = _get_box_label(rsm_st1)
            n = len(g_matrix.states)
            if (
                label not in g_matrix.matricies
                or not g_matrix.matricies[label][g_idx1, g_idx2]
            ):
                ans.setdefault(label, sp.sparse.csc_matrix((n, n), dtype=bool))[
                    g_idx1, g_idx2
                ] = True

        return ans

    graph_nfa = graph_to_nfa(graph, start_nodes, final_nodes)
    rsm_nfa = rsm_to_nfa(rsm)

    g_matrix = AdjacencyMatrixFA(graph_nfa)
    rsm_matrix = AdjacencyMatrixFA(rsm_nfa)

    while True:
        fa_matrix = intersect_automata(g_matrix, rsm_matrix)
        closure: sp.sparse.csc_matrix = fa_matrix.transitive_closure()
        g_delta = _get_g_delta(closure, fa_matrix)
        if not g_delta:
            break
        g_matrix.update_matricies(g_delta)

    start_symbol = rsm.initial_label
    if start_symbol in g_matrix.matricies:
        start_m = g_matrix.matricies[start_symbol]
        return {
            (start, final)
            for (start, final) in itertools.product(start_nodes, final_nodes)
            if start_m[
                g_matrix.states[State(start)], g_matrix.states[State(final)]
            ]
        }

    return set()