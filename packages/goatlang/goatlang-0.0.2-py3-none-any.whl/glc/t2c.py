from glc.parser import *


class ASTtoC:
    def __init__(self):
        self.code = ""
        self.indent_level = 0
        self.var_types = {}  # track variable types
        self.includes = set()  # avoid duplicate includes

    def indent(self):
        return "    " * self.indent_level

    def emit_line(self, line):
        self.code += f"{self.indent()}{line}\n"

    # ---------------- Expressions ----------------
    def expr(self, node):
        if isinstance(node, NumberExpr):
            return str(node.value)
        elif isinstance(node, FloatExpr):
            return str(node.value)
        elif isinstance(node, BoolExpr):
            return "1" if node.value else "0"
        elif isinstance(node, StringExpr):
            return f'"{node.value}"'
        elif isinstance(node, VariableExpr):
            return node.name
        elif isinstance(node, BinaryExpr):
            lhs, rhs = node.lhs, node.rhs

            # String concatenation handling
            if node.op == "+" and (
                    isinstance(lhs, StringExpr) or
                    (isinstance(lhs, VariableExpr) and self.var_types.get(lhs.name) == "string")
            ):
                # Use a temporary variable for string concatenation
                tmp_var = f"tmp_str_{id(node)}"
                self.emit_line(f"char {tmp_var}[1024];")
                self.emit_line(f'strcpy({tmp_var}, {self.expr(lhs)});')
                self.emit_line(f'strcat({tmp_var}, {self.expr(rhs)});')
                return tmp_var
            else:
                return f"({self.expr(lhs)} {node.op} {self.expr(rhs)})"
        else:
            raise NotImplementedError(f"Unknown expr: {node}")

    # ---------------- Statements ----------------
    def stmt(self, node):
        if isinstance(node, LetStmt):
            ctype_map = { "int": "int", "float": "float", "bool": "int", "string": "char" }
            ctype = ctype_map.get(node.type, "int")
            val = self.expr(node.value)

            # ROOT CAUSE FIX: Check if variable already exists.
            # If so, treat as a reassignment, not a new declaration.
            # This prevents creating a new variable inside a loop's scope (shadowing).
            if node.name in self.var_types:
                if node.type == "string":
                    self.emit_line(f"strcpy({node.name}, {val});")
                else:
                    self.emit_line(f"{node.name} = {val};")
            else:
                # This is a new variable declaration
                if node.type == "string":
                    self.emit_line(f"{ctype} {node.name}[1024];")
                    self.emit_line(f"strcpy({node.name}, {val});")
                else:
                    self.emit_line(f"{ctype} {node.name} = {val};")
                self.var_types[node.name] = node.type

        elif isinstance(node, PrintStmt):
            val = self.expr(node.value)
            fmt = "%d"
            # Determine the correct format specifier for printf
            if isinstance(node.value, FloatExpr):
                fmt = "%f"
            elif isinstance(node.value, StringExpr):
                fmt = "%s"
            elif isinstance(node.value, VariableExpr):
                t = self.var_types.get(node.value.name, "int")
                fmt = {"int": "%d", "float": "%f", "bool": "%d", "string": "%s"}.get(t, "%d")
            self.emit_line(f'printf("{fmt}\\n", {val});')

        elif isinstance(node, IfStmt):
            cond = self.expr(node.condition)
            self.emit_line(f"if ({cond}) {{")
            self.indent_level += 1
            for s in node.then_body:
                self.stmt(s)
            self.indent_level -= 1
            self.emit_line("}")
            if node.else_body:
                self.emit_line("else {")
                self.indent_level += 1
                for s in node.else_body:
                    self.stmt(s)
                self.indent_level -= 1
                self.emit_line("}")

        elif isinstance(node, WhileStmt):
            cond = self.expr(node.condition)
            self.emit_line(f"while ({cond}) {{")
            self.indent_level += 1
            for s in node.body:
                self.stmt(s)
            self.indent_level -= 1
            self.emit_line("}")

        elif isinstance(node, ExprStmt):
            # Handle assignments
            if (isinstance(node.expr, BinaryExpr) and
                    node.expr.op == "=" and
                    isinstance(node.expr.lhs, VariableExpr)):

                lhs = node.expr.lhs.name
                rhs = self.expr(node.expr.rhs)

                if lhs in self.var_types:
                    # Also fixed string re-assignment here for consistency.
                    if self.var_types[lhs] == "string":
                        self.emit_line(f"strcpy({lhs}, {rhs});")
                    else:
                        self.emit_line(f"{lhs} = {rhs};")
                else:
                    # Implicitly declare new variables as int
                    self.emit_line(f"int {lhs} = {rhs};")
                    self.var_types[lhs] = "int"
            else:
                # Not an assignment, just evaluate the expression
                val = self.expr(node.expr)
                self.emit_line(f"{val};")

        else:
            raise NotImplementedError(f"Unknown stmt type: {node}")

    # ---------------- Function ----------------
    def function(self, node: FunctionStmt):
        # Add necessary includes
        if "stdio.h" not in self.includes:
            self.emit_line("#include <stdio.h>")
            self.includes.add("stdio.h")
        if "string.h" not in self.includes:
            self.emit_line("#include <string.h>")
            self.includes.add("string.h")
        if "stdbool.h" not in self.includes:
            self.emit_line("#include <stdbool.h>")
            self.includes.add("stdbool.h")

        self.emit_line("")
        self.emit_line("int main() {")
        self.indent_level += 1
        for s in node.body:
            self.stmt(s)
        self.emit_line("return 0;")
        self.indent_level -= 1
        self.emit_line("}")

