from dataclasses import dataclass
from textwrap import indent
from typing import List, Union, Optional, TypeVar, Generic

from lark import Tree, Token

T = TypeVar("T")


def curly_block(inner: str, indentation_level=1):
    indentation = ' ' * 4 * indentation_level
    last_indentation = ' ' * (indentation_level - 1)
    return "{\n" + indent(inner, indentation) + "\n" + last_indentation + "}"


class TreeWithLanguageUnit(Tree, Generic[T]):
    def __init__(self, tree: Tree, unit: T):
        super().__init__(tree.data, tree.children, tree.meta)
        self.unit = unit


class TokenAndLanguageUnit(Generic[T]):
    def __init__(self, token: Token, unit: T):
        self.unit = unit
        self.token = token

    def __repr__(self):
        return self.token.__repr__()

    def __str__(self):
        return self.token


LanguageUnitContainer = Union[TreeWithLanguageUnit, TokenAndLanguageUnit]


@dataclass
class Type:
    simple_types: List[TokenAndLanguageUnit]

    def __str__(self):
        return ".".join(str(t.unit) for t in self.simple_types)


@dataclass
class PrimaryExpression:
    pass


@dataclass
class SimpleLiteral(PrimaryExpression):
    value: TokenAndLanguageUnit

    def __str__(self):
        return str(self.value.unit)


@dataclass
class FunctionParameter:
    name: TokenAndLanguageUnit
    type: TreeWithLanguageUnit

    def __str__(self):
        return f"{self.name.unit} {self.type.unit}"


class Statement:
    pass


@dataclass
class StatementsBlock:
    statements: List[TreeWithLanguageUnit[Statement]]

    def __str__(self):
        return "\n".join(str(it.unit) for it in self.statements)


@dataclass
class VariableDeclaration:
    var_or_let: TokenAndLanguageUnit
    variable_name: TokenAndLanguageUnit
    type: TreeWithLanguageUnit[Type]

    def __str__(self):
        return " ".join([str(self.var_or_let.unit),
                         str(self.variable_name.unit),
                         str(self.type.unit)])


@dataclass
class PostfixUnarySuffix:
    pass


@dataclass
class PostfixUnaryExpression:
    primary_expression: Union[TreeWithLanguageUnit[PrimaryExpression],
                              TokenAndLanguageUnit]
    suffixes: List[TreeWithLanguageUnit[PostfixUnarySuffix]]

    def __str__(self):
        suffixes = "".join(str(suf.unit) for suf in self.suffixes)
        return str(self.primary_expression.unit) + suffixes


@dataclass
class PrefixUnaryExpression:
    prefix_operator: Optional[TokenAndLanguageUnit]
    postfix_unary_expression: LanguageUnitContainer

    def __str__(self):
        operator = "" if self.prefix_operator is None else self.prefix_operator.unit
        return operator + str(self.postfix_unary_expression.unit)


@dataclass
class MultiplicativeExpression:
    children: List[
        Union[TokenAndLanguageUnit, TreeWithLanguageUnit[PrefixUnaryExpression]]]

    def __str__(self):
        return " ".join((str(el.unit) for el in self.children))


@dataclass
class AdditiveExpression:
    children: List[Union[TokenAndLanguageUnit, LanguageUnitContainer]]

    def __str__(self):
        return " ".join((str(it.unit) for it in self.children))


@dataclass
class Comparison:
    children: List[Union[TreeWithLanguageUnit[AdditiveExpression], TokenAndLanguageUnit]]

    def __str__(self):
        return " ".join(str(it.unit) for it in self.children)


@dataclass
class Equality:
    comparison_and_operators: List[Union[
        LanguageUnitContainer,
        TokenAndLanguageUnit]]

    def __str__(self):
        return " ".join(str(exp.unit) for exp in self.comparison_and_operators)


@dataclass
class Conjunction:
    equalities: List[LanguageUnitContainer]

    def __str__(self):
        return " and ".join(str(eq.unit) for eq in self.equalities)


@dataclass
class Disjunction:
    conjunctions: List[LanguageUnitContainer]

    def __str__(self):
        return " or ".join(str(con.unit) for con in self.conjunctions)


@dataclass
class Expression(Statement, PrimaryExpression):
    disjunction: TreeWithLanguageUnit[Disjunction]

    def __str__(self):
        return str(self.disjunction.unit)


@dataclass
class CollectionLiteral(PrimaryExpression):
    expressions: List[LanguageUnitContainer]

    def __str__(self):
        if len(self.expressions) == 0:
            return "[]"
        else:
            return "[" + ", ".join(str(x.unit) for x in self.expressions) + "]"


@dataclass
class ForStatement(Statement):
    name: TokenAndLanguageUnit
    expression: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        return f"for {self.name.unit} in {self.expression.unit} " \
               + curly_block(str(self.statements_block.unit))


@dataclass
class WhileStatement(Statement):
    expression: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]


@dataclass
class ElseExpression:
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        return 'else ' + curly_block(str(self.statements_block.unit))


@dataclass
class ElseIfExpression:
    condition: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        return f'elif {self.condition.unit}' + curly_block(str(self.statements_block.unit))


@dataclass
class IfExpression(PrimaryExpression):
    condition: TreeWithLanguageUnit[Expression]
    statements_block: TreeWithLanguageUnit[StatementsBlock]
    elif_expressions: List[LanguageUnitContainer]
    optional_else: Optional[TreeWithLanguageUnit[ElseExpression]]

    def __str__(self):
        else_str = "" if self.optional_else is None else str(self.optional_else.unit)
        return "if " + str(self.condition.unit) + " " + curly_block(str(self.statements_block.unit)) + \
               " " + "\n".join(str(it.unit) for it in self.elif_expressions) + else_str


@dataclass
class IndexingSuffix(PostfixUnarySuffix):
    expression: TreeWithLanguageUnit[Expression]

    def __str__(self):
        return "[" + str(self.expression.unit) + "]"


@dataclass
class NavigationSuffix(PostfixUnarySuffix):
    name: TokenAndLanguageUnit

    def __str__(self):
        return "." + self.name.unit


@dataclass
class ReturnStatement:
    expression: Optional[TreeWithLanguageUnit]

    def __str__(self):
        if self.expression is None:
            return "ret"
        else:
            return f"ret {self.expression.unit}"


@dataclass
class FunctionDeclaration:
    name: TokenAndLanguageUnit
    function_parameters: List[TreeWithLanguageUnit[FunctionParameter]]
    return_type: TokenAndLanguageUnit
    statements_block: TreeWithLanguageUnit[StatementsBlock]

    def __str__(self):
        parameters = " ".join(str(x.unit) for x in self.function_parameters)
        parentheses = "()" if parameters == '' else "(" + parameters + ")"
        return self.name.unit + parentheses + " " + self.return_type.unit + " " + curly_block(
            str(self.statements_block.unit))


@dataclass
class Start:
    function_declarations: List[TreeWithLanguageUnit[FunctionDeclaration]]

    def __str__(self):
        return "\n\n".join(str(it.unit) for it in self.function_declarations)


@dataclass
class Assignment(Statement):
    left: LanguageUnitContainer
    operator: TokenAndLanguageUnit
    right: TreeWithLanguageUnit[Expression]

    def __str__(self):
        return f"{str(self.left.unit)} {str(self.operator.unit)} {str(self.right.unit)}"


@dataclass
class FunctionCallArguments(PostfixUnarySuffix):
    expressions: List[LanguageUnitContainer]

    def __str__(self):
        return ", ".join(str(e.unit) for e in self.expressions)


@dataclass
class CallSuffix(PostfixUnarySuffix):
    function_call_arguments: Optional[TreeWithLanguageUnit[FunctionCallArguments]] = None

    def __str__(self):
        if self.function_call_arguments is None:
            return "()"
        return "(" + str(self.function_call_arguments.unit) + ")"


@dataclass
class ParenthesizedExpression(PostfixUnarySuffix):
    child: LanguageUnitContainer

    def __str__(self):
        return "(" + str(self.child.unit) + ")"
