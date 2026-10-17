/* Canonical semantic table shell. */
(function (UI) {
  UI.table = function (headers, rows, emptyText, options) {
    if (!rows.length) return '<div class="empty">' + UI.esc(emptyText || "No data") + "</div>";
    const layout = options && options.equalColumns ? ' data-ui-column-layout="equal"' : '';
    const headerType = options && options.headerType || 'table-header';
    return '<div class="scroll"><table data-ui="table"' + layout + '><thead><tr>' +
      headers.map(function (heading) {
        const numeric = heading && typeof heading === "object" && heading.numeric;
        const label = heading && typeof heading === "object" ? heading.label : heading;
        const lines = heading && Array.isArray(heading.lines) ? heading.lines : null;
        const content = lines ? lines.map(function (line) {
          return '<span class="monitor-table-header-line">' + UI.esc(line) + '</span>';
        }).join(' ') : UI.esc(label);
        return '<th data-ui-type="' + UI.esc(headerType) + '"' + (numeric ? ' data-ui-numeric="true"' : '') + '>' + content + "</th>";
      }).join("") +
      "</tr></thead><tbody>" + rows.map(function (row) {
        return "<tr>" + row.map(function (value, index) {
          return '<td data-ui-type="table-cell"' + (headers[index] && headers[index].numeric ? ' data-ui-numeric="true"' : '') + '>' + value + "</td>";
        }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  };

  // Multiple measurements with distinct units share the same numeric anchor.
  UI.labelValues = function (items) {
    return '<span class="monitor-label-values">' + items.map(function (item) {
      return '<span class="monitor-label-value"><span data-ui-type="supporting">' + UI.esc(item.label || '') +
        '</span><span data-ui-type="value">' + UI.esc(UI.value(item.value)) + '</span></span>';
    }).join('') + '</span>';
  };
})(window.MonitorUI);
