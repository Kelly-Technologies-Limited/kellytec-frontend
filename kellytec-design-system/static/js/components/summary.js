/* A compact summary of caller-owned display values. */
(function (UI) {
  UI.summary = function (config) {
    const fields = (config.fields || []).map(function (field) {
      const value = UI.value(field.value || {});
      const content = value !== UI.EMPTY && field.datetime
        ? '<time datetime="' + UI.esc(field.datetime) + '">' + UI.esc(value) + '</time>' : UI.esc(value);
      return '<div class="monitor-summary-field"><dt data-ui-type="field-label">' + UI.esc(field.label) + '</dt><dd data-ui-type="metadata-value" data-freshness-field="' + UI.esc(field.key || "") + '">' + content + '</dd></div>';
    }).join("");
    return '<section class="monitor-summary" aria-label="' + UI.esc(config.label || "Summary") + '"><div class="monitor-summary-head">' +
      UI.statusBadge(config.status.value, UI.value(config.status)) + '</div><dl class="monitor-summary-fields">' + fields + '</dl></section>';
  };
})(window.MonitorUI);
