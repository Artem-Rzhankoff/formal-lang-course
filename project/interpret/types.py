from abc import ABC, abstractmethod
from pyformlang.cfg import CFG, Production, Variable, Terminal, Epsilon
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
            raise TypeError("Sets must have same type")

        return self.set == value.set

    def __iter__(self):
        return iter(self.items)


class LTriple:
    def __init__(self, start, label, final):
        if type(start) != type(
            final
        ):  # есть ощущение, что для ребра нужна строгая проверка
            raise TypeError()
        self.start = start
        self.label = label
        self.final = final
        self.type = type(start)

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
    var_prefix = "VAR#"

    def __init__(self, cfg: CFG, vars: list[str] = []):
        self._grammar = cfg
        self.type = LSet({Variable(var.value) for var in cfg.variables}).type
        self.vars = vars

    @property
    def grammar(self) -> CFG:
        productions = [
            prod
            for prod in self._grammar.productions
            if not (str(prod.head.value) in self.vars and len(prod.body) == 0)
        ]
        return CFG(start_symbol=self._grammar.start_symbol, productions=productions)

    def __eq__(self, value: "LCFG"):
        return self.grammar == value.grammar and self.type == value.type

    @classmethod
    def from_string(cfg_class, regex: str, starting_symbol="S") -> "LCFG":
        return cfg_class(Regex(regex).to_cfg(starting_symbol))

    @classmethod
    def from_var(cfg_class, var_name: str) -> "LCFG":
        start_symbol = Variable(f"{cfg_class.var_prefix}{var_name}")
        return cfg_class(CFG(start_symbol=start_symbol, productions=[]), [start_symbol])

    def add_start_symbol(self, start_symbol: str):
        productions = [
            (
                Production(Variable(start_symbol), p.body)
                if p.head == self._grammar.start_symbol
                else p
            )
            for p in self._grammar.productions
        ]
        self._grammar = CFG(
            start_symbol=Variable(start_symbol), productions=productions
        )

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
            return LCFG(self.grammar.concatenate(second_regex.to_cfg()), self.vars)

    def get_grammar_nonterm_names(self) -> list[str]:
        print(self.grammar.variables)
        return [
            str(var).removeprefix(self.var_prefix).split("#")[0]
            for var in self.grammar.variables
            if str(var).startswith(self.var_prefix)
        ]

    def merge_grammars(self, grammars: list[CFG]) -> "LCFG":
        acc = self.grammar
        for grammar in grammars:
            acc_prepared: CFG = LCFG.get_grammar_with_renamed_nonterms(
                acc, str(grammar.start_symbol)
            )
            grammar_prepared: CFG = LCFG.get_grammar_with_renamed_nonterms(
                grammar, str(acc.start_symbol)
            )
            rules1 = acc_prepared.productions
            rules2 = grammar_prepared.productions
            merged = set(rules1).union(set(rules2))

            acc = CFG(productions=merged, start_symbol=acc.start_symbol)
        
        print('эщкере')
        print(acc.to_text())
        print('\n\n')
        return LCFG(acc)

    @classmethod
    def get_grammar_with_renamed_nonterms(cls, grammar: CFG, var_name: str) -> "LCFG":
        productions = grammar.productions

        def prepare(production: Production) -> Production:
            body = []
            for symbol in production.body:
                if symbol in grammar.variables:
                    body.append(
                        Variable(cls._get_var_name_from_nonterm(str(symbol.value)))
                    )
                else:
                    body.append(symbol)

            head_str = str(production.head)
            head = (
                Variable(cls._get_var_name_from_nonterm(head_str))
                if head_str.startswith(f"{cls.var_prefix}")
                else production.head
            )
            return Production(head, body)

        return CFG(
            start_symbol=grammar.start_symbol,
            productions=[prepare(prod) for prod in productions],
        )

    @classmethod
    def _get_var_name_from_nonterm(cls, nonterm: str) -> str:
        if nonterm.startswith(f"{cls.var_prefix}"):
            payload = nonterm[len(cls.var_prefix) :]
            r = payload.find("#")
            var_name = payload[:r]
            return var_name
        else:
            return nonterm


class LFiniteAutomata(LAutomata, ABC):
    def __init__(self, nfa: NondeterministicFiniteAutomaton, ttype=None):
        self.nfa = nfa
        self.type = LSet({state.value for state in nfa.states}, ttype).type

    @classmethod
    def from_string(fa_class, regex: str):
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
            self.nfa.to_regex().to_cfg().concatenate(second.grammar), second.vars
        )

    def _init_state(self, state: State):
        self.nfa.add_start_state(state)
        self.nfa.add_final_state(state)
