from semantic.symbols import SymbolType, Symbol


class VariableDeclaration():
    def __init__(self, variable_name: str, variable_type: SymbolType, is_val: bool = True):
        self.variable_name = variable_name
        self.variable_type = variable_type
        self.is_val = is_val

    def __str__(self):
        return self.variable_name + " " + \
               self.variable_type.name + " " + \
               "val" if self.is_val else "var"
