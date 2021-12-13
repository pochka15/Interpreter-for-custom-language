from dataclasses import dataclass
from typing import List, Union, Optional, TypeVar, Generic

from lark import Tree, Token

T = TypeVar("T")


class TreeWithLanguageUnit(Tree, Generic[T]):
    def __init__(self, tree: Tree, unit: T):
        super().__init__(tree.data, tree.children, tree.meta)
        self.unit = unit


class TokenWithLanguageUnit(Token, Generic[T]):
    unit: T

    def __repr__(self):
        return str(self.unit)


@dataclass
class Type:
    simple_types: List[TokenWithLanguageUnit[str]]

    def __str__(self):
        return ".".join(str(t.unit) for t in self.simple_types)


@dataclass
class PrimaryExpression:
    pass


@dataclass
class SimpleLiteral(PrimaryExpression):
    value: Union[TokenWithLanguageUnit[str],
                 TokenWithLanguageUnit[bool],
                 TokenWithLanguageUnit[int],
                 TokenWithLanguageUnit[float]]

    def __str__(self):
        return str(self.value)


@dataclass
class FunctionParameter:
    name: str
    type: TokenWithLanguageUnit[Type]

    def __str__(self):
        return f"{self.name} {str(self.type.unit)}"


class Statement:
    pass


@dataclass
class StatementsBlock:
    statements: List[TreeWithLanguageUnit[Statement]]

    def __str__(self):
        return "\n".join(str(it.unit) for it in self.statements)


@dataclass
class BreakStatement:
    def __init__(self):
        self.value = "break"

    def __str__(self):
        return self.value


@dataclass
class VariableDeclaration:
    variable_name: TokenWithLanguageUnit[str]
    type: TreeWithLanguageUnit[Type]
    var_or_const: TokenWithLanguageUnit[str]

    def __repr__(self):
        return " ".join([str(self.var_or_const.unit), str(self.variable_name.unit), str(self.type.unit)])


@dataclass
class PostfixUnarySuffix:
    pass


@dataclass
class PostfixUnaryExpression:
    primary_expression: Union[TreeWithLanguageUnit[PrimaryExpression],
                              TokenWithLanguageUnit[PrimaryExpression]]
    suffixes: List[TreeWithLanguageUnit[PostfixUnarySuffix]]

    def __str__(self):
        return "".join(
            (str(self.primary_expression), *(str(suf.unit) for suf in self.suffixes)))


@dataclass
class PrefixUnaryExpression:
    prefix_operators: List[TokenWithLanguageUnit[str]]
    postfix_unary_expression: TreeWithLanguageUnit[PostfixUnaryExpression]

    def __str__(self):
        return "".join(op.unit for op in self.prefix_operators) + \
               str(self.postfix_unary_expression.unit)


@dataclass
class MultiplicativeExpression:
    prefix_unary_expression: TreeWithLanguageUnit[PrefixUnaryExpression]
    multiplicative_operators_and_prefix_unary_expressions: List[
        Union[TokenWithLanguageUnit[str], TreeWithLanguageUnit[PrefixUnaryExpression]]]

    def __str__(self):
        return " ".join([str(self.prefix_unary_expression.unit),
                         *(str(el.unit) for el in self.multiplicative_operators_and_prefix_unary_expressions)])


@dataclass
class AdditiveExpression:
    multiplicative_expression: TreeWithLanguageUnit[MultiplicativeExpression]
    right_part: List[
        Union[TokenWithLanguageUnit[str], TreeWithLanguageUnit[MultiplicativeExpression]]]

    def __str__(self):
        left = str(self.multiplicative_expression.unit)
        right = " ".join((str(exp.unit) for exp in self.right_part))
        return left + " " + right


@dataclass
class Comparison:
    additive_expressions_and_operators: List[Union[
        TreeWithLanguageUnit[AdditiveExpression],
        TreeWithLanguageUnit[TokenWithLanguageUnit[str]]]]

    def __str__(self):
        return " ".join(str(exp.unit) for exp in self.additive_expressions_and_operators)


@dataclass
class Equality:
    comparison_and_operators: List[Union[
        TreeWithLanguageUnit[Comparison],
        TokenWithLanguageUnit[str]]]

    def __str__(self):
        return " ".join(str(exp.unit) for exp in self.comparison_and_operators)


@dataclass
class Conjunction:
    equalities: List[TreeWithLanguageUnit[Equality]]

    def __str__(self):
        return " and ".join(str(eq.unit) for eq in self.equalities)


@dataclass
class Disjunction:
    conjunctions: List[TreeWithLanguageUnit[Conjunction]]

    def __str__(self):
        return " or ".join(str(con.unit) for con in self.conjunctions)


@dataclass
class Expression(Statement, PrimaryExpression):
    disjunction: TreeWithLanguageUnit[Disjunction]

    def __str__(self):
        return str(self.disjunction.unit)


@dataclass
class CollectionLiteral(PrimaryExpression):
    expressions: List[TreeWithLanguageUnit[Expression]]

    def __str__(self):
        if len(self.expressions) == 0:
            return "[]"
        else:
            return "[" + ", ".join(str(x.unit) for x in self.expressions) + "]"


@dataclass
class ForStatement(Statement):
    expression: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]


@dataclass
class WhileStatement(Statement):
    expression: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]


@dataclass
class ElifExpression:
    condition: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        return "elif " + str(self.condition.unit) + str(self.statements_block.unit)


@dataclass
class ElseExpression:
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        return str(self.statements_block.unit)


@dataclass
class IfExpression(PrimaryExpression):
    condition: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]
    elif_expressions: List[TreeWithLanguageUnit[ElifExpression]]
    optional_else: Optional[TreeWithLanguageUnit[ElseExpression]]

    def __str__(self):
        else_str = "" if self.optional_else == None else str(self.optional_else.unit)
        return "if " + str(self.condition.unit) \
               + " {\n" + str(self.statements_block.unit) \
               + "\n}\n" + "\n".join(str(it.unit) for it in self.elif_expressions) + else_str


@dataclass
class IndexingSuffix(PostfixUnarySuffix):
    expression: TreeWithLanguageUnit[Expression]

    def __str__(self):
        "[" + str(self.expression.unit) + "]"


@dataclass
class CallSuffix(PostfixUnarySuffix):
    expressions: List[TreeWithLanguageUnit[Expression]]

    def __str__(self):
        inner = ", ".join(str(e.unit) for e in self.expressions)
        return "(" + inner + ")"


@dataclass
class NavigationSuffix(PostfixUnarySuffix):
    name: TokenWithLanguageUnit[str]

    def __str__(self):
        return "." + self.name.unit


@dataclass
class DirectlyAssignableExpression:
    expression: Union[TreeWithLanguageUnit[VariableDeclaration],
                      TreeWithLanguageUnit[PostfixUnaryExpression]]
    assignable_suffix: Optional[Union[
        TreeWithLanguageUnit[IndexingSuffix],
        TreeWithLanguageUnit[NavigationSuffix]]]

    def __str__(self):
        return f"{self.expression.unit}{self.assignable_suffix.unit}"


@dataclass
class ReturnExpression:
    expression: TreeWithLanguageUnit[Expression]

    def __str__(self):
        return "ret " + str(self.expression.unit)


@dataclass
class FunctionDeclaration:
    name: TokenWithLanguageUnit[str]
    function_parameters: List[TreeWithLanguageUnit[FunctionParameter]]
    return_type: TokenWithLanguageUnit[str]
    statements_block: TreeWithLanguageUnit[StatementsBlock]


def __str__(self):
    return str(self.name.unit) + \
           "(" + ", ".join(str(it.unit) for it in self.function_parameters) + ")" + \
           str(self.return_type.unit) + \
           " {\n" + str(self.statements_block.unit) + "\n}"


@dataclass
class Start:
    function_declarations: List[TreeWithLanguageUnit[FunctionDeclaration]]

    def __str__(self):
        return "\n".join(str(it.unit) for it in self.function_declarations)


@dataclass
class Assignment(Statement):
    left: Union[TreeWithLanguageUnit[DirectlyAssignableExpression],
                TreeWithLanguageUnit[PrefixUnaryExpression]]
    operator: TokenWithLanguageUnit[str]
    right: TreeWithLanguageUnit[Expression]

    def __str__(self):
        return f"{str(self.left.unit)} {str(self.operator.unit)} {str(self.right.unit)}"


@dataclass
class JumpStatement(Statement):
    value: Union[TreeWithLanguageUnit[ReturnExpression], TokenWithLanguageUnit[str]]

    def __str__(self):
        return str(self.value.unit)
