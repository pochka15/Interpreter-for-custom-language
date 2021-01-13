class Scope:
    id = 0

    def __init__(self, parent_scope=None):
        self.id = Scope.id
        Scope.id += 1
        self.symbols = {}
        self.parent_scope = parent_scope

    def __hash__(self):
        return id

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return f"Scope {str(self.id)}:\n{str(self.symbols)}"

    def __setitem__(self, key, value):
        self.symbols[key] = value

    def __getitem__(self, item):
        return self.symbols[item]
