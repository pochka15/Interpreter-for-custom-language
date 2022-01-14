from dataclasses import dataclass
from typing import List, Dict, Union

from interpreter.language_units import UnitType


@dataclass
class Variable:
    name: str
    type: UnitType
    is_bound: bool = False
    is_const: bool = False


@dataclass
class Function:
    name: str
    return_type: UnitType
    params: List[Variable]


ClosureItem = Union[Variable, Function]


class Closure:
    name_to_item: Dict[str, ClosureItem]
    id = 0

    def __init__(self, parent=None):
        self.id = Closure.id
        Closure.id += 1
        self.name_to_item = {}
        self.parent: Closure = parent

    def __str__(self):
        return str(self.id) + str(self.name_to_item)

    def __setitem__(self, key, value):
        self.name_to_item[key] = value

    def __getitem__(self, item):
        return self.name_to_item.get(item, None)

    def lookup(self, item) -> ClosureItem:
        x = self.name_to_item.get(item, None)
        if x is None and self.parent is not None:
            return self.parent.lookup(item)
        return x
