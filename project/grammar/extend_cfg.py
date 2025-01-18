from pathlib import Path
from dataclasses import dataclass, field
from typing import Set, Dict
from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

# вопрос в том, для чего это нужно вообще

@dataclass(frozen=True)
class ExtendedCFG:
    nonterminals: Set[Variable]
    terminals: Set[str]
    starting_symbol: Variable
    productions: Dict[Variable, Regex]

def extend_contex_free_grammar(contex_free_grammar: CFG = None) -> ExtendedCFG:
    if contex_free_grammar.start_symbol is not None:
        starting_symbol = contex_free_grammar.start_symbol
    else:
        starting_symbol = Variable("S")
    
    nonterminals = set(contex_free_grammar.variables)
    nonterminals.add(starting_symbol)
    
    productions: Dict[Variable, Regex] = {}
    for production in contex_free_grammar.productions:
        subautomata = Regex(
            " ".join(symbol.value for symbol in production.body)
            if len(production.body) > 0
            else "$"
        )
        productions[production.head] = (
            productions[production.head].union(subautomata) # интересно что такое union для двух регулярок
            if production.head in productions
            else subautomata
        )
    
    return ExtendedCFG(
        nonterminals=nonterminals,
        terminals=set(contex_free_grammar.terminals),
        starting_symbol=starting_symbol,
        productions=productions,
    )