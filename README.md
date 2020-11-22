# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own.

## About the language

The language itself is like a mixture of Kotlin, Python, Elm and maybe some other languages that attracted me. It's a statically typed general-purpose, class-based, object-oriented language programming language.

## Basic syntax

See [this link](./Basic%20syntax.md).

## Grammar

See [this link](./Language%20grammar.md).

## How to launch

**Prerequisites:** *TODO for future*

"cd" to the folder (src/main.py) containing main.py and enter:

```bash
python main.py input.txt
```

## Functional requirements

- Interpret the designed language.
- Show the error line when an error occurs while parsing.
- Show the error message when an error occurs.

## Non-functional requirements

- The interpreter must be written in python 3.
- The parsing time must take less than 2 seconds for 1000 lines of code 

## How it's tested

It's used "pytest" library for the unit testing. The same time the interpreter is tested by analyzing some pre-configured **correct** and **incorrect** code snippets.\
*TODO(@pochka15): think about how different phases will be tested*
