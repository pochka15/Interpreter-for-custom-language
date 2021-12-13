from lark import Transformer, v_args

from interpreter.language_units import *


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming

@v_args(tree=True)
class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)

    # TODO(@pochka15): should I use a default token?
    # __default_token__ = wrapped_token()

    def start(self, node: Tree):
        return TreeWithLanguageUnit(node, Start(node.children))
