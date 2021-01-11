import re

keywords = ("private", "public", "true", "false", "import", "from", "val",
            "var", "abstract", "overridden", "return", "continue",
            "break", "else", "class", "interface", "while", "for", "this", "in")


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


def with_pre_tag(in_str: str) -> str:
    return "<pre>" + in_str + "</pre>"
