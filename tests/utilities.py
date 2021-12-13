from typing import Tuple, Iterable

import pyperclip
from lark import Token
from lark.lark import Tree

from interpreter.tree_transformer import TreeTransformer


def transformed(tree: Tree):
    return TreeTransformer().transform(tree)


def clip(tree: Tree):
    pyperclip.copy(str(tree))


def compare_trees(expected_tree: Tree, actual_tree: Tree) -> Tuple[bool, str]:
    if not (expected_tree == actual_tree):
        for t1, t2 in zip(expected_tree.iter_subtrees_topdown(), actual_tree.iter_subtrees_topdown()):
            if not t1.data == t2.data:
                return (False, f'"{t1.data}" is not equal to the "{t2.data}"' + f"""
Expected tree:
{expected_tree.pretty()}
------
Actual tree:
{actual_tree.pretty()}
    """)

        # When the data is equal compare all the tokens
        for actual_token, expected_token in zip(iter_tokens(actual_tree), iter_tokens(expected_tree)):
            if not actual_token == expected_token:
                return (False, f"Expected token: {expected_token.__repr__()}\nActual token: {actual_token.__repr__()}\n"
                               f"Actual tree:\n {str(actual_tree)}")

        # Default fail
        return (False, "Trees are different!\n"
                       f"Expected tree:\n{expected_tree}\nActual tree:\n{actual_tree}")
    return True, ""


def iter_tokens(tree: Tree) -> Iterable[Token]:
    for t in tree.iter_subtrees_topdown():
        for child in t.children:
            if isinstance(child, Token):
                yield child
