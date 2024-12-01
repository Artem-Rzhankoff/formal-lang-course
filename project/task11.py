from antlr4 import ParserRuleContext, CommonTokenStream, InputStream
from project.GraphLanguageListener import GraphLanguageListener
from project.GraphLanguageLexer import GraphLanguageLexer
from project.GraphLanguageParser import GraphLanguageParser


def _parse(program: str) -> GraphLanguageParser:
    return GraphLanguageParser(CommonTokenStream(GraphLanguageLexer(InputStream(program))) )

# Второе поле показывает корректна ли строка (True, если корректна)
def program_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = _parse(program)
    parser.removeErrorListeners()
    parser.program()

    is_correct = parser.getNumberOfSyntaxErrors() == 0
    tree = parser.program()
    print(tree.toStringTree())
    return (tree, is_correct)



def nodes_count(tree: ParserRuleContext) -> int:
    pass

def tree_to_program(tree: ParserRuleContext) -> str:
    pass

class TreeListener(GraphLanguageListener):

    def __init__(self):
        self.nodes_count = 0
        self.stack = []

    def enterEveryRule(self, ctx):
        self.nodes_count += 1

    def visitTerminal(self, node):
        self.nodes_count += 1