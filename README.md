# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own.

## About the language

The language itself is like a mixture of Kotlin, Python, Elm and maybe some other languages that attracted me. It's a statically typed general-purpose, class-based, object-oriented language programming language.

## Basic syntax

See [this link](./Basic%20syntax.md).

## Grammar

See [this link](./grammar.lark).

## How to launch

**Prerequisites:** *TODO for future*

"cd" to the folder (src/main.py) containing main.py and enter:

```bash
python main.py input.txt
```

## Used libraries

- "lark" for parsing
- "pytest" for testing

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

## Roadmap

1. Create EBNF grammar for the examples given in the Basic syntax. **Don't create syntax for classes yet**
   1. Test it.

2. Interpret created grammar.
3. Create EBNF grammar for the classes.
4. Interpret grammar for classes.

### Finished tasks

- [x] Add the first version of grammar for assignment, function declarations and function calls

### Somewhere in a *LONG-LONG* future

1. Make some small helpful tools for the code editor like syntax highlighting, ...
