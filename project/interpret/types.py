from abc import ABC, abstractmethod
from pyformlang.cfg import CFG, Production, Variable
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
from pyformlang.regular_expression import Regex
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
            raise TypeError("All items in both sets must be of the same type")

        return self.set == value.set

    def __iter__(self):
        return iter(self.items)


class LTriple:
    def __init__(self, start, label, final):
        if type(start) != type(final):
            raise TypeError("Start and final must be of the same type")
        self.start = start
        self.label = label
        self.final = final

    def __eq__(self, value: "LTriple"):
        if self.type != value.type:
            raise TypeError()

        return (
            self.start == value.start
            and self.label == value.label
            and self.final == value.final
        )


class LAutomata:
    @abstractmethod
    def union(self, second: "LAutomata") -> "LAutomata": ...

    @abstractmethod
    def intersect(self, second: "LAutomata") -> "LAutomata": ...

    @abstractmethod
    def concat(self, second: "LAutomata") -> "LAutomata": ...


class LCFG(LAutomata, ABC):
    VAR_PREFIX = "VAR#"

    def __init__(self, cfg: CFG, from_var = False):
        self._grammar = cfg
        self.from_var = from_var

    @property
    def grammar(self) -> CFG:
        def is_eps_prod_from_st(production: Production):
            return production.head == self._grammar.start_symbol and len(production.body) == 0
        productions = [
            prod
            for prod in self._grammar.productions
            if not (self.from_var and is_eps_prod_from_st(prod))
        ]
        return CFG(start_symbol=self._grammar.start_symbol, productions=productions)

    def __eq__(self, value: "LCFG"):
        return self.grammar == value.grammar and self.type == value.type

    @classmethod
    def from_var(cfg_class, var_name: str) -> "LCFG":
        start_symbol = Variable(f"{cfg_class.VAR_PREFIX}{var_name}")
        return cfg_class(CFG(start_symbol=start_symbol, productions=[]), True)

    def union(self, second) -> "LCFG":
        if isinstance(second, LCFG):
            return LCFG(self.grammar.union(second.grammar))
        elif isinstance(second, LFiniteAutomata):
            second_regex: Regex = second.nfa.to_regex()
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
            second_regex: Regex = second.nfa.to_regex()
            return LCFG(self.grammar.concatenate(second_regex.to_cfg()))
        
    def add_start_symbol(self, start_symbol: str):
        start_var = Variable(start_symbol)
        start_production = Production(start_var, [self._grammar.start_symbol])
        self._grammar = CFG(
            start_symbol=Variable(start_symbol), productions=list(self._grammar.productions) + [start_production]
        )

    def merge_grammars(self, grammars: list[CFG]) -> "LCFG":
        acc = LCFG._get_grammar_with_renamed_nonterms(self.grammar)
        for grammar in grammars:
            grammar_prepared: CFG = LCFG._get_grammar_with_renamed_nonterms(grammar)
            rules1 = acc.productions
            rules2 = grammar_prepared.productions
            merged = set(rules1).union(set(rules2))

            acc = CFG(productions=merged, start_symbol=acc.start_symbol)
        return LCFG(acc)

    @classmethod
    def _get_grammar_with_renamed_nonterms(cls, grammar: CFG) -> CFG:
        productions = grammar.productions
        start_symbol_str = str(grammar.start_symbol.value)
        def prepare(production: Production) -> Production:
            body = []
            for symbol in production.body:
                if symbol in grammar.variables:
                    body.append(
                        Variable(cls._get_var_name_from_nonterm(start_symbol_str, str(symbol.value)))
                    )
                else:
                    body.append(symbol)

            head_str = str(production.head)
            head = (
                Variable(cls._get_var_name_from_nonterm(head_str))
                if head_str.startswith(f"{cls.VAR_PREFIX}")
                else Variable(f"{start_symbol_str}#{head_str}")
                if head_str != start_symbol_str
                else Variable(head_str)
            )
            return Production(head, body)

        return CFG(
            start_symbol=grammar.start_symbol,
            productions=[prepare(prod) for prod in productions],
        )

    @classmethod
    def _get_var_name_from_nonterm(cls, st_var: str, nonterm: str) -> str:
        if nonterm.startswith(f"{cls.VAR_PREFIX}"):
            payload = nonterm[len(cls.VAR_PREFIX) :]
            r = payload.find("#")
            var_name = payload[:r]
            return var_name
        elif nonterm == st_var:
            return nonterm
        else:
            return f"{st_var}#{nonterm}"


class LFiniteAutomata(LAutomata, ABC):
    def __init__(self, nfa: NondeterministicFiniteAutomaton, ttype=None):
        self.nfa = nfa

    @classmethod
    def from_string(fa_class, regex: str):
        return fa_class(regex_to_dfa(regex))
    
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

        return LCFG(
            self.nfa.to_regex().to_cfg().concatenate(second.grammar)
        )

    def edges(self) -> LSet:
        edges = set()
        for (s_from, symbol), s_to_set in self.nfa.to_dict().items():
            for s_to in s_to_set:
                edges.add(LTriple(s_from.value, symbol.value, s_to.value))
        return LSet(edges)

    def nodes(self) -> LSet:
        return LSet({state.value for state in self.nfa.symbols})

    def add_edge(self, edge: LTriple):
        NondeterministicFiniteAutomaton.from_networkx
        start_state = State(edge.start)
        final_state = State(edge.final)
        self._init_state(edge.start)
        self._init_state(edge.final)
        self.nfa.add_transition(start_state, Symbol(edge.label), final_state)

    def remove_edge(self, edge: LTriple):
        self.nfa.remove_transition(edge.start, edge.label, edge.final)

    def add_vertex(self, vertex):
        self._init_state(State(vertex))

    def remove_vertex(self, vertex):
        self.nfa.states.remove(State(vertex))

    def _init_state(self, state: State):
        self.nfa.add_start_state(state)
        self.nfa.add_final_state(state)