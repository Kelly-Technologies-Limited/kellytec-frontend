/* CSS font sizes describe screen pixels, including stretched and rotated SVGs. */
(function (UI) {
  const original = new WeakMap();
  UI.bindChartText = function (root) {
    const charts = Array.from(root.querySelectorAll('svg[data-ui-chart]'));
    function update() {
      charts.forEach(function (chart) {
        const m = chart.getScreenCTM();
        let zoom = 1;
        for (let node = chart; node; node = node.parentElement) zoom *= Number(getComputedStyle(node).zoom) || 1;
        if (!m || !chart.getBoundingClientRect().width || m.a <= 0 || m.d <= 0) return;
        chart.querySelectorAll('text').forEach(function (text) {
          if (!original.has(text)) original.set(text, text.getAttribute('transform') || '');
          const x = Number(text.getAttribute('x') || 0), y = Number(text.getAttribute('y') || 0);
          const rotate = text.hasAttribute('data-axis-vertical') ? 'rotate(-90 ' + x + ' ' + y + ')' : original.get(text);
          text.setAttribute('transform', 'translate(' + x + ' ' + y + ') scale(' + (zoom / m.a) + ' ' + (zoom / m.d) + ') translate(' + (-x) + ' ' + (-y) + ') ' + rotate);
        });
      });
    }
    const observer = new ResizeObserver(update);
    charts.forEach(function (chart) { observer.observe(chart); });
    update();
    let alive = true;
    if (document.fonts) document.fonts.ready.then(function () { if (alive) update(); });
    return function () { alive = false; observer.disconnect(); };
  };
})(window.MonitorUI);
