from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton, EpsilonNFA)
from typing import Set
from pyformlang.regular_expression import Regex

def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    nfa : EpsilonNFA = Regex(regex).to_epsilon_nfa()
    dfa : DeterministicFiniteAutomaton = nfa.to_deterministic()

    return dfa.minimize()

def graph_to_nfa(
  graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    nfa : NondeterministicFiniteAutomaton = NondeterministicFiniteAutomaton.from_networkx(graph).remove_epsilon_transitions()

    nodes : Set[int] = set(graph.nodes)
    start_nodes = start_states if start_states else nodes
    final_nodes = final_states if final_states else nodes

    for x in start_nodes:
        nfa.add_start_state(x)
    for x in final_nodes:
        nfa.add_final_state(x)

    return nfa
