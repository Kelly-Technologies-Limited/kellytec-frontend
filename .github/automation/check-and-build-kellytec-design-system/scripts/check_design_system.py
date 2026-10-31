"""Validate design-system source syntax before building the package."""

import ast
from pathlib import Path

if __name__ == "__main__":
    paths = [
        path
        for path in Path("src/kellytec-design-system").rglob("*.py")
        if not {"build", "dist"}.intersection(path.parts)
    ]
    if not paths:
        raise ValueError("Design System source validation requires Python source files")
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
