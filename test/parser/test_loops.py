from lark import Tree, Token

from test.parser.utilities import *


def test_for_with_labeled_break(lark):
    snippet = r"""
    myLabel@
    for x in db.values {
        break@ myLabel
    }"""
    expected = Tree('start', [Tree('for_statement', [Tree('label', [Token('NAME', 'myLabel')]), Token('NAME', 'x'),
                                                     Tree('postfix_unary_expression',
                                                          [Token('NAME', 'db'),
                                                           Tree('navigation_suffix', [Token('NAME', 'values')])]),
                                                     Tree('statements_block',
                                                          [Tree('jump_statement',
                                                                [Tree('break_at', [Token('NAME', 'myLabel')])])])])])
    actual = lark.parse(snippet)
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes


def test_for_with_nested_for(lark):
    snippet = r"""
for x in db.values {
    print("outer")
    for y in db.otherValues {
        print("inner")
    }
}"""
    expected = Tree('start',
                    [Tree('for_statement',
                          [Token('NAME', 'x'),
                           Tree('postfix_unary_expression', [Token('NAME', 'db'),
                                                             Tree(
                                                                 'navigation_suffix',
                                                                 [
                                                                     Token('NAME',
                                                                           'values')])]),
                           Tree('statements_block', [Tree('postfix_unary_expression',
                                                          [Token('NAME', 'print'),
                                                           Tree('call_suffix', [
                                                               Tree('function_call_arguments',
                                                                    [Token('STRING', '"outer"')])])]),
                                                     Tree('for_statement', [Token('NAME', 'y'),
                                                                            Tree(
                                                                                'postfix_unary_expression',
                                                                                [Token('NAME', 'db'),
                                                                                 Tree(
                                                                                     'navigation_suffix',
                                                                                     [
                                                                                         Token('NAME',
                                                                                               'otherValues')])]),
                                                                            Tree('statements_block',
                                                                                 [Tree(
                                                                                     'postfix_unary_expression',
                                                                                     [Token('NAME',
                                                                                            'print'),
                                                                                      Tree(
                                                                                          'call_suffix',
                                                                                          [Tree(
                                                                                              'function_call_arguments',
                                                                                              [Token(
                                                                                                  'STRING',
                                                                                                  '"inner"')])])])])])])])])
    actual = lark.parse(snippet)
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes


def test_loop_fails_when_in_omitted(lark):
    try:
        tree = lark.parse(r"""
    for x db.values {
        print(x)
    }""")
    except Exception:
        pass
    else:
        pytest.fail("Exception must be raised here, there shouldn't be generated a tree:\n" + tree.pretty())


def test_while_statement(lark):
    snippet = r"""
    while if x < 5 {closeToZero(x)} else {true} {
        x -= 1
    }"""

    expected = Tree('start', [Tree('while_statement', [Tree('if_expression', [
        Tree('comparison', [Token('NAME', 'x'), Token('COMPARISON_OPERATOR', '<'), Token('DEC_NUMBER', '5')]),
        Tree('statements_block', [Tree('postfix_unary_expression', [Token('NAME', 'closeToZero'), Tree('call_suffix', [
            Tree('function_call_arguments', [Token('NAME', 'x')])])])]), Token('ELSE', 'else'),
        Tree('statements_block', [Token('BOOLEAN', 'true')])]), Tree('statements_block', [
        Tree('assignment', [Token('NAME', 'x'), Token('ASSIGNMENT_AND_OPERATOR', '-='), Token('DEC_NUMBER', '1')])])])])

    actual = lark.parse(snippet)
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes


def test_for_in_list(lark):
    snippet = r"""
    for v in [v1, v2, v3] {
        print(v)
    }
    """
    expected = Tree('start', [Tree('for_statement', [Token('NAME', 'v'), Tree('collection_literal',
                                                                              [Token('NAME', 'v1'), Token('NAME', 'v2'),
                                                                               Token('NAME', 'v3')]),
                                                     Tree('statements_block', [
                                                         Tree('postfix_unary_expression',
                                                              [Token('NAME', 'print'), Tree('call_suffix', [
                                                                  Tree('function_call_arguments',
                                                                       [Token('NAME', 'v')])])])])])])
    actual = lark.parse(snippet)
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes


def test_while_with_function_call_expression(lark):
    snippet = r"""
while funCall(hello) {
    print("inside while")
}"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('while_statement', [Tree('postfix_unary_expression', [Token('NAME', 'funCall'),
                                                                                         Tree('call_suffix', [Tree(
                                                                                             'function_call_arguments',
                                                                                             [Token('NAME',
                                                                                                    'hello')])])]),
                                                       Tree('statements_block', [Tree('postfix_unary_expression',
                                                                                      [Token('NAME', 'print'),
                                                                                       Tree('call_suffix', [Tree(
                                                                                           'function_call_arguments', [
                                                                                               Token('STRING',
                                                                                                     '"inside while"')])])])])])])
    result, mes = trees_comparison_result(expected, actual)
    assert result, mes
