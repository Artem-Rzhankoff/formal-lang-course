from antlr4 import ParserRuleContext, CommonTokenStream, InputStream, ParseTreeWalker, TerminalNode
from project.GraphLanguageListener import GraphLanguageListener
from project.GraphLanguageLexer import GraphLanguageLexer
from project.GraphLanguageParser import GraphLanguageParser


def _parse(program: str) -> GraphLanguageParser:
    return GraphLanguageParser(CommonTokenStream(GraphLanguageLexer(InputStream(program))))

# Второе поле показывает корректна ли строка (True, если корректна)
def program_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = _parse(program)
    parser.removeErrorListeners()

    tree = parser.program()
    is_correct = parser.getNumberOfSyntaxErrors() == 0
    return (tree, is_correct)

def nodes_count(tree: ParserRuleContext) -> int:
    listener = TreeListener()
    walker = ParseTreeWalker()

    walker.walk(listener, tree)

    return listener.nodes_count

def tree_to_program(tree: ParserRuleContext) -> str:
    if isinstance(tree, TerminalNode):
        return tree.getText()
    result = []
    for child in tree.children:
        child_text = tree_to_program(child)
        result.append(' ')
        result.append(child_text)
    
    return ''.join(result)

class TreeListener(GraphLanguageListener):
    def __init__(self):
        self.nodes_count = 0

    def enterEveryRule(self, ctx):
        self.nodes_count += 1