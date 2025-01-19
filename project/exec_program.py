from project.task11 import program_to_tree
from project.task2 import regex_to_dfa
from project.interpret.visitor import InterpreterVisitor
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
from pyformlang.regular_expression import Regex
from project.interpret.types import LAutomata, LCFG, LFiniteAutomata

def exec_program(program: str) -> dict[str, set[tuple]]:
    tree = program_to_tree(program)

    #visitor = TypeCheckVisitor()
    #context: TypeContext = visitor.visit(tree)

    interpreter_visitor = InterpreterVisitor()
    interpreter_visitor.visitProgram(tree[0])

    automata : LAutomata = interpreter_visitor.envs[-1]['q']
    if isinstance(automata, LCFG):
        print('rsm')
        print(automata.grammar.start_symbol)
        print(automata.grammar.get_closure().to_text())
        print(automata.grammar.contains("acb"))
    elif isinstance(automata, LFiniteAutomata):
        print('nfa')
        print(automata.nfa.accepts("bc"))
    else:
        print(f'Кринж {automata}')


if __name__ == "__main__":
    program = """
let g is graph

add vertex 1 to g
add vertex 2 to g
add vertex 3 to g
add vertex 4 to g
add vertex 5 to g
remove vertices [1, 2, 3] from g

let q = ("a".q."b") | "c"
    """
    exec_program(program)