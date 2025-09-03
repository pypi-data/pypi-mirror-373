import ast

# Replace this string with the path to your Python file
file_path = '/Users/emmanuel/dev/kywy/src/kywy/client/application_builder_test.py'


def extract_globals(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    globals = []
    for node in tree.body:  # only top-level (global scope)
        if isinstance(node, ast.Assign):
            # handle multiple targets (e.g., a = b = 3)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    globals.append(target.id)
        elif isinstance(node, ast.AnnAssign):
            # annotated assignment (e.g., x: int = 5)
            target = node.target
            if isinstance(target, ast.Name):
                globals.append(target.id)
    return globals


if __name__ == "__main__":
    vars = extract_globals(file_path)
    print("Global variables:", vars)
