from typing import Tuple

import pyperclip
import pytest
from lark.lark import Lark, Tree

from main import initialized_lark_from_file, fetched_tokens


@pytest.fixture(scope="module")
def lark() -> Lark:
    return initialized_lark_from_file('../../grammar.lark')


def clip(tree: Tree):
    pyperclip.copy(str(tree))


def trees_comparison_result(expected_tree: Tree, actual_tree: Tree) -> Tuple[bool, str]:
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
        for actual_token, expected_token in zip(fetched_tokens(actual_tree), fetched_tokens(expected_tree)):
            if not actual_token == expected_token:
                return (False, f"Expected token: {expected_token.__repr__()}\nActual token: {actual_token.__repr__()}\n"
                               f"Actual tree:\n {str(actual_tree)}")

        # Default fail
        return (False, "Trees are different!\n"
                       f"Expected tree:\n{expected_tree}\nActual tree:\n{actual_tree}")
    return True, ""
