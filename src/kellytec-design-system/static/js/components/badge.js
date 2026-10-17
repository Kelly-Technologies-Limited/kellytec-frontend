/* Generic bubble construction. Callers own domain state → tone mapping. */
(function (UI) {
  UI.statusBadge = function (status, label, id) {
    const normalized = ["healthy", "warning", "critical", "unknown", "inactive"].includes(status) ? status : "unknown";
    return '<span class="badge ' + UI.esc(normalized) + '"' +
      (id ? ' id="' + UI.esc(id) + '"' : "") +
      ">" + UI.esc(label || UI.statusText(normalized)) + "</span>";
  };

  UI.compactBadge = function (tone, label, classes) {
    const allowed = ["neutral", "healthy", "warning", "critical", "unknown"];
    const safeTone = allowed.includes(tone) ? tone : "unknown";
    return '<span class="monitor-bubble monitor-bubble-compact ' + UI.esc(classes || "") + '" data-tone="' + safeTone + '" data-ui-type="badge-compact">' + UI.esc(label) + '</span>';
  };
  UI.metricBadge = function (label, value, tone, classes) {
    return '<span class="monitor-bubble monitor-bubble-metric ' + UI.esc(classes || "") + '" data-tone="' + UI.esc(["healthy", "critical", "unknown"].includes(tone) ? tone : "unknown") + '" data-ui-type="badge-metric"><span>' + UI.esc(label) + '</span><strong>' + UI.esc(value) + '</strong></span>';
  };
})(window.MonitorUI);
