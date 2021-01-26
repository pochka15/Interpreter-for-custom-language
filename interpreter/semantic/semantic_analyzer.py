from typing import List

from lark import Tree
from lark.visitors import Interpreter

from language_units import Type, CallSuffix, Identifier, FunctionDeclaration
from semantic.scopes import DescribedUnitContainer
from semantic.semantic_utilities import *
from semantic.unit_descriptions import *


def with_added_unit_description(node: LanguageUnitContainer,
                                description: UnitDescription) -> DescribedUnitContainer:
    node.unit.description = description
    return node


class SemanticAnalyzer(Interpreter):
    def __init__(self, scopes: List[Scope]):
        super().__init__()
        self.scopes = scopes
        root_scope = Scope(None)
        self.scopes.append(root_scope)
        self.current_scope = root_scope
        t = TreeWithLanguageUnit(Tree('function_declaration', []), FunctionDeclaration('print', 'void'))
        self.current_scope.put(with_added_unit_description(t, UnitWithTypeDs(t.unit.name, t.unit.return_type)))

    def BLOCK_END(self, _: LanguageUnitContainer):
        self.current_scope = self.current_scope.enclosing_scope

    def visit_primary_expression_node(self, pair: TokenAndLanguageUnit):
        # TODO(@pochka15): add symbols
        if isinstance(pair.unit, str):
            pair.token.type == "STRING"
            pass
        elif isinstance(pair.unit, bool):
            pair.token.type == "BOOLEAN"
            pass
        elif isinstance(pair.unit, Identifier):
            pair.token.type == "NAME"
            searched_symbol_name: str = str(pair.unit)
            found_declaration = self.current_scope.find_declaration(searched_symbol_name)
            if found_declaration is None:
                # TODO(@pochka15): test
                raise_declaration_is_not_found(searched_symbol_name, pair)
            self.current_scope.put(with_added_unit_description(pair, found_declaration))
        elif isinstance(pair.unit, int):
            pair.token.type == "DEC_NUMBER"
        elif isinstance(pair.unit, float):
            pair.token.type == "FLOAT_NUMBER"


    # def statements_block(self, node: LanguageUnitContainer):
    #     new_scope = Scope(self.current_scope)
    #     self.current_scope = new_scope
    #     self.scopes.append(new_scope)

    def call_suffix(self, node: TreeWithLanguageUnit):
        # type_arguments are not supported yet
        self.visit(node.unit.function_call_arguments)

    def function_call_arguments(self, node: TreeWithLanguageUnit):
        for child in node.children:
            self.visit(child)

    def postfix_unary_expression(self, node: TreeWithLanguageUnit):
        def check_suffix_can_be_applied(description, suffix):
            assert isinstance(description, CallableDs), "Expressions of not Сallable type are not supplied yet"
            assert isinstance(suffix, CallSuffix), "Suffix must be of type CallSuffix"
            # Here I take a list of expressions and compare them with formal parameters
            check_formal_actual_parameters_match(
                description.formal_parameters,
                extract_unit(suffix, "function_call_arguments").expressions)

        primary_expression_token = node.unit.primary_expression
        self.visit_primary_expression_node(primary_expression_token)
        current_description: CallableDs = primary_expression_token.unit.description
        current_type = None
        for suffix in extracted_list_units(node, "suffixes"):
            self.visit(suffix)
            check_suffix_can_be_applied(current_description, suffix)
            current_type = current_description.return_type
        assert current_type is not None
        self.current_scope.put(
            with_added_unit_description(
                node, UnitWithTypeDs(str(node.unit), current_type)))

    def variable_declaration(self, node: LanguageUnitContainer):
        type_name = extract_unit(node, "type_name")
        assert len(type_name.simple_user_types) == 1, f"this type is not supported {str(node.unit)}"
        var_type_node: LanguageUnitContainer = type_name.simple_user_types[0]
        var_name_node: LanguageUnitContainer = node.unit.variable_name

        # TODO(@pochka15): what about symbols should each variable declaration unit child be somehow added to the table?
        check_type_exists(str(var_type_node.unit), self.current_scope, var_type_node)
        check_declaration_doesnt_exist(str(var_name_node.unit), self.current_scope, var_name_node)

        self.current_scope.put(
            with_added_unit_description(
                node, UnitWithTypeDs(str(var_name_node.unit), str(var_type_node.unit))))


def extract_unit(node: TreeWithLanguageUnit, *path_to_target_attribute):
    """Extract unit recursively using the given attributes"""
    for at in path_to_target_attribute:
        node = getattr(node.unit, at)
    return node.unit


def extracted_list_units(unit, list_attribute_name: str):
    lst = getattr(unit, list_attribute_name)
    for elem in lst:
        yield elem.unit
