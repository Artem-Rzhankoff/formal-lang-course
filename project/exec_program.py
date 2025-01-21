from project.task11 import program_to_tree
from project.task2 import regex_to_dfa
from project.interpret.visitor import InterpreterVisitor
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
from pyformlang.regular_expression import Regex
from project.interpret.types import LAutomata, LCFG, LFiniteAutomata
from pyformlang.cfg import CFG, Variable, Production, Epsilon

def merge_grammars(first: CFG, second: CFG) -> CFG:
    start_symbol = Variable('S')
    rules1 = first.productions
    rules2 = second.productions
    foo = set(rules1).union(set(rules2)).union({Production(start_symbol, [first.start_symbol])}).union({Production(start_symbol, [second.start_symbol])})

    return CFG(productions=foo, start_symbol=start_symbol)

def add_start_symbol(grammar: CFG, start_symbol: str):
    extra_production = Production(Variable(start_symbol), [grammar.start_symbol])
    productions = set(grammar.productions) | {extra_production}

    return CFG(start_symbol=start_symbol, productions=productions)


def exec_program(program: str) -> dict[str, set[tuple]]:
    tree = program_to_tree(program)

    #visitor = TypeCheckVisitor()
    #context: TypeContext = visitor.visit(tree)

    interpreter_visitor = InterpreterVisitor()
    interpreter_visitor.visitProgram(tree[0])


    automata : LAutomata = interpreter_visitor.envs[-1]['q']
    if isinstance(automata, LCFG):
        print('rsm')
        print(automata.grammar.to_normal_form().to_text())
        print(automata.grammar.contains(['"a"', '"a"', '"a"']))
    elif isinstance(automata, LFiniteAutomata):
        print('nfa')
        print(automata.nfa.accepts(['"a"']))
    else:
        print(f'Кринж {automata}')

if __name__ == "__main__":
    program = """
let q = "a" ^ [2 .. 5] 
    """
    exec_program(program)
# let q = ("a".q."b") | "c"