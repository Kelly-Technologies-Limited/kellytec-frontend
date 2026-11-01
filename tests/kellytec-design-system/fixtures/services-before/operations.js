/* Shared server-card renderer. */
(function (UI) {
  function attr(value) {
    return UI.esc(value).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function renderSuperfactors(server) {
    const cells = server.superfactor_cells || [];
    if (!server.superfactor_source) return "";
    return '<div class="monitor-superfactors">' +
      '<div class="monitor-workload-head"><h3 data-ui-type="cell-heading">Superfactors</h3></div>' +
      '<div class="monitor-superfactor-table">' +
      '<div class="monitor-superfactor-head" data-ui-type="label"><span>factor_id</span><span>Value</span><span>Status</span><span>Log</span></div>' +
      cells.map(function (cell) {
        const status = cell.placeholder ? "—" : (cell.status || "unknown");
        const identity = [cell.output_id, cell.session_id, cell.resolution].join(" | ");
        const statusBody = UI.compactBadge(({ok:"neutral", pending:"neutral", nd:"warning", err:"critical"})[cell.status] || "unknown", status);
        return '<div class="monitor-superfactor-row monitor-superfactor-row-' + UI.esc(cell.tone || "unknown") + '" data-ui-type="table-detail" title="' + attr(cell.detail || "") + '">' +
          '<div class="monitor-superfactor-name" title="' + attr(identity) + '">' + UI.esc(cell.output_id || "") + '</div>' +
          '<div class="monitor-superfactor-current" title="' + attr(cell.value_detail || cell.value || "") + '">' + UI.esc(cell.value || "-") + '</div>' +
          '<div class="monitor-superfactor-state">' + statusBody + '</div>' +
          '<div class="monitor-superfactor-log">' + UI.esc(cell.log || "") + '</div>' +
          '</div>';
      }).join("") + "</div></div>";
  }

  function workloadStatusTone(status) {
    if (status === "live" || status === "success" || status === "in_progress") return "ok";
    if (status === "warning") return "warn";
    if (status === "offline" || status === "failed") return "bad";
    return "unknown";
  }

  function workloadUpdatedAt(value) {
    if (!value) return { short: "—", full: "—" };
    const full = UI.value({ kind: "datetime_et", value: value });
    const match = full.match(/(\d{2}:\d{2}:\d{2}\s+E[DS]?T)$/);
    return { short: match ? match[1] : full, full: full };
  }

  function renderWorkloadSection(title, section) {
    const rows = (section || {}).rows || [];
    return '<section class="monitor-workload-section">' +
      '<div class="monitor-workload-head"><h3 data-ui-type="cell-heading">' + UI.esc(title) + '</h3></div>' +
      '<div class="monitor-workload-table">' +
      '<div class="monitor-superfactor-head monitor-workload-table-head" data-ui-type="label"><span>Services</span><span>Status</span><span>Updated At</span><span>Reason</span></div>' +
      rows.map(function (row) {
        const status = row.status || "—";
        const updatedAt = workloadUpdatedAt(row.kind === "job" ? row.status_at : row.observed_at);
        const reason = row.reason || "—";
        return '<div class="monitor-superfactor-row monitor-workload-row" data-ui-type="table-detail" title="' + attr(reason) + '">' +
          '<div class="monitor-workload-service" title="' + attr(row.name || "") + '">' + UI.esc(row.name || "") + '</div>' +
          '<div class="monitor-superfactor-state">' + UI.compactBadge(({ok:"healthy",warn:"warning",bad:"critical"})[workloadStatusTone(status)] || "unknown", status) + '</div>' +
          '<div class="monitor-workload-updated" title="' + attr(updatedAt.full) + '">' + UI.esc(updatedAt.short) + '</div>' +
          '<div class="monitor-superfactor-log" title="' + attr(reason) + '">' + UI.esc(reason) + '</div>' +
          '</div>';
      }).join("") + '</div></section>';
  }

  function renderWorkloads(server) {
    const workloads = server.workloads || {};
    if (!workloads.runtime && !workloads.jobs) return "";
    return '<div class="monitor-workloads">' +
      renderWorkloadSection("Runtime", workloads.runtime || {}) +
      renderWorkloadSection("Job", workloads.jobs || {}) +
      '</div>';
  }

  function renderServer(server) {
    const status = server.status || "unknown";
    return UI.cell(
      '<div class="monitor-server-head"><div class="monitor-server-title-block"><h3 data-ui-type="cell-title">' + UI.esc(server.project_id || "") + '</h3><div class="monitor-server-role" data-ui-type="label">' +
      UI.esc(server.role || "") + "</div></div>" + UI.statusBadge(status, server.status_text) + "</div>" +
      '<div class="monitor-server-metrics">' +
      (server.fields || []).map(function (field) { return UI.renderField(field, "monitor-server-metric"); }).join("") +
      "</div>" + renderSuperfactors(server) + renderWorkloads(server),
      { className: "monitor-server status-" + status }
    );
  }

  UI.registerRenderer("servers", {
    render: function (card) {
      const servers = card.servers || [];
      const body = servers.length ?
        '<div class="monitor-server-list">' + servers.map(renderServer).join("") + "</div>" :
        '<div class="empty">No server data</div>';
      return { className: "monitor-card-servers", html: body };
    }
  });
})(window.MonitorUI);
