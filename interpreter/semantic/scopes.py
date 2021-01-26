from dataclasses import dataclass
from typing import Optional, Dict, Union, Any

from lark import Tree, Token


@dataclass
class DescribedUnit:
    description: Any


@dataclass
class TreeWithDescribedUnit:
    tree: Tree
    unit: Union[DescribedUnit, Any]


@dataclass
class TokenAndDescribedUnit:
    token: Token
    unit: Union[Any, DescribedUnit]


DescribedUnitContainer = Union[TreeWithDescribedUnit, TokenAndDescribedUnit]


class Scope:
    _id = 0

    def __init__(self, parent_scope=None):
        self.id = Scope._id
        Scope._id += 1
        self.declarations: Dict[str, DescribedUnitContainer] = {}
        self.enclosing_scope = parent_scope

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return "Scope " + str(self.id) + ":\n" + '\n'.join(declaration for declaration in self.declarations)

    def put(self, node: DescribedUnitContainer):
        self.declarations[node.unit.description.name] = node

    def find_declared_node(self, declaration_name, current_scope_only=False) -> Optional[DescribedUnitContainer]:
        found = self.declarations.get(declaration_name)
        if found is not None:
            return found

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.find_declared_node(declaration_name)
