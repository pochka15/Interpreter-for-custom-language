from typing import Iterable

from lark import Lark, Tree
from lark.lexer import Token

from code_snippet_generation import with_bold_keywords, with_italic_comments, with_pre_tag
from interpretation.custom_interpreter import CustomInterpreter
from scanner.scanner import load_grammar, Scanner
from semantic.semantic_analyzer import SemanticAnalyzer
from tree_transformer import TreeTransformer


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


def prev_main():
    with open("../test files/test_file_1.txt", "r") as f:
        snippet = f.read()
    lark = initialize_lark_from_file('../grammar.lark')
    tree: Tree = TreeTransformer().transform(lark.parse(snippet))
    SemanticAnalyzer().visit(tree)
    CustomInterpreter().visit(tree)


def debug_tokens(tokens: Iterable[Token]):
    for token in tokens:
        if token.type != 'WS' and token.type != 'NEWLINE':
            print(token.value)


def main():
    with open('../grammar.txt') as f:
        grammar = load_grammar(f)
    debug_term_defs(grammar)
    scanner = Scanner(grammar)
    with open("../test files/test_file_1.txt", "r") as f:
        debug_tokens(scanner.iter_tokens(f))


def debug_term_defs(grammar):
    for matcher in grammar.terminal_matchers:
        print(matcher.name + ": " + str(matcher))


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
