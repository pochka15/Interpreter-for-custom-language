from lark import Tree
from lark.visitors import Interpreter

from language_units import CallSuffix, Identifier, BuiltinUnit, String, Bool, Float, Int
from semantic.semantic_utilities import *
from semantic.unit_descriptions import *


def add_unit_description(container: LanguageUnitContainer,
                         description: UnitDescription) -> DescribedUnitContainer:
    container.unit.description = description
    return container


int_int_sum_operator_ds = OperatorDs('+', 'int', 'int', 'int', lambda x, y: x + y)

int_int_sub_operator_ds = OperatorDs('-', 'int', 'int', 'int', lambda x, y: x - y)


def builtin_nodes():
    print_description = CallableDs('print', 'str', [UnitWithTypeDs('param', 'str')], 'void', print)
    print_tree = TreeWithLanguageUnit(Tree('builtin_function', []), BuiltinUnit(str(print_description)))

    print2_description = CallableDs('print2', 'int', [UnitWithTypeDs('param', 'int')], 'void', print)
    print2_tree = TreeWithLanguageUnit(Tree('builtin_function', []), BuiltinUnit(str(print2_description)))

    int_int_sum_tree = TreeWithLanguageUnit(Tree('builtin_operator', []), BuiltinUnit(str(int_int_sum_operator_ds)))

    int_int_sub_tree = TreeWithLanguageUnit(Tree('builtin_operator', []), BuiltinUnit(str(int_int_sub_operator_ds)))
    nodes = [(add_unit_description(print_tree, print_description), print_description.name),
             (add_unit_description(int_int_sum_tree, int_int_sub_operator_ds),
              generate_name_of_operator_func(
                  int_int_sum_operator_ds.name,
                  int_int_sum_operator_ds.left_expr_type,
                  int_int_sum_operator_ds.right_expr_type)),
             (add_unit_description(int_int_sub_tree, int_int_sub_operator_ds),
              generate_name_of_operator_func(
                  int_int_sub_operator_ds.name,
                  int_int_sub_operator_ds.left_expr_type,
                  int_int_sub_operator_ds.right_expr_type)),
             (add_unit_description(print2_tree, print2_description), print2_description.name)]
    for node, name in nodes:
        yield node, name


class SemanticAnalyzer(Interpreter):
    def __init__(self, scopes=None):
        super().__init__()
        if scopes is None:
            scopes = []
        self.scopes = scopes
        root_scope = Scope(None)
        self.scopes.append(root_scope)
        self.current_scope = root_scope
        # TODO(@pochka15):check
        for (node, name) in builtin_nodes():
            self.current_scope.put(node, name)

    def start(self, node):
        return self.visit_children(node)

    def visit(self, node):
        if isinstance(node, Tree) and node.data == 'start':
            return self.visit_children(node)
        unit = node.unit
        if isinstance(unit, String):
            add_unit_description(node, UnitWithTypeDs(str(unit), 'str'))
        elif isinstance(unit, Bool):
            add_unit_description(node, UnitWithTypeDs(str(unit), 'bool'))
        elif isinstance(unit, Float):
            add_unit_description(node, UnitWithTypeDs(str(unit), 'float'))
        elif isinstance(unit, Int):
            add_unit_description(node, UnitWithTypeDs(str(unit), 'int'))
        elif isinstance(node.unit, Identifier):
            searched_symbol_name: str = str(node.unit)
            # TODO(@pochka15): find the function declaration properly
            # try_to_find_function_declaration()
            found_declaration = self.current_scope.find_declared_node(searched_symbol_name)
            if found_declaration is None:
                # TODO(@pochka15): test
                raise_declaration_is_not_found(searched_symbol_name, node)
            found_unit_description = found_declaration.unit.description
            if isinstance(found_unit_description, UnitWithTypeDs):
                id_type = found_unit_description.type
            else:
                raise Exception("Unknown type of the found declaration: " + str(found_declaration.unit))
            add_unit_description(node, IdentifierDs(str(node.unit), id_type, found_declaration))
        else:
            return super().visit(node)

    def additive_expression(self, node: TreeWithLanguageUnit):
        def bound_func():
            print("TODO(@pochka15):")

        first_expr_node = node.unit.multiplicative_expression
        self.visit(first_expr_node)
        # TODO(@pochka15): remove the assumption that all the types must be equal to the first_expr_node type
        op_and_expr_iter = iter(node.unit.additive_operators_with_multiplicative_expressions)
        prev_expr_node = first_expr_node
        for op_node in op_and_expr_iter:
            next_expr_node = next(op_and_expr_iter)
            self.visit(next_expr_node)
            found_node = try_to_find_appropriate_operator_node(
                prev_expr_node, next_expr_node, str(op_node.unit), self.current_scope)
            op_node.unit.description = found_node.unit.description
            prev_expr_node = next_expr_node
        assert op_node is not None
        ds = AdditiveExpressionDs(str(node.unit), op_node.unit.description.return_type, bound_func)
        add_unit_description(node, ds)

    def assignment(self, node: TreeWithLanguageUnit):
        self.visit(node.unit.right_expression)
        if isinstance(node.unit.left_expression, TokenAndLanguageUnit):
            self.visit(node.unit.left_expression)
        else:
            self.visit(node.unit.left_expression)
        check_can_assign_expression(node.unit.left_expression, node.unit.right_expression)
        assert isinstance(node.unit.right_expression, TokenAndLanguageUnit)
        left_expression = extract_unit(node, "left_expression")
        if isinstance(left_expression.description, IdentifierDs):
            description = left_expression.description.bound_declaration.unit.description
        else:
            description = extract_unit(node, "left_expression").description
        description.bound_definition = node.unit.right_expression

    def call_suffix(self, node: TreeWithLanguageUnit):
        # type_arguments are not supported yet
        self.visit(node.unit.function_call_arguments)

    def function_call_arguments(self, node: TreeWithLanguageUnit):
        # for each expression check if it's ok
        # TODO(@pochka15): now it takes only the first argument
        assert len(node.unit.expressions) == 1
        self.visit(node.unit.expressions[0])

    def postfix_unary_expression(self, node: TreeWithLanguageUnit):
        def check_suffix_can_be_applied(description, suffix):
            assert isinstance(description, CallableDs), "Expressions of not Сallable type are not supplied yet"
            assert isinstance(suffix, CallSuffix), "Suffix must be of type CallSuffix"
            # Here I take a list of expressions and compare them with formal parameters
            check_formal_actual_parameters_match(
                description.formal_parameters,
                suffix.function_call_arguments.unit.expressions)

        primary_expression_node = node.unit.primary_expression
        self.visit(primary_expression_node)
        bound_function_node: DescribedUnitContainer = primary_expression_node.unit.description.bound_declaration
        current_description: CallableDs = bound_function_node.unit.description
        current_type = None
        for suffix_node in node.unit.suffixes:
            self.visit(suffix_node)
            check_suffix_can_be_applied(current_description, suffix_node.unit)
            current_type = current_description.return_type
        assert current_type is not None
        add_unit_description(node, UnitWithTypeDs(str(node.unit), current_type))

    def variable_declaration(self, node: LanguageUnitContainer):
        type_unit = extract_unit(node, "type")
        assert len(type_unit.simple_user_types) == 1, f"this type is not supported {str(node.unit)}"
        var_type_node: LanguageUnitContainer = type_unit.simple_user_types[0]
        var_name_node: LanguageUnitContainer = node.unit.variable_name

        check_type_exists(str(var_type_node.unit), self.current_scope, var_type_node)
        check_declaration_doesnt_exist(str(var_name_node.unit), self.current_scope, var_name_node)

        self.current_scope.put(
            add_unit_description(
                node, VariableDeclarationDs(str(var_name_node.unit), str(var_type_node.unit))),
            node.unit.description.name)
