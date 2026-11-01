"""Service rows are pure escaped presentation, with caller-owned state and time."""

import subprocess

from kellytec_design_system.assets import shared_ui_script


def test_service_table_escapes_every_display_value_without_reinterpreting_it():
    script = "global.window={};\n" + shared_ui_script() + r'''
const assert = require('node:assert/strict');
const UI = window.MonitorUI;
assert.equal(typeof UI.serviceTable, 'function', 'Shared service table is required');
global.document={createElement:() => ({set textContent(value) {
  this.innerHTML=String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
}})};
const html = UI.serviceTable([{
  name:'<img src=x onerror=alert(1)>', status:'waiting', tone:'warning',
  updatedAt:{short:'03:30:00 EST',full:'2026-11-01 03:30:00 EST " detail'},
  reason:'No execution <yet> & pending "review"'
}]);
assert.ok(!html.includes('<img'));
assert.ok(html.includes('&lt;img'));
assert.ok(html.includes('data-tone="warning"'));
assert.ok(html.includes('>waiting</span>'));
assert.ok(html.includes('03:30:00 EST &quot; detail'));
assert.ok(html.includes('No execution &lt;yet&gt; &amp; pending &quot;review&quot;'));
assert.ok(!html.includes('superfactor'));
assert.ok(!html.includes('2026-11-01T'));
const empty = UI.serviceTable([]);
assert.ok(empty.includes('Services') && empty.includes('Reason'));
assert.ok(!empty.includes('data-ui="service-row"'));
'''
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
