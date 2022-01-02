import io
import os
from pathlib import Path

import pytest
from lark import Tree, Token

from interpreter.main import load_grammar
from interpreter.parser.parser import RecursiveDescentParser, UnexpectedToken, PrimaryExpressionException
from interpreter.scanner.scanner import Scanner
from tests.utilities import compare_trees


@pytest.fixture(scope="function")
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
                                    Tree('statements_block', [Tree('return_statement', [])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_disjunction(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a or b }"""

    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block', [Tree('return_statement',
                                                                   [Tree('disjunction', [Token('NAME', 'a'),
                                                                                         Token('NAME', 'b')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_conjunction(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a and b and k }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('conjunction',
                                                                                             [Token('NAME', 'a'),
                                                                                              Token('NAME', 'b'),
                                                                                              Token('NAME',
                                                                                                    'k')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_equality(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a == b }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block',
                                         [Tree('return_statement', [Tree('equality', [Token('NAME', 'a'),
                                                                                      Token('EQUALITY_OPERATOR', '=='),
                                                                                      Token('NAME', 'b')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_additive_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a + b - k }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('additive_expression',
                                                                                             [Token('NAME', 'a'),
                                                                                              Token('ADDITIVE_OPERATOR',
                                                                                                    '+'),
                                                                                              Token('NAME', 'b'),
                                                                                              Token('ADDITIVE_OPERATOR',
                                                                                                    '-'),
                                                                                              Token('NAME',
                                                                                                    'k')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_add_multiply(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a + b * k }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('additive_expression',
                                                                                             [Token('NAME', 'a'),
                                                                                              Token('ADDITIVE_OPERATOR',
                                                                                                    '+'),
                                                                                              Tree(
                                                                                                  'multiplicative_expression',
                                                                                                  [Token('NAME', 'b'),
                                                                                                   Token(
                                                                                                       'MULTIPLICATIVE_OPERATOR',
                                                                                                       '*'),
                                                                                                   Token('NAME',
                                                                                                         'k')])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_prefix_unary_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret -a }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'bool'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('prefix_unary_expression',
                                                                                             [Token('ADDITIVE_OPERATOR',
                                                                                                    '-'),
                                                                                              Token('NAME',
                                                                                                    'a')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_assignment(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
            let x int = a + b
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('assignment', [Tree('variable_declaration',
                                                                                       [Token('LET', 'let'),
                                                                                        Token('NAME', 'x'), Tree('type',
                                                                                                                 [Token(
                                                                                                                     'NAME',
                                                                                                                     'int')])]),
                                                                                  Token('ASSIGNMENT_OPERATOR', '='),
                                                                                  Tree('additive_expression',
                                                                                       [Token('NAME', 'a'),
                                                                                        Token('ADDITIVE_OPERATOR', '+'),
                                                                                        Token('NAME', 'b')])])])])])

    with io.StringIO(snippet) as f:
        # res, msg = compare_trees(expected, parser.parse(f))
        # assert res, msg
        print(parser.parse(f))


# noinspection PyTypeChecker
def test_multiple_assignments(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
            let x int = n1 + n2
            let y int = n3 + n4
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('assignment', [Tree('variable_declaration',
                                                                                       [Token('LET', 'let'),
                                                                                        Token('NAME', 'x'), Tree('type',
                                                                                                                 [Token(
                                                                                                                     'NAME',
                                                                                                                     'int')])]),
                                                                                  Token('ASSIGNMENT_OPERATOR', '='),
                                                                                  Tree('additive_expression',
                                                                                       [Token('NAME', 'n1'),
                                                                                        Token('ADDITIVE_OPERATOR', '+'),
                                                                                        Token('NAME', 'n2')])]),
                                                              Tree('assignment', [Tree('variable_declaration',
                                                                                       [Token('LET', 'let'),
                                                                                        Token('NAME', 'y'), Tree('type',
                                                                                                                 [Token(
                                                                                                                     'NAME',
                                                                                                                     'int')])]),
                                                                                  Token('ASSIGNMENT_OPERATOR', '='),
                                                                                  Tree('additive_expression',
                                                                                       [Token('NAME', 'n3'),
                                                                                        Token('ADDITIVE_OPERATOR', '+'),
                                                                                        Token('NAME', 'n4')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_multiple_line_additive_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
            let x int = n1 +
                      n2
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('assignment', [Tree('variable_declaration',
                                                                                       [Token('LET', 'let'),
                                                                                        Token('NAME', 'x'), Tree('type',
                                                                                                                 [Token(
                                                                                                                     'NAME',
                                                                                                                     'int')])]),
                                                                                  Token('ASSIGNMENT_OPERATOR', '='),
                                                                                  Tree('additive_expression',
                                                                                       [Token('NAME', 'n1'),
                                                                                        Token('ADDITIVE_OPERATOR', '+'),
                                                                                        Token('NAME', 'n2')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_one_function_parameter(parser: RecursiveDescentParser):
    snippet = r"""
        test(a int) int {
            ret a
        }"""
    expected = Tree('start', [Tree('function_declaration', [Token('NAME', 'test'), Tree('function_parameters', [
        Tree('function_parameter', [Token('NAME', 'a'), Tree('type', [Token('NAME', 'int')])])]), Token('NAME', 'int'),
                                                            Tree('statements_block',
                                                                 [Tree('return_statement', [Token('NAME', 'a')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_three_function_parameters(parser: RecursiveDescentParser):
    snippet = r"""
        test(age int, isMale bool, name str) int {
            ret a
        }"""
    expected = Tree('start', [Tree('function_declaration', [Token('NAME', 'test'), Tree('function_parameters', [
        Tree('function_parameter', [Token('NAME', 'age'), Tree('type', [Token('NAME', 'int')])]),
        Tree('function_parameter', [Token('NAME', 'isMale'), Tree('type', [Token('NAME', 'bool')])]),
        Tree('function_parameter', [Token('NAME', 'name'), Tree('type', [Token('NAME', 'str')])])]),
                                                            Token('NAME', 'int'),
                                                            Tree('statements_block',
                                                                 [Tree('return_statement', [Token('NAME', 'a')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_zero_function_parameters(parser: RecursiveDescentParser):
    snippet = r"""
        test() void {
            ret
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('return_statement', [])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_postfix_unary_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { ret a(b, d) }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block',
                                         [Tree('return_statement', [Tree('postfix_unary_expression', [
                                             Token('NAME', 'a'),
                                             Tree('call_suffix', [Token('NAME',
                                                                        'b'),
                                                                  Token('NAME',
                                                                        'd')])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_indexing_suffix(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret a[0] }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [Tree('return_statement',
                                                                   [Tree('postfix_unary_expression',
                                                                         [Token('NAME', 'a'),
                                                                          Tree('indexing_suffix',
                                                                               [Token('DEC_NUMBER',
                                                                                      '0')])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_navigation_and_call_suffix(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret a.foo() }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [
                                        Tree('return_statement', [Tree('postfix_unary_expression', [Token('NAME', 'a'),
                                                                                                    Tree(
                                                                                                        'navigation_suffix',
                                                                                                        [Token('NAME',
                                                                                                               'foo')]),
                                                                                                    Tree('call_suffix',
                                                                                                         [])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_parenthesized_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret (a) }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [Tree('return_statement', [Token('NAME', 'a')])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_parenthesized_expression2(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret ((a + b)) }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('additive_expression',
                                                                                             [Token('NAME', 'a'),
                                                                                              Token('ADDITIVE_OPERATOR',
                                                                                                    '+'),
                                                                                              Token('NAME',
                                                                                                    'b')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_parenthesized_expression3(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret (k / (a + b)) }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [
                                        Tree('return_statement', [Tree('multiplicative_expression', [Token('NAME', 'k'),
                                                                                                     Token(
                                                                                                         'MULTIPLICATIVE_OPERATOR',
                                                                                                         '/'), Tree(
                                                'additive_expression',
                                                [Token('NAME', 'a'), Token('ADDITIVE_OPERATOR', '+'),
                                                 Token('NAME', 'b')])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_collection_literal(parser: RecursiveDescentParser):
    snippet = r"""
        test() List { ret [1,2,3] }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'List'),
                                    Tree('statements_block', [Tree('return_statement', [Tree('collection_literal',
                                                                                             [Token('DEC_NUMBER', '1'),
                                                                                              Token('DEC_NUMBER', '2'),
                                                                                              Token('DEC_NUMBER',
                                                                                                    '3')])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_if_as_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() int { ret if a>b {ret a} else {ret b} }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'int'),
                                    Tree('statements_block', [Tree('return_statement', [
                                        Tree('if_expression', [Tree('comparison',
                                                                    [Token('NAME', 'a'),
                                                                     Token('COMPARISON_OPERATOR',
                                                                           '>'),
                                                                     Token('NAME', 'b')]),
                                                               Tree('statements_block', [Tree('return_statement',
                                                                                              [Token('NAME', 'a')])]),
                                                               Tree('else_expression', [
                                                                   Tree('statements_block', [Tree('return_statement', [
                                                                       Token('NAME',
                                                                             'b')])])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_if_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { if (a) { b() } }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('if_expression', [Token('NAME', 'a'),
                                                                                     Tree('statements_block', [Tree(
                                                                                         'postfix_unary_expression',
                                                                                         [Token('NAME', 'b'),
                                                                                          Tree('call_suffix',
                                                                                               [])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_else_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { if a {b()} else {k()} }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('if_expression', [Token('NAME', 'a'),
                                                                                     Tree('statements_block', [Tree(
                                                                                         'postfix_unary_expression',
                                                                                         [Token('NAME', 'b'),
                                                                                          Tree('call_suffix', [])])]),
                                                                                     Tree('else_expression', [
                                                                                         Tree('statements_block', [Tree(
                                                                                             'postfix_unary_expression',
                                                                                             [Token('NAME', 'k'),
                                                                                              Tree('call_suffix',
                                                                                                   [])])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_elseif_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
          if a {
            print(a)
          } elif b {
            print(b)
          }
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('if_expression',
                                                                   [Token('NAME', 'a'),
                                                                    Tree('statements_block', [Tree(
                                                                        'postfix_unary_expression',
                                                                        [Token('NAME', 'print'),
                                                                         Tree('call_suffix',
                                                                              [Token('NAME', 'a')])])]),
                                                                    Tree('elseif_expression',
                                                                         [Token('NAME', 'b'),
                                                                          Tree('statements_block', [
                                                                              Tree(
                                                                                  'postfix_unary_expression',
                                                                                  [Token('NAME',
                                                                                         'print'),
                                                                                   Tree('call_suffix',
                                                                                        [Token(
                                                                                            'NAME',
                                                                                            'b')])])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_elseif_with_else_expression(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
          if a {
            print(a)
          } elif b {
            print(b)
          } else {
            print(k)
          }
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [
                                        Tree('if_expression', [Token('NAME', 'a'),
                                                               Tree('statements_block', [Tree(
                                                                   'postfix_unary_expression',
                                                                   [Token('NAME', 'print'),
                                                                    Tree('call_suffix', [Token('NAME',
                                                                                               'a')])])]),
                                                               Tree('elseif_expression',
                                                                    [Token('NAME', 'b'),
                                                                     Tree('statements_block', [
                                                                         Tree(
                                                                             'postfix_unary_expression',
                                                                             [Token('NAME',
                                                                                    'print'),
                                                                              Tree('call_suffix',
                                                                                   [Token(
                                                                                       'NAME',
                                                                                       'b')])])])]),
                                                               Tree('else_expression', [
                                                                   Tree('statements_block', [Tree(
                                                                       'postfix_unary_expression',
                                                                       [Token('NAME', 'print'),
                                                                        Tree('call_suffix', [Token('NAME',
                                                                                                   'k')])])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_for_stmt(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
            for i in range(10) { print(i) }
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('for_statement', [Token('NAME', 'i'),
                                                                                     Tree('postfix_unary_expression',
                                                                                          [Token('NAME', 'range'),
                                                                                           Tree('call_suffix',
                                                                                                [Token('DEC_NUMBER',
                                                                                                       '10')])]),
                                                                                     Tree('statements_block', [Tree(
                                                                                         'postfix_unary_expression',
                                                                                         [Token('NAME', 'print'),
                                                                                          Tree('call_suffix',
                                                                                               [Token('NAME',
                                                                                                      'i')])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_wile_stmt(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { 
            while ok() { print(i) }
        }"""
    expected = Tree('start', [Tree('function_declaration',
                                   [Token('NAME', 'test'), Tree('function_parameters', []), Token('NAME', 'void'),
                                    Tree('statements_block', [Tree('while_statement', [Tree('postfix_unary_expression',
                                                                                            [Token('NAME', 'ok'),
                                                                                             Tree('call_suffix', [])]),
                                                                                       Tree('statements_block', [Tree(
                                                                                           'postfix_unary_expression',
                                                                                           [Token('NAME', 'print'),
                                                                                            Tree('call_suffix',
                                                                                                 [Token('NAME',
                                                                                                        'i')])])])])])])])

    with io.StringIO(snippet) as f:
        res, msg = compare_trees(expected, parser.parse(f))
        assert res, msg


# noinspection PyTypeChecker
def test_func_without_return_type_exceptional(parser: RecursiveDescentParser):
    snippet = r"""
        test() { ret a or b }"""

    with io.StringIO(snippet) as f:
        with pytest.raises(UnexpectedToken):
            parser.parse(f)


def test_for_without_in_exceptional(parser: RecursiveDescentParser):
    snippet = r"""
        test() {
          for i range(10) { print(i) }
        }"""

    with io.StringIO(snippet) as f:
        with pytest.raises(UnexpectedToken):
            parser.parse(f)


def test_type_with_comma_instead_of_dot_exceptional(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { ret a,b }"""

    with io.StringIO(snippet) as f:
        with pytest.raises(PrimaryExpressionException):
            parser.parse(f)


# noinspection PyTypeChecker
def test_not_matched_parentheses_exceptionalp(parser: RecursiveDescentParser):
    snippet = r"""
        test() void { ret (a(b)(k }"""

    with io.StringIO(snippet) as f:
        with pytest.raises(UnexpectedToken):
            parser.parse(f)
