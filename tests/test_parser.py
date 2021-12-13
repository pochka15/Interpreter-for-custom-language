import io
import os
from pathlib import Path

import pytest
from lark import Tree, Token

from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.main import load_grammar
from tests.utilities import compare_trees, clip


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


# noinspection PyTypeChecker
def test_disjunction(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a or b }"""

    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('return_statement',
                                         [Tree('disjunction', [Token('NAME', 'a'), Token('NAME', 'b')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_conjunction(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a and b and c }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('return_statement', [Tree('conjunction',
                                                                   [Token('NAME', 'a'), Token('NAME', 'b'),
                                                                    Token('CONST', 'c')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_equality(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a == b }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('return_statement', [Tree('equality', [Token('NAME', 'a'),
                                                                                Token('EQUALITY_OPERATOR', '=='),
                                                                                Token('NAME', 'b')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# TODO(@pochka15):
# noinspection PyTypeChecker
def test_additive_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a + b - c }"""

    with io.StringIO(snippet) as f:
        tree = parser.parse(f)
        print(tree.pretty())
        clip(tree)


# TODO(@pochka15):
# noinspection PyTypeChecker
def test_add_multiply(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a + b * c }"""

    with io.StringIO(snippet) as f:
        tree = parser.parse(f)
        print(tree.pretty())
        clip(tree)


# TODO(@pochka15):
# noinspection PyTypeChecker
def test_prefix_unary_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret -a }"""

    with io.StringIO(snippet) as f:
        tree = parser.parse(f)
        print(tree.pretty())
        clip(tree)


# TODO(@pochka15):
def test_multiple_statements(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { 
            x = a + b
            y = c + d
        }"""

    with io.StringIO(snippet) as f:
        tree = parser.parse(f)
        print(tree.pretty())
        clip(tree)

# TODO(@pochka15): test function parameters