
# semantic.py
# Semantic Analyzer for the Function Definition Compiler


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def analyze(self, program):
        self.symbol_table = {}
        self.errors = []

        statements = program.get("statements", [])

        # First pass: collect function definitions
        for statement in statements:
            if statement.get("type") == "FunctionDef":
                name = statement["name"]
                params = statement["params"]

                # Check duplicate function definitions
                if name in self.symbol_table:
                    self.errors.append(
                        "Duplicate function definition: " + name
                    )
                else:
                    self.symbol_table[name] = params

                # Check duplicate parameter names
                seen = set()

                for param in params:
                    if param in seen:
                        self.errors.append(
                            "Duplicate parameter '" + param +
                            "' in function '" + name + "'"
                        )
                    seen.add(param)

        # Second pass: check statements and function calls
        for statement in statements:
            self.check_node(statement, False)

        return self.errors

    def check_node(self, node, inside_function):

        if isinstance(node, list):
            for item in node:
                self.check_node(item, inside_function)
            return

        if not isinstance(node, dict):
            return

        node_type = node.get("type")

        # Function definition
        if node_type == "FunctionDef":
            for statement in node.get("body", []):
                self.check_node(statement, True)
            return

        # Return statement
        if node_type == "Return":
            if not inside_function:
                self.errors.append(
                    "Return statement outside a function"
                )

            self.check_node(node.get("value"), inside_function)
            return

        # Function call
        if node_type == "Call":
            name = node["name"]
            args = node.get("args", [])

            if name not in self.symbol_table:
                self.errors.append(
                    "Call to undefined function: " + name
                )

            else:
                expected = len(self.symbol_table[name])
                actual = len(args)

                if expected != actual:
                    self.errors.append(
                        "Function '" + name + "' expects " +
                        str(expected) + " argument(s), but got " +
                        str(actual)
                    )

            # Check nested function calls in arguments
            self.check_node(args, inside_function)
            return

        # Visit other child nodes, such as assignments,
        # print statements and binary expressions
        for key, value in node.items():
            if key != "type":
                self.check_node(value, inside_function)


def analyze(program):
    """Public entry point for semantic analysis."""
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(program)

    return analyzer.symbol_table, errors

