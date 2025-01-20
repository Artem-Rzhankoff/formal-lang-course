from project.task11 import program_to_tree
from project.task2 import regex_to_dfa
from project.interpret.visitor import InterpreterVisitor
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
from pyformlang.regular_expression import Regex
from project.interpret.types import LAutomata, LCFG, LFiniteAutomata
from pyformlang.cfg import CFG, Variable, Production

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

    # cfg = CFG.from_text("""A -> a B | c
    #                     S -> A """, start_symbol=Variable("S"))
    # print(cfg.contains('c'))
    # cfg1 = CFG.from_text("""B -> A b
    #                      S -> B""", start_symbol=Variable("S"))
    # print(cfg1.variables)
    # cfg2 = merge_grammars(cfg, cfg1)
    # print(cfg2.contains('c'))
    # print(cfg2.contains(['a', 'c', 'b']))
    # print(cfg2.productions)

    automata : LAutomata = interpreter_visitor.envs[-1]['q']
    if isinstance(automata, LCFG):
        print('rsm')
        print(automata.grammar.start_symbol)
        #print(automata.grammar.get_closure().to_text())
        print(automata.grammar.contains("acb"))
    elif isinstance(automata, LFiniteAutomata):
        print('nfa')
        print(automata.nfa.accepts("bc"))
    else:
        print(f'Кринж {automata}')

    cfg : CFG = Regex("a").to_cfg()
    cfg1 : CFG = CFG(start_symbol="B")
    cfg2 = cfg.concatenate(cfg1).union(Regex("c").to_cfg())
    cfg2 = add_start_symbol(cfg2, "A")
    #print(cfg2.productions, cfg2.start_symbol)

    cfg3 : CFG = Regex("b").to_cfg()
    cfg4 : CFG = CFG(start_symbol="A")
    cfg5 = cfg3.concatenate(cfg4)
    cfg5 = add_start_symbol(cfg5, "B")

    result = merge_grammars(cfg2, cfg5)
    print(result.is_empty())
    print(result.variables)
    print(result.productions)
    print(result.contains("acb"))

if __name__ == "__main__":
    program = """
let a = "a" . b
let b = a . "b"
let c = b
    """
    exec_program(program)
# let q = ("a".q."b") | "c"