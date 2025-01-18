from dataclasses import dataclass
from typing import Dict
from pathlib import Path
from project.grammar.extend_cfg import ExtendedCFG
from pyformlang.finite_automaton import EpsilonNFA

@dataclass(frozen=True)
class RecursiveStateMachine:
    starting_symbol: str
    subautomatons: Dict[str, EpsilonNFA]

def rsm_from_extended_cfg(
    extended_contex_free_grammar: ExtendedCFG
) -> RecursiveStateMachine:    
    return RecursiveStateMachine(
        starting_symbol=extended_contex_free_grammar.starting_symbol,
        subautomatons={
            nonterminal: subautomata.to_epsilon_nfa()
            for nonterminal, subautomata in extended_contex_free_grammar.productions.items()
        },
    )