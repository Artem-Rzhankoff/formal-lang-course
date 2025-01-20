from antlr4 import ParserRuleContext
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG

from project.GraphLanguageParser import GraphLanguageParser
from project.GraphLanguageVisitor import GraphLanguageVisitor
from project.interpret.types import LFiniteAutomata, LTriple, LSet, LAutomata, LCFG

class InterpreterVisitor(GraphLanguageVisitor):
    def __init__(self):
        self.envs = [{}]
        self.processing = set()  # Для отслеживания обрабатываемых переменных (рекурсия)
        self.pending = {}

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
        self.set_var(var, value)

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
            return ctx.getText().strip('"')
        elif ctx.VAR():
            env = self.envs[-1]
            var = env[ctx.getText()]
            if isinstance(var, LCFG):
                nonterms = LCFG.get_grammar_nonterm_names()
                grammars : list[CFG] = [env[nonterm].grammar for nonterm in nonterms]
                return var.merge_grammars(grammars)
            return var
        elif ctx.edge_expr():
            return self.visitEdge_expr(ctx.edge_expr())
        elif ctx.set_expr():
            return self.visitSet_expr(ctx.set_expr())
        elif ctx.regexpr():
            return self.visitRegexpr(ctx.regexpr())
        else:
            return
    
    def visitEdge_expr(self, ctx):
        RecursiveAutomaton.from_regex()
        return LTriple(
            self.visit(ctx.expr(0)),
            self.visit(ctx.expr(1)),
            self.visit(ctx.expr(2))
        )
    
    def visitSet_expr(self, ctx):
        expr_nodes = ctx.expr()
        return LSet(set(self.visit(expr) for expr in expr_nodes))
    
    def visitRegexpr(self, ctx):
        if ctx.CHAR():
            return LFiniteAutomata.from_string(ctx.getText().strip('"'))
        elif ctx.VAR(): # еще нельзя допускать правила вида A -> A, левую рекурсию короче
            var = ctx.getText()
            if var in self.envs[-1]:
                return self.envs[1][var]
            return LCFG.from_var(var)
        elif ctx.getChild(0).getText() == '(':
            return self.visit(ctx.regexpr(0))
        elif ctx.getChild(1).getText() =='|':
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.union(second)
        elif ctx.getChild(1).getText() == '^':
            expr = self.visit(ctx.regexpr(0))
            range = self.visit(ctx.regexpr(1))
            return  
        elif ctx.getChild(1).getText() == '.':
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.concat(second)
        else: # &
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.intersect(second)

    