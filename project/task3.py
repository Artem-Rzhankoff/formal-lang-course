from project.task2 import NondeterministicFiniteAutomaton, regex_to_dfa, graph_to_nfa
import scipy.sparse as sp
from collections.abc import Iterable
from pyformlang.finite_automaton import Symbol
from functools import reduce
from networkx import MultiDiGraph

class AdjacencyMatrixFA:
    def __init__(self, automation : NondeterministicFiniteAutomaton = None) -> None:
        self.matricies = {}

        if automation is None:
            self.states = set()
            self.alphabet = set()
            self.start_states = set()
            self.final_states = set()

        self.states = automation.states
        self.states_count = len(self.states)
        self.alphabet = automation.symbols

        graph = automation.to_networkx()

        for s in self.alphabet:
            self.matricies[s] = sp.csr_matrix((self.states_count, self.states_count), dtype=bool)

        for u, v, edge_labels in graph.edges(data=True):
            for _, value in edge_labels.items():
                self.matricies[value][u, v] = True
        
        self.start_states = automation.start_states
        self.final_states = automation.final_states

    def accepts(self, word: Iterable[Symbol]) -> bool:
        symbols = list(word)

        for start in self.start_states:
            if self._accepts_helper(symbols, start):
                return True
        
        return False
    
    def is_empty(self) -> bool:
        tr_clos = self.transitive_closure()

        for st, fn in self.start_states, self.final_states:
            if tr_clos[st, fn]:
                return False
            
        return True


    def transitive_closure(self):
        # алгоритм уоршалла
        reach = reduce(lambda x, y: x | y, self.matricies)
        
        for k in range(self.states_count):
            for i in range(self.states_count):
                for j in range(self.states_count):
                    reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

        return reach

    def _accepts_helper(self, word: list[Symbol], state: int) -> bool:
        if (word.count == 0):
            return True

        symbol = word[0]

        for assume_next in self.states:
            if self.matricies[symbol][state, assume_next]:
                if self._accepts_helper(word[1:], assume_next):
                    return True
        
        return False
    

def intersect_automata(automaton1: AdjacencyMatrixFA,
        automaton2: AdjacencyMatrixFA) -> AdjacencyMatrixFA:
    A1, A2 = automaton1.matricies, automaton2.matricies

    intersect = AdjacencyMatrixFA()

    intersect.states_count = automaton1.states_count * automaton2.states_count
    intersect.matricies = [sp.kron(M1, M2, format='csr') for M1, M2 in zip(A1, A2)]
    intersect.states = [(i1 * automaton2 + i2) for i1 in automaton1.states for i2 in automaton2.states]
    intersect.start_states = [(s1 * automaton2.states_count + s2) for s1 in automaton1.start_states for s2 in automaton2.start_states]
    intersect.final_states = [(f1 * automaton2.states_count + f2) for f1 in automaton1.final_states for f2 in automaton2.final_states]
    intersect.alphabet = automaton1.alphabet.union(automaton2.alphabet)

def tensor_based_rpq(regex: str, graph: MultiDiGraph, start_nodes: set[int],
      final_nodes: set[int]) -> set[tuple[int, int]]:
    
    adj_matrix_by_reg = AdjacencyMatrixFA(regex_to_dfa(regex))
    adj_matrix_by_graph = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))

    intersect = intersect_automata(adj_matrix_by_reg, adj_matrix_by_graph)

    tr_cl = intersect.transitive_closure()

    return {(st, fn) for st in start_nodes for fn in final_nodes if tr_cl[st, fn]}

