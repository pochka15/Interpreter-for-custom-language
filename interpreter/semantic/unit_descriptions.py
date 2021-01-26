from dataclasses import dataclass
from typing import List


@dataclass
class UnitDescription:
    name: str


@dataclass
class UnitWithTypeDs(UnitDescription):
    type: str


@dataclass
class CallableDs(UnitDescription):
    formal_parameters: List[UnitWithTypeDs]
    return_type: str
