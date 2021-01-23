from typing import List

from lark import Visitor, Tree

from semantic.scopes import Scope


def is_val(string: str):
    return True if string == 'val' else False


class SemanticVisitor(Visitor):
    def __init__(self, scopes: List[Scope]):
        super().__init__()
        self.scopes = scopes
        self.current_scope = Scope(None)

    # TODO(@pochka15): block_end now is a token
    def block_end(self, _: Tree):
        self.current_scope = self.current_scope.parent_scope

    def statements_block(self, _: Tree):
        new_scope = Scope(self.current_scope)
        self.current_scope = new_scope
        self.scopes.append(new_scope)

    def start(self, _: Tree):
        self.scopes.append(self.current_scope)

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
        print("In semantics variable decl:")
        print(*tree.children)
