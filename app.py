
# app.py
# Flask web application for the Function Definition Compiler

from flask import Flask, render_template, request, jsonify
from lexer import tokenize
from parser import parse, ParseError
from ast_nodes import build_ast, display_ast
from semantic import analyze

import io
from contextlib import redirect_stdout

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compile", methods=["POST"])
def compile_program():

    data = request.get_json(silent=True) or {}
    source_code = data.get("code", "")

    result = {
        "lexical": "Not run",
        "syntax": "Not run",
        "semantic": "Not run",
        "tokens": [],
        "output": "",
        "ast": "",
        "symbol_table": {}
    }

    if not source_code.strip():
        result["output"] = "Please enter a program."
        return jsonify(result)

    # Stage 1: Lexical analysis
    try:
        tokens = tokenize(source_code)

        result["lexical"] = "Successful"
        result["tokens"] = [
            {"type": token[0], "value": token[1]}
            for token in tokens
        ]

    except SyntaxError as error:
        result["lexical"] = "Failed"
        result["output"] = "Lexical error: " + str(error)
        return jsonify(result)

    # Stage 2: Syntax analysis
    try:
        program = parse(tokens)
        result["syntax"] = "Successful"

    except ParseError as error:
        result["syntax"] = "Failed"
        result["output"] = (
            "Lexical analysis successful.\n"
            "Syntax error: " + str(error)
        )
        return jsonify(result)

    # Stage 3: AST construction and display
    try:
        ast = build_ast(program)

        buffer = io.StringIO()

        with redirect_stdout(buffer):
            display_ast(ast)

        result["ast"] = buffer.getvalue()

    except (ValueError, KeyError, TypeError) as error:
        result["output"] = "AST construction error: " + str(error)
        return jsonify(result)

    # Stage 4: Semantic analysis
    symbol_table, errors = analyze(program)

    result["symbol_table"] = symbol_table
    result["semantic"] = "Failed" if errors else "Successful"

    output = [
        "Lexical analysis successful.",
        "Tokens recognized: " + str(len(tokens)),
        "Syntax analysis successful."
    ]

    if errors:
        output.extend(["", "Semantic errors:"])

        for error in errors:
            output.append("- " + error)

        output.extend([
            "",
            "Semantic analysis failed.",
            "Program is invalid."
        ])
    else:
        output.extend([
            "Semantic analysis successful.",
            "Program is valid."
        ])

    result["output"] = "\n".join(output)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
