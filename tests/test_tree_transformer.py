import io
import os
from pathlib import Path

import pytest

from interpreter.main import load_grammar
from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.tree_transformer import TreeTransformer
from interpreter.language_units import *


def find_node(tree, tree_data):
    for found in tree.iter_subtrees():
        if found.data == tree_data:
            return found


@pytest.fixture(scope="module")
def parser():
    with open(Path(os.getenv('PROJECT_ROOT')) / 'grammar.txt') as f:
        grammar = load_grammar(f)
        return RecursiveDescentParser(Scanner(grammar))


@pytest.fixture(scope="module")
def tree_1(parser):
    snippet = """
    print() void {
        ret
    }"""
    with io.StringIO(snippet) as f:
        return TreeTransformer().transform(parser.parse(f))


def test_return_statement(tree_1: Tree):
    node = find_node(tree_1, "return_statement")
    unit = node.unit
    assert node is not None, "node wasn't found"
    assert isinstance(unit, ReturnStatement)
    assert unit.expression is None
