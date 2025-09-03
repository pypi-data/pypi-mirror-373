from glc.lexer import TokenType, Token


# -------------------- AST Nodes --------------------
class ASTNode:
    pass


class Expr(ASTNode):
    pass


class NumberExpr(Expr):
    def __init__(self, value):
        self.value = value


class FloatExpr(Expr):
    def __init__(self, value):
        self.value = value


class BoolExpr(Expr):
    def __init__(self, value):
        self.value = value


class StringExpr(Expr):
    def __init__(self, value):
        self.value = value


class VariableExpr(Expr):
    def __init__(self, name):
        self.name = name


class BinaryExpr(Expr):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


# -------------------- Statements --------------------
class Stmt(ASTNode):
    pass


class ExprStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr


class LetStmt(Stmt):
    def __init__(self, name, type_, value):
        self.name = name
        self.type = type_
        self.value = value


class PrintStmt(Stmt):
    def __init__(self, value):
        self.value = value


class FunctionStmt(Stmt):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class IfStmt(Stmt):
    def __init__(self, condition, then_body, else_body):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class WhileStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


# -------------------- Parser --------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.END, "")

    def consume(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, type_, text=None):
        tok = self.peek()
        if tok.type == type_ and (text is None or tok.text == text):
            self.consume()
            return True
        return False

    # -------------------- Expressions --------------------
    def parse_primary(self):
        tok = self.peek()

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self.consume()
            expr = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                raise SyntaxError("Expected ')' after expression")
            return expr

        # Boolean literal
        if tok.type == TokenType.KEYWORD and tok.text in {"true", "false"}:
            self.consume()
            return BoolExpr(tok.text == "true")

        # Number literal
        if tok.type == TokenType.NUMBER:
            self.consume()
            if "." in tok.text:
                return FloatExpr(float(tok.text))
            else:
                return NumberExpr(int(tok.text))

        # String literal
        if tok.type == TokenType.STRING:
            self.consume()
            return StringExpr(tok.text)

        # Identifier
        if tok.type == TokenType.IDENTIFIER:
            self.consume()
            return VariableExpr(tok.text)

        raise SyntaxError(f"Unexpected token: {tok}")

    def parse_expression(self):
        lhs = self.parse_primary()
        while True:
            tok = self.peek()
            # Stop at these tokens
            if tok.type in {TokenType.RPAREN, TokenType.RBRACE, TokenType.END}:
                break
            # Only continue if we have a binary operator
            if tok.type not in {
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.GT,
                TokenType.LT,
                TokenType.GTE,
                TokenType.LTE,
                TokenType.EQ,
                TokenType.NEQ,
            }:
                break
            op = self.consume().text
            rhs = self.parse_primary()
            lhs = BinaryExpr(lhs, op, rhs)
        return lhs

    # -------------------- Statements --------------------
    def parse_statement(self):
        tok = self.peek()

        # Variable declaration
        if tok.type == TokenType.KEYWORD and tok.text in {
            "int",
            "float",
            "bool",
            "string",
        }:
            type_tok = self.consume()
            name_tok = self.consume()
            if not name_tok.type == TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected variable name, got {name_tok}")
            if not self.match(TokenType.ASSIGN):
                raise SyntaxError("Expected '='")
            value = self.parse_expression()
            return LetStmt(name_tok.text, type_tok.text, value)

        # Print statement
        elif tok.type == TokenType.KEYWORD and tok.text == "print":
            self.consume()
            if not self.match(TokenType.LPAREN):
                raise SyntaxError("Expected '(' after print")
            expr = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                raise SyntaxError("Expected ')' after print")
            return PrintStmt(expr)

        # If statement
        # If statement
        elif tok.type == TokenType.KEYWORD and tok.text == "if":
            self.consume()  # consume 'if'
            if not self.match(TokenType.LPAREN):
                raise SyntaxError("Expected '(' after if")
            condition = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                raise SyntaxError("Expected ')' after if condition")
            if not self.match(TokenType.LBRACE):
                raise SyntaxError("Expected '{' for if body")
            then_body = []
            while not self.match(TokenType.RBRACE):
                then_body.append(self.parse_statement())
            else_body = []
            if self.match(TokenType.KEYWORD, "else"):
                if not self.match(TokenType.LBRACE):
                    raise SyntaxError("Expected '{' for else body")
                while not self.match(TokenType.RBRACE):
                    else_body.append(self.parse_statement())
            return IfStmt(condition, then_body, else_body)
        # While statement
        elif tok.type == TokenType.KEYWORD and tok.text == "while":
            self.consume()  # consume 'while'
            if not self.match(TokenType.LPAREN):
                raise SyntaxError("Expected '(' after while")
            condition = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                raise SyntaxError("Expected ')' after while condition")
            if not self.match(TokenType.LBRACE):
                raise SyntaxError("Expected '{' for while body")
            body = []
            while not self.match(TokenType.RBRACE):
                body.append(self.parse_statement())
            return WhileStmt(condition, body)
        # Expression statement
        else:
            if (
                self.pos + 1 < len(self.tokens)
                and self.peek().type == TokenType.IDENTIFIER
                and self.pos + 2 < len(self.tokens)
                and self.tokens[self.pos + 1].type == TokenType.ASSIGN
            ):
                # This is an assignment: identifier = expression
                name_tok = self.consume()
                if not self.match(TokenType.ASSIGN):
                    raise SyntaxError("Expected '='")
                value = self.parse_expression()
                # Create a LetStmt without type (or create a new AssignStmt class)
                return LetStmt(name_tok.text, None, value)
            else:
                # This is just an expression
                return ExprStmt(self.parse_expression())

    # -------------------- Function --------------------
    def parse_function(self):
        if not self.match(TokenType.KEYWORD, "fn"):
            raise SyntaxError("Expected 'fn'")
        name_tok = self.consume()
        if not name_tok.type == TokenType.IDENTIFIER:
            raise SyntaxError("Expected function name")
        if not self.match(TokenType.LPAREN):
            raise SyntaxError("Expected '('")
        if not self.match(TokenType.RPAREN):
            raise SyntaxError("Expected ')'")
        if not self.match(TokenType.LBRACE):
            raise SyntaxError("Expected '{'")
        body = []
        while not self.match(TokenType.RBRACE):
            body.append(self.parse_statement())
        return FunctionStmt(name_tok.text, body)
