from dataclasses import dataclass
from typing import List, Any, Optional

from semantic.scopes import DescribedUnitContainer


def generate_name_of_callable(callable_name, formal_parameter_types: List[str]):
    return callable_name + "(" + ", ".join(
        str(param) for param in formal_parameter_types) + ")"


def generate_name_of_operator_func(operator_name, left_expr_type: str, right_expr_type: str):
    return operator_name + f"({left_expr_type}, {right_expr_type})"


@dataclass
class UnitDescription:
    name: str

    def __str__(self):
        return self.name


@dataclass
class UnitWithTypeDs(UnitDescription):
    type: str

    def __str__(self):
        return f"{self.name} {self.type}"


@dataclass
class CallableDs(UnitWithTypeDs):
    formal_parameters: List[UnitWithTypeDs]
    return_type: str
    bound_function: Any

    def __str__(self):
        return self.name + "(" + ", ".join(
            str(param) for param in self.formal_parameters) + ")" + " -> " + self.return_type


@dataclass
class IdentifierDs(UnitWithTypeDs):
    bound_declaration: DescribedUnitContainer


@dataclass
class VariableDeclarationDs(UnitWithTypeDs):
    bound_definition: Optional[DescribedUnitContainer] = None


@dataclass
class AdditiveExpressionDs(UnitWithTypeDs):
    bound_function: Optional[Any]


@dataclass
class OperatorDs(UnitDescription):
    left_expr_type: str
    right_expr_type: str
    return_type: str
    bound_function: Optional[Any] = None

    def __str__(self):
        return f"{self.name}({self.left_expr_type}, {self.right_expr_type}) -> {self.return_type}"
