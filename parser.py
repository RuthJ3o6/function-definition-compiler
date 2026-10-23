
# parser.py.
# Recursive-descent parser for the Function Definition Compiler


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    # Get token type or value from lexer tuples
    def kind(self, token):
        if token is None:
            return "EOF"

        return token[0]

    def value(self, token):
        if token is None:
            return ""

        return token[1]

    def current(self):
        if self.pos >= len(self.tokens):
            return None

        return self.tokens[self.pos]

    def at(self, expected):
        token = self.current()

        if token is None:
            return expected == "EOF"

        return (
            self.kind(token) == expected
            or self.value(token) == expected
        )

    def error(self, message):
        token = self.current()

        if token is None:
            location = "at end of input"
        else:
            location = "near " + repr(self.value(token))

        raise ParseError(
            "Syntax error " + location + ": " + message
        )

    def take(self, expected):
        if not self.at(expected):
            token = self.current()

            if token is None:
                found = "end of input"
            else:
                found = repr(self.value(token))

            self.error(
                "expected " + repr(expected) +
                ", found " + found
            )

        token = self.current()
        self.pos += 1
        return token

    def take_id(self):
        if not self.at("id"):
            self.error("expected an identifier")

        return self.take("id")[1]

    def take_number(self):
        if not self.at("number"):
            self.error("expected a number")

        return self.take("number")[1]

    # Program -> TopLevelStatement*
    def parse(self):
        statements = []

        while self.current() is not None:
            statements.append(self.parse_top_level())

        return {
            "type": "Program",
            "statements": statements
        }

    # Top-level statements
    def parse_top_level(self):
        if self.at("def"):
            return self.parse_function()

        if self.at("print"):
            node = self.parse_print()
            self.take(";")
            return node

        if self.at("id"):
            if self.pos + 1 < len(self.tokens):
                next_token = self.tokens[self.pos + 1]

                if next_token[1] == "(":
                    node = self.parse_call()
                    self.take(";")
                    return node

                if next_token[1] == "=":
                    node = self.parse_assignment()
                    self.take(";")
                    return node

        self.error(
            "expected a function definition, assignment, "
            "function call, or print statement"
        )

    # FunctionDef -> def id ( ParamList ) begin Body end ;
    def parse_function(self):
        self.take("def")

        name = self.take_id()
        self.take("(")

        params = []

        if not self.at(")"):
            params.append(self.take_id())

            while self.at(","):
                self.take(",")
                params.append(self.take_id())

        self.take(")")
        self.take("begin")

        body = []

        while self.current() is not None and not self.at("end"):
            body.append(self.parse_body_statement())

        self.take("end")
        self.take(";")

        return {
            "type": "FunctionDef",
            "name": name,
            "params": params,
            "body": body
        }

    # Statements permitted inside a function
    def parse_body_statement(self):
        if self.at("return"):
            node = self.parse_return()
            self.take(";")
            return node

        if self.at("print"):
            node = self.parse_print()
            self.take(";")
            return node

        if self.at("id"):
            if self.pos + 1 < len(self.tokens):
                next_token = self.tokens[self.pos + 1]

                if next_token[1] == "(":
                    node = self.parse_call()
                    self.take(";")
                    return node

                if next_token[1] == "=":
                    node = self.parse_assignment()
                    self.take(";")
                    return node

        self.error(
            "expected return, print, assignment, "
            "or function call inside function"
        )

    # Return -> return Expr ;
    def parse_return(self):
        self.take("return")

        return {
            "type": "Return",
            "value": self.parse_expr()
        }

    # Print -> print ( Expr )
    def parse_print(self):
        self.take("print")
        self.take("(")

        expr = self.parse_expr()

        self.take(")")

        return {
            "type": "Print",
            "value": expr
        }

    # Assignment -> id = Expr
    def parse_assignment(self):
        name = self.take_id()
        self.take("=")

        return {
            "type": "Assignment",
            "name": name,
            "value": self.parse_expr()
        }

    # Call -> id ( Arguments )
    def parse_call(self):
        name = self.take_id()
        self.take("(")

        args = []

        if not self.at(")"):
            args.append(self.parse_expr())

            while self.at(","):
                self.take(",")
                args.append(self.parse_expr())

        self.take(")")

        return {
            "type": "Call",
            "name": name,
            "args": args
        }

    # Expr -> Term ((+ | -) Term)*
    def parse_expr(self):
        node = self.parse_term()

        while self.at("+") or self.at("-"):
            op = self.value(self.current())
            self.pos += 1

            right = self.parse_term()

            node = {
                "type": "BinaryOp",
                "op": op,
                "left": node,
                "right": right
            }

        return node

    # Term -> Factor ((* | /) Factor)*
    def parse_term(self):
        node = self.parse_factor()

        while self.at("*") or self.at("/"):
            op = self.value(self.current())
            self.pos += 1

            right = self.parse_factor()

            node = {
                "type": "BinaryOp",
                "op": op,
                "left": node,
                "right": right
            }

        return node

    # Factor -> id | number | Call | ( Expr )
    def parse_factor(self):
        if self.at("id"):
            if self.pos + 1 < len(self.tokens):
                if self.tokens[self.pos + 1][1] == "(":
                    return self.parse_call()

            return {
                "type": "Identifier",
                "name": self.take_id()
            }

        if self.at("number"):
            return {
                "type": "Number",
                "value": self.take_number()
            }

        if self.at("("):
            self.take("(")
            node = self.parse_expr()
            self.take(")")
            return node

        self.error(
            "expected an identifier, number, function call, "
            "or parenthesized expression"
        )


def parse(tokens):
    """Public entry point used by main.py and app.py."""
    return Parser(tokens).parse()
