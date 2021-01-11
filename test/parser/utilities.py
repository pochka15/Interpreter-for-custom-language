from typing import Iterable

import pyperclip
import pytest
from lark import Token
from lark.lark import Lark, Tree

from main import initialized_lark_from_file


@pytest.fixture(scope="module")
def lark() -> Lark:
    return initialized_lark_from_file('../../grammar.lark')


def clip(tree: Tree):
    pyperclip.copy(str(tree))


def tokens(tree: Tree) -> Iterable[Token]:
    for t in tree.iter_subtrees_topdown():
        for child in t.children:
            if isinstance(child, Token):
                yield child


def compare_trees(expected_tree: Tree, actual_tree: Tree):
    if not (expected_tree == actual_tree):
        for t1, t2 in zip(expected_tree.iter_subtrees_topdown(), actual_tree.iter_subtrees_topdown()):
            if not t1.data == t2.data:
                pytest.fail(f'"{t1.data}" is not equal to the "{t2.data}"' + f"""
Expected tree:
{expected_tree.pretty()}
------
Actual tree:
{actual_tree.pretty()}
    """, False)

        # When the data is equal compare all the tokens
        for actual_token, expected_token in zip(tokens(actual_tree), tokens(expected_tree)):
            if not actual_token == expected_token:
                pytest.fail(f"Expected token: {expected_token.__repr__()}\nActual token: {actual_token.__repr__()}\n"
                            f"Actual tree:\n {str(actual_tree)}", False)

        # Default fail
        pytest.fail("Trees are different!\n"
                    f"Expected tree:\n{expected_tree}\nActual tree:\n{actual_tree}", False)
