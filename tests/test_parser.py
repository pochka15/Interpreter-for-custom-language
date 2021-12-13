import io
import os
from pathlib import Path

import pytest
from lark import Tree

from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.main import load_grammar
from tests.utilities import compare_trees


@pytest.fixture(scope="module")
def parser():
    with open(Path(os.getenv('PROJECT_ROOT')) / 'grammar.txt') as f:
        grammar = load_grammar(f)
        return RecursiveDescentParser(Scanner(grammar))


# noinspection PyTypeChecker
def test_function_declaration_without_type_parameters(parser: RecursiveDescentParser):
    snippet = r"""
    print() void {
        return
    }"""

    expected_tree = Tree()
    with io.StringIO(snippet) as f:
        compare_trees(expected_tree, parser.parse(f))
