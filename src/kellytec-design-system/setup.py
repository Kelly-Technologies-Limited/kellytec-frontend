"""Map the product's Python source tree to its public import namespace."""

from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

SOURCE = "."
NAMESPACE = "kellytec_design_system"


class ProductBuildPy(build_py):
    """Exclude the product's build entrypoint from its import package."""

    def find_package_modules(self, package: str, package_dir: str) -> list[tuple[str, str, str]]:
        """Return runtime modules without shipping setup.py as application code."""
        return [
            module
            for module in super().find_package_modules(package, package_dir)
            if Path(module[2]).name != "setup.py"
        ]


setup(
    packages=[
        NAMESPACE,
        *(
            f"{NAMESPACE}.{name}"
            for name in find_packages(
                where=SOURCE, include=("contracts", "contracts.*", "components", "components.*")
            )
        ),
    ],
    package_dir={NAMESPACE: SOURCE},
    cmdclass={"build_py": ProductBuildPy},
)
