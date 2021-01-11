from lark import Lark

from code_snippet_generation import with_bold_keywords, with_italic_comments, with_this_keyword_in_bold, with_pre_tag
from semantic_visitor import SemanticVisitor
from tree_transformer import TreeTransformer


def initialized_lark_from_file(relative_path_to_file: str) -> Lark:
    with open(relative_path_to_file) as grammar_file:
        return Lark(grammar_file, start='start')


def pretty(snippet: str) -> str:
    return with_pre_tag(
        with_this_keyword_in_bold(
            with_italic_comments(
                with_bold_keywords(snippet))))


def print_scopes(scopes):
    for scope_id, scope in scopes.items():
        print("Scope " + str(scope_id) + ":")
        print(scope.symbols)


def main():
    snippet = r"""
a int val = 5
b int val = 6
c int val = a + b
print(c)
"""
    lark = initialized_lark_from_file('../grammar.lark')
    lark_tree = lark.parse(snippet)
    scopes = {}
    transformed_tree = TreeTransformer().transform(lark_tree)
    SemanticVisitor(scopes).visit_topdown(transformed_tree)

    print(snippet)
    print(lark_tree.pretty())
    print("---\nAfter transformation:")
    print(transformed_tree.pretty())
    print_scopes(scopes)


if __name__ == "__main__":
    main()
