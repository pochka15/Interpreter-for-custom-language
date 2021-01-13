from dataclasses import dataclass


@dataclass
class SymbolType:
    name: str

    def __str__(self):
        return self.name


class Symbol:
    def __init__(self, name: str, sym_type: SymbolType):
        self.sym_type = sym_type
        self.name = name

# class DirectlyAssignableExpression(Symbol):
#     def __init__(self, name: str, sym_type: SymbolType):
#         super().__init__(name, sym_type)
