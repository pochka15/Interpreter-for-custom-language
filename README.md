# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own.

## About the language

The language itself is like a mixture of Kotlin, Python and maybe some other languages that attracted me. It's a statically typed general-purpose, class-based, object-oriented language programming language.

## Language wiki and grammar

- On the wiki pages([link](https://github.com/pochka15/Interpreter-for-custom-language/wiki/Basics)) you can find how to use the language.
- In this [link](./grammar.lark) you can see the whole grammar of the language written in *Lark's* custom EBNF format.

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
- Show the error line, message when an error occurs while parsing.

## Non-functional requirements

- The interpreter must be written in python 3.
- The parsing time must take less than 2 seconds for any 1000 lines of code

## How it's tested

The "pytest" library is used for the unit testing. The same time the interpreter is tested by analyzing some pre-configured **correct** and **incorrect** code snippets.\

## Roadmap

1. Interpret created language.

### Finished tasks

From the newest to latest tasks:
 
- [x] Write the language wiki
- [x] Add the first version of grammar for assignment, function declarations and function calls

### Somewhere in a *LONG-LONG* future

1. Make some small helpful tools for the code editor like syntax highlighting, ...
