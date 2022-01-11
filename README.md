# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own. It's a drill university project for the compilation
techniques course.

## About the language

The syntax of the language is a mixture of a python and some mainstream languages like kotlin or swift. It's a
statically typed general-purpose, programming language. It's made to perform simple operations on variables, call
functions and write small scripts.

See the example snippet [here](./test%20files/test_file_1.txt)

## Wiki and grammar

- On the [wiki pages](https://github.com/pochka15/Interpreter-for-custom-language/wiki/Basics) you can read about the
  language more deeply.
- Following this [link](./grammar.txt) you can see the whole grammar of the language written in a custom EBNF format.

## Prerequisites

- python3 version 3.8

```bash
# Install the virtual environment
python3 -m pip install --user virtualenv

# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Root project catalog
python3 -m pip install -r requirements.txt
```

## How to launch

"cd" to the folder (src/main.py) containing main.py and enter:

```bash
python3 main.py input.txt
```

## Functional requirements

- Frontend
    - build AST for the predefined EBNF grammar file
    - make it possible to write visitors for the AST
- Backend: Make it possible to read a text file then write the interpretation result to the standard output
- Errors
    - show the error message, containing the line of an error during the scanning (tokenizing) process

### What should be interpreted

1. Variable declaration (numbers, bool, literal constants)
2. Operations on variables: + - * /
3. Control flow (if expression, for, while loop)
4. Function call

## Non-functional requirements

- Portability
    - macOS, Windows, Linux platforms must be supported
- Is open sourced?
    - yes
- Maintainability, scalability
    - the project is not going to be supported in the future but the code must be readable and should follow the SOLID,
      and KISS principles
- How it should be run
    - it must be able to run the interpreter in the offline mode using the command line
- Performance
    - the frontend part of a language must take < 0.1 min. for the file containing < 1000 lines of code. The backend is
      executed by python, so the performance must be close to the python itself.
- Language
    - The interpreter must be written in python 3 without the usage of existing libraries that do the whole parsing
      process

## Interpretation

It's build an AST tree for the whole given input txt file. Then all the expressions are executed using python under the
hood. Functions can be declared anywhere in the file and there should be one **main()** entrypoint function which
returns void type.

Here's showed what happens during the interpretation process:

1. **Scanning**: take grammar and the input file, create a stream of tokens out of it
2. **Parsing**: build the AST for the stream of tokens
3. **Transformation**: pass the AST to the transformer which maps nodes to custom nodes like NodeWithLanguageUnit where
   language unit is a data structure representing some language rule like an assignment for example
4. **Semantic analysis**: for each node (going bottom-up) ensure that they can be interpreted correctly. Check if types
   are correct and so on
5. **Interpretation**: for each node (going top-down) execute statements and evaluate expressions

## Tests

The "pytest" library is used for the unit testing. The same time the interpreter is tested by analyzing some
pre-configured **correct** and **incorrect** code snippets.

The frontend part should be tested by comparing the actual and expected syntax trees for the predefined small code
snippets of different language structures.

## Scanner tests

Scanner is tested by matching the generated token sequence with an expected sequence

```python
def test_name(grammar: str):
    token = 'Hello'
    tokens = [Token('NAME', 'Hello')]
    iterator = iter(tokens)
    with io.StringIO(token) as f:
        for token in Scanner(grammar).iter_tokens(f):
            expected = next(iterator)
            assert token.type == expected.type
            assert token.value == expected.value
```

### Parser tests

Parser is tested by generating the AST trees and matching it with expected trees

```python
def test_disjunction(parser: RecursiveDescentParser):
    snippet = r"""
        test() bool { ret a or b }"""

    expected = Tree('start', ...)
    with io.StringIO(snippet) as f:
        result, message = compare_trees(expected, parser.parse(f))
        assert result, message
```

### Interpreter tests

To test the interpreter we use test files. There will be compared the output of the interpretation with the expected
values.
