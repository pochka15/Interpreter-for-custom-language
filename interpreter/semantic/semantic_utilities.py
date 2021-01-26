from typing import List

from lark.tree import Meta

from language_units import TreeWithLanguageUnit, LanguageUnitContainer, TokenAndLanguageUnit
from semantic.scopes import Scope, DescribedUnitContainer
from semantic.unit_descriptions import UnitWithTypeDs


def extracted_meta(container: LanguageUnitContainer):
    if isinstance(container, TreeWithLanguageUnit):
        return container.meta.line, container.meta.column
    if isinstance(container, TokenAndLanguageUnit):
        return container.token.line, container.token.column
    raise Exception("Container is of incorrect type: " + str(container))


def check_formal_actual_parameters_match(formal_parameters: List[UnitWithTypeDs],
                                         actual_parameters: List[DescribedUnitContainer]):
    """
    Check if the formal parameters of the function call arguments match the actual_parameters (called arguments)
    passed by user
    :param formal_parameters: list of described units
    :param actual_parameters: list of expressions nodes containing units described units
    """
    for formal, actual in zip(formal_parameters, actual_parameters):
        line, column = extracted_meta(actual)
        actual_type = actual.unit.description.type
        # TODO(@pochka15): test
        assert formal.type == actual_type, \
            f"In line [{line}:{column}]: type '{actual_type}' doesn't match the formal parameter type '{formal.type}'"


def raise_declaration_is_not_found(declaration_name, token):
    line, column = extracted_meta(token)
    raise Exception(f"In line [{line}:{column}]: {str(token.unit)}\n"
                    f"Declaration '{declaration_name}' is not found")


def check_type_exists(type_name: str, scope: Scope, node_containing_type: DescribedUnitContainer):
    builtin_types = ['int', 'bool', 'float', 'str']
    for t in builtin_types:
        if t == type_name:
            return
    found_type = scope.find_declaration(type_name)
    if found_type is None:
        line, column = extracted_meta(node_containing_type)
        raise Exception(f"In line [{line}:{column}]: {str(node_containing_type.unit)}\n"
                        f"'{type_name}' type is not found")


def check_declaration_doesnt_exist(name: str, scope: Scope, node_containing_declaration: DescribedUnitContainer):
    found_declaration = scope.find_declaration(name)
    if found_declaration is not None:
        line, column = extracted_meta(node_containing_declaration)
        raise Exception(f"In line [{line}:{column}]: {str(node_containing_declaration.unit)}\n"
                        f"'{name}' has already been declared")
