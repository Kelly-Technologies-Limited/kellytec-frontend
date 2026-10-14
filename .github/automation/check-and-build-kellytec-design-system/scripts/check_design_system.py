"""Validate design-system source syntax before building the package."""

import ast
from pathlib import Path

if __name__ == "__main__":
    for path in Path("kellytec-design-system").rglob("*.py"):
        if not {"build", "dist"}.intersection(path.parts):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
