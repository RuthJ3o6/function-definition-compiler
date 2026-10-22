
from flask import Flask, render_template, request, jsonify
from lexer import tokenize
from parser import parse, ParseError
from ast_nodes import build_ast, display_ast
from semantic_analyzer import analyze

import io
from contextlib import redirect_stdout

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json(silent=True) or {}
    source_code = data.get("code", "")

    token_list = []

    try:
        # STEP 1: LEXICAL ANALYSIS
        tokens = tokenize(source_code)

        for token in tokens:
            token_list.append({
                "type": token[0],
                "value": token[1]
            })

        # STEP 2: SYNTAX ANALYSIS
        parsed_data = parse(tokens)

        # STEP 3: ABSTRACT SYNTAX TREE GENERATION
        ast_root = build_ast(parsed_data)

        ast_buffer = io.StringIO()

        with redirect_stdout(ast_buffer):
            display_ast(ast_root)

        ast_output = ast_buffer.getvalue()

        # STEP 4: SEMANTIC ANALYSIS
        symbol_table, errors = analyze(parsed_data)

        # STEP 5: COMPILER OUTPUT
        output_text = (
            "Lexical analysis successful.\n"
            f"Tokens recognized: {len(tokens)}\n"
            "Syntax analysis successful.\n"
        )

        if errors:
            output_text += "Semantic analysis failed.\n"

            for error in errors:
                output_text += f"- {error}\n"

            semantic_status = "Failed"

        else:
            output_text += (
                "Semantic analysis successful.\n"
                "Program is valid."
            )

            semantic_status = "Successful"

        return jsonify({
            "lexical": "Successful",
            "syntax": "Successful",
            "semantic": semantic_status,
            "tokens": token_list,
            "output": output_text,
            "ast": ast_output,
            "symbol_table": symbol_table
        })

    except ParseError as error:
        return jsonify({
            "lexical": "Successful" if token_list else "Not performed",
            "syntax": "Failed",
            "semantic": "Not performed",
            "tokens": token_list,
            "output": f"Syntax analysis failed:\n{error}",
            "ast": "Syntax tree unavailable because parsing failed.",
            "symbol_table": {}
        })

    except Exception as error:
        return jsonify({
            "lexical": "Failed",
            "syntax": "Not performed",
            "semantic": "Not performed",
            "tokens": token_list,
            "output": f"Compilation error: {error}",
            "ast": "Syntax tree unavailable.",
            "symbol_table": {}
        })


if __name__ == "__main__":
    app.run(debug=True)
