from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from project.task3 import intersect_automata, AdjacencyMatrixFA

def intersect_nfa(first: NondeterministicFiniteAutomaton, second: NondeterministicFiniteAutomaton) -> NondeterministicFiniteAutomaton:
    intersect = intersect_automata(AdjacencyMatrixFA(first), AdjacencyMatrixFA(second))
    return intersect.automation