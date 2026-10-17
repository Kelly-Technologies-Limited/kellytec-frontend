/* One tooltip per bound card. Never changes data, status or value formatting. */
(function (UI) {
  let nextId = 0;
  UI.bindTooltip = function (root) {
    const hits = Array.from(root.querySelectorAll('[data-ui-tooltip]'));
    if (!hits.length) return function () {};
    const tip = document.createElement('div');
    tip.className = 'monitor-tooltip'; tip.id = 'monitor-tooltip-' + (++nextId);
    tip.setAttribute('role', 'tooltip'); tip.setAttribute('data-ui-type', 'tooltip');
    tip.hidden = true; root.appendChild(tip);
    const controller = new AbortController();
    let active = null;
    function hide() {
      tip.hidden = true;
      if (active) active.removeAttribute('aria-describedby');
      active = null;
    }
    function show(hit, x, y) {
      if (active !== hit) hide();
      active = hit; tip.textContent = (hit.getAttribute('data-ui-tooltip') || hit.getAttribute('aria-label'));
      tip.hidden = false; hit.setAttribute('aria-describedby', tip.id);
      tip.style.left = Math.max(8, Math.min(window.innerWidth - tip.offsetWidth - 12, x + 14)) + 'px';
      tip.style.top = Math.max(8, Math.min(window.innerHeight - tip.offsetHeight - 12, y + 14)) + 'px';
    }
    function listen(target, name, fn) { target.addEventListener(name, fn, {signal: controller.signal}); }
    hits.forEach(function (hit) {
      if (!hit.hasAttribute('tabindex')) hit.setAttribute('tabindex', '0');
      if (!hit.hasAttribute('aria-label')) hit.setAttribute('aria-label', (hit.getAttribute('data-ui-tooltip') || hit.getAttribute('aria-label')));
    });
    listen(root, 'pointermove', function (event) {
      const hit = event.target.closest('[data-ui-tooltip]');
      if (hit && root.contains(hit)) show(hit, event.clientX, event.clientY); else hide();
    });
    listen(root, 'pointerleave', hide);
    listen(root, 'focusin', function (event) {
      const hit = event.target.closest('[data-ui-tooltip]');
      if (!hit) return;
      const r = hit.getBoundingClientRect(); show(hit, r.left + r.width / 2, r.top + r.height / 2);
    });
    listen(root, 'focusout', hide);
    listen(document, 'keydown', function (event) { if (event.key === 'Escape') hide(); });
    listen(window, 'resize', hide);
    listen(window, 'scroll', hide);
    return function () { hide(); controller.abort(); tip.remove(); };
  };
})(window.MonitorUI);
