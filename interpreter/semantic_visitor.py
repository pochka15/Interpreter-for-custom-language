from lark import Visitor, Tree

from semantic.scopes import Scope
from semantic.symbols import Symbol, SymbolType
from language_units import VariableDeclaration


def is_val(tree: Tree):
    return True if tree.children[0] == 'val' else False


class SemanticVisitor(Visitor):
    def __init__(self, scopes):
        super().__init__()
        self.scopes = scopes
        self.current_scope = Scope(None)

    def block_end(self, _: Tree):
        print("Block end, leaving the current scope: " + str(self.current_scope.id))
        self.current_scope = self.current_scope.parent_scope
        print("Current scope: " + str(self.current_scope.id))

    def statements_block(self, _: Tree):
        s = Scope(self.current_scope)
        self.current_scope = s
        self.scopes[s.id] = s

    def start(self, _: Tree):
        self.scopes[self.current_scope.id] = self.current_scope

    def assignment(self, tree: Tree):
        # left_subtree, right_subtree = tree.children
        # left_name = left_subtree.data
        # what_type = "TODO(@pochka15): type"
        # self.current_scope[left_name] = Symbol(left_name, SymbolType(what_type))
        pass

    def call_suffix(self, tree: Tree):
        # function_call_arguments_tree = tree.children[0]
        pass

    def variable_declaration(self, tree: Tree):
        variable_name_tree, variable_type_tree, val_or_var_tree = tree.children
        decl = VariableDeclaration(variable_name_tree.children[0],
                                   SymbolType(variable_type_tree.children[0]),
                                   is_val(val_or_var_tree))
        self.current_scope.symbols[decl.variable_name] = Symbol(decl.variable_name, decl.variable_type)
