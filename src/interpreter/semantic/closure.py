from dataclasses import dataclass
from typing import Any, List, Dict, Union


class DefaultValue:
    """Class which is primarily made for the Symbol class"""
    pass


@dataclass
class Variable:
    name: str
    type: str
    identifier: int
    value: Any = DefaultValue
    is_const: bool = False


@dataclass
class Function:
    name: str
    return_type: str
    identifier: int
    params: List[Variable]


class Closure:
    name_to_symbol: Dict[str, Union[Variable, Function]]
    id = 0

    def __init__(self, parent=None):
        self.id = Closure.id
        Closure.id += 1
        self.name_to_symbol = {}
        self.parent = parent

    def __str__(self):
        return str(self.id) + str(self.name_to_symbol)

    def __setitem__(self, key, value):
        self.name_to_symbol[key] = value

    def __getitem__(self, item):
        return self.name_to_symbol[item]
