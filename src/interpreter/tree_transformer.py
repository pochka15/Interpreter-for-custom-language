from lark import Transformer, v_args

from interpreter.language_units import *


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming

@v_args(tree=True)
class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)

    def def_token(self, token: Token):
        return TokenAndLanguageUnit(token, token.value)

    __default_token__ = def_token

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

    def additive_expression(self, node):
        children = node.children
        first = children[0]
        rest = children[1:]
        return TreeWithLanguageUnit(node, AdditiveExpression(first, rest))

    def prefix_unary_expression(self, node):
        children = node.children
        if len(children) == 2:
            operator, expr = children
        else:
            operator = None
            expr = children[0]
        return TreeWithLanguageUnit(node, PrefixUnaryExpression(operator, expr))
