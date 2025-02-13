from project.GraphLanguageVisitor import GraphLanguageVisitor
from project.type_checker.types import TypeEnviroment, Type


class TypeCheckerVisitor(GraphLanguageVisitor):
    UNION_OPERATOR = "|"
    CONCAT_OPERATOR = "."
    INTERSECT_OPERATOR = "&"
    RANGE_OPERATOR = "^"

    def __init__(self):
        self.env = TypeEnviroment()

    def visitProgram(self, ctx):
        self.visitChildren(ctx)

    def visitDeclare(self, ctx):
        var_name = ctx.VAR().getText()
        self.env.add(var_name, Type.GRAPH)
        return Type.VOID

    def visitBind(self, ctx):
        var_name = ctx.VAR().getText()
        type: Type = self.visitExpr(ctx.expr())
        self.env.add(var_name, type)
        return Type.VOID

    def visitAdd(self, ctx):
        graph_name = ctx.VAR().getText()
        type = self.env.get(graph_name)
        self._check_types_consistency(
            type,
            Type.GRAPH,
            f"Variable '{graph_name}' must be of type GRAPH to add elements.",
        )

        item_type = self.visitExpr(ctx.expr())
        adding_type = ctx.children[1].getText()

        expected_item_type = Type.NUM if adding_type == "vertex" else Type.EDGE
        self._check_types_consistency(
            item_type,
            expected_item_type,
            f"Cannot add {item_type} as a {adding_type}. Expected {expected_item_type}.",
        )

        return Type.VOID

    def visitRemove(self, ctx):
        graph_name = ctx.VAR().getText()
        type = self.env.get(graph_name)
        self._check_types_consistency(
            type,
            Type.GRAPH,
            f"Variable '{graph_name}' must be of type GRAPH to remove elements.",
        )

        item_type = self.visitExpr(ctx.expr())
        remove_type = ctx.children[1].getText()
        expected_item_type = (
            Type.NUM
            if remove_type == "vertex"
            else Type.EDGE
            if remove_type == "edge"
            else Type.SET
            if remove_type == "vertices"
            else None
        )
        if expected_item_type is not None:
            self._check_types_consistency(
                item_type,
                expected_item_type,
                f"Cannot remove {item_type} as a {remove_type}. Expected {expected_item_type}.",
            )

        return Type.VOID

    def visitExpr(self, ctx):
        if ctx.NUM():
            return Type.NUM
        elif ctx.CHAR():
            return Type.CHAR
        elif ctx.VAR():
            var_name = ctx.getText()
            return self.env.get(var_name)
        elif ctx.edge_expr():
            return self.visitEdge_expr(ctx.edge_expr())
        elif ctx.set_expr():
            return self.visitSet_expr(ctx.set_expr())
        elif ctx.regexpr():
            return self.visitRegexpr(ctx.regexpr())
        elif ctx.select():
            return self.visitSelect(ctx.select())
        else:
            raise ValueError("Unsupported expression type.")

    def visitEdge_expr(self, ctx):
        types = [self.visitExpr(expr) for expr in ctx.expr()]
        expected_types = [Type.NUM, Type.CHAR, Type.NUM]

        for i in range(len(types)):
            try:
                self._check_types_consistency(
                    types[i],
                    expected_types[i],
                    f"Edge expression part {i + 1} must be of type {expected_types[i]}, but got {types[i]}.",
                )
            except ValueError:
                raise ValueError(
                    "Invalid edge expression. Expected types: NUM, CHAR, NUM."
                )

        return Type.EDGE

    def visitSet_expr(self, ctx):
        # Our language excludes any other types
        for expr in ctx.expr():
            if self.visitExpr(expr) != Type.NUM:
                raise ValueError("Set expressions can only contain NUM types.")

        return Type.SET

    def visitRegexpr(self, ctx):
        if ctx.CHAR():
            return Type.CHAR
        elif ctx.VAR():
            var_name = ctx.VAR().getText()
            if var_name not in self.env:
                return Type.CFG

            type = self.env.get(var_name)
            if type == Type.CFG:
                return type
            elif type == Type.FA or type == Type.CHAR:
                return Type.FA

            raise ValueError(
                f"Variable '{var_name}' must be of type CFG, FA, or CHAR in regular expressions."
            )
        elif ctx.getChild(0).getText() == "(":
            return self.visitRegexpr(ctx.regexpr(0))
        elif ctx.getChild(1).getText() == self.RANGE_OPERATOR:
            expr_type = self.visitRegexpr(ctx.regexpr(0))
            range_type = self.visitRange(ctx.range_())

            self._check_types_consistency_multi(
                expr_type,
                [Type.FA, Type.CFG, Type.CHAR],
                f"Range operator requires FA, CFG, or CHAR, but got {expr_type}.",
            )
            self._check_types_consistency(
                range_type,
                Type.RANGE,
                f"Range operator must be applied to a RANGE type, but got {range_type}.",
            )
            return expr_type
        elif ctx.getChild(1).getText() in [self.CONCAT_OPERATOR, self.UNION_OPERATOR]:
            first_type = self.visitRegexpr(ctx.regexpr(0))
            second_type = self.visitRegexpr(ctx.regexpr(1))
            self._check_types_consistency_multi(
                first_type,
                [Type.FA, Type.CFG, Type.CHAR],
                f"First operand must be FA, CFG, or CHAR, but got {first_type}.",
            )
            self._check_types_consistency_multi(
                second_type,
                [Type.FA, Type.CFG, Type.CHAR],
                f"Second operand must be FA, CFG, or CHAR, but got {second_type}.",
            )
            return Type.CFG if Type.CFG in [first_type, second_type] else Type.FA
        else:
            first_type = self.visitRegexpr(ctx.regexpr(0))
            second_type = self.visitRegexpr(ctx.regexpr(1))
            self._check_types_consistency_multi(
                first_type,
                [Type.FA, Type.CFG, Type.CHAR],
                f"First operand must be FA or CFG, but got {first_type}.",
            )
            self._check_types_consistency_multi(
                second_type,
                [Type.FA, Type.CFG, Type.CHAR],
                f"Second operand must be FA or CFG, but got {second_type}.",
            )
            if first_type == Type.CFG and second_type == Type.CFG:
                raise ValueError("Cannot perform operation on two CFG types.")
            return Type.CFG if Type.CFG in [first_type, second_type] else Type.FA

    def visitRange(self, ctx):
        return Type.RANGE

    def visitV_filter(self, ctx):
        type = self.visitExpr(ctx.expr())
        self._check_types_consistency(
            type, Type.SET, f"Filter expression must be of type SET, but got {type}."
        )

        return Type.VOID

    def visitSelect(self, ctx):
        for filter in ctx.v_filter():
            if filter:
                self.visitV_filter(filter)

        diff = 1 if len(ctx.VAR()) > 4 else 0

        graph_name = ctx.VAR(3 + diff).getText()

        self._check_types_consistency(
            self.env.get(graph_name),
            Type.GRAPH,
            f"Variable '{graph_name}' must be of type GRAPH for selection.",
        )

        result_var2 = ctx.VAR(1).getText() if len(ctx.VAR()) > 4 else None

        grammar_type = self.visitExpr(ctx.expr())
        self._check_types_consistency_multi(
            grammar_type,
            [Type.CHAR, Type.FA, Type.CFG],
            f"Grammar expression must be CHAR, FA, or CFG, but got {grammar_type}.",
        )

        return Type.SET if result_var2 is None else Type.SET_TUPLES

    def _check_types_consistency(
        self, actual: Type, expected: Type, error_message: str = None
    ):
        if actual != expected:
            raise ValueError(
                error_message
                or f"Type mismatch. Expected {expected}, but got {actual}."
            )

    def _check_types_consistency_multi(
        self, actual: Type, expected: list[Type], error_message: str = None
    ):
        if not any(actual == exp for exp in expected):
            raise ValueError(
                error_message
                or f"Type mismatch. Expected one of {expected}, but got {actual}."
            )
