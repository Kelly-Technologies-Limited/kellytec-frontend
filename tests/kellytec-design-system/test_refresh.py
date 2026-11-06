"""The installed browser controller preserves manual mode and owns its timers."""

import json
import subprocess

import pytest
from kellytec_design_system.assets import ROOT
from kellytec_design_system.contract.refresh_policy import RefreshPolicy


@pytest.mark.parametrize("interval", [0, 1, True, -1, 86401, 60.5])
def test_invalid_intervals_are_not_admitted(interval):
    with pytest.raises(ValueError):
        RefreshPolicy(interval)


def test_manual_mode_can_be_enabled_without_replacing_the_controller():
    assert RefreshPolicy().as_dict() == {"mode": "manual", "interval_seconds": None}
    script = r'''
const assert=require('node:assert/strict');
const events={}, timers=new Map();let next=0,calls=0,release,errors=0;
global.window={UI:{},addEventListener:(k,v)=>events[k]=v,removeEventListener:k=>delete events[k]};
global.document={visibilityState:'visible',addEventListener:(k,v)=>events[k]=v,removeEventListener:k=>delete events[k]};
global.setTimeout=(fn,delay)=>{timers.set(++next,{fn,delay});return next;};
global.clearTimeout=id=>timers.delete(id);
'''
    script += "require(" + json.dumps(str(ROOT / "static/js/runtime/refresh.js")) + ");"
    script += r'''
(async()=>{
 const controller=window.UI.refreshController({refresh:()=>{calls++;return new Promise(r=>release=r);},onError:()=>errors++});
 controller.configure({mode:'manual',interval_seconds:null});controller.start();
 assert.equal(timers.size,0);assert.equal(calls,0);
 const first=controller.refresh(),second=controller.refresh();assert.strictEqual(first,second);
 await Promise.resolve();assert.equal(calls,1);release();await first;
 assert.equal(timers.size,0);
 controller.configure({mode:'interval',interval_seconds:60});
 assert.equal([...timers.values()][0].delay,60000);
 document.visibilityState='hidden';events.visibilitychange();assert.equal(timers.size,0);
 document.visibilityState='visible';events.visibilitychange();await Promise.resolve();assert.equal(calls,2);
 controller.configure({mode:'manual',interval_seconds:null});release();await controller.refresh();
 assert.equal(timers.size,0);
 controller.configure({mode:'interval',interval_seconds:600});
 assert.equal([...timers.values()][0].delay,600000);
 const queued=[...timers.values()][0].fn;controller.configure({mode:'manual',interval_seconds:null});
 queued();await Promise.resolve();assert.equal(calls,2);
 controller.configure({mode:'interval',interval_seconds:60});events.pagehide();
 assert.equal(timers.size,0);assert.equal(Object.keys(events).length,0);
 await assert.rejects(controller.refresh(),/closed/);assert.equal(errors,0);
 const failing=window.UI.refreshController({refresh:async()=>{throw Error('unavailable');},onError:()=>errors++});
 failing.configure({mode:'interval',interval_seconds:60});failing.start();
 [...timers.values()][0].fn();await new Promise(resolve=>setImmediate(resolve));
 assert.equal(errors,1);assert.equal(timers.size,1);failing.close();
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True, timeout=15)
