import re
from itertools import chain
from typing import Iterator, Optional

from tokens import Token, TokenType


class Production:
    def __init__(self, production_as_string: str) -> None:
        self.left_side, self.right_side = production_as_string.split(" -> ")

    def __repr__(self) -> str:
        return f"{self.left_side} -> {self.right_side}"


configured_productions = (
    Production('S -> DecDigit Add'),
    Production('Add -> + DecDigit'),
)

token_regexes_and_token_type = {
    r"\d": TokenType.DecDigit,
    "+": TokenType.ADD,
}


def matched_single_char_token(single_char: str) -> Optional[Token]:
    for reg, tok_type in token_regexes_and_token_type.items():
        if re.search(reg, single_char):
            return Token(tok_type, single_char)
    return None


def tokens_from_string(txt: str) -> Iterator[Token]:
    """Generate tokens from the text. It's a draft version of lexer"""
    for char in txt:
        if (t := matched_single_char_token(char)) is not None:
            yield t
        else:
            break


# TODO(@pochka15): how to set type to the configured_productions
def productions_from(non_terminal_symbol) -> Iterator[Production]:
    for p in configured_productions:
        if p.left_side == non_terminal_symbol:
            yield p


def non_terminals(symbols_sequence):
    # TODO(@pochka15): edit
    # for symbol in symbols_sequence:
    #     if symbol == 'S':
    #         yield symbol
    yield "S"

def recursive_derivations(non_terminal_symbol: str, tokens: Iterator[Token]):
    """
    Return all the derivations that were made starting from the given non_non_terminal_symbol.

    This is a draft version of parser.
    """
    try:
        next_token = next(tokens)
    except StopIteration:
        pass
    else:
        for p in productions_from(non_terminal_symbol):
            # TODO(@pochka15): if the production can be applied then go on
            lists_of_derivations = [recursive_derivations(non_terminal, tokens)
                                    for non_terminal
                                    in non_terminals(p.right_side)]
            return chain([p], *lists_of_derivations)
    return []


if __name__ == "__main__":
    input = "5 + 6"
    print(input)
    for derivation in recursive_derivations('S', tokens_from_string(input)):
        print(derivation)