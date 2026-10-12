/* Opaque category keys keep their visual identity across cards and refreshes. */
(function (UI) {
  const assigned = new Map();

  UI.chartSeriesStyle = function (key, catalog) {
    (catalog || []).concat([key]).forEach(function (item) {
      if (!assigned.has(item)) assigned.set(item, assigned.size);
    });
    const index = assigned.get(key);
    return { key: key, index: index, role: 'series-' + (index % 4 + 1), pattern: Math.floor(index / 4) };
  };

  UI.chartSeriesFill = function (style, namespace) {
    return style.pattern ? 'url(#' + namespace + '-series-' + style.index + ')' : UI.chartSeriesColor(style.role);
  };

  UI.chartSeriesDefinitions = function (styles, namespace) {
    return '<defs>' + styles.filter(function (style) { return style.pattern; }).map(function (style) {
      const spacing = 4 + Math.floor((style.pattern - 1) / 3) * 2;
      const color = UI.chartSeriesColor(style.role);
      const direction = [45, -45, 0][(style.pattern - 1) % 3];
      return '<pattern id="' + UI.esc(namespace) + '-series-' + style.index + '" patternUnits="userSpaceOnUse" width="' + spacing + '" height="' + spacing + '" patternTransform="rotate(' + direction + ')">' +
        '<rect width="' + spacing + '" height="' + spacing + '" fill="' + color + '"/>' +
        '<line x1="0" y1="0" x2="0" y2="' + spacing + '" stroke="var(--monitor-surface-raised)" stroke-width="2"/></pattern>';
    }).join('') + '</defs>';
  };

  UI.chartSeriesSwatch = function (style) {
    const color = UI.chartSeriesColor(style.role);
    if (!style.pattern) return 'background:' + color;
    const spacing = 4 + Math.floor((style.pattern - 1) / 3) * 2;
    const angle = [45, -45, 0][(style.pattern - 1) % 3];
    return 'background:repeating-linear-gradient(' + angle + 'deg,var(--monitor-surface-raised) 0px,var(--monitor-surface-raised) 2px,' + color + ' 2px,' + color + ' ' + spacing + 'px)';
  };
})(window.MonitorUI);
