
# main.py
# Main integration program for the Function Definition Compiler

from lexer import tokenize
from parser import parse, ParseError
from ast_nodes import build_ast, display_ast
from semantic import analyze


# Sample programs for testing

VALID_PROGRAM = """
def add(a, b) begin
    result = a + b;
    return result;
end;

total = add(10, 20);
print(total);
"""

DUPLICATE_PARAMETER_PROGRAM = """
def add(a, a) begin
    return a;
end;
"""

UNDEFINED_FUNCTION_PROGRAM = """
result = multiply(10, 20);
"""

WRONG_ARGUMENT_COUNT_PROGRAM = """
def add(a, b) begin
    return a + b;
end;

result = add(10);
"""

SYNTAX_ERROR_PROGRAM = """
def add(a, b) begin
    return a + b
end;
"""


def run_compiler(source_code):

    print("\n" + "=" * 45)
    print("FUNCTION DEFINITION COMPILER")
    print("=" * 45)

    # Stage 1: Lexical Analysis
    print("\n1. LEXICAL ANALYSIS")

    try:
        tokens = tokenize(source_code)

        for token in tokens:
            print(token)

    except SyntaxError as error:
        print("Lexer Error:", error)
        return

    # Stage 2: Syntax Analysis
    print("\n2. SYNTAX ANALYSIS")

    try:
        parse_tree = parse(tokens)
        print("Syntax analysis successful.")

    except ParseError as error:
        print("Parser Error:", error)
        return

    # Stage 3: AST Construction
    print("\n3. ABSTRACT SYNTAX TREE")

    try:
        ast = build_ast(parse_tree)
        display_ast(ast)

    except (ValueError, KeyError, TypeError) as error:
        print("AST Construction Error:", error)
        return

    # Stage 4: Semantic Analysis
    print("\n4. SEMANTIC ANALYSIS")

    symbol_table, errors = analyze(parse_tree)

    print("Function Symbol Table:")
    print(symbol_table)

    if errors:
        print("\nSemantic errors found:")

        for error in errors:
            print("-", error)

        print("\nCompilation failed: semantic errors detected.")

    else:
        print("No semantic errors found.")
        print("\nCompilation successful!")


def enter_program():

    print("\nEnter your program.")
    print("Type ENDINPUT on a new line to finish.")

    lines = []

    while True:
        line = input()

        if line == "ENDINPUT":
            break

        lines.append(line)

    return "\n".join(lines)


def main():

    while True:
        print("\n===== MAIN MENU =====")
        print("1. Run valid program")
        print("2. Test duplicate parameters")
        print("3. Test undefined function")
        print("4. Test incorrect argument count")
        print("5. Test syntax error")
        print("6. Enter your own program")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            run_compiler(VALID_PROGRAM)

        elif choice == "2":
            run_compiler(DUPLICATE_PARAMETER_PROGRAM)

        elif choice == "3":
            run_compiler(UNDEFINED_FUNCTION_PROGRAM)

        elif choice == "4":
            run_compiler(WRONG_ARGUMENT_COUNT_PROGRAM)

        elif choice == "5":
            run_compiler(SYNTAX_ERROR_PROGRAM)

        elif choice == "6":
            source_code = enter_program()
            run_compiler(source_code)

        elif choice == "7":
            print("Compiler closed.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

