from typing import Iterator, Optional, List, TextIO

from lark import Tree, Token

from scanner.scanner import Scanner


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
        self.tokens_iterator: Optional[Iterator[Token]] = None
        self.cached_tokens = []
        self.peeked_token: Optional[Token] = None

    def parse(self, file: TextIO) -> Tree:
        self.tokens_iterator = self.scanner.iter_tokens(file)
        root = self.build_start_node()
        token = self.next_token()
        if token is not None:
            raise Exception("Couldn't parse: " + str(token) + "\nExpected no more tokens")
        return root

    # start: (function_declaration (NEWLINE function_declaration)*)?
    def build_start_node(self) -> Tree:
        children = []
        if self.peek_token() is not None:
            first = self.build_function_declaration()
            rest = self.build_rest_function_declarations()
            children = [first] + rest
        return Tree("start", children)

    def build_rest_function_declarations(self) -> List:
        token = self.next_token()
        out = []
        while token is not None:
            strict_match(token, 'NEWLINE')
            out.append(self.build_function_declaration())
            token = self.next_token()
        return out

    # function_declaration: NAME "(" function_parameters ")" function_return_type "{" statements_block "}"
    def build_function_declaration(self) -> Tree:
        name = self.next_token()
        strict_match(name, "NAME")
        strict_match(self.next_token(), "LEFT_PAREN")
        token = self.peek_token()
        if match(token, "RIGHT_PAREN"):
            function_parameters = Tree("function_parameters", [])
        else:
            function_parameters = self.build_function_parameters()
        strict_match(self.next_token(), "RIGHT_PAREN")
        function_return_type = self.build_function_return_type()
        statements_block = self.build_statements_block()
        return Tree("function_declaration", [name, function_parameters, function_return_type, statements_block])

    # function_parameters: (function_parameter ("," function_parameter)*)?
    def build_function_parameters(self) -> Tree:
        first = self.build_function_parameter()
        children = [first] + self.build_rest_function_parameters()
        return Tree("function_parameters", children)

    # Inline
    # function_return_type: NAME
    def build_function_return_type(self) -> Token:
        token = self.next_token()
        strict_match(token, "NAME")
        return token

    # statements_block: (statement (NEWLINE statement+)*)?
    def build_statements_block(self) -> Tree:
        strict_match(self.next_token(), "LEFT_CURLY_BR")
        children = []
        self.skip_new_lines()
        if not match(self.peek_token(), "RIGHT_CURLY_BR"):
            first = self.build_statement()
            children = [first] + self.build_rest_statements_block()
            self.skip_new_lines()
        strict_match(self.next_token(), "RIGHT_CURLY_BR")
        return Tree("statements_block", children)

    def cache_token(self, token):
        self.cached_tokens.append(token)
        return token

    def next_token(self) -> Optional[Token]:
        try:
            peeked = self.peeked_token
            if peeked is not None:
                self.peeked_token = None
                return peeked
            return self.cache_token(next(self.tokens_iterator))
        except StopIteration:
            return None

    def peek_token(self):
        try:
            peeked = self.peeked_token
            if peeked is not None:
                return peeked
            token = next(self.tokens_iterator)
            self.peeked_token = token
            return token
        except StopIteration:
            self.peeked_token = None
            return None

    # NAME type
    def build_function_parameter(self) -> Tree:
        name = self.next_token()
        strict_match(name, "NAME")
        _type = self.build_type()
        return Tree("function_parameter", [name, _type])

    # NAME ("." NAME)*
    def build_type(self) -> Tree:
        name = self.next_token()
        strict_match(name, "NAME")
        children = [name]
        token = self.peek_token()
        while token is not None and match(token, "DOT"):
            name = self.next_token()
            strict_match(name, "NAME")
            children.append(name)
        return Tree("type", children)

    # (comma function_parameter)*
    def build_rest_function_parameters(self) -> List[Tree]:
        out = []
        while match(self.peek_token(), "COMMA"):
            self.next_token()
            param = self.build_function_parameter()
            out.append(param)
        return out

    def build_statement(self) -> Tree:
        return self.next_token()

    def build_rest_statements_block(self) -> List[Tree]:
        out = []
        while self.skip_new_lines() > 0 and not match(self.peek_token(), "RIGHT_CURLY_BR"):
            statement = self.build_statement()
            out.append(statement)
        return out

    def skip_new_lines(self) -> int:
        counter = 0
        while match(self.peek_token(), "NEWLINE"):
            self.next_token()
            counter += 1
        return counter
