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
a ((Hmm<Kek, Lol<Inner1, Inner2>>.What<The, Hell>)) val = 5
"""

    lark = initialized_lark_from_file('../grammar.lark')
    parsed_tree = lark.parse(snippet)
    print(parsed_tree.pretty())
    transformed_tree = TreeTransformer().transform(parsed_tree)
    assert isinstance(transformed_tree, Tree)

    print(transformed_tree.pretty())

    for tree in transformed_tree.iter_subtrees_topdown():
        if not tree.meta.empty and isinstance(tree, TreeWithLanguageUnit):
            print(tree.unit.__class__)
            print("line:", tree.meta.end_line)
            print(tree.unit, '\n')


if __name__ == "__main__":
    main()
