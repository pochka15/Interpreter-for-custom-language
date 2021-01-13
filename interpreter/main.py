from typing import Iterable

from lark import Lark, Tree
from lark.lexer import Token

from code_snippet_generation import with_bold_keywords, with_italic_comments, with_this_keyword_in_bold, with_pre_tag
from language_units import TreeWithLanguageUnit
from tree_transformer import TreeTransformer


def initialized_lark_from_file(relative_path_to_file: str) -> Lark:
    with open(relative_path_to_file) as grammar_file:
        return Lark(grammar_file, start='start', propagate_positions=True)


def fetched_tokens(tree: Tree) -> Iterable[Token]:
    for t in tree.iter_subtrees_topdown():
        for child in t.children:
            if isinstance(child, Token):
                yield child


def pretty(snippet: str) -> str:
    return with_pre_tag(
        with_this_keyword_in_bold(
            with_italic_comments(
                with_bold_keywords(snippet))))


def main():
    snippet = r"""
a int val = 1
b int val = 2
c int val = a + b
"""

    lark = initialized_lark_from_file('../grammar.lark')
    parsed_tree = lark.parse(snippet)
    transformed_tree = TreeTransformer().transform(parsed_tree)

    print(transformed_tree)
    print(transformed_tree.pretty())
    for tree in transformed_tree.children:
        if not tree.meta.empty and isinstance(tree, TreeWithLanguageUnit):
            print("line: " + str(tree.meta.end_line))
            print("  k" + str(tree.language_unit))


if __name__ == "__main__":
    main()
