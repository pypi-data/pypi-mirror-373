import ast
import os
import shutil
import importlib
from pathlib import Path

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.join(_CURRENT_DIR, '..')

EXTRA_LINES = sorted(
    importlib.import_module('formatters.float').EXTRA_LINES +
    importlib.import_module('formatters.dates').EXTRA_LINES,
    reverse=True
)

INPUT_DIR = Path(os.path.join(_ROOT_DIR, 'hestia_earth', 'schema', 'pydantic'))
OUTPUT_FILE = Path(os.path.join(INPUT_DIR, '__init__.py'))

seen_classes = set()
seen_imports = set()
unique_defs = []


for file in INPUT_DIR.glob("*.py"):
    tree = ast.parse(file.read_text(), filename=str(file))
    for node in tree.body:
        # Handle imports
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            # Skip relative imports (like `from . import Foo`)
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                continue
            imp = ast.unparse(node)
            if imp not in seen_imports:
                seen_imports.add(imp)
                unique_defs.append(imp)
        # Handle classes
        elif isinstance(node, ast.ClassDef):
            if node.name not in seen_classes:
                seen_classes.add(node.name)
                unique_defs.append(ast.unparse(node))
        # Handle top-level functions (sometimes generated)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name not in seen_classes:
                seen_classes.add(node.name)
                unique_defs.append(ast.unparse(node))


def _clean_dir(folder: str):
    os.makedirs(folder, exist_ok=True)
    shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)


def main():
    _clean_dir(INPUT_DIR)

    code = "\n\n".join([
        'from pydantic import AliasChoices',
        'from hestia_earth.schema import SchemaType'
    ] + EXTRA_LINES + unique_defs)
    code = code.replace(
        "field_id: Optional[str] = Field(None, alias='@id', description='Unique id assigned by HESTIA', examples=['@hestia-unique-id-1'])",
        ""
    )

    # Write out combined file
    with open(OUTPUT_FILE, "w") as f:
        f.write(code)

    print(f"✅ Combined models written to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
