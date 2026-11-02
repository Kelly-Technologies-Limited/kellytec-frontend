"""The shared table aligns optional numeric columns without changing old callers."""

import json
import subprocess

from kellytec_design_system.assets import ROOT, design_system_css


def test_numeric_column_and_multiple_basis_values_use_shared_structure():
    base = ROOT / "static/js"
    script = "global.window={UI:{esc:String}};" + "".join("require(" + json.dumps(str(base / path)) + ");" for path in ["formatters/value.js", "components/table.js"])
    script += """
    const UI=window.UI;
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
    assert 'label-value' in result["numeric"] and '2.10%' in result["numeric"]
    assert 'Notional' in result["numeric"] and '—' in result["numeric"]
    css = design_system_css()
    assert 'font-variant-numeric: tabular-nums' in css
    assert '[data-ui="table"] [data-ui-numeric="true"]' in css


def test_interactive_empty_table_retains_headers_and_escaped_actions():
    script='global.window={UI:{esc:v=>String(v).replaceAll("<","&lt;")}};'
    script+='require('+json.dumps(str(ROOT/'static/js/components/table.js'))+');'
    script+='console.log(window.UI.table([{label:"<value>",lines:["contract","underlying","<instrument type>"],action:{key:"<key>",label:"Filter value",active:true},sort:"desc"}],[],"No matches",{keepHeaders:true,stickyHeader:true,stickyFirst:true,density:"compact",columnWidths:[112]}));'
    result=subprocess.check_output(['node','-e',script],text=True)
    assert '<thead>' in result and 'No matches' in result
    assert 'data-table-action="&lt;key>"' in result
    assert 'aria-sort="descending"' in result
    assert 'data-sticky-header="true"' in result

    assert 'data-ui-column-layout="fixed" style="width:112px"' in result
    assert '<colgroup><col style="width:112px"></colgroup>' in result
    assert result.count('class="table-header-line"') == 3
    assert '<span class="table-header-label">' in result
    assert 'data-ui-table-density="compact"' in result
    assert 'class="table-header-indicator"' in result
    assert result.index('<button') < result.index('table-header-label') < result.index('</button>')
    assert '&lt;instrument type>' in result and '<instrument type>' not in result
