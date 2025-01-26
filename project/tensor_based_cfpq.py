import itertools

import scipy as sp
from copy import deepcopy
from scipy.sparse import csc_matrix
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import State
from pyformlang.rsa import Box, RecursiveAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton.finite_automaton import to_symbol
from pyformlang.cfg import CFG, Epsilon, Production, Terminal
from pyformlang.regular_expression import Regex
from project.task3 import intersect_automata, AdjacencyMatrixFA, get_edges_from_fa
from project.task2 import graph_to_nfa

import networkx as nx

__all__ = ["cfg_to_rsm", "ebnf_to_rsm", "tensor_based_cfpq"]


def cfg_to_text(cfg: CFG) -> str:
    ans = []
    for prod in cfg.productions:
        ans.append(
            str(prod.head) + " -> " + " ".join([str(x.value) for x in prod.body])
        )

    return "\n".join(ans) + "\n"


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    cfg_norm = cfg.to_normal_form()
    if cfg.generate_epsilon():
        eps_prod = Production(cfg_norm.start_symbol, [])
        cfg_norm = CFG(
            start_symbol=cfg_norm.start_symbol,
            productions=list(cfg_norm.productions) + [eps_prod],
        )
    print("cfg_to_rsm")
    print(cfg_norm.to_text())
    return RecursiveAutomaton.from_text(cfg_to_text(cfg_norm), cfg.start_symbol)


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(ebnf)


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
    graph_nfa: NondeterministicFiniteAutomaton,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    def _get_g_delta(
        _closure: csc_matrix,
        _intersection: AdjacencyMatrixFA,
    ) -> dict[Symbol, csc_matrix]:
        def _unpack_kron_state(kron_state: State) -> tuple[State, State]:
            return State(kron_state[0]), State(kron_state[1])

        def _get_box_label(rsm_state: State) -> Symbol:
            return rsm_state.value.value[0]

        ans: dict[Symbol, sp.sparse.csc_matrix] = {}
        for idx1, idx2 in zip(*_closure.nonzero()):
            kron_st1, kron_st2 = (
                _intersection.idx_by_state[idx1],
                _intersection.idx_by_state[idx2],
            )
            g_st1, rsm_st1 = _unpack_kron_state(kron_st1)
            g_st2, rsm_st2 = _unpack_kron_state(kron_st2)

            g_idx1, g_idx2 = g_matrix.states[g_st1], g_matrix.states[g_st2]

            assert _get_box_label(rsm_st1) == _get_box_label(rsm_st2)

            if not (
                (rsm_matrix.states[rsm_st1] in rsm_matrix.start_states)  # инвертируем
                and (rsm_matrix.states[rsm_st2] in rsm_matrix.final_states)
            ):
                continue

            label = _get_box_label(rsm_st1)
            n = len(g_matrix.states)
            if (
                label not in g_matrix.matricies
                or not g_matrix.matricies[label][g_idx1, g_idx2]
            ):
                ans.setdefault(label, csc_matrix((n, n), dtype=bool))[
                    g_idx1, g_idx2
                ] = True

        return ans

    # rsm_nfa = rsm_to_nfa(RecursiveAutomaton.from_regex(Regex("a*"), Symbol("S")))
    rsm_nfa = rsm_to_nfa(rsm)
    g_matrix = AdjacencyMatrixFA(graph_nfa)
    rsm_matrix = AdjacencyMatrixFA(rsm_nfa)
    while True:
        fa_matrix = intersect_automata(g_matrix, rsm_matrix)
        closure: csc_matrix = fa_matrix.transitive_closure()
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
            if start_m[g_matrix.states[State(start)], g_matrix.states[State(final)]]
        }

    return set()
