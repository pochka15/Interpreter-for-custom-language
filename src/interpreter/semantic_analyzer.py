from typing import Dict

from lark import Visitor

from interpreter.language_units import *
from interpreter.language_units import TreeWithUnit
from interpreter.semantic.closure import Closure, Variable, ClosureItem, Function


@dataclass
class Executable:
    func: Any
    return_type: Optional[str] = None


class ReassignException(Exception):
    pass


class InvalidRedeclaration(Exception):
    pass


class TypeMismatchException(Exception):
    pass


def description(node: AnyNode):
    if isinstance(node, TreeWithUnit):
        return str(node.unit)
    if isinstance(node, SimpleLiteral):
        return f"line: {node.origin.line}, {node.origin}"
    elif isinstance(node, Name):
        return f"line: {node.line}, {node}"


def resolve_closure_item_type(item: ClosureItem) -> UnitType:
    if isinstance(item, Variable):
        return item.type
    if isinstance(item, Function):
        param_types = [param.type for param in item.params]
        return FunctionType(param_types, item.return_type)


def match_types(left: UnitType, right: UnitType, message_before=''):
    if not str(left) == str(right):
        raise TypeMismatchException(
            message_before + f"\nTypes don't match:\n"
                             f"{str(left)} != {str(right)}")


class SemanticAnalyzer(Visitor):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.closure = Closure()
        self.main_func = None
        self.test_outputs: List[str] = []
        self.delayed_tasks: List = []
        # node id -> return_statement_node.unit.expression
        self.id_to_return_expression_node: Dict[int, AnyNode] = {}

    def get_statements_block_type(self, identifier: int, closure: Closure) -> Optional[UnitType]:
        """
        Get the type which is bound to the statements block which can contain a return expression
        :param closure: closure which is used to resolve type
        :param identifier: id of the statements block
        :return: the type of the return expression in the statement's block or None by default
        """
        return self.resolve_type(self.id_to_return_expression_node.get(identifier, None), closure)

    def resolve_type(self, node: AnyNode, closure: Closure) -> UnitType:
        if isinstance(node, TreeWithUnit):
            unit = node.unit
            if isinstance(unit, ResolvableByStatementsBlock):
                return unit.resolve_type(
                    lambda id_: self.get_statements_block_type(id_, closure))
            if isinstance(unit, Resolvable):
                return unit.resolve_type(lambda x: self.resolve_type(x, closure))
            if isinstance(unit, Typed):
                return unit.type
        if isinstance(node, SimpleLiteral):
            return node.type
        elif isinstance(node, Name):
            return resolve_closure_item_type(closure.lookup(node))

    def analyze(self, tree):
        self.visit(tree)
        for task in self.delayed_tasks:
            task()
        return self.main_func

    # noinspection PyMethodMayBeStatic
    def start(self, node: TreeWithUnit[Start]):
        functions = [x for x in node.unit.function_declarations
                     if str(x.unit.name) == 'main']
        assert len(functions) == 1

    # Store variable into the closure
    def variable_declaration(self, node: TreeWithUnit[VariableDeclaration]):
        is_const = node.unit.var_or_let == 'let'
        variable = Variable(node.unit.variable_name,
                            node.unit.type,
                            is_const=is_const)
        self.closure[node.unit.variable_name] = variable

    def assignment(self, node: TreeWithUnit[Assignment]):
        def update_variable_type_if_necessary(closure: Closure):
            if isinstance(node.unit.left, TreeWithUnit):
                unit: VariableDeclaration = node.unit.left.unit
                t = self.resolve_type(node.unit.left, closure)
                if (isinstance(t, IterableType)
                        and isinstance(t.item_type, UnknownIterableItemType)):
                    closure[unit.variable_name].type = self.resolve_type(node.unit.right, closure)

        def bind_value(closure: Closure):
            if isinstance(node.unit.left, TreeWithUnit):
                name = node.unit.left.unit.variable_name
            else:
                name = node.unit.left
            closure[name].is_bound = True

        def match_types_(closure):
            if isinstance(node.unit.left, TreeWithUnit):
                unit: VariableDeclaration = node.unit.left.unit
                t = closure[unit.variable_name].type
                # When unit is a VariableDeclaration I want to take its type from the closure
                # because I update it in the update_variable_type_if_necessary()
                match_types(t,
                            self.resolve_type(node.unit.right, closure),
                            message_before="Couldn't assign variable, " + description(node))
            else:
                match_types(self.resolve_type(node.unit.left, closure),
                            self.resolve_type(node.unit.right, closure),
                            message_before="Couldn't assign variable, " + description(node))

        # test if left can be assigned or reassigned checking if it's a constant symbol
        def can_assign(closure):
            left = node.unit.left
            if isinstance(left, TreeWithUnit):
                left_unit = left.unit
                assert isinstance(left_unit, VariableDeclaration)
                variable = closure[left_unit.variable_name]
                if variable is not None and variable.is_bound:
                    raise InvalidRedeclaration(
                        f"variable with the name '{left_unit.variable_name}' cannot be declared again")
            if isinstance(left, Name):
                if closure[left].is_const:
                    raise ReassignException(f"Variable cannot be reassigned because it was declared as let\n"
                                            f"{description(node)}")

        self.delayed_tasks.append(lambda: update_variable_type_if_necessary(self.closure))
        self.delayed_tasks.append(lambda: match_types_(self.closure))
        self.delayed_tasks.append(lambda: can_assign(self.closure))
        self.delayed_tasks.append(lambda: bind_value(self.closure))

    def additive_expression(self, tree: TreeWithUnit[AdditiveExpression]):
        pass

    def statements_block(self, node: TreeWithUnit[StatementsBlock]):
        statements = node.unit.statements
        if len(statements) > 0:
            statement = statements[-1].unit
            if isinstance(statement, ReturnStatement):
                self.id_to_return_expression_node[node.identifier] = statement.expression

    # - test function declaration is not declared again
    # - test if returned type is same as the type of the returned value
    def function_declaration(self, node: TreeWithUnit[FunctionDeclaration]):
        pass

    def postfix_unary_expression(self, node: TreeWithUnit[PostfixUnaryExpression]):
        pass

    def call_suffix(self, node: TreeWithUnit[CallSuffix]):
        if isinstance(node.unit, NavigationSuffix):
            raise NotImplementedError("Navigation suffix is not implemented")
