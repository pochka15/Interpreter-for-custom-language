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

    def lookup(self, name: str):
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

    # noinspection PyUnresolvedReferences
    def visit_once(self, node: TreeWithUnit) -> Any:
        """
        Visit the node only once. Comparing to the default 'visit' function it doesn't visit nodes recursively
        :param node: node that is visited
        :return: any value that is returned from the called function
        """
        return self._call_userfunc(node)

    def eval(self, node: AnyNode):
        """
        Evaluate the expression which is bound to the given node
        :param node: node that gets evaluated.
        :return: the result of the evaluated expression
        """
        if isinstance(node, TreeWithUnit):
            return self.visit_once(node)
        if isinstance(node, SimpleLiteral):
            return node.value
        elif isinstance(node, Name):
            return self.closure.lookup(node)

    def interpret(self, tree):
        self.visit_once(tree)
        if self.is_test:
            return self.test_outputs

    def new_closure(self, func):
        """
        Utility function that evaluates given function in a new nested closure
        :param func: function that is called
        :return: the return value of the called function
        """
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
                return self.visit_once(node.unit.statements_block)

            return self.new_closure(inner)

        name = node.unit.name
        self.closure.name_to_function[name] = fn

    def statements_block(self, node: TreeWithUnit[StatementsBlock]):
        def inner():
            statements = node.unit.statements
            return_value = None
            for x in statements:
                value = self.visit_once(x)
                if isinstance(x, TreeWithUnit) and isinstance(x.unit, ReturnStatement):
                    return_value = value
            return return_value

        return self.new_closure(inner)

    def return_statement(self, node: TreeWithUnit[ReturnStatement]) -> Any:
        return self.eval(node.unit.expression)

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

        return value

    def assignment(self, node: TreeWithUnit[Assignment]):
        value = self.eval(node.unit.right)
        left = node.unit.left
        # Variable declaration
        if isinstance(node.unit.left, TreeWithUnit):
            variable_declaration = left.unit
            assert isinstance(variable_declaration, VariableDeclaration)
            name = variable_declaration.variable_name
        # Reassignment
        else:
            name = left
        self.closure.name_to_value[name] = value

    def call_func(self, name: str, args):
        fn = self.closure.lookup(name)
        if fn is None:
            raise Exception("Couldn't find")
        return fn(*args)

    def postfix_unary_expression(self, node: TreeWithUnit[PostfixUnaryExpression]):
        assert len(node.unit.suffixes) == 1, "More than one suffix can not be interpreted yet"
        suffix = node.unit.suffixes[0]

        expression = self.eval(node.unit.primary_expression)
        result = None

        if isinstance(suffix.unit, CallSuffix):
            func = expression
            expressions = suffix.unit.function_call_arguments
            arguments = [self.eval(expr) for expr in expressions]
            result = func(*arguments)

        if isinstance(suffix.unit, IndexingSuffix):
            argument = self.eval(suffix.unit.expression)
            result = expression[argument]

        return result

    def collection_literal(self, node: TreeWithUnit[CollectionLiteral]) -> List:
        return [self.eval(expr) for expr in node.unit.expressions]
