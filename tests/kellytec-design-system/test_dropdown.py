"""Exercise the installed dropdown through actual browser interactions.

These tests are mandatory in verify_installed_package's ordinary pytest run.
Local runs may choose Chrome with KELLYTEC_UI_BROWSER_PATH; CI uses the pinned
Playwright Chromium installed by the Check and Build workflow.
"""

import os

import pytest
from playwright.sync_api import expect, sync_playwright

from kellytec_design_system.assets import design_system_css, shared_ui_script


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        executable = os.environ.get("KELLYTEC_UI_BROWSER_PATH")
        with playwright.chromium.launch(executable_path=executable) as instance:
            yield instance


@pytest.fixture
def page(browser):
    page = browser.new_page(viewport={"width": 900, "height": 700})
    page.route("**/*", lambda route: route.abort())
    page.set_content('<main data-ui-density="compact" style="padding:30px;display:grid;gap:12px;width:480px">'
                     '<label for="kind-trigger">Data</label><div id="kind"></div>'
                     '<label for="identity-trigger">Data ID</label><div id="identity"></div>'
                     '<button id="outside" style="position:fixed;right:20px;top:20px">Outside</button></main>')
    page.add_style_tag(content=design_system_css())
    page.add_script_tag(content=shared_ui_script())
    page.evaluate("""() => {
      window.events = []; window.callbacks = [];
      document.querySelector('#identity').addEventListener('change', e => events.push(e.detail.value));
      window.kind = UI.dropdown(document.querySelector('#kind'), {
        label: 'Data', items: [{id:'std',label:'Standardized'}, {id:'raw',label:'Raw'}], value:'std'
      });
      window.identity = UI.dropdown(document.querySelector('#identity'), {
        label: 'Data ID', searchable:true, items: [
          {id:'alpha',label:'Alpha prices'}, {id:'disabled',label:'Disabled prices',disabled:true},
          {id:'beta',label:'Beta trades'}, {id:'gamma',label:'Gamma book'}
        ], onChange: value => callbacks.push(value)
      });
    }""")
    yield page
    page.close()


def assert_selected(page, value, label):
    expect(page.get_by_role("combobox", name="Data ID", exact=True)).to_have_text(label)
    assert page.evaluate("identity.value()") == value
    assert page.locator("#identity").get_attribute("data-value") == value
    assert page.locator("#identity-trigger").evaluate("el => el.value") == value


def test_reselection_starts_with_all_choices_and_search_does_not_commit(page):
    trigger = page.get_by_role("combobox", name="Data ID", exact=True)
    trigger.click()
    page.get_by_role("option", name="Alpha prices", exact=True).click()
    assert_selected(page, "alpha", "Alpha prices")
    trigger.click()
    expect(page.get_by_role("option")).to_have_count(4)
    search = page.get_by_role("searchbox", name="Search Data ID", exact=True)
    search.fill("beta")
    expect(page.get_by_role("option")).to_have_count(1)
    assert_selected(page, "alpha", "Alpha prices")
    assert page.evaluate("events") == ["alpha"]
    page.get_by_role("option", name="Beta trades", exact=True).click()
    assert_selected(page, "beta", "Beta trades")
    trigger.click()
    expect(search).to_have_value("")
    expect(page.get_by_role("option")).to_have_count(4)
    page.get_by_role("option", name="Beta trades", exact=True).click()
    assert page.evaluate("events") == ["alpha", "beta"]
    assert page.evaluate("callbacks") == ["alpha", "beta"]


def test_escape_outside_click_and_tab_cancel_without_losing_selected_value(page):
    page.evaluate("identity.setValue('alpha')")
    trigger = page.get_by_role("combobox", name="Data ID", exact=True)
    for dismissal in ("Escape", "outside", "Tab"):
        trigger.click()
        search = page.get_by_role("searchbox", name="Search Data ID", exact=True)
        search.fill("Gamma")
        if dismissal == "outside":
            page.locator("#outside").click()
        else:
            search.press(dismissal)
        expect(trigger).to_have_attribute("aria-expanded", "false")
        expect(page.get_by_role("listbox", name="Data ID", exact=True)).not_to_be_visible()
        assert_selected(page, "alpha", "Alpha prices")
    assert page.evaluate("events") == []


def test_keyboard_commits_active_choice_skips_disabled_and_disabled_control_stays_closed(page):
    trigger = page.get_by_role("combobox", name="Data ID", exact=True)
    trigger.focus()
    trigger.press("ArrowDown")
    search = page.get_by_role("searchbox", name="Search Data ID", exact=True)
    search.press("ArrowDown")
    search.press("Enter")
    assert_selected(page, "beta", "Beta trades")
    expect(trigger).to_be_focused()
    trigger.press("ArrowUp")
    search.press("ArrowUp")
    search.press("Enter")
    assert_selected(page, "alpha", "Alpha prices")
    trigger.click()
    expect(page.get_by_role("option", name="Disabled prices", exact=True)).to_be_disabled()
    page.evaluate("identity.setDisabled(true)")
    expect(trigger).to_be_disabled()
    expect(trigger).to_have_attribute("aria-expanded", "false")
    assert page.evaluate("events") == ["beta", "alpha"]


def test_modes_share_trigger_and_popup_style_and_long_options_scroll(page):
    triggers = page.get_by_role("combobox")
    styles = triggers.evaluate_all("""nodes => nodes.map(node => {
      const s=getComputedStyle(node); return {height:node.getBoundingClientRect().height,
        font:s.font,border:s.border,background:s.backgroundColor,padding:s.padding};
    })""")
    assert styles[0] == styles[1]
    assert styles[0]["height"] == 26
    assert page.locator("select, datalist").count() == 0
    page.get_by_role("combobox", name="Data", exact=True).click()
    expect(page.get_by_role("searchbox")).to_have_count(0)
    plain_background = page.get_by_role("listbox", name="Data", exact=True).evaluate(
        "el => getComputedStyle(el.parentElement).backgroundColor")
    page.get_by_role("option", name="Raw", exact=True).click()
    assert page.evaluate("kind.value()") == "raw"
    page.evaluate("identity.replace(Array.from({length:60}, (_,i) => ({id:'item-'+i,label:'Item '+i})))")
    page.get_by_role("combobox", name="Data ID", exact=True).click()
    listing = page.get_by_role("listbox", name="Data ID", exact=True)
    assert listing.evaluate("el => getComputedStyle(el.parentElement).backgroundColor") == plain_background
    assert listing.evaluate("el => el.scrollHeight > el.clientHeight")
    page.get_by_role("option", name="Item 59", exact=True).click()
    assert_selected(page, "item-59", "Item 59")


def test_replace_updates_labels_preserves_valid_selection_and_lifecycle_does_not_duplicate_events(page):
    page.evaluate("identity.setValue('beta')")
    page.evaluate("identity.replace([{id:'beta',label:'Beta updated'},{id:'feed',label:'Feed one'}], {label:'FeedKey'})")
    expect(page.get_by_role("combobox", name="FeedKey", exact=True)).to_have_text("Beta updated")
    assert page.evaluate("identity.value()") == "beta"
    page.get_by_role("combobox", name="FeedKey", exact=True).click()
    expect(page.get_by_role("searchbox", name="Search FeedKey", exact=True)).to_be_visible()
    page.evaluate("identity.replace([{id:'feed',label:'Feed one'}])")
    assert page.evaluate("identity.value()") == ""
    expect(page.get_by_role("combobox", name="FeedKey", exact=True)).to_have_attribute("aria-expanded", "false")
    page.evaluate("""() => {
      identity.destroy();
      window.identity = UI.dropdown(document.querySelector('#identity'), {
        label:'Data ID',searchable:true,items:[{id:'safe',label:'<img src=x onerror=alert(1)>'}]
      });
    }""")
    page.get_by_role("combobox", name="Data ID", exact=True).click()
    page.get_by_role("option", name="<img src=x onerror=alert(1)>", exact=True).click()
    assert page.locator("#identity img").count() == 0
    assert page.evaluate("events") == ["safe"]


def test_empty_id_is_a_selectable_choice_without_becoming_the_placeholder(page):
    page.evaluate("""() => {
      identity.replace([{id:'',label:'All rows'}, {id:'symbol',label:'Symbol'}]);
    }""")
    assert_selected(page, "", "All rows")
    trigger = page.get_by_role("combobox", name="Data ID", exact=True)
    trigger.click()
    page.get_by_role("option", name="Symbol", exact=True).click()
    trigger.click()
    search = page.get_by_role("searchbox", name="Search Data ID", exact=True)
    search.press("ArrowUp")
    search.press("Enter")
    assert_selected(page, "", "All rows")
    assert page.evaluate("events") == ["symbol", ""]
    page.evaluate("identity.replace([])")
    assert_selected(page, "", "Select…")


def test_table_header_popover_escapes_scroll_clipping_and_cleans_up(page):
    page.evaluate("""() => {
      const scroll=document.createElement('div');
      scroll.style.cssText='overflow:hidden;width:180px;height:45px;position:fixed;right:8px;bottom:8px';
      scroll.innerHTML=UI.table([{label:'Value',action:{key:'value',label:'Filter value'}}],[],'No matching rows',{keepHeaders:true});
      document.body.append(scroll);
      const anchor=scroll.querySelector('[data-table-action]');
      anchor.onclick=()=>{
        const content=document.createElement('div');content.innerHTML='<label>Value<input data-ui="input"></label><button data-ui="button">Apply</button>';
        window.surface=UI.popover(anchor,content,{label:'Value column',onClose:()=>window.popoverCloses=(window.popoverCloses||0)+1});
      };
    }""")
    expect(page.get_by_role('columnheader',name='Value')).to_be_visible()
    expect(page.get_by_text('No matching rows',exact=True)).to_be_attached()
    trigger=page.get_by_role('button',name='Filter value',exact=True)
    trigger.click()
    popup=page.get_by_role('dialog',name='Value column',exact=True)
    expect(popup).to_be_visible()
    assert popup.evaluate('el=>el.parentElement===document.body')
    assert popup.evaluate('el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight}')
    page.keyboard.press('Escape')
    expect(popup).to_have_count(0)
    expect(trigger).to_be_focused()
    assert page.evaluate('popoverCloses')==1
    trigger.click()
    page.locator('#outside').click()
    expect(popup).to_have_count(0)
    assert page.evaluate('popoverCloses')==2
