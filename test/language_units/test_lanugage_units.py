from collections import Iterable
from typing import Iterator

from language_units import *
from test.language_units.utilities import *


def extract_unit(tree, *path_to_target_attribute):
    """Extract unit recursively using the given attributes"""
    for at in path_to_target_attribute:
        tree = getattr(tree.unit, at)
    return tree.unit


def extracted_list_units(unit, list_attribute_name):
    lst = getattr(unit, list_attribute_name)
    for elem in lst:
        yield elem.unit


def parse_find_transform(lark: Lark, snippet: str, tree_data) -> Iterator:
    for found in lark.parse(snippet).iter_subtrees_topdown():
        if found.data == tree_data:
            yield transformed(found)


def test_variable_declaration(lark):
    snippet = "a int val = 1"
    variable_declaration = next(parse_find_transform(lark, snippet, "variable_declaration")).unit
    assert isinstance(variable_declaration, VariableDeclaration)
    assert str(variable_declaration) == "a int val"


def test_prefix_unary_expression(lark):
    snippet = r"""
    a + -!b
    """
    prefix_unary_expression = next(parse_find_transform(lark, snippet, "prefix_unary_expression")).unit
    assert str(prefix_unary_expression) == "-!b"


def test_directly_assignable_expression(lark):
    snippet = "arr[0] = 5"
    root = next(parse_find_transform(lark, snippet, "directly_assignable_expression"))
    assert str(extract_unit(root, 'postfix_unary_expression')) == 'arr'
    assert extract_unit(root, 'assignable_suffix', 'expression') == 0


def test_additive_expression(lark):
    snippet = "counter += 1 + 5 - 6"
    root = next(parse_find_transform(lark, snippet, "additive_expression"))
    assert str(extract_unit(root, 'multiplicative_expression')) == '1'
    assert str(root.unit.additive_operators_with_multiplicative_expressions) == '[+, 5, -, 6]'


def test_assignment(lark):
    snippet = "a int val = 5"
    root = next(parse_find_transform(lark, snippet, "assignment"))
    var_decl = extract_unit(root, 'left_expression')
    assert (isinstance(var_decl, VariableDeclaration))
    assert str(extract_unit(root, 'operator')) == '='
    assert str(extract_unit(root, 'right_expression')) == '5'


def test_function_call_arguments(lark):
    snippet = "print(a, b, c)"
    root = next(parse_find_transform(lark, snippet, "function_call_arguments"))
    assert str(root.unit) == "a, b, c"


def test_disjunction(lark):
    snippet = "a || b"
    root = next(parse_find_transform(lark, snippet, "disjunction"))
    assert str(root.unit) == snippet
    expected = ('a', 'b')
    for exp, actual in zip(expected, extracted_list_units(root.unit, "conjunctions")):
        assert exp == str(actual)


def test_equality(lark):
    snippet = "a bool val = x != y"
    root = next(parse_find_transform(lark, snippet, "equality"))
    assert str(root.unit) == "x != y"


def test_call_suffix(lark):
    snippet = "some(a, b)"
    root = next(parse_find_transform(lark, snippet, "call_suffix"))
    assert str(root.unit) == "(a, b)"


def test_postfix_unary_expression(lark):
    snippet = "a()(1)"
    root = next(parse_find_transform(lark, snippet, "postfix_unary_expression"))
    assert str(root.unit) == "a()(1)"
    primary_expression = extract_unit(root, "primary_expression")
    assert primary_expression == "a"
    expected = ('()', "(1)")
    for exp, act in zip(expected, extracted_list_units(root.unit, "suffixes")):
        assert exp == str(act)


def test_multiplicative_expression(lark):
    snippet = "a * b / c % d"
    root = next(parse_find_transform(lark, snippet, "multiplicative_expression"))
    assert str(root.unit) == snippet


def test_import_targets(lark):
    snippet = "from some import target1 as t1, target2 as t2"
    root = next(parse_find_transform(lark, snippet, "import_targets"))
    assert str(root.unit) == "target1 as t1, target2 as t2"


def test_from_path(lark):
    snippet = "from ..kek.lol import something"
    root = next(parse_find_transform(lark, snippet, "from_path"))
    assert str(root.unit) == "..kek.lol"


def test_type(lark):
    snippet = "a ((Hmm<Kek, Lol<Inner1, Inner2>>.What<The, Hell>)) val = 5"
    root = next(parse_find_transform(lark, snippet, "type"))
    assert isinstance(root.unit, Type)
    assert str(root.unit) == "(Hmm<Kek, Lol<Inner1, Inner2>>.What<The, Hell>)"
