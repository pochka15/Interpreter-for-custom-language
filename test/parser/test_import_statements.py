from lark import Tree, Token
from test.parser.utilities import *


def test_multiple_imports(lark):
    snippet = r"import a import b from c import d"
    expected = Tree('start', [Tree('import_without_from', [Token('NAME', 'a')]),
                              Tree('import_without_from', [Token('NAME', 'b')]),
                              Tree('import_with_from',
                                   [Tree('from_path', [Token('NAME', 'c')]),
                                    Token('NAME', 'd')])])
    trees_comparison_result(expected, lark.parse(snippet))


def test_multiple_as_imports(lark):
    snippet = r"""
    from ..car.mercedes import print_car as p_cr, lol_kek as l_k"""
    expected = Tree('start', [Tree('import_with_from', [
        Tree('from_path', [Token('RELATIVE_LOCATION', '..'), Token('NAME', 'car'), Token('NAME', 'mercedes')]),
        Tree('import_targets', [Tree('as_name', [Token('NAME', 'print_car'), Token('NAME', 'p_cr')]),
                                Tree('as_name', [Token('NAME', 'lol_kek'), Token('NAME', 'l_k')])])])])
    trees_comparison_result(expected, lark.parse(snippet))


def test_different_symbols_in_import_statement(lark):
    snippet = "from .cur import *"
    expected = Tree('start', [Tree('import_with_from',
                                   [Tree('from_path', [Token('RELATIVE_LOCATION', '.'), Token('NAME', 'cur')]),
                                    Token('ALL_TARGETS', '*')])])
    actual = lark.parse(snippet)
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes
