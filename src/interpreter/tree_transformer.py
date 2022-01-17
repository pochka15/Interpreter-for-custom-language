from lark import Transformer, v_args

from interpreter.language_units import *


def last(elements: List):
    if len(elements) > 0:
        return elements[-1]


def get_line(node):
    if isinstance(node, TreeWithUnit):
        return node.meta.line
    return node.line


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming
@v_args(tree=True)
class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)
        self.counter = 0

    def next_id(self):
        x = self.counter
        self.counter += 1
        return x

    def DEC_NUMBER(self, token):
        return SimpleLiteral(int(token), token.line)

    def BOOLEAN(self, token):
        return SimpleLiteral(token == 'true', token.line)

    def FLOAT_NUMBER(self, token):
        return SimpleLiteral(float(token), token.line)

    def STRING(self, token):
        return SimpleLiteral(token.strip('"'), token.line)

    def NAME(self, token):
        return token

    def start(self, node: Tree):
        node.meta.line = 0
        return TreeWithUnit(node, Start(node.children), self.next_id())

    # function_declaration: NAME "(" function_parameters ")" function_return_type "{" statements_block "}"
    def function_declaration(self, node):
        children = node.children
        name = children[0]
        node.meta.line = get_line(name)
        return TreeWithUnit(
            node,
            FunctionDeclaration(name=name,
                                function_parameters=children[1].children,
                                return_type=children[2],
                                statements_block=children[3]),
            identifier=self.next_id())

    # return_statement: RETURN expression?
    def return_statement(self, node):
        children = node.children
        expression = children[0] if len(children) > 0 else None
        if expression is not None:
            node.meta.line = get_line(expression)
        return TreeWithUnit(node, ReturnStatement(expression), self.next_id())

    def disjunction(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, Disjunction(node.children), self.next_id())

    def conjunction(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, Conjunction(node.children), self.next_id())

    def equality(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, Equality(node.children), self.next_id())

    def prefix_unary_expression(self, node):
        operator, expr = node.children
        node.meta.line = get_line(operator)
        return TreeWithUnit(node, PrefixUnaryExpression(operator, expr), self.next_id())

    def if_expression(self, node):
        children = node.children
        it = iter(children)

        condition = next(it)
        statements_block = next(it)

        rest = [*(x for x in it)]

        else_if_expressions = [x for x in rest if x.data == 'elseif_expression']

        else_expression = None
        last_expression = last(rest)
        if last_expression is not None and \
                last_expression.data == 'else_expression':
            else_expression = last_expression

        node.meta.line = get_line(condition)
        return TreeWithUnit(node, IfExpression(condition,
                                               statements_block,
                                               else_if_expressions,
                                               else_expression), self.next_id())

    def elseif_expression(self, node):
        children = node.children
        assert len(children) == 2
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, ElseIfExpression(*children), self.next_id())

    def else_expression(self, node):
        children = node.children
        assert len(children) == 1
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, ElseExpression(*children), self.next_id())

    def function_parameter(self, node):
        children = node.children
        assert len(children) == 2
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, FunctionParameter(*children), self.next_id())

    def statements_block(self, node):
        children = node.children
        if len(node.children) > 0:
            node.meta.line = get_line(children[0])
        return TreeWithUnit(node, StatementsBlock(children), self.next_id())

    def variable_declaration(self, node):
        children = node.children
        assert len(children) == 3
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, VariableDeclaration(*children), self.next_id())

    def postfix_unary_expression(self, node):
        children = node.children
        assert len(children) > 0
        node.meta.line = get_line(children[0])
        return TreeWithUnit(
            node, PostfixUnaryExpression(children[0], children[1:]), self.next_id())

    def multiplicative_expression(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, MultiplicativeExpression(node.children), self.next_id())

    def parenthesized_expression(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, ParenthesizedExpression(node.children[0]), self.next_id())

    def additive_expression(self, node):
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, AdditiveExpression(node.children), self.next_id())

    def comparison(self, node):
        children = node.children
        node.meta.line = get_line(node.children[0])
        return TreeWithUnit(node, Comparison(children), self.next_id())

    def collection_literal(self, node):
        children = node.children
        if len(children) > 0:
            node.meta.line = get_line(children[0])
        return TreeWithUnit(node, CollectionLiteral(children), self.next_id())

    def for_statement(self, node):
        children = node.children
        assert len(children) == 3
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, ForStatement(*children), self.next_id())

    def while_statement(self, node):
        children = node.children
        assert len(children) == 2
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, WhileStatement(*children), self.next_id())

    def indexing_suffix(self, node):
        children = node.children
        if len(children) > 0:
            node.meta.line = get_line(children[0])
        return TreeWithUnit(node, IndexingSuffix(children[0]), self.next_id())

    def call_suffix(self, node):
        children = node.children
        if len(children) > 0:
            node.meta.line = get_line(children[0])
        return TreeWithUnit(node, CallSuffix(children), self.next_id())

    def navigation_suffix(self, node):
        children = node.children
        if len(children) > 0:
            node.meta.line = get_line(children[0])
        return TreeWithUnit(node, NavigationSuffix(children[0]), self.next_id())

    def assignment(self, node):
        children = node.children
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, Assignment(*children), self.next_id())

    def type(self, node):
        children = node.children
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, Type(children), self.next_id())

    def break_statement(self, node):
        children = node.children
        node.meta.line = get_line(children[0])
        return TreeWithUnit(node, BreakStatement(), self.next_id())
