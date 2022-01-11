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
    snippet = r"""
        main() None {
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


# Declare function. Call it form main().
# Expect correct result returned
def test_function_declaration(grammar: str):
    snippet = r"""
    someValue() int {
        ret 1
    }
    
    main() None {
        test_print(str(someValue()))
    }
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == '1'


def test_str_concatenation(grammar: str):
    snippet = r"""
    main() None {
        test_print("Hello" + " " + "world")
    }    
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == "Hello world"


# Pass arguments.
# Expect all arguments got executed
def test_function_arguments(grammar: str):
    snippet = r"""
    format(name str, age int) str {
        ret "Name: " + name + ", age: " + str(age) 
    }
    
    main() None {
        test_print(format("Bob", 10))
    }    
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == 'Name: Bob, age: 10'


# Make nested function calls
# Expect expression executes correctly
def test_nested_function_calls(grammar: str):
    snippet = r"""
    sum(one int, another int) int {
        ret one + another 
    }
    
    main() None {
        test_print(str(sum(sum(sum(1, 2), 3), 4)))
    }    
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == str(1 + 2 + 3 + 4)


# Execute additive expression.
# Expect correct result
def test_additive_expression(grammar: str):
    snippet = r"""
    main() None {
        test_print(str(1 + 2 - 3))
    }
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == '0'


# Execute multiple statements.
# Expect correct result
def test_multiple_statements(grammar: str):
    snippet = r"""
    someString() str {
        ret "someString"
    }
    
    main() None {
        test_print(str(1 + 2))
        test_print(someString())
    }
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == '3'
    assert outputs[1] == 'someString'


# Reassign variable
# Expect variable has a correct value
def test_reassignment(grammar: str):
    snippet = r"""
    main() None {
        var x int = 1
        x = 2
        test_print(str(x))
    }
    """
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        outputs = interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))

    assert outputs[0] == '2'