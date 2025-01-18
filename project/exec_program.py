from project.task11 import program_to_tree
from project.interpret.visitor import InterpreterVisitor
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol

def exec_program(program: str) -> dict[str, set[tuple]]:
    tree = program_to_tree(program)

    #visitor = TypeCheckVisitor()
    #context: TypeContext = visitor.visit(tree)

    interpreter_visitor = InterpreterVisitor()
    interpreter_visitor.visitProgram(tree[0])

    nfa : NondeterministicFiniteAutomaton = interpreter_visitor.envs[-1]['g'].nfa
    print(nfa.get_number_transitions())
    print(nfa.states)


if __name__ == "__main__":
    program = """
let g is graph

add vertex 1 to g
add vertex 2 to g
add vertex 3 to g
add vertex 4 to g
add vertex 5 to g
remove vertices [1, 2, 3] from g
    """
    exec_program(program)