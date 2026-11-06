"""Run the shared verify qualified artifacts operation."""

import argparse

from kellytec_automation.integrations.github.context import output
from kellytec_automation.qualification.evidence.verify import verify_qualified_artifacts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True)
    product = parser.parse_args().product
    for name, value in verify_qualified_artifacts(product).items():
        output(name, value)
