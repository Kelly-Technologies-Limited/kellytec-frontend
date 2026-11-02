/* Canonical semantic table shell. */
(function (UI) {
  UI.table = function (headers, rows, emptyText, options) {
    options = options || {};
    if (!rows.length && !options.keepHeaders) return '<div class="empty">' + UI.esc(emptyText || "No data") + "</div>";
    const widths = options.columnWidths;
    if (widths && (!Array.isArray(widths) || widths.length !== headers.length ||
      widths.some(width => !Number.isInteger(width) || width <= 0))) {
      throw new TypeError('Table columnWidths must contain one positive integer per header');
    }
    const layout = widths ? ' data-ui-column-layout="fixed" style="width:' + widths.reduce((sum, width) => sum + width, 0) + 'px"' :
      options.equalColumns ? ' data-ui-column-layout="equal"' : '';
    const columnGroup = widths ? '<colgroup>' + widths.map(width => '<col style="width:' + width + 'px">').join('') + '</colgroup>' : '';
    const headerType = options.headerType || 'table-header';
    const compact = options.density === 'compact';
    const density = compact ? ' data-ui-table-density="compact"' : '';
    const sticky = (options.stickyHeader ? ' data-sticky-header="true"' : '') + (options.stickyFirst ? ' data-sticky-first="true"' : '');
    return '<div class="scroll ' + UI.esc(options.scrollClass || '') + '"><table data-ui="table" class="' + UI.esc(options.className || '') + '"' + layout + sticky + density + '>' + columnGroup + '<thead><tr>' +
      headers.map(function (heading) {
        const numeric = heading && typeof heading === "object" && heading.numeric;
        const label = heading && typeof heading === "object" ? heading.label : heading;
        const lines = heading && Array.isArray(heading.lines) ? heading.lines : null;
        const content = lines ? lines.map(function (line) {
          return '<span class="table-header-line">' + UI.esc(line) + '</span>';
        }).join(' ') : UI.esc(label);
        const action = heading && heading.action;
        const sort = heading && heading.sort;
        const ariaSort = sort ? ' aria-sort="' + (sort === 'asc' ? 'ascending' : 'descending') + '"' : '';
        const indicator = '<span class="table-header-indicator" aria-hidden="true">' + (sort === 'asc' ? '↑' : sort === 'desc' ? '↓' : '⌄') + '</span>';
        const button = action ? '<button type="button" class="table-header-action" data-table-action="' + UI.esc(action.key) + '" aria-label="' + UI.esc(action.label) + '" aria-haspopup="dialog" aria-expanded="false" data-active="' + !!action.active + '">' +
          (compact ? '<span class="table-header-label">' + content + '</span>' + indicator : indicator) + '</button>' : '';
        const headingContent = !action ? content : compact ? button :
          '<span class="table-header-content"><span class="table-header-label">' + content + '</span>' + button + '</span>';
        return '<th data-ui-type="' + UI.esc(headerType) + '" title="' + UI.esc(label) + '"' +
          (compact ? ' aria-label="' + UI.esc(label) + '"' : '') + ariaSort +
          (numeric ? ' data-ui-numeric="true"' : '') + '>' + headingContent + '</th>';
      }).join('') + '</tr></thead><tbody>' + (rows.length ? rows.map(function (row) {
        return '<tr>' + row.map(function (value, index) {
          return '<td data-ui-type="table-cell"' + (headers[index] && headers[index].numeric ? ' data-ui-numeric="true"' : '') + '>' + value + '</td>';
        }).join('') + '</tr>';
      }).join('') : '<tr><td colspan="' + Math.max(1, headers.length) + '" class="empty">' + UI.esc(emptyText || 'No data') + '</td></tr>') + '</tbody></table></div>';
  };

  // Multiple measurements with distinct units share the same numeric anchor.
  UI.labelValues = function (items) {
    return '<span class="label-values">' + items.map(function (item) {
      return '<span class="label-value"><span data-ui-type="supporting">' + UI.esc(item.label || '') +
        '</span><span data-ui-type="value">' + UI.esc(UI.value(item.value)) + '</span></span>';
    }).join('') + '</span>';
  };
})(window.UI);
