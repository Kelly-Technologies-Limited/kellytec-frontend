"""Numeric descriptors keep unit/precision and existing defaults across Python/JS."""

import json
import subprocess

import pytest
from kellytec_design_system.assets import ROOT
from kellytec_design_system.contracts import display_value


def render(specs):
    script = "global.window={MonitorUI:{}};require(" + json.dumps(str(ROOT / "static/js/formatters/value.js")) + ");console.log(JSON.stringify(" + json.dumps(specs) + ".map(window.MonitorUI.value)));"
    return json.loads(subprocess.check_output(["node", "-e", script], text=True))


def test_fixed_units_precision_null_and_negative_zero():
    specs = [
        display_value("money", 1235, currency="USD", fraction_digits=2),
        display_value("money", -5, currency="USD", fraction_digits=2),
        display_value("ratio", .0444, fraction_digits=3),
        display_value("ratio", 1.8, fraction_digits=2),
        display_value("duration_seconds", 61.25, fraction_digits=2),
        display_value("percent_points", 37.9, fraction_digits=2),
        display_value("percent_points", 0, fraction_digits=2),
        display_value("percent_points", None, fraction_digits=2),
        display_value("money", -.001, currency="USD", fraction_digits=2),
        display_value("decimal", -.00001, fraction_digits=2),
        display_value("percent_points", -.001, fraction_digits=2),
    ]
    assert render(specs) == ["$1,235.00", "-$5.00", "0.044×", "1.80×", "61.25 s", "37.90%", "0.00%", "—", "$0.00", "0.00", "0.00%"]


def test_old_numeric_defaults_are_unchanged():
    assert render([
        display_value("money", 1235.2, currency="USD"),
        display_value("decimal", 1), display_value("price", 1),
        display_value("quantity", 1.125), display_value("percent_points", 1.25),
        display_value("duration_ms", 65000),
        display_value("money", 128885.97, currency="USD", compact="millions"),
    ]) == ["$1,235", "1", "1.00", "1.125", "1.3%", "1.1 min", "$0.13M"]


@pytest.mark.parametrize("kind", ["money", "decimal", "quantity", "price", "duration_seconds", "ratio"])
@pytest.mark.parametrize("digits", [-1, 21, True, 1.5, "2"])
def test_bad_precision_rejected_in_both_contracts(kind, digits):
    kwargs = {"currency": "USD"} if kind == "money" else {}
    with pytest.raises(ValueError, match="fraction_digits"):
        display_value(kind, 1, fraction_digits=digits, **kwargs)
    assert render([{"kind": kind, "value": 1, "fraction_digits": digits, **kwargs}]) == ["—"]


def test_fixed_seconds_never_accept_negative_duration():
    assert render([display_value("duration_seconds", -1), display_value("duration_seconds", None)]) == ["—", "—"]
