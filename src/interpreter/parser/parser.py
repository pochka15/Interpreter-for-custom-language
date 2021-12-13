from typing import List, TextIO

from lark import Tree, Token

from interpreter.scanner.scanner import Scanner
from interpreter.scanner.tokens_controller import TokensController


class UnknownToken(Exception):
    pass


def strict_match(token: Token, expected_type: str, err_msg: str = "") -> bool:
    if token is None:
        raise Exception("Tried to match None token")
    if token.type != expected_type:
        raise UnknownToken(f"Unknown token type found: {str(token)}, expected to see: {expected_type}\n{err_msg}")
    return True


def match(token: Token, expected_type: str) -> bool:
    if token is None:
        return False
    return token.type == expected_type


class RecursiveDescentParser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.tokens_controller = TokensController()

    def parse(self, file: TextIO) -> Tree:
        self.tokens_controller.update_tokens(self.scanner.iter_tokens(file))
        root = self.build_start_node()
        token = self.tokens_controller.next()
        if token is not None:
            raise Exception("Couldn't parse: " + str(token) + "\nExpected no more tokens")
        return root

    # start: function_declaration*
    def build_start_node(self):
        children = []
        while self.tokens_controller.peek() is not None:
            children.append(self.build_function_declaration())
        return Tree("start", children)

    # function_declaration: NAME "(" function_parameters ")" function_return_type "{" statements_block "}"
    def build_function_declaration(self):
        name = self.tokens_controller.next()
        strict_match(name, "NAME")
        strict_match(self.tokens_controller.next(), "LEFT_PAREN")
        token = self.tokens_controller.peek()
        if match(token, "RIGHT_PAREN"):
            function_parameters = Tree("function_parameters", [])
        else:
            function_parameters = self.build_function_parameters()
        strict_match(self.tokens_controller.next(), "RIGHT_PAREN")
        function_return_type = self.build_function_return_type()
        statements_block = self.build_statements_block()
        return Tree("function_declaration", [name,
                                             function_parameters,
                                             function_return_type,
                                             statements_block])

    # function_parameters: (function_parameter ("," function_parameter)*)?
    def build_function_parameters(self):
        first = self.build_function_parameter()
        children = [first] + self.build_rest_function_parameters()
        return Tree("function_parameters", children)

    # Inline function_return_type: NAME
    def build_function_return_type(self) -> Token:
        token = self.tokens_controller.next()
        strict_match(token, "NAME")
        return token

    # Optional inline: statements_block: statement*
    def build_statements_block(self):
        strict_match(self.tokens_controller.next(), "LEFT_CURLY_BR")
        children = []
        self.skip_new_lines()
        if not match(self.tokens_controller.peek(), "RIGHT_CURLY_BR"):
            first = self.build_statement()
            children = [first] + self.build_rest_statements_block()
            self.skip_new_lines()
        strict_match(self.tokens_controller.next(), "RIGHT_CURLY_BR")
        if len(children) == 1:
            return children[0]
        return Tree("statements_block", children)

    # NAME type
    def build_function_parameter(self) -> Tree:
        name = self.tokens_controller.next()
        strict_match(name, "NAME")
        _type = self.build_type()
        return Tree("function_parameter", [name, _type])

    # NAME ("." NAME)*
    def build_type(self) -> Tree:
        name = self.tokens_controller.next()
        strict_match(name, "NAME")
        children = [name]
        token = self.tokens_controller.peek()
        while token is not None and match(token, "DOT"):
            name = self.tokens_controller.next()
            strict_match(name, "NAME")
            children.append(name)
        return Tree("type", children)

    # (comma function_parameter)*
    def build_rest_function_parameters(self) -> List:
        out = []
        while match(self.tokens_controller.peek(), "COMMA"):
            self.tokens_controller.next()
            param = self.build_function_parameter()
            out.append(param)
        return out

    # TODO(@pochka15): impl
    # Inline statement: assignment | for_statement | while_statement | expression | jump_statement
    def build_statement(self):
        token = self.tokens_controller.peek()
        if match(token, "RETURN") or match(token, "BREAK"):
            return self.build_jump_statement()
        raise Exception("not implemented")

    def build_rest_statements_block(self) -> List:
        out = []
        while self.skip_new_lines() > 0 and not match(self.tokens_controller.peek(), "RIGHT_CURLY_BR"):
            statement = self.build_statement()
            out.append(statement)
        return out

    # Inline jump_statement: return_expression | BREAK
    def build_jump_statement(self) -> Tree:
        if match(self.tokens_controller.peek(), "RETURN"):
            return self.build_return_statement()
        token = self.tokens_controller.next()
        strict_match(token, "BREAK")
        return token

    # Inline expression: disjunction
    def build_expression(self) -> Tree:
        return self.build_disjunction()

    # return_statement: RETURN expression?
    def build_return_statement(self):
        def is_new_line() -> bool:
            return match(self.tokens_controller.peek(), "NEWLINE")

        strict_match(self.tokens_controller.next(), "RETURN")
        next_is_new_line = self.tokens_controller.include_new_lines(is_new_line)
        if not next_is_new_line:
            children = [self.build_expression()]
        else:
            children = []
        return Tree("return_statement", children)

    def skip_new_lines(self):
        token = self.tokens_controller.peek()
        counter = 0
        while match(token, "NEWLINE"):
            counter += 1
            self.tokens_controller.next()
            token = self.tokens_controller.peek()
        return counter

    # // Optional inline
    # disjunction: conjunction (OR conjunction)*
    def build_disjunction(self):
        children = [self.build_conjunction()]
        while match(self.tokens_controller.peek(), "OR"):
            self.tokens_controller.next()
            children.append(self.build_conjunction())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("disjunction", children)

    # // Optional inline
    # conjunction: equality (AND equality)*
    def build_conjunction(self):
        children = [self.build_equality()]
        while match(self.tokens_controller.peek(), "AND"):
            self.tokens_controller.next()
            children.append(self.build_equality())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("conjunction", children)

    # // Optional inline
    # equality: comparison (EQUALITY_OPERATOR comparison)*
    def build_equality(self):
        children = [self.build_comparison()]
        while match(self.tokens_controller.peek(), "EQUALITY_OPERATOR"):
            children.append(self.tokens_controller.next())
            children.append(self.build_comparison())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("equality", children)

    # // Optional inline
    # comparison: additive_expression (COMPARISON_OPERATOR additive_expression)*
    def build_comparison(self):
        children = [self.build_additive_expression()]
        while match(self.tokens_controller.peek(), "COMPARISON_OPERATOR"):
            children.append(self.tokens_controller.next())
            children.append(self.build_additive_expression())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("comparison", children)

    # // Optional inline
    # additive_expression: multiplicative_expression (ADDITIVE_OPERATOR multiplicative_expression)*
    def build_additive_expression(self):
        children = [self.build_multiplicative_expression()]
        while match(self.tokens_controller.peek(), "ADDITIVE_OPERATOR"):
            children.append(self.tokens_controller.next())
            children.append(self.build_multiplicative_expression())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("additive_expression", children)

    # // Optional inline
    # multiplicative_expression: prefix_unary_expression (MULTIPLICATIVE_OPERATOR prefix_unary_expression)*
    def build_multiplicative_expression(self):
        children = [self.build_prefix_unary_expression()]
        while match(self.tokens_controller.peek(), "MULTIPLICATIVE_OPERATOR"):
            children.append(self.tokens_controller.next())
            children.append(self.build_prefix_unary_expression())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("multiplicative_expression", children)

    # // Optional inline
    # prefix_unary_expression: prefix_operator? postfix_unary_expression
    def build_prefix_unary_expression(self):
        children = []
        if (match(self.tokens_controller.peek(), "NEGATION") or
                match(self.tokens_controller.peek(), "ADDITIVE_OPERATOR")):
            children.append(self.tokens_controller.next())
        children.append(self.build_postfix_unary_expression())
        if len(children) == 1:
            return children[0]
        return Tree("prefix_unary_expression", children)

    # TODO(@pochka15): finish
    def build_postfix_unary_expression(self):
        return self.tokens_controller.next()
