from typing import Dict

from lark import Visitor

from interpreter.language_units import *
from interpreter.semantic_analyzer import description


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
        self._name_to_value: Dict[str, Any] = {}
        self._name_to_function: Dict[str, Any] = {}

    def assign_value(self, name, value):
        self._name_to_value[name] = value

    def reassign_value(self, name, value):
        if self._name_to_value.get(name, None) is not None:
            self._name_to_value[name] = value
        else:
            self.parent.reassign_value(name, value)

    def assign_function(self, name, func):
        self._name_to_function[name] = func

    def reassign_function(self, name, func):
        if self._name_to_function.get(name, None) is not None:
            self._name_to_function[name] = func
        else:
            self.parent.reassign_function(name, func)

    def lookup(self, name: str):
        x = self._name_to_function.get(name, None)
        if x is not None:
            return x

        x = self._name_to_value.get(name, None)
        if x is not None:
            return x

        if self.parent is not None:
            return self.parent.lookup(name)

        return None


def find_first_matching(pred, elements):
    for ind, element in enumerate(elements):
        if pred(element):
            return ind, element
    return -1, None


class LoopContext:

    def __init__(self, parent_context) -> None:
        self.should_break = False
        self._parent_context = parent_context


class Interpreter(Visitor):
    def __init__(self, is_test=False):
        super().__init__()
        self.is_test = is_test
        self.test_outputs: List[str] = []
        self.closure = Closure()
        self.loopContext: Optional[LoopContext] = None

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
        self.closure.assign_function('print', print)
        self.closure.assign_function('str', str)
        self.closure.assign_function('test_print', lambda it: self.test_outputs.append(it))
        self.closure.assign_function('append', lambda value, elements: elements.append(value))
        self.closure.assign_function('remove', lambda value, elements: elements.remove(value))
        self.closure.assign_function('len', lambda elements: len(elements))
        self.closure.assign_function('range', range)
        main = self.visit_once(tree)
        main()
        if self.is_test:
            return self.test_outputs

    def eval_in_closure(self, func):
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
        for x in node.unit.function_declarations:
            self.visit_once(x)
        return self.closure.lookup('main')

    def function_declaration(self, node: TreeWithUnit[FunctionDeclaration]):
        def fn(*args):
            def inner():
                params = node.unit.function_parameters
                params_iter = iter(params)
                for arg in args:
                    param = next(params_iter)
                    self.closure.assign_value(param.unit.name, arg)
                return self.visit_once(node.unit.statements_block)

            return self.eval_in_closure(inner)

        name = node.unit.name
        self.closure.assign_function(name, fn)

    def statements_block(self, node: TreeWithUnit[StatementsBlock]):
        def inner():
            statements = node.unit.statements
            return_value = None
            for x in statements:
                if self.loopContext is not None and self.loopContext.should_break:
                    break
                value = self.visit_once(x)
                if isinstance(x, TreeWithUnit) and isinstance(x.unit, ReturnStatement):
                    return_value = value
            return return_value

        return self.eval_in_closure(inner)

    def return_statement(self, node: TreeWithUnit[ReturnStatement]) -> Any:
        return self.eval(node.unit.expression)

    def break_statement(self, _) -> Any:
        self.loopContext.should_break = True

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

    def multiplicative_expression(self, node: TreeWithUnit[MultiplicativeExpression]):
        children_iter = iter(node.unit.children)
        value = self.eval(next(children_iter))
        operator = next(children_iter, None)

        while operator is not None:
            next_val = self.eval(next(children_iter))
            if operator == '*':
                value = value * next_val
            elif operator == '/':
                value = value / next_val
            elif operator == '%':
                value = value % next_val
            operator = next(children_iter, None)

        return value

    def assignment(self, node: TreeWithUnit[Assignment]):
        right = self.eval(node.unit.right)
        left = node.unit.left

        # Variable declaration
        if isinstance(node.unit.left, TreeWithUnit):
            variable_declaration = left.unit
            assert isinstance(variable_declaration, VariableDeclaration)
            name = variable_declaration.variable_name
            self.closure.assign_value(name, right)

        # Reassignment
        else:
            self.closure.reassign_value(left, right)

    def call_func(self, name: str, args):
        fn = self.closure.lookup(name)
        if fn is None:
            raise Exception("Couldn't find")
        return fn(*args)

    def postfix_unary_expression(self, node: TreeWithUnit[PostfixUnaryExpression]):
        assert len(node.unit.suffixes) == 1, \
            "More than one suffix can not be interpreted yet: " + description(node)
        suffix = node.unit.suffixes[0]

        expression = self.eval(node.unit.primary_expression)
        result = None

        if isinstance(suffix.unit, CallSuffix):
            expressions = suffix.unit.function_call_arguments
            arguments = [self.eval(expr) for expr in expressions]
            func = expression
            result = func(*arguments)

        if isinstance(suffix.unit, IndexingSuffix):
            argument = self.eval(suffix.unit.expression)
            result = expression[argument]

        return result

    def collection_literal(self, node: TreeWithUnit[CollectionLiteral]) -> List:
        return [self.eval(expr) for expr in node.unit.expressions]

    def for_statement(self, node: TreeWithUnit[ForStatement]):
        def exec_loop(items_):
            for item in items_:
                self.eval_in_closure(lambda: exec_statements_block(node.unit.name, item))

        def exec_statements_block(name, value):
            self.closure.assign_value(name, value)
            self.visit_once(node.unit.statements_block)

        items = self.eval(node.unit.expression)
        self.eval_in_loop_context(lambda: exec_loop(items))

    def while_statement(self, node: TreeWithUnit[WhileStatement]):
        def exec_loop():
            should_continue = self.eval(node.unit.expression)
            while should_continue and not self.loopContext.should_break:
                self.visit_once(node.unit.statements_block)
                should_continue = self.eval(node.unit.expression)

        self.eval_in_loop_context(exec_loop)

    def equality(self, node: TreeWithUnit[Equality]):
        children_iter = iter(node.unit.comparison_and_operators)
        left = self.eval(next(children_iter))
        operator = next(children_iter, None)
        right = self.eval(next(children_iter))
        if operator == '==':
            res = left == right
        else:
            res = left != right

        return res

    def comparison(self, node: TreeWithUnit[Comparison]):
        children_iter = iter(node.unit.children)
        value = self.eval(next(children_iter))
        operator = next(children_iter, None)

        while operator is not None:
            next_val = self.eval(next(children_iter))
            if operator == '<':
                value = value < next_val
            elif operator == '>':
                value = value > next_val
            elif operator == '>=':
                value = value >= next_val
            elif operator == '<=':
                value = value <= next_val

            operator = next(children_iter, None)

        return value

    def parenthesized_expression(self, node: TreeWithUnit[ParenthesizedExpression]):
        return self.eval(node.unit.child)

    def if_expression(self, node: TreeWithUnit[IfExpression]):
        conditions = [node.unit.condition] + [x.unit.condition for x in node.unit.elif_expressions]
        ind, condition = find_first_matching(lambda x: self.eval(x) is True, conditions)
        if ind < 0:
            if node.unit.optional_else is not None:
                return self.eval(node.unit.optional_else)
        elif ind == 0:
            return self.eval(node.unit.statements_block)
        else:
            ind = ind - 1
            return self.eval(node.unit.elif_expressions[ind].unit.statements_block)

    def else_expression(self, node: TreeWithUnit[ElseExpression]):
        return self.eval(node.unit.statements_block)

    def eval_in_loop_context(self, func):
        parent = self.loopContext
        self.loopContext = LoopContext(parent)
        ret = func()
        self.loopContext = parent
        return ret
