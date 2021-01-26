from typing import List, Union, Any

from language_units import TreeWithLanguageUnit, LanguageUnitContainer, TokenAndLanguageUnit, VariableDeclaration
from semantic.scopes import Scope, DescribedUnitContainer
from semantic.unit_descriptions import UnitWithTypeDs, IdentifierDs, OperatorDs, generate_name_of_operator_func


def extract_unit(node: TreeWithLanguageUnit, *path_to_target_attribute) -> Union[TreeWithLanguageUnit, Any]:
    """Extract unit recursively using the given attributes"""
    for at in path_to_target_attribute:
        node = getattr(node.unit, at)
    return node.unit


def extracted_list_units(unit, list_attribute_name: str):
    lst = getattr(unit, list_attribute_name)
    for elem in lst:
        yield elem.unit


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
    :param actual_parameters: list of expressions nodes containing described units
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
                    f"Declaration of '{declaration_name}' is not found")


def check_type_exists(type_name: str, scope: Scope, node_containing_type: DescribedUnitContainer):
    builtin_types = ['int', 'bool', 'float', 'str']
    for t in builtin_types:
        if t == type_name:
            return
    found_type = scope.find_declared_node(type_name)
    if found_type is None:
        line, column = extracted_meta(node_containing_type)
        raise Exception(f"In line [{line}:{column}]: {str(node_containing_type.unit)}\n"
                        f"'{type_name}' type is not found")


def check_declaration_doesnt_exist(name: str, scope: Scope, node_containing_declaration: DescribedUnitContainer):
    found_declaration = scope.find_declared_node(name)
    if found_declaration is not None:
        line, column = extracted_meta(node_containing_declaration)
        raise Exception(f"In line [{line}:{column}]: {str(node_containing_declaration.unit)}\n"
                        f"'{name}' has already been declared")


def check_can_assign_expression(left_expression_node: DescribedUnitContainer,
                                right_expression_node: DescribedUnitContainer):
    if isinstance(left_expression_node.unit.description, IdentifierDs):
        bound_declaration_to_the_left_expr = left_expression_node.unit.description.bound_declaration
        var_decl_node: VariableDeclaration = bound_declaration_to_the_left_expr
        is_val = extract_unit(var_decl_node, "var_or_val").value
        if is_val:
            line, column = extracted_meta(left_expression_node)
            raise Exception(f"In line [{line}:{column}]: "
                            f"Cannot assign '{str(left_expression_node.unit)}' because it was declared as val")

    if left_expression_node.unit.description.type != right_expression_node.unit.description.type:
        line, column = extracted_meta(left_expression_node)
        raise Exception(f"In line [{line}:{column}]: "
                        f"type mismatch {left_expression_node.unit.description.type}"
                        f" and {right_expression_node.unit.description.type}")


def try_to_find_appropriate_operator_node(left_expression_node: DescribedUnitContainer,
                                          right_expression_node: DescribedUnitContainer,
                                          operator_as_str: str,
                                          scope) -> DescribedUnitContainer:
    left_type = left_expression_node.unit.description.type
    right_type = right_expression_node.unit.description.type
    op_signature = generate_name_of_operator_func(operator_as_str, left_type, right_type)
    found = scope.find_declared_node(op_signature)
    if found is None:
        line1, column1 = extracted_meta(left_expression_node)
        line2, column2 = extracted_meta(right_expression_node)
        # TODO(@pochka15): test
        raise Exception(f"""Operator with the signature: {op_signature} is not found
There is no operator for the expressions:
{str(left_expression_node.unit)} [{line1}:{column1}]
{str(right_expression_node.unit)} [{line2}:{column2}]""")
    return found
