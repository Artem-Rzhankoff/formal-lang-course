# Generated from GraphLanguage.g4 by ANTLR 4.13.2
from antlr4 import *

if "." in __name__:
    from .GraphLanguageParser import GraphLanguageParser
else:
    from GraphLanguageParser import GraphLanguageParser


# This class defines a complete listener for a parse tree produced by GraphLanguageParser.
class GraphLanguageListener(ParseTreeListener):
    # Enter a parse tree produced by GraphLanguageParser#program.
    def enterProgram(self, ctx: GraphLanguageParser.ProgramContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#program.
    def exitProgram(self, ctx: GraphLanguageParser.ProgramContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#stmt.
    def enterStmt(self, ctx: GraphLanguageParser.StmtContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#stmt.
    def exitStmt(self, ctx: GraphLanguageParser.StmtContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#declare.
    def enterDeclare(self, ctx: GraphLanguageParser.DeclareContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#declare.
    def exitDeclare(self, ctx: GraphLanguageParser.DeclareContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#bind.
    def enterBind(self, ctx: GraphLanguageParser.BindContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#bind.
    def exitBind(self, ctx: GraphLanguageParser.BindContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#remove.
    def enterRemove(self, ctx: GraphLanguageParser.RemoveContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#remove.
    def exitRemove(self, ctx: GraphLanguageParser.RemoveContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#add.
    def enterAdd(self, ctx: GraphLanguageParser.AddContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#add.
    def exitAdd(self, ctx: GraphLanguageParser.AddContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#expr.
    def enterExpr(self, ctx: GraphLanguageParser.ExprContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#expr.
    def exitExpr(self, ctx: GraphLanguageParser.ExprContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#set_expr.
    def enterSet_expr(self, ctx: GraphLanguageParser.Set_exprContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#set_expr.
    def exitSet_expr(self, ctx: GraphLanguageParser.Set_exprContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#edge_expr.
    def enterEdge_expr(self, ctx: GraphLanguageParser.Edge_exprContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#edge_expr.
    def exitEdge_expr(self, ctx: GraphLanguageParser.Edge_exprContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#regexpr.
    def enterRegexpr(self, ctx: GraphLanguageParser.RegexprContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#regexpr.
    def exitRegexpr(self, ctx: GraphLanguageParser.RegexprContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#range.
    def enterRange(self, ctx: GraphLanguageParser.RangeContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#range.
    def exitRange(self, ctx: GraphLanguageParser.RangeContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#select.
    def enterSelect(self, ctx: GraphLanguageParser.SelectContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#select.
    def exitSelect(self, ctx: GraphLanguageParser.SelectContext):
        pass

    # Enter a parse tree produced by GraphLanguageParser#v_filter.
    def enterV_filter(self, ctx: GraphLanguageParser.V_filterContext):
        pass

    # Exit a parse tree produced by GraphLanguageParser#v_filter.
    def exitV_filter(self, ctx: GraphLanguageParser.V_filterContext):
        pass


del GraphLanguageParser
