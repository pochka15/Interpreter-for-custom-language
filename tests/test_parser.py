import io
import os
from pathlib import Path

import pytest
from lark import Tree, Token

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
def test_empty_return(parser: RecursiveDescentParser):
    snippet = r"""
    print() void {
        ret
    }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'print'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('return_expression', [])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg
