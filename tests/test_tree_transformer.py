import io
import os
from pathlib import Path

import pytest

from interpreter.language_units import *
from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.tree_transformer import TreeTransformer


def find_node(tree, tree_data):
    for found in tree.iter_subtrees():
        if found.data == tree_data:
            return found


@pytest.fixture(scope="module")
def parser():
    with open(Path(os.getenv('PROJECT_ROOT')) / 'grammar.txt') as f:
        return RecursiveDescentParser(Scanner(f.read()))


@pytest.fixture(scope="module")
def tree_1(parser):
    snippet = """
    print() void {
        ret
    }"""
    with io.StringIO(snippet) as f:
        return TreeTransformer().transform(parser.parse(f))


@pytest.fixture(scope="module")
def tree_2(parser):
    snippet = """
    print() void {
        let result1 bool = b or (c and d)
        let result2 bool = a == b + 2 + (-1)
    }"""
    with io.StringIO(snippet) as f:
        tree = parser.parse(f)
        transformed = TreeTransformer().transform(tree)
        return transformed


def test_return_statement(tree_1: Tree):
    node = find_node(tree_1, "return_statement")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, ReturnStatement)
    assert unit.expression is None


def test_disjunction(tree_2: Tree):
    node = find_node(tree_2, "disjunction")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, Disjunction)
    assert str(unit) == 'b or (c and d)'


def test_conjunction(tree_2: Tree):
    node = find_node(tree_2, "conjunction")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, Conjunction)
    assert str(unit) == 'c and d'


def test_equality(tree_2: Tree):
    node = find_node(tree_2, "equality")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, Equality)
    assert str(unit) == 'a == b + 2 + (-1)'


def test_additive_expression(tree_2: Tree):
    node = find_node(tree_2, "additive_expression")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, AdditiveExpression)
    assert str(unit) == 'b + 2 + (-1)'


def test_prefix_unary_expression(tree_2: Tree):
    node = find_node(tree_2, "prefix_unary_expression")
    assert node is not None, "node wasn't found"
    unit = node.unit
    assert isinstance(unit, PrefixUnaryExpression)
    assert str(unit) == '-1'
