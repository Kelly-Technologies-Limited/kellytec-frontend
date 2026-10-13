"""The shared lifecycle owns resize, text and tooltip cleanup on every redraw."""
import json
import subprocess

from kellytec_design_system.assets import ROOT


def test_hidden_reveal_resize_rebind_and_removal_do_not_leak_bindings():
    base = ROOT / "static/js"
    script = r'''
const assert=require('node:assert/strict');
const observers=[];
global.ResizeObserver=class {
  constructor(update){this.update=update;this.active=true;observers.push(this);}
  observe(){} disconnect(){this.active=false;}
};
let removal;
global.MutationObserver=class{constructor(update){removal=update;}observe(){}};
let textBindings=0, tipBindings=0, width=0, draws=0;
const host={innerHTML:'initial',getBoundingClientRect:()=>({width})};
const root=new EventTarget();
root.dataset={card:'example'};root.isConnected=true;
root.querySelectorAll=()=>[host];
global.document={body:{},querySelector:()=>root,querySelectorAll:()=>[root]};
global.window={MonitorUI:{registerRenderer:()=>{},
  bindChartText:()=>{textBindings++;return()=>{textBindings--;};},
  bindTooltip:()=>{tipBindings++;return()=>{tipBindings--;};}
}};
'''
    script += "".join("require(" + json.dumps(str(base / path)) + ");" for path in ["charts/responsive.js", "components/card.js"])
    script += r'''
const UI=window.MonitorUI;
UI.rendererFor=()=>({bind:()=>UI.bindResponsiveChart(root,'.plot',w=>{draws++;return 'width '+w;})});
UI.bindCard({id:'example'});
assert.equal(draws,0);assert.equal(textBindings,1);assert.equal(tipBindings,1);
width=466;observers[0].update();assert.equal(host.innerHTML,'width 466');
width=320;observers[0].update();assert.equal(host.innerHTML,'width 320');
observers[0].update();assert.equal(draws,2);
assert.equal(textBindings,1);assert.equal(tipBindings,1);
UI.bindCard({id:'example'});
assert.equal(observers.filter(o=>o.active).length,1);
assert.equal(textBindings,1);assert.equal(tipBindings,1);
width=0;observers[1].update();assert.equal(host.innerHTML,'width 320');
width=466;observers[1].update();assert.equal(host.innerHTML,'width 466');
root.isConnected=false;removal();
assert.equal(observers.filter(o=>o.active).length,0);
assert.equal(textBindings,0);assert.equal(tipBindings,0);
'''
    subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
