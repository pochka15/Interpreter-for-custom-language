from lark import Tree, Token

from test.parser.utilities import *


def test_interface_with_type_parameters(lark):
    snippet = r"""
Male <T1, T2> Human interface {
    shouldSleepAtTime(time Time) bool
}
"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('interface_declaration', [Token('NAME', 'Male'), Tree('type_arguments', [
        Tree('type', [Token('NAME', 'T1')]), Tree('type', [Token('NAME', 'T2')])]),
                                                             Tree('parents', [Token('NAME', 'Human')]),
                                                             Tree('interface_body', [
                                                                 Tree('function_declaration_without_body',
                                                                      [Token('NAME', 'shouldSleepAtTime'),
                                                                       Tree('function_parameters', [
                                                                           Tree('function_parameter',
                                                                                [Token('NAME', 'time'), Tree('type', [
                                                                                    Token('NAME', 'Time')])])]),
                                                                       Token('FUNCTION_RETURN_TYPE', 'bool')])])])])
    compare_trees(expected, actual)


def test_interface_with_multiple_function_declarations(lark):
    snippet = r"""
Male interface {
    hashCode() int
    printable<T1>() void
    mood() str {
        return "OK"
    }
    shouldSleepAtTime(time Time) bool
    wantsToEat() bool {return true}
}
"""

    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('interface_declaration', [Token('NAME', 'Male'), Tree('interface_body', [
        Tree('function_declaration_without_body',
             [Token('NAME', 'hashCode'), Tree('function_parameters', []), Token('FUNCTION_RETURN_TYPE', 'int')]),
        Tree('function_declaration_without_body',
             [Token('NAME', 'printable'), Tree('type_arguments', [Tree('type', [Token('NAME', 'T1')])]),
              Tree('function_parameters', []), Token('FUNCTION_RETURN_TYPE', 'void')]), Tree('function_declaration',
                                                                                             [Token('NAME', 'mood'),
                                                                                              Tree(
                                                                                                  'function_parameters',
                                                                                                  []), Token(
                                                                                                 'FUNCTION_RETURN_TYPE',
                                                                                                 'str'),
                                                                                              Tree('statements_block', [
                                                                                                  Tree('jump_statement',
                                                                                                       [Token('RETURN',
                                                                                                              'return'),
                                                                                                        Token('STRING',
                                                                                                              '"OK"')])])]),
        Tree('function_declaration_without_body', [Token('NAME', 'shouldSleepAtTime'), Tree('function_parameters', [
            Tree('function_parameter', [Token('NAME', 'time'), Tree('type', [Token('NAME', 'Time')])])]),
                                                   Token('FUNCTION_RETURN_TYPE', 'bool')]), Tree('function_declaration',
                                                                                                 [Token('NAME',
                                                                                                        'wantsToEat'),
                                                                                                  Tree(
                                                                                                      'function_parameters',
                                                                                                      []), Token(
                                                                                                     'FUNCTION_RETURN_TYPE',
                                                                                                     'bool'), Tree(
                                                                                                     'statements_block',
                                                                                                     [Tree(
                                                                                                         'jump_statement',
                                                                                                         [Token(
                                                                                                             'RETURN',
                                                                                                             'return'),
                                                                                                             Token(
                                                                                                                 'BOOLEAN',
                                                                                                                 'true')])])])])])])
    compare_trees(expected, actual)


def test_interface_function_declaration_without_return_type(lark):
    try:
        tree = lark.parse(r"""
Male interface <T1, T2> Human, Printable, Hashable {
    # printable has a missed type here type is missed
    hashCode() int printable<T1>() mood() str { return "OK" }
}""")
    except Exception:
        pass
    else:
        pytest.fail("Exception must be raised, there was generated a tree:\n" + tree.pretty(), False)


def test_interface_with_function_declarations(lark):
    snippet = r"""
Some interface {
    lol(param str val) int
    kek(kek int) str {return "kek"}
}"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('interface_declaration', [Token('NAME', 'Some'), Tree('interface_body', [
        Tree('function_declaration_without_body', [Token('NAME', 'lol'), Tree('function_parameters', [
            Tree('function_parameter', [Token('NAME', 'param'), Tree('type', [Token('NAME', 'str')]),
                                        Tree('val_or_var', [Token('VAL', 'val')])])]),
                                                   Token('FUNCTION_RETURN_TYPE', 'int')]), Tree('function_declaration',
                                                                                                [Token('NAME', 'kek'),
                                                                                                 Tree(
                                                                                                     'function_parameters',
                                                                                                     [Tree(
                                                                                                         'function_parameter',
                                                                                                         [Token('NAME',
                                                                                                                'kek'),
                                                                                                          Tree('type', [
                                                                                                              Token(
                                                                                                                  'NAME',
                                                                                                                  'int')])])]),
                                                                                                 Token(
                                                                                                     'FUNCTION_RETURN_TYPE',
                                                                                                     'str'), Tree(
                                                                                                    'statements_block',
                                                                                                    [Tree(
                                                                                                        'jump_statement',
                                                                                                        [Token('RETURN',
                                                                                                               'return'),
                                                                                                         Token('STRING',
                                                                                                               '"kek"')])])])])])])
    compare_trees(expected, actual)


def test_interface_with_parent_interfaces(lark):
    snippet = r"""
Other<T, P> Parent1, Parent2 interface {
    lol() int
} """
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('interface_declaration', [Token('NAME', 'Other'), Tree('type_arguments', [
        Tree('type', [Token('NAME', 'T')]), Tree('type', [Token('NAME', 'P')])]), Tree('parents',
                                                                                       [Token('NAME', 'Parent1'),
                                                                                        Token('NAME', 'Parent2')]),
                                                             Tree('interface_body', [
                                                                 Tree('function_declaration_without_body',
                                                                      [Token('NAME', 'lol'),
                                                                       Tree('function_parameters', []),
                                                                       Token('FUNCTION_RETURN_TYPE', 'int')])])])])
    compare_trees(expected, actual)


def test_while_with_disjunction_expression(lark):
    snippet = r"""
while ok(mood) || goodWeather(today) {
    print("Everything will be ok")
}"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('while_statement', [Tree('disjunction', [Tree('postfix_unary_expression', [Token('NAME', 'ok'), Tree('call_suffix', [Tree('function_call_arguments', [Token('NAME', 'mood')])])]), Tree('postfix_unary_expression', [Token('NAME', 'goodWeather'), Tree('call_suffix', [Tree('function_call_arguments', [Token('NAME', 'today')])])])]), Tree('statements_block', [Tree('postfix_unary_expression', [Token('NAME', 'print'), Tree('call_suffix', [Tree('function_call_arguments', [Token('STRING', '"Everything will be ok"')])])])])])])
    compare_trees(expected, actual)

