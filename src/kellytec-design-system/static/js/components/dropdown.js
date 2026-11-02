/* Single-select dropdown: committed value and transient search are independent. */
(function (UI) {
  const controls = new WeakMap();
  let sequence = 0, openControl = null;

  UI.dropdown = function (root, options) {
    if (controls.has(root)) controls.get(root).destroy();
    options = options || {};
    if (!root.id) root.id = 'ui-dropdown-' + (++sequence);
    let items = normalize(options.items || []), value = '', query = '', active = null;
    let label = options.label || 'Choices', opened = false, destroyed = false;
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.id = root.id + '-trigger';
    trigger.className = 'dropdown-trigger';
    trigger.dataset.ui = 'select';
    trigger.setAttribute('role', 'combobox');
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');
    const display = document.createElement('span');
    display.className = 'dropdown-value';
    const chevron = document.createElement('span');
    chevron.className = 'dropdown-chevron';
    chevron.setAttribute('aria-hidden', 'true');
    trigger.append(display, chevron);
    const popup = document.createElement('div');
    popup.className = 'dropdown-popup';
    popup.hidden = true;
    const list = document.createElement('div');
    list.id = root.id + '-listbox';
    list.className = 'dropdown-list';
    list.setAttribute('role', 'listbox');
    trigger.setAttribute('aria-controls', list.id);
    const search = options.searchable ? document.createElement('input') : null;
    if (search) {
      search.type = 'search';
      search.className = 'dropdown-search';
      search.dataset.ui = 'input';
      search.setAttribute('role', 'searchbox');
      search.setAttribute('aria-controls', list.id);
      search.autocomplete = 'off';
      popup.append(search);
      search.addEventListener('input', function () {
        query = search.value.toLocaleLowerCase();
        active = (filtered().find(item => !item.disabled) || {}).id ?? null;
        renderList();
      });
      // Only a committed option produces the host's public change event.
      search.addEventListener('change', event => event.stopPropagation());
      search.addEventListener('keydown', keydown);
    }
    popup.append(list);
    root.dataset.ui = 'dropdown';
    root.replaceChildren(trigger, popup);

    function normalize(next) {
      const ids = new Set();
      return next.map(item => {
        if (typeof item.id !== 'string' || ids.has(item.id)) {
          throw new TypeError('Dropdown items require unique string ids');
        }
        ids.add(item.id);
        return {id:item.id, label:String(item.label == null ? item.id : item.label), disabled:!!item.disabled};
      });
    }
    function filtered() { return items.filter(item => item.label.toLocaleLowerCase().includes(query)); }
    function renderValue() {
      const item = items.find(item => item.id === value);
      display.textContent = item ? item.label : (options.placeholder || 'Select…');
      trigger.title = item ? item.label : '';
      trigger.value = value;
      root.dataset.value = value;
      trigger.setAttribute('aria-label', label);
      list.setAttribute('aria-label', label);
      if (search) {
        search.setAttribute('aria-label', 'Search ' + label);
        search.placeholder = 'Search ' + label;
      }
    }
    function renderList() {
      list.replaceChildren();
      const visible = filtered();
      visible.forEach(item => {
        const option = document.createElement('button');
        option.type = 'button';
        option.tabIndex = -1;
        option.className = 'dropdown-option';
        option.id = root.id + '-option-' + items.indexOf(item);
        option.setAttribute('role', 'option');
        option.setAttribute('aria-selected', String(item.id === value));
        option.setAttribute('aria-disabled', String(item.disabled));
        option.dataset.active = String(item.id === active);
        option.disabled = item.disabled;
        option.title = item.label;
        const text = document.createElement('span');
        text.textContent = item.label;
        option.append(text);
        option.addEventListener('click', () => commit(item.id));
        list.append(option);
      });
      if (!visible.length) {
        const empty = document.createElement('p');
        empty.className = 'dropdown-empty';
        empty.setAttribute('role', 'status');
        empty.textContent = 'No matches';
        list.append(empty);
      }
      const current = list.querySelector('[data-active="true"]');
      [trigger, search].filter(Boolean).forEach(element => {
        if (current) element.setAttribute('aria-activedescendant', current.id);
        else element.removeAttribute('aria-activedescendant');
      });
      if (current && opened) current.scrollIntoView({block:'nearest'});
    }
    function close(focus) {
      if (!opened) return;
      opened = false;
      popup.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      trigger.removeAttribute('aria-activedescendant');
      if (search) search.removeAttribute('aria-activedescendant');
      document.removeEventListener('pointerdown', outside);
      document.removeEventListener('focusin', outside);
      if (openControl === controller) openControl = null;
      if (focus) trigger.focus({preventScroll:true});
    }
    function outside(event) { if (!root.contains(event.target)) close(false); }
    function open(direction) {
      if (destroyed || trigger.disabled || opened) return;
      if (openControl) openControl.close();
      openControl = controller;
      query = '';
      if (search) search.value = '';
      const enabled = items.filter(item => !item.disabled);
      active = enabled.some(item => item.id === value) ? value :
        (((direction === -1 ? enabled[enabled.length - 1] : enabled[0]) || {}).id ?? null);
      opened = true;
      popup.hidden = false;
      trigger.setAttribute('aria-expanded', 'true');
      renderList();
      document.addEventListener('pointerdown', outside);
      document.addEventListener('focusin', outside);
      (search || trigger).focus({preventScroll:true});
    }
    function setValue(next, settings) {
      next = next == null ? '' : String(next);
      if (next && !items.some(item => item.id === next)) throw new RangeError('Unknown dropdown value: ' + next);
      const changed = next !== value;
      value = next;
      renderValue();
      if (opened) renderList();
      if (changed && settings && settings.emit) {
        root.dispatchEvent(new CustomEvent('change', {bubbles:true, detail:{value:value}}));
        if (options.onChange) options.onChange(value);
      }
    }
    function commit(next) {
      if (!items.some(item => item.id === next && !item.disabled)) return;
      close(true);
      setValue(next, {emit:true});
    }
    function keydown(event) {
      if (event.key === 'Escape' && opened) { event.preventDefault(); close(true); return; }
      if (event.key === 'Tab') { close(false); return; }
      if (event.key === 'Enter' && opened) {
        event.preventDefault();
        if (active !== null) commit(active);
        return;
      }
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      event.preventDefault();
      const direction = event.key === 'ArrowDown' ? 1 : -1;
      if (!opened) { open(direction); return; }
      const enabled = filtered().filter(item => !item.disabled);
      if (!enabled.length) return;
      const index = enabled.findIndex(item => item.id === active);
      active = enabled[(index + direction + enabled.length) % enabled.length].id;
      renderList();
    }
    trigger.addEventListener('click', () => opened ? close(false) : open(1));
    trigger.addEventListener('keydown', keydown);
    const controller = {
      value: () => value,
      setValue: setValue,
      replace: function (next, settings) {
        const replacement = normalize(next);
        settings = settings || {};
        const nextValue = Object.prototype.hasOwnProperty.call(settings, 'value') ? settings.value : value;
        close(false);
        items = replacement;
        if (settings.label != null) label = String(settings.label);
        setValue(items.some(item => item.id === nextValue) ? nextValue : '', {emit:false});
      },
      setDisabled: function (disabled) { trigger.disabled = !!disabled; if (disabled) close(false); },
      close: () => close(false),
      destroy: function () {
        close(false);
        destroyed = true;
        root.replaceChildren();
        delete root.dataset.ui;
        delete root.dataset.value;
        controls.delete(root);
      }
    };
    controls.set(root, controller);
    setValue(options.value || '', {emit:false});
    controller.setDisabled(options.disabled);
    return controller;
  };
})(window.UI);

/* Anchored interactive surface outside scroll containers. Caller owns content. */
(function(UI) {
  let opened = null;
  UI.popover = function(anchor, content, options) {
    options = options || {};
    if(opened)opened.close();
    const root=document.createElement('div');root.className='ui-popover';root.dataset.ui='popover';
    root.setAttribute('role','dialog');root.setAttribute('aria-label',options.label || 'Options');root.tabIndex=-1;
    root.append(content);document.body.append(root);
    let closed=false;
    function reposition(){
      if(closed)return;
      const a=anchor.getBoundingClientRect(),gap=8,margin=8;
      const width=Math.min(options.width || 340,window.innerWidth-margin*2);
      root.style.width=width+'px';root.style.maxHeight=(window.innerHeight-margin*2)+'px';
      root.style.left=Math.max(margin,Math.min(a.left,window.innerWidth-width-margin))+'px';
      const height=root.getBoundingClientRect().height;
      root.style.top=Math.max(margin,Math.min(a.bottom+gap,window.innerHeight-height-margin))+'px';
    }
    function close(focus){
      if(closed)return;closed=true;root.remove();anchor.setAttribute('aria-expanded','false');
      document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',keydown);
      window.removeEventListener('resize',reposition);window.removeEventListener('scroll',onScroll,true);
      if(opened===controller)opened=null;if(focus && anchor.isConnected)anchor.focus({preventScroll:true});
      if(options.onClose)options.onClose();
    }
    function outside(event){if(!root.contains(event.target) && !anchor.contains(event.target))close(false);}
    function keydown(event){if(event.key==='Escape'){event.preventDefault();close(true);}}
    function onScroll(event){if(!root.contains(event.target))reposition();}
    const controller={close:()=>close(false),reposition,element:root};opened=controller;
    anchor.setAttribute('aria-expanded','true');reposition();
    document.addEventListener('pointerdown',outside);document.addEventListener('keydown',keydown);
    window.addEventListener('resize',reposition);window.addEventListener('scroll',onScroll,true);
    (root.querySelector('button,input,[tabindex="0"]') || root).focus({preventScroll:true});
    return controller;
  };
})(window.UI);
