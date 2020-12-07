import pyperclip
from lark import Lark

from code_snippet_generation import with_bold_keywords, with_italic_comments, with_this_keyword_in_bold, with_pre_tag


def print_parsed(text_to_parse: str):
    print(lark.parse(text_to_parse).pretty())


def tmp():
    code = r"""
    names List<str> val = ["Rob", "Bob", "Ann"] 

    # It's the same as
    names List<str> val = new(["Rob", "Bob", "Ann"])
    """
    res = with_pre_tag(
        with_this_keyword_in_bold(
            with_italic_comments(
                with_bold_keywords(code))))
    print(res)
    pyperclip.copy(res)


def initialized_lark_from_file(relative_path_to_file):
    with open(relative_path_to_file) as grammar_file:
        return Lark(grammar_file, start='start')


if __name__ == "__main__":
    lark = initialized_lark_from_file("../grammar.lark")
    snippet = r"""
for x in rng:
    x = 1
    y = "hello"
    """

    print_parsed(snippet)
