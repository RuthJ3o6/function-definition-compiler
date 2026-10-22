
# ast_nodes.py
# AST construction for the Function Definition Compiler


class ASTNode:
    def __init__(self, node_type, **fields):
        self.node_type = node_type
        self.fields = fields


# Program and function-related nodes

class Program(ASTNode):
    def __init__(self, statements):
        super().__init__("Program", statements=statements)


class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        super().__init__(
            "FunctionDef",
            name=name,
            params=params,
            body=body
        )


class Parameter(ASTNode):
    def __init__(self, name):
        super().__init__("Parameter", name=name)


# Statement nodes

class Assignment(ASTNode):
    def __init__(self, name, value):
        super().__init__("Assignment", name=name, value=value)


class FunctionCall(ASTNode):
    def __init__(self, name, args):
        super().__init__("FunctionCall", name=name, args=args)


class Return(ASTNode):
    def __init__(self, value):
        super().__init__("Return", value=value)


class Print(ASTNode):
    def __init__(self, value):
        super().__init__("Print", value=value)


# Expression nodes

class BinaryOp(ASTNode):
    def __init__(self, op, left, right):
        super().__init__(
            "BinaryOp",
            op=op,
            left=left,
            right=right
        )


class Identifier(ASTNode):
    def __init__(self, name):
        super().__init__("Identifier", name=name)


class Number(ASTNode):
    def __init__(self, value):
        super().__init__("Number", value=value)


# Convert parser dictionaries into AST nodes

def build_ast(data):

    if isinstance(data, list):
        return [build_ast(item) for item in data]

    if not isinstance(data, dict):
        return data

    node_type = data["type"]

    if node_type == "Program":
        return Program(build_ast(data["statements"]))

    elif node_type == "FunctionDef":
        params = [Parameter(p) for p in data["params"]]
        body = build_ast(data["body"])
        return FunctionDef(data["name"], params, body)

    elif node_type == "Assignment":
        return Assignment(
            data["name"],
            build_ast(data["value"])
        )

    elif node_type == "Call":
        return FunctionCall(
            data["name"],
            build_ast(data["args"])
        )

    elif node_type == "Return":
        return Return(build_ast(data["value"]))

    elif node_type == "Print":
        return Print(build_ast(data["value"]))

    elif node_type == "BinaryOp":
        return BinaryOp(
            data["op"],
            build_ast(data["left"]),
            build_ast(data["right"])
        )

    elif node_type == "Identifier":
        return Identifier(data["name"])

    elif node_type == "Number":
        return Number(data["value"])

    raise ValueError("Unknown AST node type: " + node_type)


# Display the AST as a tree

def display_ast(node, indent=0):

    prefix = "  " * indent

    if isinstance(node, list):
        for item in node:
            display_ast(item, indent)
        return

    if not isinstance(node, ASTNode):
        print(prefix + str(node))
        return

    print(prefix + node.node_type)

    for name, value in node.fields.items():

        if isinstance(value, list):
            print(prefix + "  " + name + ":")
            display_ast(value, indent + 2)

        elif isinstance(value, ASTNode):
            print(prefix + "  " + name + ":")
            display_ast(value, indent + 2)

        else:
            print(prefix + "  " + name + ": " + str(value))

