from typing import Optional, Iterator

from lark import Token

from interpreter.utils.custom_queue import CustomQueue


def match(token: Token, expected_type: str) -> bool:
    if token is None:
        return False
    return token.type == expected_type


class TokensController:
    def __init__(self):
        self.tokens = iter([])
        self.should_ignore_new_lines = True
        self.peeked_tokens = CustomQueue()
        self.cached_tokens = []

    def include_new_lines(self, func):
        prev = self.should_ignore_new_lines
        self.should_ignore_new_lines = False
        ret = func()
        self.should_ignore_new_lines = prev
        return ret

    def next(self) -> Optional[Token]:
        def inner_next():
            token = None
            if self.peeked_tokens.empty():
                try:
                    token = next(self.tokens)
                except StopIteration:
                    pass
            else:
                token = self.peeked_tokens.get(block=False)
            return token

        token = inner_next()
        if self.should_ignore_new_lines:
            while match(token, "NEWLINE"):
                token = self.next()
        if token is not None:
            self.cached_tokens.append(token)
        return token

    def peek(self) -> Optional[Token]:
        def inner_peek():
            if self.peeked_tokens.empty():
                token = self.next()
                self.peeked_tokens.put(token)
                return token
            else:
                return self.peeked_tokens.peek()

        if self.should_ignore_new_lines:
            if self.peeked_tokens.empty():
                self._skip_all_new_lines()
                return inner_peek()
            else:
                self.remove_new_lines_from_peeked()
                if self.peeked_tokens.empty():
                    return self.peek()
                else:
                    return inner_peek()
        else:
            return inner_peek()

    def reload(self, tokens: Iterator[Token]):
        self.tokens = tokens
        self.should_ignore_new_lines = True
        self.peeked_tokens = CustomQueue()
        self.cached_tokens = []

    # Ugly utility method for the should_ignore_new_lines()
    def _skip_all_new_lines(self):
        token = self.next()
        self.peeked_tokens.put(token)
        while match(token, "NEWLINE"):
            self.peeked_tokens.get()
            token = self.next()
            self.peeked_tokens.put(token)

    def remove_new_lines_from_peeked(self):
        token = self.peeked_tokens.peek()
        while match(token, "NEWLINE"):
            self.peeked_tokens.get()
            token = self.peeked_tokens.peek()
