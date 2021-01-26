from dataclasses import dataclass
from typing import List, Union, Optional, Any

from lark import Tree, Token


class TreeWithLanguageUnit(Tree):
    def __init__(self, tree: Tree, unit: Any):
        super().__init__(tree.data, tree.children, tree.meta)
        self.unit = unit


@dataclass
class TokenAndLanguageUnit:
    token: Token
    unit: Any

    def __repr__(self):
        return str(self.unit)


LanguageUnitContainer = Union[TreeWithLanguageUnit, TokenAndLanguageUnit]


@dataclass
class Identifier:
    name: str

    def __str__(self):
        return self.name


@dataclass
class VariableDeclaration:
    variable_name: TokenAndLanguageUnit
    type_name: Optional[TokenAndLanguageUnit]
    is_val: bool = True

    def __repr__(self):
        lst = [str(self.variable_name.unit)]
        if self.type_name is not None:
            lst.append(str(self.type_name.unit))
        lst.append("val" if self.is_val else "var")
        return " ".join(lst)


@dataclass
class Expression:
    disjunction: LanguageUnitContainer

    def __str__(self):
        return str(self.disjunction.unit)


@dataclass
class Assignment:
    left_expression: TreeWithLanguageUnit
    operator: TokenAndLanguageUnit
    right_expression: LanguageUnitContainer

    def __str__(self):
        return f"{str(self.left_expression.unit)} {str(self.operator.unit)} {str(self.right_expression.unit)}"


@dataclass
class IndexingSuffix:
    expression: LanguageUnitContainer

    def __str__(self):
        return "[" + str(self.expression.unit) + "]"


@dataclass
class FunctionCallArguments:
    expressions: List[LanguageUnitContainer]

    def __str__(self):
        return ", ".join(str(ex.unit) for ex in self.expressions)


@dataclass
class NavigationSuffix:
    nav_path: TokenAndLanguageUnit

    def __str__(self):
        return "." + str(self.nav_path.unit)


@dataclass
class AdditiveExpression:
    multiplicative_expression: LanguageUnitContainer
    additive_operators_with_multiplicative_expressions: List[LanguageUnitContainer]

    def __str__(self):
        return " ".join([str(self.multiplicative_expression.unit),
                         " ".join((str(exp.unit) for exp in
                                   self.additive_operators_with_multiplicative_expressions))])


@dataclass
class PostfixUnaryExpression:
    primary_expression: LanguageUnitContainer
    suffixes: List[LanguageUnitContainer]

    def __str__(self):
        return "".join((str(self.primary_expression),
                        *(str(suf.unit) for suf in self.suffixes)))


@dataclass
class DirectlyAssignableExpression:
    postfix_unary_expression: LanguageUnitContainer
    assignable_suffix: LanguageUnitContainer

    def __str__(self):
        return f"{self.postfix_unary_expression.unit}{self.assignable_suffix.unit}"


@dataclass
# TODO(@pochka15):
class FunctionDeclaration:
# function_declaration: NAME type_arguments? function_parameters VISIBILITY_MODIFIER? OVERRIDDEN? FUNCTION_RETURN_TYPE? "{" statements_block "}"
    name: str
    return_type: str


@dataclass
class CallSuffix:
    type_arguments: Optional[LanguageUnitContainer]
    function_call_arguments: LanguageUnitContainer

    def __str__(self):
        t = "<" + str(self.type_arguments) + ">" if self.type_arguments is not None else ""
        return t + "(" + str(self.function_call_arguments.unit) + ")"


@dataclass
class PrefixUnaryExpression:
    prefix_operators: List[TokenAndLanguageUnit]
    postfix_unary_expression: LanguageUnitContainer

    def __str__(self):
        return "".join(str(op.unit) for op in self.prefix_operators) + \
               str(self.postfix_unary_expression.unit)


@dataclass
class Disjunction:
    conjunctions: List[LanguageUnitContainer]

    def __str__(self):
        return " || ".join(str(con.unit) for con in self.conjunctions)


@dataclass
class Conjunction:
    equalities: List[LanguageUnitContainer]

    def __str__(self):
        return " && ".join(str(eq.unit) for eq in self.equalities)


@dataclass
class Equality:
    comparison: LanguageUnitContainer
    equality_operators_and_comparisons: List[LanguageUnitContainer]

    def __str__(self):
        return " ".join([str(self.comparison.unit),
                         *(str(ec.unit) for ec in self.equality_operators_and_comparisons)])


@dataclass
class Comparison:
    additive_expression: LanguageUnitContainer
    comparison_operators_and_additive_expressions: List[LanguageUnitContainer]

    def __str__(self):
        return str(self.additive_expression.unit) \
               + " ".join(str(ca.unit) for ca in self.comparison_operators_and_additive_expressions)


@dataclass()
class ImportWithoutFrom:
    as_names: List[LanguageUnitContainer]

    def __str__(self):
        return "import " + ", ".join(str(as_name.unit) for as_name in self.as_names)


@dataclass
class ImportWithFrom:
    from_path: LanguageUnitContainer
    import_targets: LanguageUnitContainer

    def __str__(self):
        return "from " + str(self.from_path.unit) + " import " + str(self.import_targets.unit)


@dataclass
class FromPath:
    relative_location: Optional[TokenAndLanguageUnit]
    path: List[TokenAndLanguageUnit]

    def __str__(self):
        beg = self.relative_location.unit if self.relative_location is not None else ""
        return beg + ".".join(str(p.unit) for p in self.path)


@dataclass
class ImportTargets:
    as_names: List[LanguageUnitContainer]

    def __str__(self):
        return ", ".join(str(name.unit) for name in self.as_names)


@dataclass
class AsName:
    name: TokenAndLanguageUnit
    alias: TokenAndLanguageUnit

    def __str__(self):
        return str(self.name.unit) + " as " + str(self.alias.unit)


@dataclass
class MultiplicativeExpression:
    prefix_unary_expression: LanguageUnitContainer
    multiplicative_operators_and_prefix_unary_expressions: List[LanguageUnitContainer]

    def __str__(self):
        return " ".join([str(self.prefix_unary_expression.unit),
                         *(str(el.unit) for el in self.multiplicative_operators_and_prefix_unary_expressions)])


@dataclass
class TypeArguments:
    comma_separated_types: List[LanguageUnitContainer]

    def __str__(self):
        return "<" + ", ".join(str(t.unit) for t in self.comma_separated_types) + ">"


@dataclass
class SimpleUserType:
    name: TokenAndLanguageUnit
    type_arguments: Optional[LanguageUnitContainer]

    def __str__(self):
        second_part = f"{str(self.type_arguments.unit)}" if self.type_arguments is not None else ""
        return str(self.name.unit) + second_part


@dataclass
class Type:
    simple_user_types: List[LanguageUnitContainer]
    is_parenthesized: bool

    def __str__(self):
        inner = ".".join(str(t.unit) for t in self.simple_user_types)
        if self.is_parenthesized:
            return "(" + inner + ")"
        return inner
