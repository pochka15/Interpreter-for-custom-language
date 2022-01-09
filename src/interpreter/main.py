from typing import Iterable

from lark import Lark, Tree
from lark.lexer import Token

from interpreter.code_snippet_generation import with_italic_comments, with_pre_tag, with_bold_keywords
from interpreter.interpretation import Interpreter
from interpreter.parser.parser import RecursiveDescentParser
from interpreter.scanner.scanner import Scanner
from interpreter.tree_transformer import TreeTransformer


def initialize_lark_from_file(relative_path_to_file: str) -> Lark:
    with open(relative_path_to_file) as grammar_file:
        return Lark(grammar_file, start='start', propagate_positions=True)


def iter_tokens(tree: Tree) -> Iterable[Token]:
    for t in tree.iter_subtrees_topdown():
        for child in t.children:
            if isinstance(child, Token):
                yield child


def make_pretty(snippet: str) -> str:
    return with_pre_tag(
        with_italic_comments(
            with_bold_keywords(snippet)))


def debug_tokens(tokens: Iterable[Token]):
    for token in tokens:
        if token.type != 'WS' and token.type != 'NEWLINE':
            print(token.value)


def main():
    with open('../../grammar.txt') as f:
        data = f.read()
    scanner = Scanner(data)
    parser = RecursiveDescentParser(scanner)
    with open("../../test files/test_file_2.txt") as f:
        tree = parser.parse(f)
        transformed = TreeTransformer().transform(tree)
        Interpreter().interpret(transformed)
        # print(transformed)
        print('Done')


if __name__ == "__main__":
    main()
    # copy(make_pretty("""
    # # Create a list
    # c numbers List = [1, 2, 3]
    # 
    # # Get element by index
    # c first_element int = numbers[0] # Indexation starts from 0
    # 
    # # Add element to the end
    # numbers.add(4)
    # 
    # c fourth_element = numbers[3]
    # """))
