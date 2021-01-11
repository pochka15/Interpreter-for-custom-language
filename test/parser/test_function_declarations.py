from lark import Tree, Token

from test.parser.utilities import *


def test_function_declaration_without_type_parameters(lark):
    snippet = r"""
    print() {
        return "Without type"
    }"""
    expected_tree = Tree('start', [Tree('function_declaration',
                                        [Token('NAME', 'print'), Tree('function_parameters', []),
                                         Tree('statements_block', [Tree('jump_statement',
                                                                        [Token('RETURN', 'return'),
                                                                         Token('STRING',
                                                                               '"Without type"')])])])])
    compare_trees(expected_tree, lark.parse(snippet))


def test_function_declaration_with_type_parameters(lark):
    snippet = r"""
print<T1, T2>(){
    return "With type"
}"""
    expected_tree = Tree('start', [Tree('function_declaration', [Token('NAME', 'print'), Tree('type_arguments', [
        Tree('type', [Token('NAME', 'T1')]), Tree('type', [Token('NAME', 'T2')])]), Tree('function_parameters', []),
                                                                 Tree('statements_block', [Tree('jump_statement',
                                                                                                [Token('RETURN',
                                                                                                       'return'),
                                                                                                 Token('STRING',
                                                                                                       '"With type"')])])])])
    compare_trees(expected_tree, lark.parse(snippet))


def test_function_declaration_with_parameters(lark):
    snippet = r"""
print(arg1 int, arg2 str){
    return str(arg1) + arg2
}"""
    expected_tree = Tree('start', [
        Tree('function_declaration', [Token('NAME', 'print'),
                                      Tree('function_parameters', [
                                          Tree('function_parameter',
                                               [Token('NAME', 'arg1'),
                                                Tree('type', [Token('NAME', 'int')])]),
                                          Tree('function_parameter',
                                               [Token('NAME', 'arg2'), Tree('type', [
                                                   Token('NAME', 'str')])])]),
                                      Tree('statements_block', [Tree('jump_statement',
                                                                     [Token('RETURN',
                                                                            'return'),
                                                                      Tree(
                                                                          'additive_expression',
                                                                          [Tree(
                                                                              'postfix_unary_expression',
                                                                              [Token(
                                                                                  'NAME',
                                                                                  'str'),
                                                                                  Tree(
                                                                                      'call_suffix',
                                                                                      [
                                                                                          Tree(
                                                                                              'function_call_arguments',
                                                                                              [
                                                                                                  Token(
                                                                                                      'NAME',
                                                                                                      'arg1')])])]),
                                                                              Token(
                                                                                  'ADDITIVE_OPERATOR',
                                                                                  '+'),
                                                                              Token(
                                                                                  'NAME',
                                                                                  'arg2')])])])])]
                         )
    compare_trees(expected_tree, lark.parse(snippet))


def test_function_declaration_with_overridden_hint(lark):
    snippet = r"""
    print() private overridden {
        return "overridden"
    }"""
    expected = Tree('start', [Tree('function_declaration', [Token('NAME', 'print'), Tree('function_parameters', []),
                                                            Token('VISIBILITY_MODIFIER', 'private'),
                                                            Token('OVERRIDDEN', 'overridden'), Tree('statements_block',
                                                                                                    [Tree(
                                                                                                        'jump_statement',
                                                                                                        [Token('RETURN',
                                                                                                               'return'),
                                                                                                         Token('STRING',
                                                                                                               '"overridden"')])])])])
    compare_trees(expected, lark.parse(snippet))


def test_function_declaration_with_return_type(lark):
    snippet = r"""
print() private overridden ReturnType {
    return new("arg for the constructor")
}"""
    expected = Tree('start', [Tree('function_declaration', [Token('NAME', 'print'), Tree('function_parameters', []),
                                                            Token('VISIBILITY_MODIFIER', 'private'),
                                                            Token('OVERRIDDEN', 'overridden'),
                                                            Token('FUNCTION_RETURN_TYPE', 'ReturnType'),
                                                            Tree('statements_block', [Tree('jump_statement',
                                                                                           [Token('RETURN', 'return'),
                                                                                            Tree(
                                                                                                'postfix_unary_expression',
                                                                                                [Token('NAME', 'new'),
                                                                                                 Tree('call_suffix', [
                                                                                                     Tree(
                                                                                                         'function_call_arguments',
                                                                                                         [Token(
                                                                                                             'STRING',
                                                                                                             '"arg for the constructor"')])])])])])])])
    compare_trees(expected, lark.parse(snippet))
