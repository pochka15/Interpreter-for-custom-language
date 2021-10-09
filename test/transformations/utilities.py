import pyperclip
import pytest
from lark.lark import Lark, Tree

from main import initialize_lark_from_file
from tree_transformer import TreeTransformer


@pytest.fixture(scope="module")
def lark() -> Lark:
    return initialize_lark_from_file('../../grammar.lark')


def transformed(tree: Tree):
    return TreeTransformer().transform(tree)


def clip(tree: Tree):
    pyperclip.copy(str(tree))
