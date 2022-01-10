import io
import os
from pathlib import Path

import pytest

from interpreter.interpretation import Interpreter
from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.tree_transformer import TreeTransformer


@pytest.fixture
def grammar():
    with open(Path(os.getenv('PROJECT_ROOT')) / "grammar.txt") as f:
        return f.read()


@pytest.fixture
def root() -> Path:
    return Path(os.getenv('PROJECT_ROOT'))


def test_print_works(grammar: str):
    snippet = """
        main() void {
          let a int = 10
          test_print(str(a))
        }"""
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    with io.StringIO(snippet) as f:
        outputs = Interpreter(is_test=True).interpret(
            TreeTransformer().transform(
                parser.parse(f)))
        assert outputs[0] == '10'
