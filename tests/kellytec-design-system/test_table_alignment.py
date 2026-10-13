"""The shared table aligns optional numeric columns without changing old callers."""

import json
import subprocess

from kellytec_design_system.assets import ROOT, design_system_css


def test_numeric_column_and_multiple_basis_values_use_shared_structure():
    base = ROOT / "static/js"
    script = "global.window={MonitorUI:{esc:String}};" + "".join("require(" + json.dumps(str(base / path)) + ");" for path in ["formatters/value.js", "components/table.js"])
    script += """
    const UI=window.MonitorUI;
    console.log(JSON.stringify({
      old:UI.table(['Name','Value'],[['a','1']]),
      equal:UI.table(['Name',{label:'Win Rate (%)',numeric:true}],[['a','100.00%']],null,{equalColumns:true}),
      numeric:UI.table(['Name',{label:'MAE (%)',numeric:true}],[['a',UI.labelValues([{label:'Premium',value:{kind:'percent_points',value:2.1,fraction_digits:2}},{label:'Notional',value:{kind:'percent_points',value:null,fraction_digits:2}}])]])
    }));
    """
    result = json.loads(subprocess.check_output(["node", "-e", script], text=True))
    assert 'data-ui-numeric' not in result["old"]
    assert 'data-ui-column-layout' not in result["old"]
    assert 'data-ui-column-layout="equal"' in result["equal"]
    assert result["numeric"].count('data-ui-numeric="true"') == 2
    assert 'monitor-label-value' in result["numeric"] and '2.10%' in result["numeric"]
    assert 'Notional' in result["numeric"] and '—' in result["numeric"]
    css = design_system_css()
    assert 'font-variant-numeric: tabular-nums' in css
    assert '[data-ui="table"] [data-ui-numeric="true"]' in css
