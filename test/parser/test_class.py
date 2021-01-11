from lark import Tree, Token

from test.parser.utilities import *


def test_abstract_class_declaration(lark):
    snippet = r"""
Male Human, Printable abstract class {
    foo() abstract str
}
"""
    actual = lark.parse(snippet)
    expected = (Tree('start',
                     [Tree('abstract_class_declaration', [Token('NAME', 'Male'),
                                                          Tree('parents', [Token('NAME', 'Human'),
                                                                           Token('NAME',
                                                                                 'Printable')]),
                                                          Token('ABSTRACT', 'abstract'),
                                                          Tree('abstract_class_body',
                                                               [Tree('abstract_class_member_declaration', [
                                                                   Tree(
                                                                       'abstract_function_declaration',
                                                                       [Token('NAME', 'foo'),
                                                                        Tree('function_parameters',
                                                                             []),
                                                                        Token('ABSTRACT',
                                                                              'abstract'),
                                                                        Token(
                                                                            'FUNCTION_RETURN_TYPE',
                                                                            'str')])])])])]))
    compare_trees(expected, actual)


def test_abstract_class_with_function_declarations(lark):
    snippet = r"""
    Male abstract class {
        foo() abstract str
        bar() { return "bar" }
    }"""

    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('abstract_class_declaration', [Token('NAME', 'Male'), Token('ABSTRACT', 'abstract'),
                                                                  Tree('abstract_class_body',
                                                                       [Tree('abstract_class_member_declaration', [
                                                                           Tree('abstract_function_declaration',
                                                                                [Token('NAME', 'foo'),
                                                                                 Tree('function_parameters', []),
                                                                                 Token('ABSTRACT', 'abstract'),
                                                                                 Token('FUNCTION_RETURN_TYPE',
                                                                                       'str')])]),
                                                                        Tree('abstract_class_member_declaration', [
                                                                            Tree('function_declaration',
                                                                                 [Token('NAME', 'bar'),
                                                                                  Tree(
                                                                                      'function_parameters',
                                                                                      []),
                                                                                  Tree('statements_block',
                                                                                       [Tree(
                                                                                           'jump_statement',
                                                                                           [Token(
                                                                                               'RETURN',
                                                                                               'return'),
                                                                                               Token(
                                                                                                   'STRING',
                                                                                                   '"bar"')])])])])])])])
    compare_trees(expected, actual)


def test_abstract_class_with_function_and_property_declarations(lark):
    snippet = r"""
Male abstract class {
    foo() str {return "foo"}
    bar int abstract val
    lol bool public var = false
}
"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('abstract_class_declaration', [Token('NAME', 'Male'), Token('ABSTRACT', 'abstract'),
                                                                  Tree('abstract_class_body',
                                                                       [Tree('abstract_class_member_declaration', [
                                                                           Tree('function_declaration',
                                                                                [Token('NAME', 'foo'),
                                                                                 Tree('function_parameters',
                                                                                      []),
                                                                                 Token('FUNCTION_RETURN_TYPE',
                                                                                       'str'),
                                                                                 Tree('statements_block', [
                                                                                     Tree('jump_statement', [
                                                                                         Token('RETURN',
                                                                                               'return'),
                                                                                         Token('STRING',
                                                                                               '"foo"')])])])]),
                                                                        Tree('abstract_class_member_declaration', [
                                                                            Tree('abstract_property_declaration',
                                                                                 [Token('NAME', 'bar'),
                                                                                  Tree('type',
                                                                                       [Token('NAME', 'int')]),
                                                                                  Token('ABSTRACT', 'abstract'),
                                                                                  Tree('val_or_var',
                                                                                       [Token('VAL', 'val')])])]),
                                                                        Tree('abstract_class_member_declaration', [
                                                                            Tree('property_assignment',
                                                                                 [Token('NAME', 'lol'),
                                                                                  Tree('type',
                                                                                       [Token('NAME', 'bool')]),
                                                                                  Token('VISIBILITY_MODIFIER',
                                                                                        'public'),
                                                                                  Tree('val_or_var',
                                                                                       [Token('VAR', 'var')]),
                                                                                  Token('BOOLEAN',
                                                                                        'false')])])])])])
    compare_trees(expected, actual)


def test_class_function_declarations_without_new_line_fails(lark):
    try:
        tree = lark.parse(r"""
        Male class abstract {
            foo() str {return "foo"} bar int val lol bool public var = false kek() abstract bool
        }
        """)
    except Exception:
        pass
    else:
        pytest.fail("It must be raised an exception, there was generated a tree:\n" + tree.pretty(), False)


def test_class_with_overridden_function_declaration(lark):
    snippet = r"""
MyClass <T, P> Parent class {
    foo(arg int val) private overridden str {
        return str(arg)
    }
}"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('non_abstract_class_declaration', [Token('NAME', 'MyClass'), Tree('type_arguments', [
        Tree('type', [Token('NAME', 'T')]), Tree('type', [Token('NAME', 'P')])]),
                                                                      Tree('parents', [Token('NAME', 'Parent')]),
                                                                      Tree('non_abstract_class_body', [
                                                                          Tree('non_abstract_class_member_declaration',
                                                                               [Tree('function_declaration',
                                                                                     [Token('NAME', 'foo'),
                                                                                      Tree('function_parameters', [
                                                                                          Tree('function_parameter',
                                                                                               [Token('NAME', 'arg'),
                                                                                                Tree('type', [
                                                                                                    Token('NAME',
                                                                                                          'int')]),
                                                                                                Tree('val_or_var', [
                                                                                                    Token('VAL',
                                                                                                          'val')])])]),
                                                                                      Token('VISIBILITY_MODIFIER',
                                                                                            'private'),
                                                                                      Token('OVERRIDDEN', 'overridden'),
                                                                                      Token('FUNCTION_RETURN_TYPE',
                                                                                            'str'),
                                                                                      Tree('statements_block', [
                                                                                          Tree('jump_statement', [
                                                                                              Token('RETURN', 'return'),
                                                                                              Tree(
                                                                                                  'postfix_unary_expression',
                                                                                                  [Token('NAME', 'str'),
                                                                                                   Tree('call_suffix', [
                                                                                                       Tree(
                                                                                                           'function_call_arguments',
                                                                                                           [Token(
                                                                                                               'NAME',
                                                                                                               'arg')])])])])])])])])])])
    compare_trees(expected, actual)


def test_class_with_property_declaration_and_assignment(lark):
    snippet = r"""
MyClass class {
    lol private val = kek()
    kek int val
}"""
    actual = lark.parse(snippet)
    expected = Tree('start', [Tree('non_abstract_class_declaration', [Token('NAME', 'MyClass'),
                                                                      Tree('non_abstract_class_body', [
                                                                          Tree('non_abstract_class_member_declaration',
                                                                               [Tree('property_assignment',
                                                                                     [Token('NAME', 'lol'),
                                                                                      Token('VISIBILITY_MODIFIER',
                                                                                            'private'),
                                                                                      Tree('val_or_var',
                                                                                           [Token('VAL', 'val')]),
                                                                                      Tree('postfix_unary_expression',
                                                                                           [Token('NAME', 'kek'),
                                                                                            Tree('call_suffix', [Tree(
                                                                                                'function_call_arguments',
                                                                                                [])])])])]),
                                                                          Tree('non_abstract_class_member_declaration',
                                                                               [Tree('property_declaration',
                                                                                     [Token('NAME', 'kek'), Tree('type',
                                                                                                                 [Token(
                                                                                                                     'NAME',
                                                                                                                     'int')]),
                                                                                      Tree('val_or_var', [Token('VAL',
                                                                                                                'val')])])])])])])
    compare_trees(expected, actual)


def test_abstract_declaration_in_non_abstract_class_fails(lark):
    snippet = r"""
MyClass class {
    bad abstract int
}"""
    try:
        actual = lark.parse(snippet)
    except:
        pass
    else:
        pytest.fail("Exception must be raised, there was generated a tree:\n" + actual.pretty(), False)
