from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    MULT = auto()
    MOD = auto()
    DIV = auto()
    ADD = auto()
    SUB = auto()
    DecDigit = auto()


@dataclass
class Token:
    type: TokenType
    attribute_value: str
