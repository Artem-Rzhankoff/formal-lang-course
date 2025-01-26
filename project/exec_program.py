from project.task11 import program_to_tree
from project.task2 import regex_to_dfa
from project.interpret.visitor import InterpreterVisitor
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
from pyformlang.regular_expression import Regex
from project.interpret.types import LAutomata, LCFG, LFiniteAutomata
from pyformlang.cfg import CFG, Variable, Production, Epsilon


def merge_grammars(first: CFG, second: CFG) -> CFG:
    start_symbol = Variable("S")
    rules1 = first.productions
    rules2 = second.productions
    foo = (
        set(rules1)
        .union(set(rules2))
        .union({Production(start_symbol, [first.start_symbol])})
        .union({Production(start_symbol, [second.start_symbol])})
    )

    return CFG(productions=foo, start_symbol=start_symbol)


def add_start_symbol(grammar: CFG, start_symbol: str):
    extra_production = Production(Variable(start_symbol), [grammar.start_symbol])
    productions = set(grammar.productions) | {extra_production}

    return CFG(start_symbol=start_symbol, productions=productions)


def exec_program(program: str) -> dict[str, set[tuple]]:
    tree = program_to_tree(program)

    # visitor = TypeCheckVisitor()
    # context: TypeContext = visitor.visit(tree)

    interpreter_visitor = InterpreterVisitor()
    interpreter_visitor.visitProgram(tree[0])

    automata: LAutomata = interpreter_visitor.envs[-1]["r33"]
    foo: CFG = interpreter_visitor.envs[-1]["s30"].grammar
    print("exec")
    print(foo.to_text())
    if isinstance(automata, LCFG):
        print("rsm")
        print(automata.grammar.to_text())
        print(automata.grammar.contains(['"a"', '"a"', '"a"']))
    elif isinstance(automata, LFiniteAutomata):
        print("nfa")
        print(automata.nfa.accepts(['"a"']))
    else:
        print(f"Кринж {automata}")


if __name__ == "__main__":
    program = """
let g10 is graph
add edge (0, "c", 11) to g10
add edge (0, "g", 13) to g10
add edge (0, "c", 16) to g10
add edge (0, "e", 17) to g10
add edge (0, "g", 19) to g10
add edge (1, "f", 0) to g10
add edge (1, "d", 13) to g10
add edge (1, "b", 15) to g10
add edge (1, "h", 18) to g10
add edge (2, "c", 0) to g10
add edge (2, "h", 3) to g10
add edge (2, "f", 5) to g10
add edge (2, "f", 12) to g10
add edge (2, "c", 17) to g10
add edge (2, "f", 19) to g10
add edge (3, "g", 0) to g10
add edge (3, "g", 1) to g10
add edge (3, "e", 4) to g10
add edge (3, "c", 5) to g10
add edge (3, "b", 6) to g10
add edge (3, "a", 9) to g10
add edge (3, "h", 12) to g10
add edge (3, "a", 14) to g10
add edge (3, "b", 15) to g10
add edge (3, "b", 18) to g10
add edge (4, "a", 3) to g10
add edge (4, "e", 6) to g10
add edge (4, "g", 7) to g10
add edge (4, "a", 10) to g10
add edge (4, "c", 12) to g10
add edge (4, "h", 13) to g10
add edge (4, "f", 17) to g10
add edge (5, "d", 1) to g10
add edge (5, "h", 7) to g10
add edge (5, "e", 9) to g10
add edge (5, "e", 14) to g10
add edge (5, "h", 16) to g10
add edge (5, "e", 18) to g10
add edge (6, "g", 0) to g10
add edge (6, "b", 3) to g10
add edge (6, "e", 5) to g10
add edge (6, "e", 8) to g10
add edge (6, "f", 10) to g10
add edge (6, "d", 13) to g10
add edge (6, "h", 14) to g10
add edge (6, "a", 15) to g10
add edge (6, "a", 18) to g10
add edge (6, "e", 19) to g10
add edge (7, "h", 3) to g10
add edge (7, "f", 4) to g10
add edge (7, "e", 6) to g10
add edge (7, "c", 8) to g10
add edge (7, "f", 14) to g10
add edge (7, "h", 15) to g10
add edge (7, "g", 17) to g10
add edge (7, "h", 18) to g10
add edge (8, "b", 1) to g10
add edge (8, "e", 2) to g10
add edge (8, "f", 3) to g10
add edge (8, "c", 6) to g10
add edge (8, "g", 7) to g10
add edge (8, "g", 9) to g10
add edge (8, "c", 15) to g10
add edge (8, "e", 16) to g10
add edge (8, "d", 17) to g10
add edge (8, "a", 19) to g10
add edge (9, "c", 1) to g10
add edge (9, "g", 11) to g10
add edge (9, "b", 12) to g10
add edge (9, "e", 13) to g10
add edge (9, "a", 14) to g10
add edge (9, "h", 15) to g10
add edge (9, "b", 16) to g10
add edge (9, "c", 19) to g10
add edge (10, "a", 1) to g10
add edge (10, "a", 8) to g10
add edge (10, "h", 13) to g10
add edge (10, "c", 14) to g10
add edge (10, "f", 15) to g10
add edge (10, "e", 16) to g10
add edge (10, "b", 17) to g10
add edge (10, "h", 18) to g10
add edge (10, "a", 19) to g10
add edge (11, "a", 0) to g10
add edge (11, "b", 2) to g10
add edge (11, "g", 7) to g10
add edge (11, "e", 8) to g10
add edge (11, "d", 9) to g10
add edge (11, "b", 10) to g10
add edge (11, "a", 13) to g10
add edge (11, "d", 18) to g10
add edge (12, "d", 1) to g10
add edge (12, "h", 6) to g10
add edge (12, "b", 8) to g10
add edge (12, "b", 9) to g10
add edge (12, "d", 10) to g10
add edge (12, "b", 11) to g10
add edge (12, "b", 15) to g10
add edge (12, "h", 16) to g10
add edge (12, "b", 19) to g10
add edge (13, "a", 3) to g10
add edge (13, "c", 5) to g10
add edge (13, "g", 7) to g10
add edge (13, "e", 8) to g10
add edge (13, "c", 14) to g10
add edge (13, "h", 15) to g10
add edge (14, "e", 1) to g10
add edge (14, "c", 7) to g10
add edge (14, "c", 9) to g10
add edge (14, "e", 10) to g10
add edge (14, "d", 13) to g10
add edge (14, "c", 16) to g10
add edge (14, "f", 19) to g10
add edge (15, "a", 0) to g10
add edge (15, "h", 1) to g10
add edge (15, "d", 2) to g10
add edge (15, "h", 5) to g10
add edge (15, "a", 6) to g10
add edge (15, "b", 11) to g10
add edge (15, "b", 14) to g10
add edge (15, "c", 18) to g10
add edge (16, "g", 3) to g10
add edge (16, "b", 4) to g10
add edge (16, "e", 5) to g10
add edge (16, "f", 6) to g10
add edge (16, "a", 7) to g10
add edge (16, "f", 8) to g10
add edge (16, "d", 13) to g10
add edge (16, "c", 14) to g10
add edge (16, "a", 18) to g10
add edge (16, "f", 19) to g10
add edge (17, "g", 3) to g10
add edge (17, "g", 7) to g10
add edge (17, "e", 8) to g10
add edge (17, "h", 12) to g10
add edge (17, "c", 16) to g10
add edge (18, "c", 2) to g10
add edge (18, "d", 3) to g10
add edge (18, "g", 4) to g10
add edge (18, "c", 8) to g10
add edge (18, "h", 10) to g10
add edge (18, "f", 13) to g10
add edge (18, "c", 16) to g10
add edge (18, "e", 19) to g10
add edge (19, "d", 2) to g10
add edge (19, "d", 3) to g10
add edge (19, "h", 5) to g10
add edge (19, "e", 7) to g10
add edge (19, "d", 11) to g10
add edge (19, "a", 12) to g10
add edge (19, "c", 13) to g10
add edge (19, "d", 17) to g10
add edge (19, "a", 18) to g10

let s211 = "a"^[0 .. 0] | "b" . s211
let s12 = s113 . s211
let s113 = "a"^[0 .. 0] | "a" . s113

let r14 = for v in [0, 1, 2, 3, 5, 6, 7, 10, 11, 12, 14, 17, 18, 19] for u in [0, 1, 3, 7, 10, 11, 12, 13, 14, 18, 19] return u, v where u reachable from v in g10 by s12
    """
    exec_program(program)

# (6, 12) (12, 7) (3, 7) (12, 13) (19, 0)