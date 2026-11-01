/* Pure service-row presentation; applications own state and time interpretation. */
(function (UI) {
  /** Render display rows: {name, status, tone, updatedAt:{short, full}, reason}. */
  UI.serviceTable = function (rows) {
    return '<div class="monitor-service-table" data-ui="service-table">' +
      '<div class="monitor-service-table-head" data-ui-type="label"><span>Services</span><span>Status</span><span>Updated At</span><span>Reason</span></div>' +
      rows.map(function (row) {
        return '<div class="monitor-service-row" data-ui="service-row" data-ui-type="table-detail" title="' + UI.esc(row.reason) + '">' +
          '<div class="monitor-service-name" title="' + UI.esc(row.name) + '">' + UI.esc(row.name) + '</div>' +
          '<div class="monitor-service-state">' + UI.compactBadge(row.tone, row.status) + '</div>' +
          '<div class="monitor-service-updated" title="' + UI.esc(row.updatedAt.full) + '">' + UI.esc(row.updatedAt.short) + '</div>' +
          '<div class="monitor-service-reason" title="' + UI.esc(row.reason) + '">' + UI.esc(row.reason) + '</div>' +
          '</div>';
      }).join('') + '</div>';
  };
})(window.MonitorUI);
