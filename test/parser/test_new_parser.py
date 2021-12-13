import io

from lark import Tree, Token
from parser.utilities import trees_comparison_result

from parser.parser import RecursiveDescentParser


def test_function_declaration_without_type_parameters(parser: RecursiveDescentParser):
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

    with io.StringIO(snippet) as f:
        trees_comparison_result(expected_tree, parser.parse(f))
