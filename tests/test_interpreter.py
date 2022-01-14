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


def interpret(snippet: str, grammar: str):
    scanner = Scanner(grammar)
    parser = RecursiveDescentParser(scanner)
    interpreter = Interpreter(is_test=True)
    with io.StringIO(snippet) as f:
        return interpreter.interpret(
            TreeTransformer().transform(
                parser.parse(f)))


def test_print_works(grammar: str):
    snippet = r"""
        main() None {
          let a int = 10
          test_print(str(a))
        }"""
    outputs = interpret(snippet, grammar)
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
    outputs = interpret(snippet, grammar)
    assert outputs[0] == '1'


def test_str_concatenation(grammar: str):
    snippet = r"""
    main() None {
        test_print("Hello" + " " + "world")
    }    
    """
    outputs = interpret(snippet, grammar)
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
    outputs = interpret(snippet, grammar)
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
    outputs = interpret(snippet, grammar)
    assert outputs[0] == str(1 + 2 + 3 + 4)


# Execute additive expression.
# Expect correct result
def test_additive_expression(grammar: str):
    snippet = r"""
    main() None {
        test_print(str(1 + 2 - 3))
    }
    """
    outputs = interpret(snippet, grammar)
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
    outputs = interpret(snippet, grammar)
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
    outputs = interpret(snippet, grammar)
    assert outputs[0] == '2'


def test_collection_literal(grammar: str):
    snippet = r"""
       main() None {
           let elements List = [0, 1, 2]
           test_print(str(elements[0 + 2]))
       }
       """
    outputs = interpret(snippet, grammar)
    assert outputs[0] == '2'


def test_boolean_expression(grammar: str):
    snippet = r"""
       main() None {
           let condition1 bool = true
           let condition2 bool = false
           test_print(str(condition1))
           test_print(str(condition2))
       }
       """
    outputs = interpret(snippet, grammar)
    assert outputs[0] == 'True'
    assert outputs[1] == 'False'


def test_for_statement(grammar: str):
    snippet = r"""
       main() None {
           for x in ["Hello", "world"] {
                test_print(x)
           }
       }
       """
    outputs = interpret(snippet, grammar)
    assert outputs[0] == 'Hello'
    assert outputs[1] == 'world'


def test_for_statement_with_no_cycles(grammar: str):
    snippet = r"""
       main() None {
           for x in [] {
                test_print(x)
           }
       }
       """
    outputs = interpret(snippet, grammar)
    assert len(outputs) == 0


def test_multiplication(grammar: str):
    snippet = r"""
       main() None {
           test_print(str(2 * 3))
       }
       """
    outputs = interpret(snippet, grammar)
    assert outputs[0] == '6'


def test_reminder_operator(grammar: str):
    snippet = r"""
       main() None {
           test_print(str(4 % 2))
       }
       """
    outputs = interpret(snippet, grammar)
    assert outputs[0] == '0'
