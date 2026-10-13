"""Optional precision changes display only; defaults remain compatible."""

import json
import subprocess

import pytest
from kellytec_design_system.assets import ROOT
from kellytec_design_system.contracts import display_value


def rendered(specs):
    script = (
        "global.window={MonitorUI:{}};require("
        + json.dumps(str(ROOT / "static/js/formatters/value.js"))
        + ");console.log(JSON.stringify("
        + json.dumps(specs)
        + ".map(window.MonitorUI.value)));"
    )
    return json.loads(subprocess.check_output(["node", "-e", script], text=True))


@pytest.mark.parametrize("kind,scale", [("percent_points", 1), ("percent_ratio", 100)])
def test_fixed_percent_precision_through_python_and_javascript(kind, scale):
    values = [0, 1, 134.8, 1.25, -1.25, None]
    specs = [
        display_value(
            kind, value / scale if value is not None else None, fraction_digits=1
        )
        for value in values
    ]
    assert rendered(specs) == ["0.0%", "1.0%", "134.8%", "1.3%", "-1.3%", "—"]
    assert rendered([display_value(kind, 0), display_value(kind, 1 / scale)]) == [
        "0%",
        "1%",
    ]
    assert rendered(
        [
            display_value(kind, 0, fraction_digits=0),
            display_value(kind, 0, fraction_digits=20),
        ]
    ) == ["0%", "0.00000000000000000000%"]


@pytest.mark.parametrize("digits", [-1, 21, True, 1.5, "1"])
def test_invalid_percent_precision_is_rejected(digits):
    with pytest.raises(ValueError, match="fraction_digits"):
        display_value("percent_points", 0, fraction_digits=digits)
    assert rendered(
        [{"kind": "percent_points", "value": 0, "fraction_digits": digits}]
    ) == ["—"]


def test_precision_does_not_extend_nonnumeric_display_kinds():
    with pytest.raises(ValueError, match="fraction_digits"):
        display_value("text", 1, fraction_digits=1)
