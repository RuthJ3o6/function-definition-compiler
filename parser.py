# parser.py
# Recursive-descent parser for the grammar in grammar.txt.
 
class ParseError(Exception):
    pass
 
 
class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0
 
    def _field(self, token, name, default=None):
        if isinstance(token, dict):
            return token.get(name, default)
        return getattr(token, name, default)
 
    def value(self, token):
        return str(self._field(token, "value", self._field(token, "lexeme", "")))
 
    def kind(self, token):
        raw = self._field(token, "type", self._field(token, "kind", ""))
        raw = str(raw).upper()
        # Keywords may be represented by their spelling or by a token type.
        aliases = {
            "IDENTIFIER": "ID", "IDENT": "ID",
            "INTEGER": "NUMBER", "NUM": "NUMBER",
            "FLOAT": "NUMBER", "INT": "NUMBER",
            "SEMICOLON": ";", "COMMA": ",",
            "LPAREN": "(", "RPAREN": ")",
            "ASSIGN": "=", "PLUS": "+", "MINUS": "-",
            "MULTIPLY": "*", "TIMES": "*", "DIVIDE": "/",
            "SLASH": "/"
        }
        if raw in aliases:
            return aliases[raw]
        spelling = self.value(token)
        if spelling in {"def", "begin", "end", "return", "print",
                        "(", ")", ",", ";", "=", "+", "-", "*", "/"}:
            return spelling
        if raw in {"DEF", "BEGIN", "END", "RETURN", "PRINT"}:
            return raw.lower()
        if raw in {"ID", "NUMBER", "EOF"}:
            return raw
        return raw
 
    def current(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
 
    def at(self, expected):
        tok = self.current()
        return tok is not None and (
            self.kind(tok) == expected or self.value(tok) == expected
        )
 
    def location(self):
        tok = self.current()
        if tok is None:
            return "at end of input"
        line = self._field(tok, "line", "?")
        col = self._field(tok, "column", self._field(tok, "col", "?"))
        return f"at line {line}, column {col}"
 
    def error(self, message):
        raise ParseError(f"Syntax error {self.location()}: {message}")
 
    def take(self, expected):
        if not self.at(expected):
            got = self.value(self.current()) if self.current() else "end of input"
            self.error(f"expected {expected!r}, found {got!r}")
        tok = self.current()
        self.pos += 1
        return tok
 
    def take_id(self):
        if not self.at("ID"):
            self.error("expected an identifier")
        tok = self.current()
        self.pos += 1
        return self.value(tok)
 
    def take_number(self):
        if not self.at("NUMBER"):
            self.error("expected a number")
        tok = self.current()
        self.pos += 1
        return self.value(tok)
 
    def parse(self):
        statements = []
        while self.current() is not None and not self.at("EOF"):
            before = self.pos
            statements.append(self.parse_top_level())
            if self.pos == before:
                self.error("parser made no progress")
        if self.at("EOF"):
            self.pos += 1
        if self.current() is not None:
            self.error("unexpected tokens after program")
        return {"type": "Program", "statements": statements}
 
    def parse_top_level(self):
        if self.at("def"):
            return self.parse_function()
        if self.at("print"):
            node = self.parse_print()
            self.take(";")
            return node
        if self.at("ID") and self.pos + 1 < len(self.tokens):
            nxt = self.tokens[self.pos + 1]
            nxt_value = self.value(nxt)
            nxt_kind = self.kind(nxt)
            if nxt_value == "(" or nxt_kind == "(":
                node = self.parse_call()
                self.take(";")
                return node
            if nxt_value == "=" or nxt_kind == "=":
                node = self.parse_assignment()
                self.take(";")
                return node
        self.error("expected a function definition, assignment, function call, or print statement")
 
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
        # The sample grammar has a semicolon after a function definition.
        self.take(";")
        return {"type": "FunctionDef", "name": name,
                "params": params, "body": body}
 
    def parse_body_statement(self):
        if self.at("return"):
            node = self.parse_return()
            self.take(";")
            return node
        if self.at("print"):
            node = self.parse_print()
            self.take(";")
            return node
        if self.at("ID") and self.pos + 1 < len(self.tokens):
            nxt = self.tokens[self.pos + 1]
            if self.value(nxt) == "(" or self.kind(nxt) == "(":
                node = self.parse_call()
                self.take(";")
                return node
            if self.value(nxt) == "=" or self.kind(nxt) == "=":
                node = self.parse_assignment()
                self.take(";")
                return node
        self.error("expected return, print, assignment, or function call in function body")
 
    def parse_return(self):
        self.take("return")
        return {"type": "Return", "value": self.parse_expr()}
 
    def parse_print(self):
        self.take("print")
        self.take("(")
        expr = self.parse_expr()
        self.take(")")
        return {"type": "Print", "value": expr}
 
    def parse_assignment(self):
        name = self.take_id()
        self.take("=")
        return {"type": "Assignment", "name": name, "value": self.parse_expr()}
 
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
        return {"type": "Call", "name": name, "args": args}
 
    # Expr -> Term ((+ | -) Term)*
    def parse_expr(self):
        node = self.parse_term()
        while self.at("+") or self.at("-"):
            op = self.value(self.current())
            self.pos += 1
            right = self.parse_term()
            node = {"type": "BinaryOp", "op": op, "left": node, "right": right}
        return node
 
    # Term -> Factor ((* | /) Factor)*
    def parse_term(self):
        node = self.parse_factor()
        while self.at("*") or self.at("/"):
            op = self.value(self.current())
            self.pos += 1
            right = self.parse_factor()
            node = {"type": "BinaryOp", "op": op, "left": node, "right": right}
        return node
 
    def parse_factor(self):
        if self.at("ID"):
            # An identifier followed by '(' is a function call.
            if self.pos + 1 < len(self.tokens):
                nxt = self.tokens[self.pos + 1]
                if self.value(nxt) == "(" or self.kind(nxt) == "(":
                    return self.parse_call()
            return {"type": "Identifier", "name": self.take_id()}
        if self.at("NUMBER"):
            return {"type": "Number", "value": self.take_number()}
        if self.at("("):
            self.take("(")
            node = self.parse_expr()
            self.take(")")
            return node
        self.error("expected an identifier, number, function call, or parenthesized expression")
 
 
def parse(tokens):
    """Public entry point used by main.py."""
    return Parser(tokens).parse()
