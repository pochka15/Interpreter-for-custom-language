from typing import Dict

from lark import Visitor

from interpreter.language_units import *


def is_val(tree: Tree):
    return True if tree.children[0] == 'val' else False


@dataclass
class Executable:
    func: Any
    return_type: Optional[str] = None


class Closure:
    def __init__(self, parent=None):
        super().__init__()
        self.parent: Closure = parent
        self.name_to_value: Dict[str, Any] = {}
        self.name_to_function: Dict[str, Any] = {}
        self.values = []

    def lookup(self, name):
        x = self.name_to_function.get(name, None)
        if x is not None:
            return x

        x = self.name_to_value.get(name, None)
        if x is not None:
            return x

        if self.parent is not None:
            return self.parent.lookup(name)

        return None


class Interpreter(Visitor):
    def __init__(self, is_test=False):
        super().__init__()
        self.is_test = is_test
        self.test_outputs: List[str] = []
        self.closure = Closure()
        # stack of the returned values from functions
        self.returned_values = []

    # noinspection PyUnresolvedReferences
    def visit_once(self, node: TreeWithUnit):
        self._call_userfunc(node)

    def eval(self, node: AnyNode):
        if isinstance(node, TreeWithUnit):
            self.visit_once(node)
            return self.closure.values.pop()
        if isinstance(node, SimpleLiteral):
            return node.value
        elif isinstance(node, Name):
            return self.closure.name_to_value[node]

    def interpret(self, tree):
        self.visit_once(tree)
        if self.is_test:
            return self.test_outputs

    def new_closure(self, func):
        parent = self.closure
        self.closure = Closure(parent)
        ret = func()
        self.closure = parent
        return ret

    def start(self, node: TreeWithUnit[Start]):
        # Add builtins
        self.closure.name_to_function['print'] = print
        self.closure.name_to_function['str'] = str
        self.closure.name_to_function['test_print'] = lambda it: self.test_outputs.append(it)

        # Visit function declarations
        for x in node.unit.function_declarations:
            self.visit_once(x)

        # Visit main's statements block
        main: TreeWithUnit[FunctionDeclaration] = [
            x for x in node.unit.function_declarations
            if str(x.unit.name) == 'main'][0]
        self.visit_once(main.unit.statements_block)

    def function_declaration(self, node: TreeWithUnit[FunctionDeclaration]):
        def fn(*args):
            def inner():
                params = node.unit.function_parameters
                params_iter = iter(params)
                for arg in args:
                    param = next(params_iter)
                    self.closure.name_to_value[param.unit.name] = arg
                self.visit_once(node.unit.statements_block)
                return self.returned_values.pop()

            return self.new_closure(inner)

        name = node.unit.name
        self.closure.name_to_function[name] = fn

    def statements_block(self, node: TreeWithUnit[StatementsBlock]):
        def inner():
            statements = node.unit.statements
            for x in statements:
                self.visit_once(x)

        self.new_closure(inner)

    def return_statement(self, node: TreeWithUnit[ReturnStatement]):
        self.returned_values.append(self.eval(node.unit.expression))

    def additive_expression(self, node: TreeWithUnit[AdditiveExpression]):
        children_iter = iter(node.unit.children)
        value = self.eval(next(children_iter))
        operator = next(children_iter, None)

        while operator is not None:
            next_val = self.eval(next(children_iter))
            if operator == '+':
                value = value + next_val
            elif operator == '-':
                value = value - next_val
            operator = next(children_iter, None)

        self.closure.values.append(value)

    def assignment(self, node: TreeWithUnit[Assignment]):
        value = self.eval(node.unit.right)
        variable_declaration = node.unit.left.unit
        assert isinstance(variable_declaration, VariableDeclaration)
        name = variable_declaration.variable_name
        self.closure.name_to_value[name] = value

    def apply_suffix(self, name, suffix, args):
        if isinstance(suffix.unit, IndexingSuffix):
            return None
        elif isinstance(suffix.unit, CallSuffix):
            # for debug
            fn = self.closure.lookup(name)
            if fn is None:
                raise Exception("Couldn't find")
            return fn(*args)
        elif isinstance(suffix.unit, NavigationSuffix):
            return None

    def postfix_unary_expression(self, node: TreeWithUnit[PostfixUnaryExpression]):
        arguments = []

        assert len(node.unit.suffixes) == 1
        suffix = node.unit.suffixes[0]

        if isinstance(suffix.unit, IndexingSuffix):
            arguments = [self.eval(suffix.unit.expression)]
        elif isinstance(suffix.unit, CallSuffix):
            if suffix.unit.function_call_arguments is None:
                arguments = []
            else:
                expressions = suffix.unit.function_call_arguments
                arguments = [self.eval(expr) for expr in expressions]
        elif isinstance(suffix.unit, NavigationSuffix):
            arguments = [suffix.unit.name]

        name = node.unit.primary_expression
        assert isinstance(name, Name)
        value = self.apply_suffix(name, suffix, arguments)
        self.closure.values.append(value)
