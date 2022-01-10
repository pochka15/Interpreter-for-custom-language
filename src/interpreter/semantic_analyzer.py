from lark import Visitor

from interpreter.language_units import *
from interpreter.language_units import TreeWithUnit
from interpreter.semantic.closure import Closure, Variable


def is_val(tree: Tree):
    return True if tree.children[0] == 'val' else False


@dataclass
class Executable:
    func: Any
    return_type: Optional[str] = None


class SemanticAnalyzer(Visitor):
    def __init__(self, is_test=False):
        super().__init__()
        self.is_test = is_test
        self.counter = 0
        self.closure = Closure()
        self.main_func = None
        self.test_outputs: List[str] = []

    def resolve_type(self, node) -> str:
        pass

    def analyze(self, tree):
        self.visit(tree)
        return self.main_func

    def start(self, node: TreeWithUnit[Start]):
        functions = [x for x in node.unit.function_declarations
                     if str(x.unit.name) == 'main']
        assert len(functions) == 1

    def variable_declaration(self, node: TreeWithUnit[VariableDeclaration]):
        is_const = node.unit.var_or_let == 'let'
        variable = Variable(node.unit.variable_name,
                            str(node.unit.type.unit),
                            is_const=is_const)
        self.closure[node.unit.variable_name] = variable

    def assignment(self, node: TreeWithUnit[Assignment]):
        variable_declaration = node.unit.left
        assert isinstance(variable_declaration, VariableDeclaration)
        self.closure[variable_declaration.variable_name].is_bound = True

    # TODO(@pochka15): go on
    def additive_expression(self, tree: TreeWithUnit[AdditiveExpression]):
        pass

    def return_statement(self, node: TreeWithUnit[ReturnStatement]):
        pass

    def statements_block(self, node: TreeWithUnit[StatementsBlock]):
        pass

    def function_declaration(self, node: TreeWithUnit[FunctionDeclaration]):
        pass

    def postfix_unary_expression(self, node: TreeWithUnit[PostfixUnaryExpression]):
        pass

    def call_suffix(self, node: TreeWithUnit[CallSuffix]):
        pass
