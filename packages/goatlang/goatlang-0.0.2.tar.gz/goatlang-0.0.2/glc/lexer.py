from enum import Enum, auto

"""
A simple lexer for a custom programming language.
Handles keywords, identifiers, numbers, strings, operators, and comments."""


class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    END = auto()
    GT = auto()  # >
    LT = auto()  #
    GTE = auto()  # >=
    LTE = auto()  # <=
    EQ = auto()  # ==
    NEQ = auto()  # !=


class Token:
    def __init__(self, type_, text, subtype=None):
        self.type = type_
        self.text = text
        self.subtype = subtype

    def __repr__(self):
        return f"{self.type.name}({self.text})"


# -------------------- Lexer --------------------
class Lexer:
    KEYWORDS = {
        "fn",
        "int",
        "struct",
        "type",
        "print",
        "float",
        "bool",
        "string",
        "if",
        "else",
        "while",
        "for",
        "return",
        "true",
        "false",
    }

    def __init__(self, source):
        self.src = source
        self.pos = 0

    def current_char(self):
        if self.pos >= len(self.src):
            return None
        return self.src[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.src):
            return None
        return self.src[peek_pos]

    def advance(self):
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()

    def next_token(self):
        self.skip_whitespace()
        c = self.current_char()

        if c is None:
            return Token(TokenType.END, "")

        # Handle comments
        if c == "#":
            while self.current_char() and self.current_char() != "\n":
                self.advance()
            return self.next_token()

        # Handle multi-line comments
        if self.src[self.pos : self.pos + 3] == '"""':
            self.pos += 3
            while (
                self.pos < len(self.src) - 2
                and self.src[self.pos : self.pos + 3] != '"""'
            ):
                self.advance()
            if self.pos < len(self.src) - 2:
                self.pos += 3
            return self.next_token()

        # Handle numbers
        if c.isdigit():
            start = self.pos
            has_dot = False
            while self.current_char() and (
                self.current_char().isdigit() or self.current_char() == "."
            ):
                if self.current_char() == ".":
                    if has_dot:  # second dot → stop
                        break
                    has_dot = True
                self.advance()
            text = self.src[start : self.pos]
            if "." in text:
                return Token(TokenType.NUMBER, text, subtype="float")
            else:
                return Token(TokenType.NUMBER, text, subtype="int")

        # Handle identifiers and keywords
        if c.isalpha() or c == "_":
            start = self.pos
            while self.current_char() and (
                self.current_char().isalnum() or self.current_char() == "_"
            ):
                self.advance()
            text = self.src[start : self.pos]
            if text in self.KEYWORDS:
                return Token(TokenType.KEYWORD, text)
            return Token(TokenType.IDENTIFIER, text)

        # Handle strings
        if c == '"':
            self.advance()  # skip opening quote
            start = self.pos
            while self.current_char() and self.current_char() != '"':
                self.advance()
            text = self.src[start : self.pos]
            if self.current_char() == '"':
                self.advance()  # skip closing quote
            return Token(TokenType.STRING, text)

        # Handle operators and punctuation
        if c == "+":
            self.advance()
            return Token(TokenType.PLUS, c)
        if c == "-":
            self.advance()
            return Token(TokenType.MINUS, c)
        if c == "*":
            self.advance()
            return Token(TokenType.STAR, c)
        if c == "/":
            self.advance()
            return Token(TokenType.SLASH, c)
        if c == ":":
            self.advance()
            return Token(TokenType.COLON, c)
        if c == ",":
            self.advance()
            return Token(TokenType.COMMA, c)
        if c == "(":
            self.advance()
            return Token(TokenType.LPAREN, c)
        if c == ")":
            self.advance()
            return Token(TokenType.RPAREN, c)
        if c == "{":
            self.advance()
            return Token(TokenType.LBRACE, c)
        if c == "}":
            self.advance()
            return Token(TokenType.RBRACE, c)

        # Handle comparison and assignment operators
        if c == "=":
            if self.peek() == "=":
                self.advance()  # consume first '='
                self.advance()  # consume second '='
                return Token(TokenType.EQ, "==")
            else:
                self.advance()
                return Token(TokenType.ASSIGN, "=")

        if c == ">":
            if self.peek() == "=":
                self.advance()  # consume '>'
                self.advance()  # consume '='
                return Token(TokenType.GTE, ">=")
            else:
                self.advance()
                return Token(TokenType.GT, ">")

        if c == "<":
            if self.peek() == "=":
                self.advance()  # consume '<'
                self.advance()  # consume '='
                return Token(TokenType.LTE, "<=")
            else:
                self.advance()
                return Token(TokenType.LT, "<")

        if c == "!":
            if self.peek() == "=":
                self.advance()  # consume '!'
                self.advance()  # consume '='
                return Token(TokenType.NEQ, "!=")
            else:
                # Handle other cases with '!' or raise error
                self.advance()
                return self.next_token()  # skip unknown character

        # Skip unknown characters
        self.advance()
        return self.next_token()


# -------------------- Test --------------------
# if __name__ == "__main__":
#     code = '''
# fn main() {
#     #Variable declarations
#     int x = 42
#     float y = 3.14
#     bool flag = true
#     string msg = "Hello, ToyLang!"
#
#     #Printing initial values
#     print(x)
#     print(y)
#     print(flag)
#     print(msg)
#
#     # Arithmetic operations
#     int sum = x + 10
#     float product = y * 2.0
#
#     print(sum)
#     print(product)
#
#     # Boolean comparison
#     bool isPositive = sum > 0
#     print(isPositive)
#
#     # String concatenation (ToyLang style)
#     string greeting = msg + " Welcome!"
#     print(greeting)
#
#     # Example conditional (for future parsing)
#     if (sum > 50) {
#         print("Sum is large!")
#     } else {
#         print("Sum is small!")
#     }
#
#     # Example while loop (for future parsing)
#     int counter = 0
#     while (counter < 5) {
#         print(counter)
#         counter = counter + 1
#     }
# }
#     '''
#
#     lexer = Lexer(code)
#     tok = lexer.next_token()
#     while tok.type != TokenType.END:
#         print(tok)
#         tok = lexer.next_token()
