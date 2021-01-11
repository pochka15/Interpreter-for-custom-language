from dataclasses import dataclass


@dataclass
class SymbolType:
    name: str


@dataclass
class Symbol:
    name: str
    type: SymbolType
