/* Stable caller-selected series roles; CSS owns every color value. */
(function (UI) {
  UI.chartSeriesColor = function (role) {
    const colors = {
      pnl: 'var(--monitor-chart-pnl)',
      filled: 'var(--monitor-chart-filled)',
      canceled: 'var(--monitor-chart-canceled)',
      'series-1': 'var(--monitor-chart-series-1)',
      'series-2': 'var(--monitor-chart-series-2)',
      'series-3': 'var(--monitor-chart-series-3)',
      'series-4': 'var(--monitor-chart-series-4)',
      'categorical-1': 'var(--monitor-chart-categorical-1)',
      'categorical-2': 'var(--monitor-chart-categorical-2)',
      'categorical-3': 'var(--monitor-chart-categorical-3)',
      'categorical-4': 'var(--monitor-chart-categorical-4)'
    };
    return colors[role] || colors.pnl;
  };
  UI.chartLegendItem = function (config) {
    const swatch = config.series ? UI.chartSeriesSwatch(config.series) : 'background:' + UI.chartSeriesColor(config.role);
    return '<span class="monitor-chart-legend ' + UI.esc(config.className || '') + '" data-ui-type="chart-legend"><i style="' + swatch + '"></i><b>' + UI.esc(config.label) + '</b>' + (config.value === undefined ? '' : '<em>' + UI.esc(config.value) + '</em>') + '</span>';
  };
})(window.MonitorUI);
