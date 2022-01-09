from typing import Any, Dict

from lark import Visitor

from dataclasses import dataclass

from interpreter.language_units import *
from interpreter.language_units import TreeWithLanguageUnit
from interpreter.semantic.closure import Closure, Variable, Function


def is_val(tree: Tree):
    return True if tree.children[0] == 'val' else False


@dataclass
class Executable:
    func: Any
    return_type: Optional[str] = None


@dataclass
class SymbolContainer:
    symbol: Variable


class Interpreter(Visitor):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.closure = Closure()
        self.main_function: TreeWithLanguageUnit[FunctionDeclaration]

        # Dictionaries for the interpretation
        self.node_to_variable: Dict[LanguageUnitContainer, Variable] = {}
        self.node_to_function: Dict[LanguageUnitContainer, Function] = {}
        self.node_to_executable: Dict[Any, Executable] = {}
        self.node_to_value: Dict[Any, Any] = {}

    def next_id(self):
        x = self.counter
        self.counter += 1
        return x

    def execute_node(self, node: LanguageUnitContainer):
        if node is TokenAndLanguageUnit:
            if node.token == 'print':
                return print

        executable = self.node_to_executable.get(node, None)
        if executable is not None:
            return executable.func()

        value = self.node_to_value.get(node, None)
        if value is not None:
            return value

    def resolve_type(self, node) -> str:
        value = self.node_to_value.get(node, None)
        if value is not None:
            return type(value).__name__

        executable = self.node_to_executable.get(node, None)
        if executable is not None:
            return executable.return_type

    def interpret(self, tree):
        self.visit(tree)
        self.execute_node(self.main_function)

    def start(self, node: TreeWithLanguageUnit[Start]):
        child: LanguageUnitContainer
        functions = [x for x in node.unit.function_declarations
                     if str(x.unit.name) == 'main']
        if len(functions) > 0:
            self.main_function = functions[0]

    def assignment(self, tree: TreeWithLanguageUnit[Assignment]):
        def executable_func():
            symbol = self.node_to_variable[tree.unit.left]
            symbol.value = self.execute_node(tree.unit.right)

        self.node_to_executable[tree] = Executable(executable_func, None)

    def variable_declaration(self, node: TreeWithLanguageUnit[VariableDeclaration]):
        is_const = node.unit.var_or_let.unit == 'let'
        symbol = Variable(node.unit.variable_name.unit,
                          str(node.unit.type.unit),
                          self.next_id(),
                          False,
                          is_const)
        self.node_to_variable[node] = symbol
        self.closure[node.unit.variable_name] = symbol
        self.node_to_variable[node] = symbol

    def additive_expression(self, tree: TreeWithLanguageUnit[AdditiveExpression]):
        def executable_func():
            children = tree.unit.children
            iterator = iter(children)
            value = self.execute_node(next(iterator))
            operator = next(iterator, None)

            while operator is not None:
                right_value = self.execute_node(next(iterator))
                if operator.unit == '-':
                    value -= right_value
                elif operator.unit == '+':
                    value += right_value
                else:
                    raise Exception(
                        f"Unknown operator: {operator.unit} at {operator.token.line}:{operator.token.column}")
                operator = next(iterator, None)

        self.node_to_executable[tree] = Executable(
            executable_func, self.resolve_type(tree.unit.children[0]))

    def return_statement(self, node: TreeWithLanguageUnit[ReturnStatement]):
        expression = node.unit.expression
        if expression is not None:
            self.node_to_executable[node] = Executable(
                lambda: self.execute_node(expression),
                self.resolve_type(expression))

    def statements_block(self, node: TreeWithLanguageUnit[StatementsBlock]):
        def executable_func():
            for statement in node.unit.statements:
                self.execute_node(statement)

        self.closure = Closure(self.closure)
        self.node_to_executable[node] = Executable(executable_func)

    def function_declaration(self, node: TreeWithLanguageUnit[FunctionDeclaration]):
        def executable_func():
            return self.execute_node(node.unit.statements_block)

        # Add parameters to the new closure
        self.closure = Closure(self.closure)
        params = []
        for param in node.unit.function_parameters:
            symbol = Variable(str(param.unit), str(param.unit.type.unit), hash(node), is_const=True)
            self.closure[str(param.unit)] = symbol
            self.node_to_variable[param] = symbol
            params.append(symbol)

        # Add function to the new closure
        self.closure = Closure(self.closure)
        return_type_unit = node.unit.return_type.unit
        name_unit = node.unit.name.unit
        func = Function(str(name_unit), str(return_type_unit), self.next_id(), params)
        self.node_to_function[node] = func
        self.closure[node] = func

        self.node_to_executable[node] = Executable(executable_func, str(return_type_unit))

    def postfix_unary_expression(self, node: TreeWithLanguageUnit[PostfixUnaryExpression]):
        def executable_func():
            assert len(node.unit.suffixes) == 1
            suffix = node.unit.suffixes[0]
            assert suffix is CallSuffix
            func = self.node_to_function[node.unit.primary_expression]
            func.params[0].value = self.execute_node(suffix)
            return self.execute_node(node.unit.primary_expression)

        return Executable(executable_func)

    def call_suffix(self, node: TreeWithLanguageUnit[CallSuffix]):
        def executable_func():
            return [self.node_to_executable[expr].func()
                    for expr in node.unit.function_call_arguments.unit.expressions]

        return Executable(executable_func)
