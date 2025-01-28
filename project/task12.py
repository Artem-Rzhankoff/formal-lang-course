from project.task11 import program_to_tree
from project.interpret.visitor import InterpreterVisitor


def typing_program(program: str) -> bool:
    return True


def exec_program(program: str) -> dict[str, set[tuple]]:
    tree = program_to_tree(program)

    interpreter_visitor = InterpreterVisitor()
    interpreter_visitor.visitProgram(tree[0])

    vars = interpreter_visitor.envs[-1]
    return {
        name: value
        for name, value in vars.items()
        if isinstance(value, set) and all(isinstance(item, tuple) for item in value)
    }
