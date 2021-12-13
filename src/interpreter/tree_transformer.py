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
        expression = node.children[0] if len(children) > 0 else None
        return TreeWithLanguageUnit(
            node,
            ReturnStatement(expression))
