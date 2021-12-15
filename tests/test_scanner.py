import io
import os
from pathlib import Path
from typing import Optional

import pytest
from lark.lexer import Token

from interpreter.scanner.scanner import Grammar, Scanner, load_grammar, CandidatesNotFoundException, \
    AmbiguousMatchException


@pytest.fixture
def grammar() -> Grammar:
    with open(Path(os.getenv('PROJECT_ROOT')) / "grammar.txt") as f:
        return load_grammar(f)


@pytest.fixture
def root() -> Path:
    return Path(os.getenv('PROJECT_ROOT'))


def find_token(tokens, type_=None, value=None) -> Optional[Token]:
    for token in tokens:
        matches = True
        if type_ is not None:
            matches = type_ == token.type
        if value is not None:
            matches = value == token.value
        if matches:
            return token
    return None


def test_long_name(grammar: Grammar):
    s = 'x' * 260
    with io.StringIO(s) as f:
        with pytest.raises(Exception):
            list(Scanner(grammar).iter_tokens(f))


def test_positions(grammar: Grammar):
    s = 'c a int = 5'
    columns = [1, 3, 7, 9, 11]
    iter_columns = iter(columns)
    with io.StringIO(s) as f:
        for token in Scanner(grammar).iter_tokens(f):
            column = next(iter_columns)
            assert token.line == 1
            assert token.column == column


def test_multiline_positions(grammar: Grammar):
    s = """foo void () {
print("Hello world", hi)
}
"""
    expectations = {
        "hi": (2, 23),
        "foo": (1, 3),
        ",": (2, 20),
        "}": (3, 1)
    }
    with io.StringIO(s) as f:
        for token in Scanner(grammar).iter_tokens(f):
            if token.type != 'NEWLINE':
                x = expectations.get(token.value)
                if x is not None:
                    assert expectations[token.value] == (token.line, token.column), "Token: " + token.value


def test_comment_and_multiline_positions(grammar: Grammar):
    s = """# comment
c a int = 5
    """
    with io.StringIO(s) as f:
        for token in Scanner(grammar, ignore_comments=False).iter_tokens(f):
            if token.type == 'COMMENT':
                assert token.line == 1
                assert token.column == 9


def test_no_chars(grammar: Grammar):
    s = ''
    with io.StringIO(s) as f:
        assert len(list(Scanner(grammar).iter_tokens(f))) == 0


def test_dec_number(grammar: Grammar):
    s = 'c a int = 50330'
    with io.StringIO(s) as f:
        assert find_token(Scanner(grammar).iter_tokens(f),
                          'DEC_NUMBER', '50330') is not None


def test_float_number(grammar: Grammar):
    s = 'c a float = 15.783 # this is a float constant'
    with io.StringIO(s) as f:
        tokens = list(Scanner(grammar).iter_tokens(f))
        assert find_token(tokens, 'FLOAT_NUMBER').value == '15.783'


def test_operators_mix(grammar: Grammar):
    s = 'c a bool = a or 5 != 7 and 8 % 6 == 15'
    with io.StringIO(s) as f:
        tokens = list(Scanner(grammar).iter_tokens(f))
        assert find_token(tokens, None, 'or').type == 'OR'
        assert find_token(tokens, None, '!=').type == 'EQUALITY_OPERATOR'
        assert find_token(tokens, None, 'and').type == 'AND'
        assert find_token(tokens, None, '%').type == 'MULTIPLICATIVE_OPERATOR'
        assert find_token(tokens, None, '==').type == 'EQUALITY_OPERATOR'


def test_relative_location(grammar: Grammar):
    s = 'c some int = foo().bar().z'
    with io.StringIO(s) as f:
        tokens = list(Scanner(grammar).iter_tokens(f))
        c = 0
        for token in tokens:
            if token.type == 'DOT':
                c += 1
        assert c == 2


def test_assignment_and_operators(grammar: Grammar):
    s = 'value += 15\n' \
        'value / 5\n' \
        'value /= 5'
    with io.StringIO(s) as f:
        tokens = list(Scanner(grammar).iter_tokens(f))
        assert find_token(tokens, value='+=').type == 'ASSIGNMENT_AND_OPERATOR'
        assert find_token(tokens, value='/=').type == 'ASSIGNMENT_AND_OPERATOR'


def test_unsupported_chars(grammar: Grammar):
    s = '$$$$$$'
    with io.StringIO(s) as f:
        with pytest.raises(CandidatesNotFoundException):
            list(Scanner(grammar).iter_tokens(f))


def test_ambiguous_grammar(grammar: Grammar):
    gr_file = 'TERMINAL: "kk"\n' \
              'ANOTHER: /k.*/'
    s = 'kk'
    with io.StringIO(s) as f:
        with io.StringIO(gr_file) as gr:
            with pytest.raises(AmbiguousMatchException):
                list(Scanner(load_grammar(gr)).iter_tokens(f))


# noinspection PyTypeChecker
def test_name(grammar: Grammar):
    s = 'Hello'
    tokens = [Token('NAME', 'Hello')]
    iterator = iter(tokens)
    with io.StringIO(s) as f:
        for token in Scanner(grammar).iter_tokens(f):
            expected = next(iterator)
            assert token.type == expected.type
            assert token.value == expected.value
