from dataclasses import dataclass
from textwrap import indent
from typing import List, Union, Optional, TypeVar, Generic, Any

from lark import Tree, Token

T = TypeVar("T")
Name = Token


def curly_block(inner: str, indentation_level=1):
    indentation = ' ' * 4 * indentation_level
    last_indentation = ' ' * (indentation_level - 1)
    return "{\n" + indent(inner, indentation) + "\n" + last_indentation + "}"


class TreeWithUnit(Tree, Generic[T]):
    def __init__(self, tree: Tree, unit: T, identifier=-1):
        super().__init__(tree.data, tree.children, tree.meta)
        self.unit = unit
        self.identifier = identifier


@dataclass
class SimpleLiteral:
    value: Any
    origin: Token

    def __repr__(self):
        return self.origin.__repr__()

    def __str__(self):
        return self.origin


AnyNode = Union[Name, SimpleLiteral, TreeWithUnit]


@dataclass
class Type:
    simple_types: List[Token]

    def __str__(self):
        return ".".join(t for t in self.simple_types)


@dataclass
class PrimaryExpression:
    pass


@dataclass
class FunctionParameter:
    name: Token
    type: TreeWithUnit[Type]

    def __str__(self):
        return f"{self.name} {self.type.unit}"


class Statement:
    pass


@dataclass
class StatementsBlock:
    statements: List[TreeWithUnit[Statement]]

    def __str__(self):
        return "\n".join(custom_str(it) for it in self.statements)


@dataclass
class VariableDeclaration:
    var_or_let: Token
    variable_name: Token
    type: TreeWithUnit[Type]

    def __str__(self):
        return " ".join([str(self.var_or_let),
                         str(self.variable_name),
                         str(self.type.unit)])


@dataclass
class PostfixUnarySuffix:
    pass


def custom_str(node: Union[AnyNode, Token]):
    if isinstance(node, TreeWithUnit):
        return str(node.unit)
    elif isinstance(node, SimpleLiteral):
        return node.origin
    return str(node)


@dataclass
class PostfixUnaryExpression:
    primary_expression: Union[TreeWithUnit, Name]
    suffixes: List[TreeWithUnit[PostfixUnarySuffix]]

    def __str__(self):
        suffixes = "".join(str(suf.unit) for suf in self.suffixes)
        return custom_str(self.primary_expression) + suffixes


@dataclass
class PrefixUnaryExpression:
    prefix_operator: Optional[Token]
    postfix_unary_expression: AnyNode

    def __str__(self):
        operator = "" if self.prefix_operator is None else self.prefix_operator
        return operator + custom_str(self.postfix_unary_expression)


@dataclass
class MultiplicativeExpression:
    children: List[AnyNode]

    def __str__(self):
        return " ".join((custom_str(el) for el in self.children))


@dataclass
class AdditiveExpression:
    children: List[AnyNode]

    def __str__(self):
        return " ".join((custom_str(it) for it in self.children))


@dataclass
class Comparison:
    children: List[AnyNode]

    def __str__(self):
        return " ".join(custom_str(it.unit) for it in self.children)


@dataclass
class Equality:
    comparison_and_operators: List[Union[AnyNode, Token]]

    def __str__(self):
        return " ".join(custom_str(exp) for exp in self.comparison_and_operators)


@dataclass
class Conjunction:
    equalities: List[AnyNode]

    def __str__(self):
        return " and ".join(custom_str(eq) for eq in self.equalities)


@dataclass
class Disjunction:
    conjunctions: List[AnyNode]

    def __str__(self):
        return " or ".join(custom_str(con) for con in self.conjunctions)


@dataclass
class Expression(Statement, PrimaryExpression):
    disjunction: AnyNode

    def __str__(self):
        return custom_str(self.disjunction)


@dataclass
class CollectionLiteral(PrimaryExpression):
    expressions: List[AnyNode]

    def __str__(self):
        if len(self.expressions) == 0:
            return "[]"
        else:
            return "[" + ", ".join(custom_str(x) for x in self.expressions) + "]"


@dataclass
class ForStatement(Statement):
    name: Token
    expression: AnyNode
    statements_block: TreeWithUnit[StatementsBlock]

    def __str__(self):
        return f"for {self.name} in {custom_str(self.expression)} " \
               + curly_block(custom_str(self.statements_block))


@dataclass
class WhileStatement(Statement):
    expression: AnyNode
    statements_block: TreeWithUnit[StatementsBlock]


@dataclass
class ElseExpression:
    statements_block: TreeWithUnit[StatementsBlock]

    def __str__(self):
        return 'else ' + curly_block(custom_str(self.statements_block))


@dataclass
class ElseIfExpression:
    condition: AnyNode
    statements_block: TreeWithUnit[StatementsBlock]

    def __str__(self):
        return f'elif {self.condition.unit}' + curly_block(custom_str(self.statements_block))


@dataclass
class IfExpression(PrimaryExpression):
    condition: AnyNode
    statements_block: TreeWithUnit[StatementsBlock]
    elif_expressions: List[TreeWithUnit[ElseIfExpression]]
    optional_else: Optional[TreeWithUnit[ElseExpression]]

    def __str__(self):
        else_str = "" if self.optional_else is None else custom_str(self.optional_else)
        return "if " + custom_str(self.condition) + " " + curly_block(custom_str(self.statements_block)) + \
               " " + "\n".join(custom_str(it) for it in self.elif_expressions) + else_str


@dataclass
class IndexingSuffix(PostfixUnarySuffix):
    expression: AnyNode

    def __str__(self):
        return "[" + custom_str(self.expression) + "]"


@dataclass
class NavigationSuffix(PostfixUnarySuffix):
    name: Token

    def __str__(self):
        return "." + self.name


@dataclass
class ReturnStatement:
    expression: Optional[AnyNode]

    def __str__(self):
        if self.expression is None:
            return "ret"
        else:
            return f"ret {custom_str(self.expression)}"


@dataclass
class FunctionDeclaration:
    name: Token
    function_parameters: List[TreeWithUnit[FunctionParameter]]
    return_type: Token
    statements_block: TreeWithUnit[StatementsBlock]

    def __str__(self):
        parameters = " ".join(custom_str(x) for x in self.function_parameters)
        parentheses = "()" if parameters == '' else "(" + parameters + ")"
        return self.name + parentheses + " " + self.return_type + " " + curly_block(
            custom_str(custom_str(self.statements_block)))


@dataclass
class Start:
    function_declarations: List[TreeWithUnit[FunctionDeclaration]]

    def __str__(self):
        return "\n\n".join(custom_str(it) for it in self.function_declarations)


@dataclass
class Assignment(Statement):
    left: AnyNode
    operator: Token
    right: AnyNode

    def __str__(self):
        return f"{custom_str(self.left)} {str(self.operator)} {custom_str(self.right)}"


@dataclass
class CallSuffix(PostfixUnarySuffix):
    function_call_arguments: List[AnyNode]

    def __str__(self):
        if len(self.function_call_arguments) == 0:
            return "()"
        return "(" + ", ".join(custom_str(e) for e in self.function_call_arguments) + ")"


@dataclass
class ParenthesizedExpression(PostfixUnarySuffix):
    child: AnyNode

    def __str__(self):
        return f"({custom_str(self.child)})"
