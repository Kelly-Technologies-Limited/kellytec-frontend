/* Stateful checkbox selection shared by factor and strategy forms. */
(function (UI) {
  UI.selection = function (root, options) {
    const selected = new Set(options.selected || []);
    let query = '', selectedOnly = false, items = options.items || [];
    root.dataset.ui = 'selection';
    root.classList.toggle('selection-compact', !!options.compact);
    root.innerHTML = '<div class="selection-tools"><input data-ui="input" type="search" aria-label="Search choices" placeholder="Search">' +
      '<button data-ui="button" type="button" data-action="select">Select filtered</button><button data-ui="button" type="button" data-action="clear">Clear filtered</button>' +
      '<label><input type="checkbox" data-action="only"> Selected only</label></div>' +
      '<div class="selection-options" role="group" aria-label="' + UI.esc(options.label || 'Choices') + '"></div><div class="selection-count" aria-live="polite"></div>';
    const list = root.querySelector('.selection-options');
    function filtered() {
      return items.filter(x => (x.label || x.id).toLowerCase().includes(query) && (!selectedOnly || selected.has(x.id)));
    }
    function render() {
      const focus = list.contains(document.activeElement) ? document.activeElement.value : null;
      const scroll = list.scrollTop;
      list.innerHTML = filtered().map(x => '<label class="selection-option" title="' + UI.esc(x.label || x.id) + '">' +
        '<input type="checkbox" value="' + UI.esc(x.id) + '"' + (selected.has(x.id) ? ' checked' : '') + '><span>' + UI.esc(x.label || x.id) + '</span></label>').join('');
      root.querySelector('.selection-count').textContent = options.count ? options.count([...selected]) : selected.size + ' selected';
      if (focus) Array.from(list.querySelectorAll('input')).find(input => input.value === focus)?.focus({preventScroll:true});
      list.scrollTop = scroll;
    }
    function changed() { render(); if (options.onChange) options.onChange([...selected]); }
    root.querySelector('input[type="search"]').addEventListener('input', e => { query = e.target.value.toLowerCase(); render(); });
    root.querySelector('[data-action="only"]').addEventListener('change', e => { selectedOnly = e.target.checked; render(); });
    root.querySelector('[data-action="select"]').addEventListener('click', () => { filtered().forEach(x => selected.add(x.id)); changed(); });
    root.querySelector('[data-action="clear"]').addEventListener('click', () => { filtered().forEach(x => selected.delete(x.id)); changed(); });
    list.addEventListener('change', e => { if (e.target.checked) selected.add(e.target.value); else selected.delete(e.target.value); changed(); });
    render();
    return {values: () => [...selected], replace: function (next) { items = next; const ids = new Set(items.map(x => x.id)); [...selected].forEach(id => { if (!ids.has(id)) selected.delete(id); }); changed(); }};
  };
})(window.MonitorUI);
