from lark import Tree, Token

from test.parser.utilities import *


def test_prefix_postfix_precedence(lark):
    snippet = r"""+person.sayHello()"""
    actual = lark.parse(snippet)
    expected = Tree('start',
                    [Tree('prefix_unary_expression', [Token('PREFIX_OPERATOR', '+'), Tree('postfix_unary_expression',
                                                                                          [Token('NAME', 'person'),
                                                                                           Tree('navigation_suffix',
                                                                                                [Token('NAME',
                                                                                                       'sayHello')]),
                                                                                           Tree('call_suffix', [
                                                                                               Tree(
                                                                                                   'function_call_arguments',
                                                                                                   [])])])])])
    compare_trees(expected, actual)


def test_suffixes_precedence(lark):
    snippet = r""""OK" == person.mood().asString()
a int val = items[0].value() """
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('equality', [Token('STRING', '"OK"'), Token('EQUALITY_OPERATOR', '=='),
                                                Tree('postfix_unary_expression', [Token('NAME', 'person'),
                                                                                  Tree('navigation_suffix',
                                                                                       [Token('NAME', 'mood')]),
                                                                                  Tree('call_suffix', [
                                                                                      Tree('function_call_arguments',
                                                                                           [])]),
                                                                                  Tree('navigation_suffix',
                                                                                       [Token('NAME', 'asString')]),
                                                                                  Tree('call_suffix', [
                                                                                      Tree('function_call_arguments',
                                                                                           [])])])]), Tree('assignment',
                                                                                                           [Tree(
                                                                                                               'directly_assignable_expression',
                                                                                                               [Tree(
                                                                                                                   'variable_declaration',
                                                                                                                   [
                                                                                                                       Token(
                                                                                                                           'NAME',
                                                                                                                           'a'),
                                                                                                                       Tree(
                                                                                                                           'type',
                                                                                                                           [
                                                                                                                               Token(
                                                                                                                                   'NAME',
                                                                                                                                   'int')]),
                                                                                                                       Token(
                                                                                                                           'VAL',
                                                                                                                           'val')])]),
                                                                                                            Token(
                                                                                                                'ASSIGNMENT_OPERATOR',
                                                                                                                '='),
                                                                                                            Tree(
                                                                                                                'postfix_unary_expression',
                                                                                                                [Token(
                                                                                                                    'NAME',
                                                                                                                    'items'),
                                                                                                                 Tree(
                                                                                                                     'indexing_suffix',
                                                                                                                     [
                                                                                                                         Token(
                                                                                                                             'DEC_NUMBER',
                                                                                                                             '0')]),
                                                                                                                 Tree(
                                                                                                                     'navigation_suffix',
                                                                                                                     [
                                                                                                                         Token(
                                                                                                                             'NAME',
                                                                                                                             'value')]),
                                                                                                                 Tree(
                                                                                                                     'call_suffix',
                                                                                                                     [
                                                                                                                         Tree(
                                                                                                                             'function_call_arguments',
                                                                                                                             [])])])])])

    compare_trees(expected, actual)


def test_disjunction_with_conjunction(lark):
    snippet = r"""
    procrastinateToday() && watchMovies() ||
    procrastinateTomorrow() && workHard()
    """
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('disjunction', [Tree('conjunction', [Tree('postfix_unary_expression',
                                                                             [Token('NAME', 'procrastinateToday'),
                                                                              Tree('call_suffix',
                                                                                   [Tree(
                                                                                       'function_call_arguments',
                                                                                       [])])]),
                                                                        Tree('postfix_unary_expression',
                                                                             [Token('NAME', 'watchMovies'),
                                                                              Tree('call_suffix', [Tree(
                                                                                  'function_call_arguments',
                                                                                  [])])])]),
                                                   Tree('conjunction', [Tree('postfix_unary_expression',
                                                                             [Token('NAME', 'procrastinateTomorrow'),
                                                                              Tree('call_suffix',
                                                                                   [Tree('function_call_arguments',
                                                                                         [])])]),
                                                                        Tree('postfix_unary_expression',
                                                                             [Token('NAME', 'workHard'),
                                                                              Tree('call_suffix', [Tree(
                                                                                  'function_call_arguments',
                                                                                  [])])])])])]
                    )
    compare_trees(expected, actual)


def test_conjunction_and_parentheses(lark):
    snippet = r"""
    x int val = leftTasksNumber < 5 && (shouldWorkToday() || shouldWorkTomorrow())
    """
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('assignment', [Tree('directly_assignable_expression', [
        Tree('variable_declaration', [Token('NAME', 'x'), Tree('type', [Token('NAME', 'int')]), Token('VAL', 'val')])]),
                                                  Token('ASSIGNMENT_OPERATOR', '='), Tree('conjunction', [
            Tree('comparison',
                 [Token('NAME', 'leftTasksNumber'), Token('COMPARISON_OPERATOR', '<'), Token('DEC_NUMBER', '5')]),
            Tree('disjunction', [Tree('postfix_unary_expression', [Token('NAME', 'shouldWorkToday'), Tree('call_suffix',
                                                                                                          [Tree(
                                                                                                              'function_call_arguments',
                                                                                                              [])])]),
                                 Tree('postfix_unary_expression', [Token('NAME', 'shouldWorkTomorrow'),
                                                                   Tree('call_suffix',
                                                                        [Tree('function_call_arguments', [])])])])])])])

    compare_trees(expected, actual)


def test_expression_with_multiple_prefixes(lark):
    snippet = r"""
    a + -!b
    c += !d
    """

    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('additive_expression', [Token('NAME', 'a'), Token('ADDITIVE_OPERATOR', '+'),
                                                           Tree('prefix_unary_expression',
                                                                [Token('PREFIX_OPERATOR', '-'),
                                                                 Token('PREFIX_OPERATOR', '!'), Token('NAME', 'b')])]),
                              Tree('assignment', [Token('NAME', 'c'), Token('ASSIGNMENT_AND_OPERATOR', '+='),
                                                  Tree('prefix_unary_expression',
                                                       [Token('PREFIX_OPERATOR', '!'), Token('NAME', 'd')])])])
    print(actual.pretty())
    compare_trees(expected, actual)


def test_assignment_and_operator(lark):
    snippet = r"""
x int val = y += z"""
    try:
        actual = lark.parse(snippet)
    except:
        pass
    else:
        pytest.fail(f"Snippet: '{snippet}' should throw an error while parsing\n"
                    f"Generated tree:\n"
                    f"{actual.pretty()}")


def test_comparison_operators_in_a_row(lark):
    snippet = r"a < (b + 3) < c"
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('comparison', [Token('NAME', 'a'), Token('COMPARISON_OPERATOR', '<'),
                                                  Tree('additive_expression',
                                                       [Token('NAME', 'b'), Token('ADDITIVE_OPERATOR', '+'),
                                                        Token('DEC_NUMBER', '3')]), Token('COMPARISON_OPERATOR', '<'),
                                                  Token('NAME', 'c')])])
    compare_trees(expected, actual)


def test_immediately_called_if_expression(lark):
    snippet = r"""(if a < b {return a} else {return b})()"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('postfix_unary_expression', [Tree('if_expression', [
        Tree('comparison', [Token('NAME', 'a'), Token('COMPARISON_OPERATOR', '<'), Token('NAME', 'b')]),
        Tree('statements_block', [Tree('jump_statement', [Token('RETURN', 'return'), Token('NAME', 'a')])]),
        Token('ELSE', 'else'),
        Tree('statements_block', [Tree('jump_statement', [Token('RETURN', 'return'), Token('NAME', 'b')])])]),
                                                                Tree('call_suffix',
                                                                     [Tree('function_call_arguments', [])])])])
    compare_trees(expected, actual)


def test_navigation_suffix_on_next_line(lark):
    snippet = r"""a int val = items[0].
hello()
k val = 5"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('assignment', [Tree('directly_assignable_expression', [
        Tree('variable_declaration', [Token('NAME', 'a'), Tree('type', [Token('NAME', 'int')]), Token('VAL', 'val')])]),
                                                  Token('ASSIGNMENT_OPERATOR', '='), Tree('postfix_unary_expression',
                                                                                          [Token('NAME', 'items'),
                                                                                           Tree('indexing_suffix', [
                                                                                               Token('DEC_NUMBER',
                                                                                                     '0')]),
                                                                                           Tree('navigation_suffix', [
                                                                                               Token('NAME', 'hello')]),
                                                                                           Tree('call_suffix', [Tree(
                                                                                               'function_call_arguments',
                                                                                               [])])])]),
                              Tree('assignment', [Tree('directly_assignable_expression', [
                                  Tree('variable_declaration', [Token('NAME', 'k'), Token('VAL', 'val')])]),
                                                  Token('ASSIGNMENT_OPERATOR', '='), Token('DEC_NUMBER', '5')])])
    compare_trees(expected, actual)
