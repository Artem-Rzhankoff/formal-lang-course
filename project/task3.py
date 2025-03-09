from project.task2 import regex_to_dfa, graph_to_nfa
import scipy.sparse as sp
import numpy as np
import functools
import operator
from collections.abc import Iterable
from pyformlang.finite_automaton import Symbol, NondeterministicFiniteAutomaton, State
from networkx import MultiDiGraph
import itertools
from typing import Type


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


def get_matrix_by_sp_format(arg1: any, shape: any, sparse_format: Type[sp.spmatrix]):
    if sparse_format in [sp.dok_matrix, sp.lil_matrix]:
        coo = sp.coo_matrix(arg1, shape, dtype=bool)
        return coo.todok() if sparse_format == sp.dok_matrix else coo.tolil()
    return sparse_format(arg1, shape, dtype=bool)


class AdjacencyMatrixFA:
    def __init__(
        self,
        automation: NondeterministicFiniteAutomaton = None,
        sparse_format: Type[sp.spmatrix] = sp.csc_matrix,
    ):
        self.matricies = {}
        self.sparse_format = sparse_format

        if automation is None:
            self.states = {}
            self.idx_by_state = {}
            self.alphabet = set()
            self.start_states = set()
            self.final_states = set()
            return

        self.states = {st: i for (i, st) in enumerate(automation.states)}
        self.idx_by_state = {i: st for (i, st) in enumerate(automation.states)}
        self.states_count = len(self.states)
        self.alphabet = automation.symbols

        edges = tuple(zip(*get_edges_from_fa(automation)))
        column_states, symbols, row_states = ([], [], []) if not edges else edges
        for s in self.alphabet:
            mask = np.equal(list(symbols), s).astype(int)
            if (
                self.sparse_format == sp.dok_matrix
                or self.sparse_format == sp.lil_matrix
            ):
                coo = sp.coo_matrix(
                    (
                        mask,
                        (
                            [self.states[state] for state in list(row_states)],
                            [self.states[state] for state in list(column_states)],
                        ),
                    ),
                    shape=(self.states_count, self.states_count),
                )
                self.matricies[s] = (
                    coo.todok() if self.sparse_format == sp.dok_matrix else coo.tolil()
                )
            else:
                self.matricies[s] = self.sparse_format(
                    (
                        mask,
                        (
                            [self.states[state] for state in list(column_states)],
                            [self.states[state] for state in list(row_states)],
                        ),
                    ),
                    shape=(self.states_count, self.states_count),
                )
            self.matricies[s] = get_matrix_by_sp_format(
                (
                    mask,
                    (
                        [self.states[state] for state in list(column_states)],
                        [self.states[state] for state in list(row_states)],
                    ),
                ),
                (self.states_count, self.states_count),
                sparse_format,
            )

        self.start_states = {self.states[key] for key in automation.start_states}
        self.final_states = {self.states[key] for key in automation.final_states}

    def accepts(self, word: Iterable[Symbol]) -> bool:
        symbols = list(word)

        configs = [(symbols, st) for st in self.start_states]

        while len(configs) > 0:
            rest, state = configs.pop()

            if len(rest) == 0 and state in self.final_states:
                return True

            for assume_next in self.states.values():
                if self.matricies[rest[0]][state, assume_next]:
                    configs.append((rest[1:], assume_next))

        return False

    def is_empty(self) -> bool:
        tr_clos = self.transitive_closure()

        for st, fn in itertools.product(self.start_states, self.final_states):
            if tr_clos[st, fn]:
                return False

        return True

    def transitive_closure(self):
        n = self.states_count
        matrices = list(self.matricies.values())

        common_matrix = self.sparse_format(
            (np.ones(n, dtype=bool), (range(n), range(n))), shape=(n, n)
        )

        return functools.reduce(operator.add, matrices, common_matrix) ** n

    def update_matricies(self, delta: dict[Symbol, Type[sp.spmatrix]]):
        for var, matrix in delta.items():
            if var in self.matricies:
                self.matricies[var] += matrix
            else:
                self.alphabet.add(var)
                self.matricies[var] = matrix


def intersect_automata(
    automaton1: AdjacencyMatrixFA,
    automaton2: AdjacencyMatrixFA,
    sparse_format: Type[sp.spmatrix] = sp.csc_matrix,
) -> AdjacencyMatrixFA:
    A1, A2 = automaton1.matricies, automaton2.matricies

    intersect = AdjacencyMatrixFA()

    intersect.states_count = automaton1.states_count * automaton2.states_count

    for k in A1.keys():
        if A2.get(k) is None:
            continue
        intersect.matricies[k] = sp.kron(
            A1[k], A2[k], format=sparse_format([[]]).getformat()
        )

    intersect.states = {
        (i1, i2): (
            automaton1.states[i1] * automaton2.states_count + automaton2.states[i2]
        )
        for i1, i2 in itertools.product(
            automaton1.states.keys(), automaton2.states.keys()
        )
    }
    intersect.idx_by_state = {i: st for st, i in intersect.states.items()}

    intersect.start_states = [
        (s1 * automaton2.states_count + s2)
        for s1, s2 in itertools.product(
            automaton1.start_states, automaton2.start_states
        )
    ]
    intersect.final_states = [
        (f1 * automaton2.states_count + f2)
        for f1, f2 in itertools.product(
            automaton1.final_states, automaton2.final_states
        )
    ]

    intersect.alphabet = automaton1.alphabet.union(automaton2.alphabet)

    return intersect


def tensor_based_rpq(
    regex: str,
    graph: MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
    sparse_format: Type[sp.spmatrix] = sp.csc_matrix,
) -> set[tuple[int, int]]:
    adj_matrix_by_reg = AdjacencyMatrixFA(regex_to_dfa(regex), sparse_format)
    adj_matrix_by_graph = AdjacencyMatrixFA(
        graph_to_nfa(graph, start_nodes, final_nodes), sparse_format
    )

    intersect = intersect_automata(
        adj_matrix_by_reg, adj_matrix_by_graph, sparse_format
    )

    tr_cl = intersect.transitive_closure()

    reg_raw_start_states = [
        key
        for key in adj_matrix_by_reg.states
        if adj_matrix_by_reg.states[key] in adj_matrix_by_reg.start_states
    ]
    reg_raw_final_states = [
        key
        for key in adj_matrix_by_reg.states
        if adj_matrix_by_reg.states[key] in adj_matrix_by_reg.final_states
    ]

    return {
        (st, fn)
        for (st, fn) in itertools.product(start_nodes, final_nodes)
        for (st_reg, fn_reg) in itertools.product(
            reg_raw_start_states, reg_raw_final_states
        )
        if tr_cl[intersect.states[(st_reg, st)], intersect.states[(fn_reg, fn)]]
    }
