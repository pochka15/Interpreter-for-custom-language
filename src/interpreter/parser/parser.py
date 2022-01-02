from typing import TextIO, Optional

from lark import Tree, Token

from interpreter.scanner.scanner import Scanner
from interpreter.scanner.tokens import Token as Tk
from interpreter.scanner.tokens_controller import TokensController


class UnexpectedToken(Exception):
    pass


class PrimaryExpressionException(Exception):
    pass


def strict_match(token: Token, expected_type: Tk, err_msg: str = "") -> bool:
    if token is None:
        raise Exception("Tried to match None token")
    if token.type != expected_type.name:
        raise UnexpectedToken(
            f"Unexpected token type found: {token} ({token.line}:{token.column}), "
            f"expected to see: {expected_type.name}\n{err_msg}")
    return True


def match(token: Token, expected_type: Tk) -> bool:
    if token is None:
        return False
    return token.type == expected_type.name


class RecursiveDescentParser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.tokens_controller = TokensController()

    def parse(self, file: TextIO) -> Tree:
        self.tokens_controller.reload(self.scanner.iter_tokens(file))
        root = self.build_start_node()
        token = self.tokens_controller.next()
        if token is not None:
            raise Exception(f"Couldn't parse: {token} ({token.type})\nExpected no more tokens")
        return root

    # start: function_declaration*
    def build_start_node(self):
        children = []
        while self.tokens_controller.peek() is not None:
            children.append(self.build_function_declaration())
        return Tree("start", children)

    # function_declaration: NAME "(" function_parameters? ")" function_return_type "{" statements_block "}"
    def build_function_declaration(self):
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        strict_match(self.tokens_controller.next(), Tk.LEFT_PAREN)

        token = self.tokens_controller.peek()
        if match(token, Tk.RIGHT_PAREN):
            function_parameters = Tree("function_parameters", [])
        else:
            function_parameters = self.build_function_parameters()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_PAREN)

        function_return_type = self.build_function_return_type()

        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        statements_block = self.build_statements_block()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)

        return Tree("function_declaration", [name,
                                             function_parameters,
                                             function_return_type,
                                             statements_block])

    # function_parameters: function_parameter ("," function_parameter)*
    def build_function_parameters(self):
        first = self.build_function_parameter()
        rest = []
        while match(self.tokens_controller.peek(), Tk.COMMA):
            self.tokens_controller.next()
            param = self.build_function_parameter()
            rest.append(param)
        children = [first] + rest
        return Tree("function_parameters", children)

    # Inline function_return_type: NAME
    def build_function_return_type(self) -> Token:
        token = self.tokens_controller.next()
        strict_match(token, Tk.NAME)
        return token

    # statements_block: statement*
    def build_statements_block(self):
        children = []
        while not match(self.tokens_controller.peek(), Tk.RIGHT_CURLY_BR):
            children.append(self.build_statement())
        return Tree("statements_block", children)

    # NAME type
    def build_function_parameter(self) -> Tree:
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        _type = self.build_type()
        return Tree("function_parameter", [name, _type])

    # NAME ("." NAME)*
    def build_type(self) -> Tree:
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        children = [name]
        token = self.tokens_controller.peek()
        while token is not None and match(token, Tk.DOT):
            name = self.tokens_controller.next()
            strict_match(name, Tk.NAME)
            children.append(name)
        return Tree("type", children)

    # Inline statement: assignment | for_statement | while_statement | expression | jump_statement
    def build_statement(self):
        possible_first_token_for_statement = Tk.FOR
        possible_first_token_return_stmt = Tk.RETURN
        possible_first_token_break = Tk.BREAK
        token = self.tokens_controller.peek()
        if match(token, possible_first_token_return_stmt) or match(token, possible_first_token_break):
            return self.build_jump_statement()
        if match(token, possible_first_token_for_statement):
            return self.build_for_statement()
        if match(token, Tk.WHILE):
            return self.build_while_statement()
        else:
            if match(token, Tk.VAR) or match(token, Tk.LET):
                return self.build_assignment()
            else:
                expression = self.build_prefix_unary_expression()
                if match(self.tokens_controller.peek(), Tk.ASSIGNMENT_AND_OPERATOR):
                    return self.build_assignment(expression)
                return self.build_expression(expression)

    # Inline jump_statement: return_expression | BREAK
    def build_jump_statement(self) -> Tree:
        if match(self.tokens_controller.peek(), Tk.RETURN):
            return self.build_return_statement()
        token = self.tokens_controller.next()
        strict_match(token, Tk.BREAK)
        return token

    # Inline expression: disjunction
    def build_expression(self, prebuilt_prefix_unary_expression: Optional = None) -> Tree:
        return self.build_disjunction(prebuilt_prefix_unary_expression)

    # return_statement: RETURN expression?
    def build_return_statement(self):
        def is_new_line() -> bool:
            return match(self.tokens_controller.peek(), Tk.NEWLINE)

        strict_match(self.tokens_controller.next(), Tk.RETURN)
        next_is_new_line = self.tokens_controller.include_new_lines(is_new_line)
        if not next_is_new_line:
            children = [self.build_expression()]
        else:
            children = []
        return Tree("return_statement", children)

    def skip_new_lines(self):
        token = self.tokens_controller.peek()
        counter = 0
        while match(token, Tk.NEWLINE):
            counter += 1
            self.tokens_controller.next()
            token = self.tokens_controller.peek()
        return counter

    # // Optional inline
    # disjunction: conjunction (OR conjunction)*
    def build_disjunction(self, prebuilt_prefix_unary_expression: Optional = None):
        children = [self.build_conjunction(prebuilt_prefix_unary_expression)]
        while match(self.tokens_controller.peek(), Tk.OR):
            self.tokens_controller.next()
            children.append(self.build_conjunction())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("disjunction", children)

    # // Optional inline
    # conjunction: equality (AND equality)*
    def build_conjunction(self, prebuilt_prefix_unary_expression: Optional = None):
        children = [self.build_equality(prebuilt_prefix_unary_expression)]
        while match(self.tokens_controller.peek(), Tk.AND):
            self.tokens_controller.next()
            children.append(self.build_equality())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("conjunction", children)

    # // Optional inline
    # equality: comparison (EQUALITY_OPERATOR comparison)?
    def build_equality(self, prebuilt_prefix_unary_expression: Optional = None):
        children = [self.build_comparison(prebuilt_prefix_unary_expression)]
        if match(self.tokens_controller.peek(), Tk.EQUALITY_OPERATOR):
            children.append(self.tokens_controller.next())
            children.append(self.build_comparison())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("equality", children)

    # // Optional inline
    # comparison: additive_expression (COMPARISON_OPERATOR additive_expression)*
    def build_comparison(self, prebuilt_prefix_unary_expression: Optional = None):
        children = [self.build_additive_expression(prebuilt_prefix_unary_expression)]
        while match(self.tokens_controller.peek(), Tk.COMPARISON_OPERATOR):
            children.append(self.tokens_controller.next())
            children.append(self.build_additive_expression())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("comparison", children)

    # // Optional inline
    # additive_expression: multiplicative_expression (ADDITIVE_OPERATOR multiplicative_expression)*
    def build_additive_expression(self, prebuilt_prefix_unary_expression: Optional = None):
        children = [self.build_multiplicative_expression(prebuilt_prefix_unary_expression)]
        while match(self.tokens_controller.peek(), Tk.ADDITIVE_OPERATOR):
            children.append(self.tokens_controller.next())
            children.append(self.build_multiplicative_expression())
        if len(children) == 1:
            return children[0]
        else:
            return Tree("additive_expression", children)

    # // Optional inline
    # multiplicative_expression: prefix_unary_expression (MULTIPLICATIVE_OPERATOR prefix_unary_expression)*
    def build_multiplicative_expression(self, prebuilt_prefix_unary_expression: Optional = None):
        x = prebuilt_prefix_unary_expression
        children = [x if x is not None else self.build_prefix_unary_expression()]
        while match(self.tokens_controller.peek(), Tk.MULTIPLICATIVE_OPERATOR):
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
        if (match(self.tokens_controller.peek(), Tk.NEGATION) or
                match(self.tokens_controller.peek(), Tk.ADDITIVE_OPERATOR)):
            children.append(self.tokens_controller.next())
        children.append(self.build_postfix_unary_expression())
        if len(children) == 1:
            return children[0]
        return Tree("prefix_unary_expression", children)

    # // Optional inline
    # postfix_unary_expression: primary_expression postfix_unary_suffix*
    def build_postfix_unary_expression(self):
        children = [self.build_primary_expression()]
        while (match(self.tokens_controller.peek(), Tk.LEFT_PAREN) or
               match(self.tokens_controller.peek(), Tk.LEFT_SQR_BR) or
               match(self.tokens_controller.peek(), Tk.DOT)):
            children.append(self.postfix_unary_suffix())

        if len(children) == 1:
            return children[0]
        return Tree("postfix_unary_expression", children)

    # // Inline
    # postfix_unary_suffix: call_suffix | indexing_suffix | navigation_suffix
    def postfix_unary_suffix(self):
        token = self.tokens_controller.peek()
        if match(token, Tk.LEFT_PAREN):
            return self.build_call_suffix()
        if match(token, Tk.LEFT_SQR_BR):
            return self.build_indexing_suffix()
        if strict_match(token, Tk.DOT, "Tried to match postfix_unary_suffix, other possible tokens: '(' or '['"):
            return self.build_navigation_suffix()

    # call_suffix: "(" function_call_arguments? ")"
    # ---
    # # Inline
    # function_call_arguments: expression("," expression)*
    def build_call_suffix(self):
        children = []
        strict_match(self.tokens_controller.next(), Tk.LEFT_PAREN)

        # First: expression?
        if not match(self.tokens_controller.peek(), Tk.RIGHT_PAREN):
            children.append(self.build_expression())

        # Rest: (',' expression)*
        while not match(self.tokens_controller.peek(), Tk.RIGHT_PAREN):
            strict_match(self.tokens_controller.next(), Tk.COMMA)
            children.append(self.build_expression())

        strict_match(self.tokens_controller.next(), Tk.RIGHT_PAREN)
        return Tree("call_suffix", children)

    # indexing_suffix: "[" expression "]"
    def build_indexing_suffix(self):
        strict_match(self.tokens_controller.next(), Tk.LEFT_SQR_BR)
        expression = self.build_expression()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_SQR_BR)
        return Tree("indexing_suffix", [expression])

    # navigation_suffix: "." NAME
    def build_navigation_suffix(self):
        dot = self.tokens_controller.next()
        strict_match(dot, Tk.DOT)
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        return Tree("navigation_suffix", [name])

    # // Inline
    # primary_expression: "(" expression ")"
    #   | identifier
    #   | simple_literal
    #   | collection_literal
    #   | if_expression
    def build_primary_expression(self):
        if match(self.tokens_controller.peek(), Tk.NAME):
            return self.build_identifier()

        if match(self.tokens_controller.peek(), Tk.LEFT_PAREN):
            return self.build_parenthesized_expression()

        simple_literal = self.try_to_build_simple_literal()
        if simple_literal is not None:
            return simple_literal

        if match(self.tokens_controller.peek(), Tk.LEFT_SQR_BR):
            return self.build_collection_literal()

        if match(self.tokens_controller.peek(), Tk.IF):
            return self.build_if_expression()

        token = self.tokens_controller.peek()
        raise PrimaryExpressionException(f"Primary expression cannot start with token: '{token}' ({token.type})")

    def try_to_build_simple_literal(self):
        simple_literal_token_types = [Tk.STRING, Tk.BOOLEAN, Tk.DEC_NUMBER, Tk.FLOAT_NUMBER]
        token = self.tokens_controller.peek()
        for type_ in simple_literal_token_types:
            if match(token, type_):
                return self.tokens_controller.next()

    # // Inline
    # identifier: NAME
    def build_identifier(self):
        token = self.tokens_controller.next()
        strict_match(token, Tk.NAME)
        return token

    # assignment: variable_declaration ASSIGNMENT_OPERATOR expression
    #   | prefix_unary_expression ASSIGNMENT_AND_OPERATOR expression
    def build_assignment(self, prebuilt_prefix_unary_expression: Optional = None):
        token = self.tokens_controller.peek()
        if match(token, Tk.VAR) or match(token, Tk.LET):
            variable_declaration = self.build_variable_declaration()
            operator = self.tokens_controller.next()
            strict_match(operator, Tk.ASSIGNMENT_OPERATOR)
            expression = self.build_expression()
            return Tree("assignment", [variable_declaration, operator, expression])
        else:
            x = prebuilt_prefix_unary_expression
            prefix_expression = x if x is not None else self.build_prefix_unary_expression()
            operator = self.tokens_controller.next()
            strict_match(operator, Tk.ASSIGNMENT_AND_OPERATOR)
            expression = self.build_expression()
            return Tree("assignment", [prefix_expression, operator, expression])

    # variable_declaration: (VAR | CONST) NAME type
    def build_variable_declaration(self):
        modifier = self.tokens_controller.next()
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        type_ = self.build_type()
        return Tree("variable_declaration", [modifier, name, type_])

    def build_parenthesized_expression(self):
        strict_match(self.tokens_controller.next(), Tk.LEFT_PAREN)
        node = self.build_expression()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_PAREN)
        return node

    # collection_literal: "[" expression ("," expression)* "]" | "[" "]"
    def build_collection_literal(self):
        children = []
        strict_match(self.tokens_controller.next(), Tk.LEFT_SQR_BR)

        if not match(self.tokens_controller.peek(), Tk.RIGHT_SQR_BR):
            children.append(self.build_expression())
            while match(self.tokens_controller.peek(), Tk.COMMA):
                self.tokens_controller.next()
                children.append(self.build_expression())

        strict_match(self.tokens_controller.next(), Tk.RIGHT_SQR_BR)
        return Tree("collection_literal", children)

    # if_expression: IF expression "{" statements_block "}"
    #   | IF expression "{" statements_block "}" elseif_expression* else_expression?
    def build_if_expression(self):
        children = []
        strict_match(self.tokens_controller.next(), Tk.IF)
        children.append(self.build_expression())
        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        children.append(self.build_statements_block())
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)

        while match(self.tokens_controller.peek(), Tk.ELIF):
            children.append(self.build_elseif_expression())

        if match(self.tokens_controller.peek(), Tk.ELSE):
            children.append(self.build_else_expression())

        return Tree("if_expression", children)

    # else_expression: ELSE "{" statements_block "}"
    def build_else_expression(self):
        match(self.tokens_controller.next(), Tk.ELSE)
        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        block = self.build_statements_block()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)
        return Tree("else_expression", [block])

    # elseif_expression: ELIF expression "{" statements_block "}"
    def build_elseif_expression(self):
        match(self.tokens_controller.next(), Tk.ELIF)
        expr = self.build_expression()
        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        block = self.build_statements_block()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)
        return Tree("elseif_expression", [expr, block])

    # for_statement: FOR NAME IN expression "{" statements_block "}"
    def build_for_statement(self):
        strict_match(self.tokens_controller.next(), Tk.FOR)
        name = self.tokens_controller.next()
        strict_match(name, Tk.NAME)
        strict_match(self.tokens_controller.next(), Tk.IN)
        expression = self.build_expression()
        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        statements_block = self.build_statements_block()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)
        return Tree("for_statement", [name, expression, statements_block])

    # while_statement: WHILE expression "{" statements_block "}"
    def build_while_statement(self):
        strict_match(self.tokens_controller.next(), Tk.WHILE)
        expression = self.build_expression()
        strict_match(self.tokens_controller.next(), Tk.LEFT_CURLY_BR)
        statements_block = self.build_statements_block()
        strict_match(self.tokens_controller.next(), Tk.RIGHT_CURLY_BR)
        return Tree("while_statement", [expression, statements_block])
