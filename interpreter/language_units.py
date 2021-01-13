from dataclasses import dataclass
from typing import List, Union

from lark import Tree


class TreeWithLanguageUnit(Tree):
    def __init__(self, tree: Tree, language_unit):
        super().__init__(tree.data, tree.children, tree.meta)
        self.language_unit = language_unit


class TokenWithLanguageUnit:
    def __init__(self, token, language_unit):
        self.token = token
        self.language_unit = language_unit

    def __repr__(self):
        return str(self.language_unit)


LanguageUnitContainer = Union[TreeWithLanguageUnit, TokenWithLanguageUnit]


@dataclass
class VariableDeclaration:
    variable_name: TokenWithLanguageUnit
    type_name: TokenWithLanguageUnit
    is_val: TokenWithLanguageUnit

    def __repr__(self):
        s0 = str(self.variable_name.language_unit)
        s1 = str(self.type_name.language_unit) if self.type_name is not None else ""
        s2 = "val" if self.is_val else "var"
        return " ".join([s0, s1, s2])


@dataclass
class Expression:
    # TODO(@pochka15): edit
    simple_literal: TokenWithLanguageUnit

    def __str__(self):
        return str(self.simple_literal.language_unit)


@dataclass
class Assignment:
    left_expression: TreeWithLanguageUnit
    operator: TokenWithLanguageUnit
    right_expression: LanguageUnitContainer

    def __str__(self):
        return f"{str(self.left_expression.language_unit)} {str(self.operator.language_unit)} {str(self.right_expression.language_unit)}"


@dataclass
class IndexingSuffix:
    expression: LanguageUnitContainer

    def __str__(self):
        return "[" + str(self.expression.language_unit) + "]"


@dataclass
class FunctionCallArguments:
    expressions: List[LanguageUnitContainer]

    def __str__(self):
        return ", ".join(str((ex.language_unit for ex in self.expressions)))


@dataclass
class NavigationSuffix:
    nav_path: TokenWithLanguageUnit

    def __str__(self):
        return "." + str(self.nav_path.language_unit)


@dataclass
class AdditiveExpression:
    left_name: TokenWithLanguageUnit
    operator: TokenWithLanguageUnit
    right_name: TokenWithLanguageUnit

    def __str__(self):
        return f"{str(self.left_name.language_unit)} " \
               f"{str(self.operator.language_unit)} " \
               f"{str(self.right_name.language_unit)}"


@dataclass
class DirectlyAssignableExpression:
    postfix_unary_expression: LanguageUnitContainer
    assignable_suffix: LanguageUnitContainer

    def __str__(self):
        return f"{self.postfix_unary_expression.language_unit}{self.assignable_suffix.language_unit}"


@dataclass
class PrefixUnaryExpression:
    prefix_operators: List[TokenWithLanguageUnit]
    postfix_unary_expression: LanguageUnitContainer

    def __str__(self):
        return "".join(str(op.language_unit) for op in self.prefix_operators) + str(
            self.postfix_unary_expression.language_unit)
