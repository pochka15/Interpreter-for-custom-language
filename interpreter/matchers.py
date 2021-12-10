from abc import ABC, abstractmethod
from re import Pattern
from typing import List


class Matcher(ABC):
    @abstractmethod
    def matches(self, s) -> bool: ...

    @property
    @abstractmethod
    def name(self):
        ...


class RegexMatcher(Matcher):

    @property
    def name(self):
        return self._name

    def __init__(self, pattern: Pattern, name):
        self._name = name
        self.pattern = pattern

    def matches(self, s):
        return self.pattern.fullmatch(s) is not None

    def __str__(self) -> str:
        return '/' + self.pattern.pattern + '/'


class StringMatcher(Matcher):

    @property
    def name(self):
        return self._name

    def __init__(self, name):
        self._name = name

    def matches(self, s: str):
        c = s.count('"')
        return s.startswith('"') and (c == 1 or (c == 2 and s.endswith('"')))

    def __str__(self) -> str:
        return f'Custom string matcher'


class AlternativeMatcher(Matcher):

    @property
    def name(self):
        return self._name

    def __init__(self, alternatives: List[str], name):
        self.alternatives = alternatives
        self._name = name

    def matches(self, s):
        for it in self.alternatives:
            if it == s:
                return True
        return False

    def __str__(self):
        return ' | '.join(self.alternatives)
