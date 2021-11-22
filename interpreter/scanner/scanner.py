import itertools
import re
from dataclasses import dataclass
from typing import List, Any, Iterator, Tuple, TextIO

from matchers import RegexMatcher, Matcher, AlternativeMatcher, StringMatcher

MAX_TOKEN_LEN = 255
DEFAULT_TERMINAL_ENTRIES = (("LEFT_PAREN", '"("'),
                            ("RIGHT_PAREN", '")"'),
                            ("LEFT_CURLY_BR", '"{"'),
                            ("RIGHT_CURLY_BR", '"}"'),
                            ("LEFT_SQR_BR", '"["'),
                            ("RIGHT_SQR_BR", '"]"'),
                            ("COMMA", '","'))


@dataclass
class Grammar:
    rule_defs: List[Any]
    terminal_matchers: List[Matcher]


@dataclass
class Token:
    type: str = ''
    value: str = ''
    line: int = 0
    column: int = 0

    def __str__(self) -> str:
        return super().__str__()


def iter_terminal_entries(file: TextIO) -> Tuple:
    """
    Iterate through the terminal grammar entries. A grammar entry is a left and right part delimited by ':' char

    :returns: a tuple containing the left and right parts of an entry.
    """

    yield from DEFAULT_TERMINAL_ENTRIES
    for line in file.readlines():
        match = re.match(r"(^[A-Z_]*):(.*)", line)

        if match is None:
            continue

        groups = match.groups()
        if len(groups) == 2:
            left, right = groups
            yield left.strip(), right.strip()


def build_matcher(name, s: str):
    # hacky string matcher
    if name == 'STRING':
        return StringMatcher(name)

    # regex matcher
    if s.startswith('/'):
        pos = s.rfind('/')
        # regex is between the first slash and the last slash
        regex = s[1:pos]
        # flags go after the last slash
        flags = s[pos:]
        has_ignore = 'i' in flags
        pattern = re.compile(regex, re.RegexFlag.IGNORECASE if has_ignore else 0)
        return RegexMatcher(pattern, name)

    # alternative matcher
    else:
        # TODO(@pochka15): fix, it doesn't exclude the "ab|cd" case. when alternative is inside str
        entries = [it.strip() for it in s.split('|')]
        if len(entries) == 0:
            entries = [s.strip()]
        strings = filter(is_quoted, entries)
        return AlternativeMatcher(list(between_first_and_last(x) for x in strings), name)


def is_quoted(it):
    return it.startswith('"') and it.endswith('"')


def between_first_and_last(x):
    return x[1: len(x) - 1]


def load_grammar(file: TextIO) -> Grammar:
    matchers = [(build_matcher(name, definition))
                for name, definition
                in iter_terminal_entries(file)]
    return Grammar([], matchers)


@dataclass
class Cursor:
    line: int = 1
    column: int = 0

    def clone(self):
        return Cursor(self.line, self.column)


def exists_matcher(matchers, name):
    for matcher in matchers:
        if matcher.name == name:
            return True
    return False


class CandidatesNotFoundException(Exception):
    pass


class AmbiguousMatchException(Exception):
    pass


class Scanner:

    def __init__(self, grammar: Grammar, ignore_ws: bool = True):
        self.ignore_ws = ignore_ws
        self.grammar = grammar
        self.end_cursor = Cursor()
        self.prev_cursor = Cursor()
        self.start_cursor = Cursor()
        self.cur_text = ''
        self.last_matched_text = ''
        self.chars = []
        self.no_more_chars = False

    def iter_tokens(self, file: TextIO) -> Iterator[Token]:
        """
        Iterate tokens
        :param file: snippet file
        :return: tokens iterator
        """

        def inner():
            candidates = self.collect_candidates()
            if len(candidates) == 0 and self.cur_text != '':
                raise CandidatesNotFoundException("Couldn't find candidates for the: " + self.cur_text)

            if len(candidates) == 1:
                candidate = candidates[0]
                if self.no_more_chars:
                    self.prev_cursor = self.end_cursor

                yield Token(candidate.name,
                            self.last_matched_text,
                            self.prev_cursor.line,
                            self.prev_cursor.column)

                if not self.no_more_chars:
                    self.start_cursor = self.prev_cursor
                    self.cur_text = self.cur_text[-1]
                    yield from inner()

            elif len(candidates) > 1:
                raise AmbiguousMatchException(
                    "Ambiguous match for: " + self.cur_text +
                    "\ncandidates: " + ', '.join([c.name for c in candidates]))

        self.chars = itertools.chain.from_iterable(file)
        self.move()
        if not self.no_more_chars:
            for x in inner():
                if self.ignore_ws:
                    if not x.type == 'WS':
                        yield x
                else:
                    yield x

    def move(self):
        try:
            char = next(self.chars)
        except StopIteration:
            self.no_more_chars = True
            return
        self.prev_cursor = self.end_cursor.clone()
        is_new_line = re.match(r'[\r\n]', char)
        if is_new_line:
            self.end_cursor.line += 1
            self.end_cursor.column = 0
            self.cur_text += char
        else:
            self.cur_text += char
            self.end_cursor.column += 1
        if len(self.cur_text) > MAX_TOKEN_LEN:
            raise Exception("Current scanned value is too large, couldn't create token for the: " + self.cur_text)

    def collect_candidates(self, collected: List[Matcher] = None) -> List[Matcher]:
        if collected is None:
            collected = []
        matchers = list(
            filter(lambda x: x.matches(self.cur_text),
                   self.grammar.terminal_matchers))
        if len(matchers) == 0:
            return collected
        old = list(filter(lambda x: x.matches(self.cur_text), collected))
        new = list(filter(lambda x: not exists_matcher(collected, x.name), matchers))
        self.last_matched_text = str(self.cur_text)
        self.move()
        if self.no_more_chars:
            return old + new
        return self.collect_candidates(old + new)

    def match(self):
        for name, matcher in self.grammar.terminal_matchers:
            if matcher.matches(self.cur_text):
                t = Token(type=name, value=self.cur_text)
                self.cur_text = ''
                return t
