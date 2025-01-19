from abc import ABC, abstractmethod
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
from pyformlang.regular_expression import Regex
from project.grammar.extend_cfg import extend_contex_free_grammar
from project.grammar.rsm import rsm_from_extended_cfg, RecursiveStateMachine
from project.task2 import regex_to_dfa
from project.interpret.utils import intersect_nfa

class LSet:
    def __init__(self, items: set, ttype=None):
        if not items:
            self.type = None
        else:
            self.type = ttype or type(next(iter(items)))
            if not all(isinstance(item, self.type) for item in items):
                raise TypeError("Set elements must have the same type")
        self.items = items
    
    def __eq__(self, value: "LSet") -> bool:
        if self.type != value.type:
            raise TypeError("Sets must have same type")
        
        return self.set == value.set
    
    def __iter__(self):
        return iter(self.items)
    
class LTriple:
    def __init__(self, start, label, final):
        if type(start) != type(final): # есть ощущение, что для ребра нужна строгая проверка
            raise TypeError()
        self.start = start
        self.label = label
        self.final = final
        self.type = type(start)
    
    def __eq__(self, value: "LTriple"):
        if self.type != value.type:
            raise TypeError()
        
        return self.start == value.start and self.label == value.label and self.final == value.final   

class LAutomata:
    @abstractmethod
    def union(self, second: "LAutomata") -> "LAutomata":
        ...
    
    @abstractmethod
    def intersect(self, second: "LAutomata") -> "LAutomata":
        ...

    @abstractmethod
    def concat(self, second: "LAutomata") -> "LAutomata":
        ...

class LCFG(LAutomata, ABC):
    def __init__(self, cfg: CFG):
        self.grammar = cfg
        #extended_cfg = extend_contex_free_grammar(cfg)
        #self.rsm : RecursiveStateMachine = rsm_from_extended_cfg(extended_cfg)
        self.type = LSet({var.value for var in cfg.variables}).type
    
    def __eq__(self, value: "LCFG"):
        return self.grammar == value.grammar and self.type == value.type

    @classmethod
    def from_string(cfg_class, regex: str, starting_symbol = "S") -> "LCFG":
        return cfg_class(Regex(regex).to_cfg(starting_symbol))
    
    def edges(self) -> LSet:
        return LSet(
            {
                LTriple(edge[0], edge[2]["label"], edge[1])
                for subautomata in self.rsm.subautomatons.values()
                for edge in subautomata.e
            }
        )
    
    def nodes(self) -> LSet:
        return LSet(
            {
                state.value
                for subautomata in self.rsm.subautomatons.values()
                for state in subautomata.states
            }
        )
    
    def union(self, second) -> "LCFG":
        if isinstance(second, LCFG):
            return LCFG(self.grammar.union(second.grammar))
        elif isinstance(second, LFiniteAutomata):
            second_regex : Regex = second.nfa.to_regex()
            return LCFG(self.grammar.union(second_regex.to_cfg()))
        else:
            raise TypeError()
        
    def intersect(self, second):
        if isinstance(second, LFiniteAutomata):
            return LCFG(self.grammar.intersection(second.nfa))
        else:
            raise TypeError()
        
    def concat(self, second):
        if isinstance(second, LCFG):
            return LCFG(self.grammar.concatenate(second.grammar))
        elif isinstance(second, LFiniteAutomata):
            second_regex : Regex = second.nfa.to_regex()
            return LCFG(self.grammar.concatenate(second_regex.to_cfg()))
    

class LFiniteAutomata(LAutomata, ABC):
    def __init__(self, nfa: NondeterministicFiniteAutomaton, ttype=None):
        self.nfa = nfa
        self.type = LSet({state.value for state in nfa.states}, ttype).type

    @classmethod
    def from_string(fa_class, regex: str):
        print(f'Регулярка {regex}')
        return fa_class(regex_to_dfa(regex))


    def edges(self) -> LSet:
        return LSet(
            {
                LTriple(state_from, mark, state_to)
                for state_from, items in self.nfa.to_dict().items()
                for mark, set_state_to in items.items()
                for state_to in (
                    set_state_to if isinstance(set_state_to, set) else {set_state_to}
                )
            }
        )

    def nodes(self) -> LSet:
        return LSet({state.value for state in self.nfa.symbols})
    
    def add_edge(self, edge: LTriple):
        start_state = State(edge.start)
        final_state = State(edge.final)
        self._init_state(edge.start)
        self._init_state(edge.final)

        self.nfa.add_transition(start_state, Symbol(edge.label), final_state)
    
    def remove_edge(self, edge: LTriple):
        self.nfa.remove_transition(edge.start, edge.label, edge.final)
        
    def add_vertex(self, vertex): # vertex - тип str ??
        self._init_state(State(vertex))
    
    def remove_vertex(self, vertex):
        self.nfa.states.remove(State(vertex))

    def union(self, second):
        if isinstance(second, LFiniteAutomata):
            return LFiniteAutomata(self.nfa.union(second.nfa))
        return second.union(self)
    
    def intersect(self, second):
        if isinstance(second, LFiniteAutomata):
            return LFiniteAutomata(intersect_nfa(self.nfa, second.nfa))
        return second.intersect(self)
    
    def concat(self, second):
        if isinstance(second, LFiniteAutomata):
            return LFiniteAutomata(self.nfa.concatenate(second.nfa))
        return second.concat(self)

    def _init_state(self, state: State):
        self.nfa.add_start_state(state)
        self.nfa.add_final_state(state)