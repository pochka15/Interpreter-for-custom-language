# Custom language interpreter

## About the project

This is an interpreter for the language that was designed by my own. It's a drill university project for the compilation
techniques course.

## About the language

The syntax of the language is like a simplified python's syntax. It's a statically typed general-purpose, programming
language. It's made to perform simple operations on variables, call functions and write small scripts.

See the language example [here](./test%20files/test_file_1.txt)

## Language wiki and grammar

- On the [wiki pages](https://github.com/pochka15/Interpreter-for-custom-language/wiki/Basics) you can find the language
  structure.
- Following this [link](./grammar.txt) you can see the whole grammar of the language written in EBNF format.
- The whitespaces are ignored in the language except the newline. All the new expressions must start with a new line.

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
    
## Interpretation

It's build an AST tree for the whole given input txt file. Then all the expressions are executed using python under the
hood. Functions can be declared anywhere in the file and there should be one **main()** entrypoint function which
returns void type.

Here's showed what happens to a token during the interpretation process:

```txt
Token 
|> [transformer] => TransformationNode (e.x. Comparison or Expression)
|> [semanticAnalyzer] => SemanticNode (e.x. Callable)
|> Interpreter
```

## Tests

The "pytest" library is used for the unit testing. The same time the interpreter is tested by analyzing some
pre-configured **correct** and **incorrect** code snippets.

The frontend part should be tested by comparing the actual and expected syntax trees for the predefined small code
snippets of different language structures.

## Scanner tests

Scanner is tested by matching the generated token sequence with an expected sequence

```python
def test_comment_token():
    snippet = "c a int # this is some comment"
    assert list(Scanner().iter_tokens()) == [Name, Comment]
```

### Transformation tests

All the token transformations into the language units are tested by comparing the input snippet with the expected AST
nodes.

```python
def test_variable_declaration():
    snippet = "c a int = 1"
    tree = parse(snippet)
    node = find_node_by_name(tree, "variable_declaration")
    assert isinstance(node, VariableDeclaration)
    assert str(node) == "c a int"


def test_assignment():
    snippet = "c a int = 5"
    tree = parse(snippet)
    node = find_node_by_name(tree, "assignment")
    var_decl = extract(node, 'left_expression')
    assert (isinstance(var_decl, VariableDeclaration))
    assert str(extract(node, 'operator')) == '='
    assert str(extract(node, 'right_expression')) == '5'
```

### Parser tests

Parser is tested by generating the AST trees and matching it with expected trees

```python
def test_for_in_list(lark):
    snippet = r"""
    for v in [v1, v2, v3] {
        print(v)
    }
    """
    expected = Tree('start', [Tree('for_statement', [Token('NAME', 'v'), Tree('collection_literal', ...), ...])])
    actual = Parser().parse(snippet)
    result, message = compare_trees(expected, actual)
    assert result, message


def test_loop_fails_when_in_omitted():
    try:
        tree = Parser().parse(r"""
    for x [1, 2, 3] {
        print(x)
    }""")
    except Exception:
        pass
    else:
        pytest.fail("Exception must be raised here, there shouldn't be generated a tree:\n" + tree)
```

### Interpreter tests

To test the interpreter we use test files. There will be compared the output of the interpretation with the expected
values.

## Interfaces

**Scanner**

- iter_tokens(): Iterator[Token]\
  It matches input characters to the pair [value, terminal_name]

**Parser** (depends on Scanner)

- parse(scanner, start): Tree\
  It iterates through the tokens of a scanner and produces an abstract syntax tree.

**Visitor**

This is an interface for the 'Visitor' pattern to visit AST nodes

- visit(tree): Tree

**Transformer** (extends Visitor)

- transform(tree): Tree\
  Transformers visit each node of the tree (bottom-up), and run the appropriate method on it according to the node's
  data.

**Semantic analyzer** (extends Visitor)

This visitor is primarily made to run the semantic analysis and prepare the tree for the interpretation.

**Tree**

- data: str - the name of the rule or alias
- children: List[Tree] - list of matched sub-rules and terminals
- meta: Meta - a data class that contains: line, column, start_pos, end_line, end_column, end_pos
    - iter_subtrees(): Iterator[Tree] - botton-up iterator
    - iter_subtrees_topdown(): Iterator[Tree]

**Token**

- type
- start_pos
- value
- line
- column
- end_line
- end_column
- end_pos

**TransformationNode**

This is a base type for all the nodes after applying the transformer on tokens

**SemanticNode**

This is a base type for all the nodes after rugging the semantic analyzer