import re

import pyperclip
from lark import Lark


def parse():
    with open('../grammar.lark') as g, \
            open('../test files/test_file_1.txt') as f:
        print(Lark(g.read(), start='start').parse(f.read()).pretty())


def with_italic_comments(in_str: str) -> str:
    pat = re.compile(r"#.*")
    search_result = pat.search(in_str)
    if search_result is not None:
        start_ind = search_result.start()
        end_ind = search_result.end()
        found_match = search_result.group()

        before = in_str[0: start_ind]
        mid = "<i>" + found_match + "</i>"
        after = with_italic_comments(in_str[end_ind: len(in_str)])
        return before + mid + after
    return in_str


def with_pre(in_str: str) -> str:
    return "<pre>" + in_str + "</pre>"


keywords = ("val", "var", "return", "class", "interface", "abstract", "overridden", "this",
            "break", "continue", "in", "private", "public", "protected", "elif", "else")


def with_bold_keywords(in_str: str) -> str:
    pat = re.compile(r"\W(" + '|'.join(keywords) + r")\W")
    search_result = pat.search(in_str)
    if search_result is not None:
        start_ind = search_result.start(1)
        end_ind = search_result.end(1)
        found_keyword = search_result.group(1)

        before = in_str[0: start_ind]
        mid = "<b>" + found_keyword + "</b>"
        after = with_bold_keywords(in_str[end_ind: len(in_str)])
        return before + mid + after
    return in_str


def with_this_keyword_in_bold(in_str: str) -> str:
    pat = re.compile(r"\W(this)\.")
    search_result = pat.search(in_str)
    if search_result is not None:
        start_ind = search_result.start(1)
        end_ind = search_result.end(1)
        found_keyword = search_result.group(1)

        before = in_str[0: start_ind]
        mid = "<b>" + found_keyword + "</b>"
        after = with_this_keyword_in_bold(in_str[end_ind: len(in_str)])
        return before + mid + after
    return in_str


def tmp():
    code = r"""
    names List<str> val = ["Rob", "Bob", "Ann"] 

    # It's the same as
    names List<str> val = new(["Rob", "Bob", "Ann"])
    """
    res = with_pre(
        with_this_keyword_in_bold(
            with_italic_comments(
                with_bold_keywords(code))))
    print(res)
    pyperclip.copy(res)


if __name__ == "__main__":
    parse()