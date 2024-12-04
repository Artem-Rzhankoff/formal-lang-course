from antlr4 import ParserRuleContext, CommonTokenStream, InputStream, ParseTreeWalker
from project.GraphLanguageListener import GraphLanguageListener
from project.GraphLanguageLexer import GraphLanguageLexer
from project.GraphLanguageParser import GraphLanguageParser


def _parse(program: str) -> GraphLanguageParser:
    return GraphLanguageParser(
        CommonTokenStream(GraphLanguageLexer(InputStream(program)))
    )


# Второе поле показывает корректна ли строка (True, если корректна)
def program_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = _parse(program)
    parser.removeErrorListeners()

    tree = parser.program()
    is_correct = parser.getNumberOfSyntaxErrors() == 0
    return (tree, is_correct)


def nodes_count(tree: ParserRuleContext) -> int:
    listener = TreeNodesCountListener()
    walker = ParseTreeWalker()

    walker.walk(listener, tree)

    return listener.nodes_count


def tree_to_program(tree: ParserRuleContext) -> str:
    listener = TreeToProgramListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    return listener.getProgram()


class TreeNodesCountListener(GraphLanguageListener):
    def __init__(self):
        self.nodes_count = 0

    def enterEveryRule(self, ctx):
        self.nodes_count += 1


class TreeToProgramListener(GraphLanguageListener):
    def __init__(self):
        self.tokens = []

    def visitTerminal(self, node):
        self.tokens.append(node.getText())

    def getProgram(self):
        return " ".join(self.tokens)
