import io
import os
from pathlib import Path

import pytest

from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.semantic_analyzer import SemanticAnalyzer, ReassignException, TypeMismatchException
from interpreter.tree_transformer import TreeTransformer


@pytest.fixture
def grammar():
    with open(Path(os.getenv('PROJECT_ROOT')) / "grammar.txt") as f:
        return f.read()


@pytest.fixture
def root() -> Path:
    return Path(os.getenv('PROJECT_ROOT'))


def analyze(snippet: str, grammar: str):
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    with io.StringIO(snippet) as f:
        SemanticAnalyzer().analyze(
            TreeTransformer().transform(
                parser.parse(f)))


def test_variable_declaration(grammar: str):
    snippet = r"""
        main() None {
          let a int = 10
        }"""
    analyze(snippet, grammar)


def test_assignment_expect_type_mismatch_int_str(grammar: str):
    snippet = r"""
            main() None {
              let a int = "Hello"
            }"""
    with pytest.raises(TypeMismatchException):
        analyze(snippet, grammar)


def test_assignment_expect_type_mismatch_int_float(grammar: str):
    snippet = r"""
            main() None {
              let a int = 1.3
            }"""
    with pytest.raises(TypeMismatchException):
        analyze(snippet, grammar)


def test_constant_assignment_expect_reassign_exception(grammar: str):
    snippet = r"""
            main() None {
              let a int = 1
              a = 2
            }"""
    with pytest.raises(ReassignException):
        analyze(snippet, grammar)


def test_reassignment(grammar: str):
    snippet = r"""
            main() None {
              var a int = 1
              a = 2
            }"""
    analyze(snippet, grammar)


def test_if_expression_type_mismatch(grammar: str):
    snippet = r"""
            main() None {
              let ok bool = true
              let a int = if ok { ret true } else { ret false}
            }"""
    with pytest.raises(TypeMismatchException):
        analyze(snippet, grammar)


def test_collection_literal(grammar: str):
    snippet = r"""
            main() None {
              let elements List = [1, 2]
              let a int = elements[0]
            }"""
    analyze(snippet, grammar)


def test_collection_literal_type_mismatch(grammar: str):
    snippet = r"""
            main() None {
              let elements List = [1, 2]
              let a bool = elements[0]
            }"""
    with pytest.raises(TypeMismatchException):
        analyze(snippet, grammar)


def test_empty_collection_initialization(grammar: str):
    snippet = r"""
            main() None {
              let elements List = []
            }"""
    analyze(snippet, grammar)
