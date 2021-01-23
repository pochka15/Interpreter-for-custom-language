from functools import partial
from operator import itemgetter
from typing import Iterable, Iterator

from lark import Transformer, Tree, Token, v_args

from language_units import *


def is_val(value: str) -> bool:
    return True if value == 'val' else False


def identity(x):
    return x


# noinspection PyTypeChecker,PyMethodMayBeStatic,PyPep8Naming


def wrapped_token(applied_func=lambda x: x):
    return lambda _, token: TokenAndLanguageUnitPair(token, applied_func(token.value))


def wrapped_tree(container, children_lambda=identity):
    def inner(_, tree):
        return TreeWithLanguageUnit(tree, container(*(children_lambda(tree.children))))

    return inner


@v_args(tree=True)
class TreeTransformer(Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)

    # ADDITIVE_OPERATOR
    # NAME
    # PREFIX_OPERATOR
    # ASSIGNMENT_AND_OPERATOR
    # ASSIGNMENT_OPERATOR
    __default_token__ = wrapped_token()

    DEC_NUMBER = wrapped_token(int)

    def VAR(self, token: Token):
        token.update("IS_VAL", token.value)
        return wrapped_token(is_val)(self, token)

    def VAL(self, token: Token):
        token.update("IS_VAL", token.value)
        return wrapped_token(is_val)(self, token)

    def statements_block(self, block_tree: Tree):
        block_tree.children.append(Token('BLOCK_END', ''))
        return block_tree

    indexing_suffix = wrapped_tree(IndexingSuffix)
    directly_assignable_expression = wrapped_tree(DirectlyAssignableExpression)
    variable_declaration = wrapped_tree(VariableDeclaration)
    expression = wrapped_tree(Expression)
    assignment = wrapped_tree(Assignment)
    disjunction = wrapped_tree(Disjunction, lambda children: tuple([children]))
    conjunction = wrapped_tree(Conjunction, lambda children: tuple([children]))
    equality = wrapped_tree(Equality, lambda children: (children[0], children[1: len(children)]))
    import_with_from = wrapped_tree(ImportWithFrom)
    as_name = wrapped_tree(AsName)
    function_call_arguments = wrapped_tree(FunctionCallArguments, lambda children: tuple([children]))
    import_targets = wrapped_tree(ImportTargets, lambda children: tuple([children]))
    type_arguments = wrapped_tree(TypeArguments, lambda children: tuple([children]))
    simple_user_type = wrapped_tree(SimpleUserType)
    postfix_unary_expression = wrapped_tree(
        PostfixUnaryExpression,
        lambda children: (children[0], children[1: len(children)]))
    import_without_from = wrapped_tree(
        ImportWithoutFrom,
        lambda children: tuple([children]))
    multiplicative_expression = wrapped_tree(
        MultiplicativeExpression,
        lambda children: (children[0], children[1: len(children)]))
    comparison = wrapped_tree(
        Comparison,
        lambda children: (children[0], children[1: len(children)]))
    additive_expression = wrapped_tree(
        AdditiveExpression,
        lambda children: (children[0], children[1: len(children)]))
    prefix_unary_expression = wrapped_tree(
        PrefixUnaryExpression,
        lambda children: (children[0:len(children) - 1], children[len(children) - 1]))

    def from_path(self, tree: Tree) -> TreeWithLanguageUnit:
        children = tree.children
        pair = children[0]
        if isinstance(pair, TokenAndLanguageUnitPair) \
                and pair.token.type == "RELATIVE_LOCATION":
            relative_location = pair
            starting_ind = 1
        else:
            relative_location = None
            starting_ind = 0
        return TreeWithLanguageUnit(tree, FromPath(relative_location,
                                                   children[starting_ind: len(children)]))

    def call_suffix(self, tree) -> TreeWithLanguageUnit:
        children = tree.children
        if len(children) == 2:
            return TreeWithLanguageUnit(tree, CallSuffix(*children))
        return TreeWithLanguageUnit(tree, CallSuffix(None, *children))

    def type(self, tree) -> TreeWithLanguageUnit:
        # children can be:
        # - Type (_parenthesized{type})
        # - 1+ SimpleUserType
        # - Name token (reduced SimpleUserType)
        children = tree.children
        first = children[0]
        if isinstance(first.unit, Type):
            first.unit.is_parenthesized = True
            return first
        return TreeWithLanguageUnit(tree, Type(children, False))

