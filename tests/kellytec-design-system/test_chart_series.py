"""Arbitrary business keys use shared categories and persistent assignments."""

import json
import subprocess

from kellytec_design_system.assets import ROOT


def test_new_categories_append_without_changing_existing_styles():
    base = ROOT / "static/js"
    script = "global.window={MonitorUI:{esc:String}};" + "".join("require(" + json.dumps(str(base / path)) + ");" for path in ["charts/series.js", "charts/legend.js"])
    script += """
    const UI=window.MonitorUI, keys=Array.from({length:13},(_,i)=>'opaque '+i);
    const before=UI.chartSeriesStyle(keys[0], keys.slice(0,4));
    const styles=keys.map(key=>UI.chartSeriesStyle(key,keys));
    const after=UI.chartSeriesStyle(keys[0],['brand-new'].concat(keys));
    console.log(JSON.stringify({before,after,styles,defs:UI.chartSeriesDefinitions(styles,'test'),legend:UI.chartLegendItem({series:styles[4],label:keys[4]})}));
    """
    data = json.loads(subprocess.check_output(["node", "-e", script], text=True))
    assert data["before"] == data["after"]
    assert len({(s["role"], s["pattern"]) for s in data["styles"]}) == 13
    assert data["styles"][4]["pattern"] > 0
    assert [style["role"] for style in data["styles"][:4]] == ["series-1", "series-2", "series-3", "series-4"]
    assert '<pattern id="test-series-4"' in data["defs"]
    assert "repeating-linear-gradient" in data["legend"]
    assert "opaque 4" in data["legend"]


def test_series_asset_is_packaged_before_legend():
    from kellytec_design_system.assets import shared_ui_script
    script = shared_ui_script()
    assert script.index("UI.chartSeriesStyle =") < script.index("UI.chartLegendItem =")
