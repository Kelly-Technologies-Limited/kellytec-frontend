"""DST labels are an explicit caller choice; existing apps retain ET by default."""
import json
import subprocess

import pytest
from kellytec_design_system.assets import ROOT
from kellytec_design_system.contracts import display_value


def test_timezone_option_is_typed_and_restricted_to_time_values():
    assert display_value("datetime_et", "2026-11-01T05:30:00Z", show_timezone=True)["show_timezone"] is True
    assert "show_timezone" not in display_value("datetime_et", "2026-11-01T05:30:00Z")
    with pytest.raises(ValueError, match="NY time"):
        display_value("text", "a", show_timezone=True)


def test_shared_browser_formatter_keeps_default_and_distinguishes_fall_back():
    source = ROOT / "static/js/formatters/value.js"
    script = "global.window = {MonitorUI: {EMPTY: '—'}};\n" + source.read_text()
    script += """
const cases = [
  {kind:'datetime_et', value:'2026-11-01T05:30:00Z'},
  {kind:'datetime_et', value:'2026-11-01T05:30:00Z', show_timezone:true},
  {kind:'datetime_et', value:'2026-11-01T06:30:00Z', show_timezone:true},
  {kind:'minute_et', value:'2026-11-01T06:30:00Z', show_timezone:true},
  {kind:'time_et', value:'2026-11-01T01:30:00', show_timezone:true},
  {kind:'time_et', value:'2026-11-01T05:30:00.123456Z', show_timezone:true, fractional_seconds:3}
];
console.log(JSON.stringify(cases.map(window.MonitorUI.value)));
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout) == ["2026-11-01 01:30:00 ET", "2026-11-01 01:30:00 EDT", "2026-11-01 01:30:00 EST", "01:30 EST", "01:30:00 ET", "01:30:00.123 EDT"]
