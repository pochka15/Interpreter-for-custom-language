from lark import Tree, Token

from test.parser.utilities import *


def test_statements_sequence_without_new_line(lark):
    try:
        snippet = r"x = foo() y = bar"
        lark.parse(snippet)
    except Exception:
        pass
    else:
        pytest.fail(f"Given no new line. Exception must be raised for the snippet: {snippet}")


def test_assignment_with_conjunction_and_disjunction(lark):
    snippet = r"""
    x int val = leftTasksNumber < 5 && (shouldWorkToday() || "Work tomorrow")
    """
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('assignment', [Tree('directly_assignable_expression', [Tree('variable_declaration', [
        Tree('variable_name', [Token('NAME', 'x')]), Tree('type', [Token('NAME', 'int')]),
        Tree('val_or_var', [Token('VAL', 'val')])])]), Tree('conjunction', [Tree('comparison',
                                                                                 [Token('NAME', 'leftTasksNumber'),
                                                                                  Token('COMPARISON_OPERATOR', '<'),
                                                                                  Token('DEC_NUMBER', '5')]),
                                                                            Tree('disjunction', [
                                                                                Tree('postfix_unary_expression',
                                                                                     [Token('NAME', 'shouldWorkToday'),
                                                                                      Tree('call_suffix', [Tree(
                                                                                          'function_call_arguments',
                                                                                          [])])]),
                                                                                Token('STRING',
                                                                                      '"Work tomorrow"')])])])])
    compare_trees(expected, actual)


def test_three_new_lined_statements(lark):
    snippet = r"""
    x int val = 2
    foo(some_val int, another_val str) str {
        return "foo" + str(some_val) + another_val
    }
    foo(x)"""
    expected_children = Tree('start',
                             [Tree('assignment', [Tree('directly_assignable_expression', [Tree('variable_declaration', [
                                 Tree('variable_name', [Token('NAME', 'x')]), Tree('type', [Token('NAME', 'int')]),
                                 Tree('val_or_var', [Token('VAL', 'val')])])]), Token('DEC_NUMBER', '2')]),
                              Tree('function_declaration', [Token('NAME', 'foo'), Tree('function_parameters', [
                                  Tree('function_parameter',
                                       [Token('NAME', 'some_val'), Tree('type', [Token('NAME', 'int')])]),
                                  Tree('function_parameter',
                                       [Token('NAME', 'another_val'), Tree('type', [Token('NAME', 'str')])])]),
                                                            Token('FUNCTION_RETURN_TYPE', 'str'),
                                                            Tree('statements_block', [
                                                                Tree('jump_statement', [Token('RETURN', 'return'),
                                                                                        Tree('additive_expression',
                                                                                             [Token('STRING',
                                                                                                    '"foo"'),
                                                                                              Token(
                                                                                                  'ADDITIVE_OPERATOR',
                                                                                                  '+'),
                                                                                              Tree(
                                                                                                  'postfix_unary_expression',
                                                                                                  [Token('NAME',
                                                                                                         'str'),
                                                                                                   Tree(
                                                                                                       'call_suffix',
                                                                                                       [Tree(
                                                                                                           'function_call_arguments',
                                                                                                           [Token(
                                                                                                               'NAME',
                                                                                                               'some_val')])])]),
                                                                                              Token(
                                                                                                  'ADDITIVE_OPERATOR',
                                                                                                  '+'),
                                                                                              Token('NAME',
                                                                                                    'another_val')])])])]),
                              Tree('postfix_unary_expression', [Token('NAME', 'foo'), Tree('call_suffix', [
                                  Tree('function_call_arguments', [Token('NAME', 'x')])])])]) \
        .children
    actual_children = lark.parse(snippet).children
    for expected, actual in zip(expected_children, actual_children):
        if not (actual == expected):
            pytest.fail(f"Expected tree: {expected.pretty()}\n------\nActual tree: {actual.pretty()}", False)


def test_if_else_expression(lark):
    snippet = r"""
if isMonday() {
    print("Monday")
} else {
    print("OtherDay")
}
    """
    expected = Tree('start', [
        Tree('if_expression', [Tree('postfix_unary_expression', [Token('NAME', 'isMonday'), Tree('call_suffix', [
            Tree('function_call_arguments', [])])]), Tree('statements_block', [Tree('postfix_unary_expression',
                                                                                    [Token('NAME', 'print'),
                                                                                     Tree('call_suffix', [
                                                                                         Tree('function_call_arguments',
                                                                                              [
                                                                                                  Token('STRING',
                                                                                                        '"Monday"')])])])]),
                               Token('ELSE', 'else'), Tree('statements_block', [Tree('postfix_unary_expression',
                                                                                     [Token('NAME', 'print'),
                                                                                      Tree('call_suffix', [Tree(
                                                                                          'function_call_arguments',
                                                                                          [Token('STRING',
                                                                                                 '"OtherDay"')])])])])])]
                    )
    actual = lark.parse(snippet)
    compare_trees(expected, actual)


def test_if_expression_inside_function_call(lark):
    snippet = r"""
lol(if kek {return "kek"} else {return "lol"})
    """
    expected = Tree('start', [Tree('postfix_unary_expression', [Token('NAME', 'lol'), Tree('call_suffix', [
        Tree('function_call_arguments', [Tree('if_expression', [Token('NAME', 'kek'), Tree('statements_block', [
            Tree('jump_statement', [Token('RETURN', 'return'), Token('STRING', '"kek"')])]), Token('ELSE', 'else'),
                                                                Tree('statements_block', [Tree('jump_statement', [
                                                                    Token('RETURN', 'return'),
                                                                    Token('STRING', '"lol"')])])])])])])])
    actual = lark.parse(snippet)
    compare_trees(expected, actual)


def test_expressions_in_parentheses(lark):
    snippet = r"""
    (a)
    lol(kek)
    (b)
    """
    actual = lark.parse(snippet)
    clip(actual)
    print(actual.pretty())


def test_similar_to_keywords_names(lark):
    snippet = r"""
abstracte int val = 5
bval int val = 2"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('assignment', [Tree('directly_assignable_expression', [Tree('variable_declaration', [
        Tree('variable_name', [Token('NAME', 'abstracte')]), Tree('type', [Token('NAME', 'int')]),
        Tree('val_or_var', [Token('VAL', 'val')])])]), Token('DEC_NUMBER', '5')]), Tree('assignment', [
        Tree('directly_assignable_expression', [Tree('variable_declaration',
                                                     [Tree('variable_name', [Token('NAME', 'bval')]),
                                                      Tree('type', [Token('NAME', 'int')]),
                                                      Tree('val_or_var', [Token('VAL', 'val')])])]),
        Token('DEC_NUMBER', '2')])])
    compare_trees(expected, actual)


def test_function_call_with_new_lined_arguments(lark):
    snippet = r"""
foo(lol,
    kek(),
    (a < b))
a int val = b"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('postfix_unary_expression', [Token('NAME', 'foo'), Tree('call_suffix', [Tree('function_call_arguments', [Token('NAME', 'lol'), Tree('postfix_unary_expression', [Token('NAME', 'kek'), Tree('call_suffix', [Tree('function_call_arguments', [])])]), Tree('comparison', [Token('NAME', 'a'), Token('COMPARISON_OPERATOR', '<'), Token('NAME', 'b')])])])]), Tree('assignment', [Tree('directly_assignable_expression', [Tree('variable_declaration', [Tree('variable_name', [Token('NAME', 'a')]), Tree('type', [Token('NAME', 'int')]), Tree('val_or_var', [Token('VAL', 'val')])])]), Token('NAME', 'b')])])
    compare_trees(expected, actual)