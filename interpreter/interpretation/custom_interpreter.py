from lark import Tree
from lark.visitors import Interpreter

from language_units import PostfixUnaryExpression
from semantic.scopes import DescribedUnitContainer
from semantic.semantic_analyzer import extract_unit
from semantic.unit_descriptions import CallableDs, AdditiveExpressionDs


class CustomInterpreter(Interpreter):
    def __init__(self):
        pass

    def start(self, node: Tree):
        self.visit_children(node)

    def postfix_unary_expression(self, node: DescribedUnitContainer):
        unit = node.unit
        primary_expression_node = unit.primary_expression
        suffixes_nodes = unit.suffixes
        f_call_node = primary_expression_node.unit.description.bound_declaration
        if isinstance(f_call_node.unit.description, CallableDs):
            arguments_node = extract_unit(suffixes_nodes[0], "function_call_arguments")
            first_arg = arguments_node.expressions[0].unit
            arg1_value = first_arg.description \
                .bound_declaration.unit.description \
                .bound_definition.unit.value
            f_call_node.unit.description.bound_function(arg1_value)
