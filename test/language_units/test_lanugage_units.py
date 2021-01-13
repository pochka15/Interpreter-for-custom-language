from language_units import *
from test.language_units.utilities import *


def test_variable_declaration(lark):
    snippet = "a int val = 1"
    parsed = lark.parse(snippet)
    found = transformed(next(parsed.find_pred(lambda t: t.data == "variable_declaration")))
    assert isinstance(found, TreeWithLanguageUnit)
    unit = found.language_unit
    assert isinstance(unit, VariableDeclaration)
    assert str(unit) == "a int val"
