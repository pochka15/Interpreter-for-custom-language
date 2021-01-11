from typing import List

from lark import Transformer, Tree


class TreeTransformer(Transformer):
    STRING = str
    NAME = str
    VAL = str
    VAR = str

    def __init__(self):
        super().__init__(visit_tokens=True)

    # def type(self, children: List[Tree]):
    #     return Tree('type', [str(children[0])])

    def statements_block(self, children: List[Tree]):
        children.append(Tree('block_end', []))
        return Tree('statements_block', children)
