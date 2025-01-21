from antlr4 import ParserRuleContext
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG

from project.GraphLanguageParser import GraphLanguageParser
from project.GraphLanguageVisitor import GraphLanguageVisitor
from project.interpret.types import LFiniteAutomata, LTriple, LSet, LAutomata, LCFG
from project.tensor_based_cfpq import cfg_to_rsm, tensor_based_cfpq
from copy import deepcopy

class InterpreterVisitor(GraphLanguageVisitor):
    def __init__(self):
        self.envs = [{}]
        self.processing = set()  # Для отслеживания обрабатываемых переменных (рекурсия)
        self.query_results = {}

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
        if isinstance(value, LCFG):
            value.add_start_symbol(var)
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
                nonterms = var.get_grammar_nonterm_names()
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
            return LFiniteAutomata.from_string(ctx.getText())
        elif ctx.VAR(): # еще нельзя допускать правила вида A -> A, левую рекурсию короче
            var = ctx.getText()
            return LCFG.from_var(var)
        elif ctx.getChild(0).getText() == '(':
            return self.visit(ctx.regexpr(0))
        elif ctx.getChild(1).getText() =='|':
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.union(second)
        elif ctx.getChild(1).getText() == '^':
            expr : LFiniteAutomata | LCFG = self.visit(ctx.regexpr(0))
            range : tuple = self.visit(ctx.range_())
            automata = expr.grammar if isinstance(expr, LCFG) else expr.nfa
            return self._apply_range_to_nfa(automata, range[0], range[1])
        elif ctx.getChild(1).getText() == '.':
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.concat(second)
        else: # &
            first : LAutomata = self.visit(ctx.regexpr(0))
            second : LAutomata = self.visit(ctx.regexpr(1))
            return first.intersect(second)
        
    def visitRange(self, ctx) -> tuple:
        n = int(ctx.NUM(0).getText())
        if ctx.getChild(2).getText() != "..":
            return tuple(n)
        m = int(ctx.NUM(1).getText()) if ctx.NUM(1) else None
        if m is not None and m < n:
            raise Exception()
        
        return n, m
    

    def _apply_range_to_nfa(self, nfa: NondeterministicFiniteAutomaton | CFG, n: int, m: int = None) -> NondeterministicFiniteAutomaton | CFG:
        subautomata : NondeterministicFiniteAutomaton | CFG = deepcopy(nfa)
        acc = deepcopy(nfa)

        for _ in range (0, n-1):
            acc = acc.concatenate(subautomata)
        
        result = CFG() if isinstance(nfa, CFG) else NondeterministicFiniteAutomaton() if n == 0 else acc

        if m is None:
            result = result.concatenate(subautomata.kleene_star())
        else:
            for _ in range(n, m):
                acc = acc.concatenate(subautomata)
                result = result.union(acc)

        print(result)
        # tuple -> LPair
        
        return LCFG(result) if result is CFG else LFiniteAutomata(result)
    
    def visitV_filter(self, ctx) -> tuple[str, LSet]:
        var_name = ctx.VAR().getText()
        values = self.visit(ctx.expr())

        if isinstance(values, tuple):
            values = LSet(list(values[0, values[1]+1]))
        elif isinstance(values, LSet):
            values = values
        elif isinstance(values, int):
            values =  LSet(list(values))
        else:
            raise Exception()
        
        return (var_name, values)

    def visitSelect(self, ctx):
        filters : dict[str, LSet] = {}
        for filter in ctx.v_filter():
            if filter:
                value = self.visitV_filter(filter)
                filters.setdefault(value[0], value[1])

        final_var = ctx.VAR(-3).getText()
        start_var = ctx.VAR(-2).getText()
        graph_name = ctx.VAR(-1).getText()

        def get_idx_by_pos(var_name):
            return 0 if var_name == start_var else 1 # она же всегда в другом случае final?

        f_rv = ctx.VAR(0).getText() 
        return_vars : tuple[str, int] = [(f_rv, get_idx_by_pos(f_rv))]
        if len(ctx.VAR()) > 4:
            s_rv = ctx.VAR(1).getText()
            return_vars.append((s_rv, get_idx_by_pos(s_rv)))


        start_nodes : set[int] | None = None
        final_nodes : set[int] | None = None

        if start_var in filters.keys:
            start_nodes = filters[start_var].items

        if final_var in filters.keys:
            final_nodes = filters[final_var].items

        
        nfa : NondeterministicFiniteAutomaton = self.envs[-1][graph_name] # тут в теории не должно быть стартовых и финальных
        for st in start_nodes:
            nfa.add_start_state(st)
        for fn in final_nodes:
            nfa.add_final_state(fn)

        grammar_expr = self.visit(ctx.expr())
        rsm : RecursiveAutomaton

        if isinstance(grammar_expr, LFiniteAutomata):
            rsm = RecursiveAutomaton.from_regex(grammar_expr.nfa.to_regex()) # еще эту регулярку надо проверить
        elif isinstance(grammar_expr, LCFG):
            rsm = cfg_to_rsm(grammar_expr.grammar)
        

        cfpq_result = tensor_based_cfpq(rsm, nfa, start_nodes, final_nodes)


        if len(return_vars) == 2:
            return cfpq_result
        else:
            idx = return_vars[0][1]
            return set([el[idx] for el in cfpq_result])
