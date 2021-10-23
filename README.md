# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own. It's a drill university project for the compilation
techniques course.

## About the language

The syntax of the language is like a simplified python's syntax. It's a statically typed general-purpose, programming
language. It's made to perform simple operations on variables, call functions and write small scripts.

## Language wiki and grammar

- On the [wiki pages](https://github.com/pochka15/Interpreter-for-custom-language/wiki/Basics) you can find the language
  structure.
- Following this [link](./grammar.lark) you can see the whole grammar of the language written in *Lark's* custom EBNF
  format.

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

- Make it possible to read a text file then write the interpretation result to the standard output
- Frontend
    - build AST for the predefined EBNF grammar file
    - make it possible to write visitors for the AST
- Errors
    - show the error message, containing the line of an error
    - stop interpreter when the there occurs an error during the parsing or semantic analysis

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

## Tests

The "pytest" library is used for the unit testing. The same time the interpreter is tested by analyzing some
pre-configured **correct** and **incorrect** code snippets.

The frontend part should be tested by comparing the actual and expected syntax trees for the predefined small code
snippets of different language structures.
