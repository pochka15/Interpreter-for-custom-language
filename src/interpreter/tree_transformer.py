from lark import Transformer, v_args

from interpreter.language_units import *


def last(elements: List):
    if len(elements) > 0:
        return elements[-1]


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming
@v_args(tree=True)
class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)

    def default_token(self, token: Token):
        return TokenAndLanguageUnit(token, token)

    def DEC_NUMBER(self, token):
        return TokenAndLanguageUnit(token, int(token))

    def BOOLEAN(self, token):
        return TokenAndLanguageUnit(token, token == 'true')

    def FLOAT_NUMBER(self, token):
        return TokenAndLanguageUnit(token, float(token))

    __default_token__ = default_token

    def start(self, node: Tree):
        return TreeWithLanguageUnit(node, Start(node.children))

    # function_declaration: NAME "(" function_parameters ")" function_return_type "{" statements_block "}"
    def function_declaration(self, node):
        children = node.children
        return TreeWithLanguageUnit(
            node,
            FunctionDeclaration(name=children[0],
                                function_parameters=children[1].children,
                                return_type=children[2],
                                statements_block=children[3]))

    # return_statement: RETURN expression?
    def return_statement(self, node):
        children = node.children
        expression = children[0] if len(children) > 0 else None
        return TreeWithLanguageUnit(node, ReturnStatement(expression))

    def disjunction(self, node):
        return TreeWithLanguageUnit(node, Disjunction(node.children))

    def conjunction(self, node):
        return TreeWithLanguageUnit(node, Conjunction(node.children))

    def equality(self, node):
        return TreeWithLanguageUnit(node, Equality(node.children))

    def prefix_unary_expression(self, node):
        children = node.children
        if len(children) == 2:
            operator, expr = children
        else:
            operator = None
            expr = children[0]
        return TreeWithLanguageUnit(node, PrefixUnaryExpression(operator, expr))

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

        return TreeWithLanguageUnit(node, IfExpression(condition,
                                                       statements_block,
                                                       else_if_expressions,
                                                       else_expression))

    def elseif_expression(self, node):
        children = node.children
        assert len(children) == 2
        return TreeWithLanguageUnit(node, ElseIfExpression(*children))

    def else_expression(self, node):
        children = node.children
        assert len(children) == 1
        return TreeWithLanguageUnit(node, ElseExpression(*children))

    def function_parameter(self, node):
        children = node.children
        assert len(children) == 2
        return TreeWithLanguageUnit(node, FunctionParameter(*children))

    def statements_block(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, StatementsBlock(children))

    def variable_declaration(self, node):
        children = node.children
        assert len(children) == 3
        return TreeWithLanguageUnit(node, VariableDeclaration(*children))

    def postfix_unary_expression(self, node):
        children = node.children
        assert len(children) > 0
        return TreeWithLanguageUnit(
            node, PostfixUnaryExpression(children[0], children[1:]))

    def multiplicative_expression(self, node):
        return TreeWithLanguageUnit(node, MultiplicativeExpression(node.children))

    def additive_expression(self, node):
        return TreeWithLanguageUnit(node, AdditiveExpression(node.children))

    def comparison(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, Comparison(children))

    def collection_literal(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, CollectionLiteral(children))

    def for_statement(self, node):
        children = node.children
        assert len(children) == 3
        return TreeWithLanguageUnit(node, ForStatement(*children))

    def while_statement(self, node):
        children = node.children
        assert len(children) == 2
        return TreeWithLanguageUnit(node, WhileStatement(*children))

    def indexing_suffix(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, IndexingSuffix(children[0]))

    def call_suffix(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, CallSuffix(*children))

    def navigation_suffix(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, NavigationSuffix(children[0]))

    def assignment(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, Assignment(*children))

    def type(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, Type(children))

    def function_call_arguments(self, node):
        children = node.children
        return TreeWithLanguageUnit(node, FunctionCallArguments(children))
