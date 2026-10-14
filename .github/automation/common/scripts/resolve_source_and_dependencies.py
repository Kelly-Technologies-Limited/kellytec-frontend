"""Run the shared resolve source and dependencies operation."""

import argparse

from kellytec_automation.common.adapter.github.context import output
from kellytec_automation.common.dependencies.resolve_source_and_dependencies import (
    resolve_source_and_dependencies,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True)
    product = parser.parse_args().product
    for name, value in resolve_source_and_dependencies(product).items():
        output(name, value)
