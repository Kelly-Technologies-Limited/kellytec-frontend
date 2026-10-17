/* Generic log-table shell; each monitor owns its field mapping. */
(function (UI) {
  function attribute(value) {
    return UI.esc(value).replace(/"/g, "&quot;");
  }

  UI.logTable = function (rows, options) {
    const config = options || {};
    const headers = config.headers || [];
    if (!rows.length && !headers.length) return '<div class="empty">' + UI.esc(config.emptyText || "No logs") + "</div>";
    const attributes = Object.keys(config.attributes || {}).map(function (name) {
      if (!/^data-[a-z0-9-]+$/.test(name)) return "";
      return ' ' + name + '="' + attribute(config.attributes[name]) + '"';
    }).join("");
    if (headers.length) {
      const controls = config.headerControls || [];
      const controlRow = controls.length ? '<tr class="monitor-log-table-controls' +
        (config.controlsClassName ? ' ' + attribute(config.controlsClassName) : '') + '">' +
        controls.map(function (control) {
          const span = control.span || 1;
          if (!Number.isInteger(span) || span < 1) throw new TypeError('Header control span must be a positive integer');
          return '<td colspan="' + span + '">' + control.html + '</td>';
        }).join('') + '</tr>' : '';
      const body = rows.length ? rows.map(function (cells) {
        return '<tr>' + cells.map(function (body) {
          return '<td data-ui-type="table-cell">' + body + '</td>';
        }).join("") + '</tr>';
      }).join("") : '<tr><td colspan="' + headers.length + '"><div class="empty">' +
        UI.esc(config.emptyText || "No logs") + '</div></td></tr>';
      return '<div class="monitor-log-table monitor-log-table--headed' +
        (config.className ? " " + attribute(config.className) : "") +
        '" data-ui="log-table" role="region" aria-label="' + attribute(config.label || "Logs") +
        '" tabindex="0"' + attributes + '><table data-ui="table"><colgroup>' +
        headers.map(function () { return '<col>'; }).join('') + '</colgroup><thead>' + controlRow + '<tr>' +
        headers.map(function (heading) {
          return '<th scope="col" data-ui-type="' + attribute(config.headerTypography || "table-header") + '">' + UI.esc(heading) + '</th>';
        }).join("") + '</tr></thead><tbody>' + body + '</tbody></table></div>';
    }
    return '<div class="monitor-log-table' + (config.className ? " " + attribute(config.className) : "") + '" data-ui="log-table" role="table" tabindex="0"' + attributes + '>' +
      rows.map(function (cells) {
        return '<div class="monitor-log-table-row" role="row">' + cells.map(function (body) {
          return UI.cell(body, { className: "monitor-log-table-cell", role: "cell", typography: "table-cell" });
        }).join("") + "</div>";
      }).join("") + "</div>";
  };
})(window.MonitorUI);
