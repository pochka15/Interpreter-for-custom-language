from abc import abstractmethod, ABC
from dataclasses import dataclass
from textwrap import indent
from typing import List, Union, Optional, TypeVar, Generic, Any

from lark import Tree, Token


class UnitType:
    pass


class UnknownIterableItemType(UnitType):
    def __str__(self) -> str:
        return "Unknown"


class SimpleType(UnitType):
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value


@dataclass
class IterableType(UnitType):
    item_type: UnitType

    def __init__(self, item_type: UnitType) -> None:
        self.item_type = item_type

    def __str__(self) -> str:
        return f'[{self.item_type}]'


@dataclass
class FunctionType(UnitType):
    param_types: List[UnitType]
    return_type: UnitType

    def __init__(self, param_types: List[UnitType], return_type: UnitType) -> None:
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self) -> str:
        params = ", ".join(str(x) for x in self.param_types)
        return f'({params}) -> {self.return_type}'


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


class Resolvable(ABC):
    """
    Abstract class for nodes which type cannot be resolved instantly
    """

    @abstractmethod
    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        """
        Resolve the type of the node by calling the given delegate function on child nodes.
        It's primarily used by the semantic analyzer when we want to resolve type of some node.
        E.x. semantic analyzer can provide with resolve_func which resolves type using the stored items in closure
        :param resolve_type_func: (AnyNode) -> UnitType. function which is used to resolve node's type.
        :return: UnitType or None
        """
        ...


class ResolvableByStatementsBlock(ABC):
    """
    Abstract class for nodes which are resolved
    """

    @abstractmethod
    def resolve_type(self, get_return_type_func) -> Optional[UnitType]:
        """
        Resolve the type of the node using the given function that returns type which is bound to the statements block.
        During the semantic analysis type is bound to the statements block when there exists a return statement
        :param get_return_type_func: function that takes an id of the statements block and the type of the returned expression
        :return: the type of the return expression in the statements block (None by default)
        """
        ...


class Typed(ABC):
    """
    Abstract class for nodes which type can be resolved instantly
    """

    @property
    @abstractmethod
    def type(self) -> Optional[UnitType]:
        ...


@dataclass
class SimpleLiteral(Typed):
    value: Any
    origin: Token

    def __repr__(self):
        return self.origin.__repr__()

    def __str__(self):
        return self.origin

    @property
    def type(self) -> Optional[UnitType]:
        return SimpleType(type(self.value).__name__)


AnyNode = Union[Name, SimpleLiteral, TreeWithUnit]


@dataclass
class Type:
    simple_types: List[Token]

    def __str__(self):
        return str(self.as_unit_type)

    @property
    def as_unit_type(self) -> Optional[UnitType]:
        if len(self.simple_types) > 1:
            raise Exception("Compound type is not supported: " + ".".join(t for t in self.simple_types))
        type_ = self.simple_types[0]
        # Type can be e.x. IntList or BoolList. We convert it to the IterableType[int], IterableType[bool]
        if type_.endswith("List"):
            item_type = type_[:-len("List")]
            if item_type == '':
                return IterableType(UnknownIterableItemType())

            # lower first letter
            item_type = item_type[:1].lower() + item_type[1:]
            return IterableType(SimpleType(item_type))
        return SimpleType(type_)


@dataclass
class PrimaryExpression:
    pass


@dataclass
class FunctionParameter(Typed):
    name: Token
    type_node: TreeWithUnit[Type]

    def __str__(self):
        return f"{self.name} {self.type_node.unit}"

    @property
    def type(self) -> Optional[UnitType]:
        return self.type_node.unit.as_unit_type


class Statement:
    pass


@dataclass
class StatementsBlock:
    statements: List[TreeWithUnit[Statement]]

    def __str__(self):
        return "\n".join(custom_str(it) for it in self.statements)


@dataclass
class VariableDeclaration(Typed):
    var_or_let: Token
    variable_name: Token
    type_node: TreeWithUnit[Type]

    def __str__(self):
        return " ".join([str(self.var_or_let),
                         str(self.variable_name),
                         str(self.type_node.unit)])

    @property
    def type(self) -> Optional[UnitType]:
        return self.type_node.unit.as_unit_type


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
class PostfixUnaryExpression(Resolvable):
    primary_expression: AnyNode
    suffixes: List[TreeWithUnit[PostfixUnarySuffix]]

    def __str__(self):
        suffixes = "".join(str(suf.unit) for suf in self.suffixes)
        return custom_str(self.primary_expression) + suffixes

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        for suffix in self.suffixes:
            if isinstance(suffix.unit, CallSuffix):
                type_ = resolve_type_func(self.primary_expression)
                assert isinstance(type_, FunctionType), "Type is: " + str(type_)
                return type_.return_type
            if isinstance(suffix.unit, IndexingSuffix):
                type_ = resolve_type_func(self.primary_expression)
                assert isinstance(type_, IterableType)
                return type_.item_type
            if isinstance(suffix.unit, NavigationSuffix):
                raise NotImplemented("Cannot resolve type. Navigation suffix is not implemented")


@dataclass
class PrefixUnaryExpression(Resolvable):
    prefix_operator: Optional[Token]
    postfix_unary_expression: AnyNode

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        return resolve_type_func(self.postfix_unary_expression)

    def __str__(self):
        operator = "" if self.prefix_operator is None else self.prefix_operator
        return operator + custom_str(self.postfix_unary_expression)


@dataclass
class MultiplicativeExpression(Resolvable):
    children: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.children[0])

    def __str__(self):
        return " ".join((custom_str(el) for el in self.children))


@dataclass
class AdditiveExpression(Resolvable):
    children: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.children[0])

    def __str__(self):
        return " ".join((custom_str(it) for it in self.children))


@dataclass
class Comparison(Resolvable):
    children: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.children[0])

    def __str__(self):
        return " ".join(custom_str(it.unit) for it in self.children)


@dataclass
class Equality(Resolvable):
    comparison_and_operators: List[Union[AnyNode, Token]]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.comparison_and_operators[0])

    def __str__(self):
        return " ".join(custom_str(exp) for exp in self.comparison_and_operators)


@dataclass
class Conjunction(Resolvable):
    equalities: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.equalities[0])

    def __str__(self):
        return " and ".join(custom_str(eq) for eq in self.equalities)


@dataclass
class Disjunction(Resolvable):
    conjunctions: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.conjunctions[0])

    def __str__(self):
        return " or ".join(custom_str(con) for con in self.conjunctions)


@dataclass
class Expression(Statement, PrimaryExpression, Resolvable):
    disjunction: AnyNode

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        # It's assumed that all the children have the same type
        return resolve_type_func(self.disjunction)

    def __str__(self):
        return custom_str(self.disjunction)


@dataclass
class CollectionLiteral(PrimaryExpression, Resolvable):
    expressions: List[AnyNode]

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        if len(self.expressions) > 0:
            return IterableType(resolve_type_func(self.expressions[0]))
        return IterableType(SimpleType("None"))

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

    def __str__(self):
        return 'while ' + str(self.expression) + " " + \
               curly_block(custom_str(self.statements_block))


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
class IfExpression(PrimaryExpression, ResolvableByStatementsBlock):
    condition: AnyNode
    statements_block: TreeWithUnit[StatementsBlock]
    elif_expressions: List[TreeWithUnit[ElseIfExpression]]
    optional_else: Optional[TreeWithUnit[ElseExpression]]

    def resolve_type(self, get_return_type_func) -> Optional[UnitType]:
        return get_return_type_func(self.statements_block.identifier)

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
    left: Union[TreeWithUnit[VariableDeclaration], Name]
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
class ParenthesizedExpression(Resolvable):
    child: AnyNode

    def resolve_type(self, resolve_type_func) -> Optional[UnitType]:
        return resolve_type_func(self.child)

    def __str__(self):
        return f"({custom_str(self.child)})"
