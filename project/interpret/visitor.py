from antlr4 import ParserRuleContext
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.GraphLanguageParser import GraphLanguageParser
from project.GraphLanguageVisitor import GraphLanguageVisitor
from project.interpret.types import LFiniteAutomata, LTriple, LSet

class InterpreterVisitor(GraphLanguageVisitor):
    def __init__(self):
        self.envs = [{}]

    def set_var(self, var_name: str, value):
        self.envs[-1][var_name] = value
    
    def visitProgram(self, ctx):
        return self.visitChildren(ctx)
    
    def visitDeclare(self, ctx):
        var = ctx.VAR().getText()
        value = NondeterministicFiniteAutomaton()
        self.set_var(var, LFiniteAutomata(value))
    
    def visitBind(self, ctx):
        var = ctx.VAR().getText()
        value = self.visit(ctx.expr())
        self.set_var(var, value) # как определять тип переменной ??

    def visitAdd(self, ctx):
        adding_type = ctx.children[1].getText()
        item_to_add = self.visit(ctx.expr())
        var_name = ctx.VAR().getText()
        var = self.envs[-1][var_name]

        if not isinstance(var, LFiniteAutomata):
            raise TypeError('Граф тоже не верно указан')
        
        if adding_type == 'vertex':
            var.add_vertex(item_to_add)
        else:
            var.add_edge(item_to_add)
    
    def visitRemove(self, ctx):
        remove_type = ctx.children[1].getText()
        item_to_remove = self.visit(ctx.expr())
        var_name = ctx.VAR().getText()
        var = self.envs[-1][var_name] # должен быть графом

        if not isinstance(var, LFiniteAutomata):
            raise TypeError('Граф не верно указан')

        if remove_type == 'vertex':
            var.remove_vertex(item_to_remove)
        elif remove_type == 'edge':
            var.remove_edge(item_to_remove)
        else:
            print(item_to_remove)
            for vertex in item_to_remove:
                var.remove_vertex(vertex)

    def visitExpr(self, ctx):
        if ctx.NUM():
            return int(ctx.getText())
        elif ctx.CHAR():
            return ctx.getText()
        elif ctx.VAR():
            return self.envs[-1][ctx.getText()]
        elif ctx.edge_expr():
            return self.visitEdge_expr(ctx.edge_expr())
        elif ctx.set_expr():
            return self.visitSet_expr(ctx.set_expr())
        elif ctx.regexpr():
            return
        else:
            return

    
    def visitRegexpr(self, ctx):
        return LFiniteAutomata.from_string(ctx.regexpr().getText()[2:-1])
    
    def visitSet_expr(self, ctx):
        expr_nodes = ctx.expr()
        return LSet(set(self.visit(expr) for expr in expr_nodes))
    
    def visitEdge_expr(self, ctx):
        print()
        return LTriple(
            self.visit(ctx.expr(0)),
            self.visit(ctx.expr(1)),
            self.visit(ctx.expr(2))
        )

    