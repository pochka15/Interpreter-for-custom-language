# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own. It's a drill university project for the compilation techniques course.

## About the language

The syntax of the language is like a mixture of Kotlin, Python. It's a statically typed general-purpose, programming language. It's made to perform simple operations on variables. Call functions and so on.

## Language wiki and grammar

- On the ([wiki pages](https://github.com/pochka15/Interpreter-for-custom-language/wiki/Basics)) you can find how to use the language.
- In this [link](./grammar.lark) you can see the whole grammar of the language written in *Lark's* custom EBNF format.

## Prerequisites

- python3 _(todo: which version, mine is Python 3.8.9)_

```bash
# Install the virtual environment
python3 -m pip install --user virtualenv

# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# root project catalog
python3 -m pip install -r requirements.txt
```

## How to launch

"cd" to the folder (src/main.py) containing main.py and enter:

```bash
python3 main.py input.txt
```

## Used libraries

- "pytest" for testing

## Functional requirements

- Interpret the designed language.
- Show the error line, message when an error occurs while parsing.

## Non-functional requirements

- The interpreter must be written in python 3.
- The parsing time must take less than 2 seconds for any 1000 lines of code

## Tests

- TODO(@pochka15): write what will be tested and how

The "pytest" library is used for the unit testing. The same time the interpreter is tested by analyzing some pre-configured **correct** and **incorrect** code snippets.

## What must be interpreted

1. Variable declaration (numbers, bool, literal constants)
2. Operations on variables: + - * /
3. Control flow (if expression, for, while loop)
4. Function call
