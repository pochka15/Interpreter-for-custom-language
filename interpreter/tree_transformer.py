from functools import partial
from typing import Iterable, Iterator

from lark import Transformer, Tree, Token, v_args

from language_units import VariableDeclaration, DirectlyAssignableExpression, Assignment, \
    TreeWithLanguageUnit, TokenWithLanguageUnit, AdditiveExpression, PrefixUnaryExpression


def is_val(value: str) -> bool:
    return True if value == 'val' else False


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming


def token_with_language_unit(applied_func, token) -> TokenWithLanguageUnit:
    return TokenWithLanguageUnit(token, applied_func(token))


def wrap_with_token_with_language_unit(_, token) -> TokenWithLanguageUnit:
    return TokenWithLanguageUnit(token, token.value)


class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)

    ADDITIVE_OPERATOR = wrap_with_token_with_language_unit
    NAME = wrap_with_token_with_language_unit
    PREFIX_OPERATOR = wrap_with_token_with_language_unit
    ASSIGNMENT_AND_OPERATOR = wrap_with_token_with_language_unit
    ASSIGNMENT_OPERATOR = wrap_with_token_with_language_unit

    def DEC_NUMBER(self, token):
        return token_with_language_unit(int, token)

    def VAR(self, token: Token):
        token.update("IS_VAL", token.value)
        return token_with_language_unit(is_val, token)

    def VAL(self, token: Token):
        token.update("IS_VAL", token.value)
        return token_with_language_unit(is_val, token)

    @v_args(tree=True)
    def statements_block(self, block_tree: Tree):
        block_tree.children.append(Token('BLOCK_END', ''))
        return block_tree

    @v_args(inline=True)
    def type(self, type_name_token) -> Token:
        return type_name_token

    # @v_args(tree=True)
    # def expression(self, expression_tree):
    #     simple_literal_token = expression_tree.children[0]
    #     return TreeWithSemanticUnit(expression_tree, Expression(simple_literal_token.value))

    @v_args(tree=True)
    def assignment(self, assignment_tree: Tree):
        it = iter(assignment_tree.children)
        left_expression = next(it)
        if len(assignment_tree.children) > 2:
            operator = next(it)
        else:
            operator = ""
        right_expression = next(it)
        return TreeWithLanguageUnit(assignment_tree,
                                    Assignment(left_expression, operator, right_expression))

    @v_args(tree=True)
    def directly_assignable_expression(self, tree) -> Tree:
        if len(tree.children) == 1:
            return tree.children[0]
        return TreeWithLanguageUnit(tree, DirectlyAssignableExpression(*tree.children))

    @v_args(tree=True)
    def variable_declaration(self, tree):
        variable_name_token, type_name_token, var_or_val_token = tree.children
        return TreeWithLanguageUnit(
            tree, VariableDeclaration(variable_name_token, type_name_token, var_or_val_token))

    @v_args(tree=True)
    def additive_expression(self, tree):
        return TreeWithLanguageUnit(tree, AdditiveExpression(*tree.children))

    @v_args(tree=True)
    # TODO(@pochka15): test this!!!
    def prefix_unary_expression(self, tree):
        prefix_operators = tree.children[0:len(tree.children) - 1]
        postfix_unary_expression = tree.children[len(tree.children) - 1]
        return TreeWithLanguageUnit(tree, PrefixUnaryExpression(prefix_operators, postfix_unary_expression))
