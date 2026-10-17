/* Small escaped SVG primitives; geometry belongs to the caller. */
(function (UI) {
  UI.svgText = function (x, y, value, attributes) {
    return '<text x="' + Number(x) + '" y="' + Number(y) + '" ' + (attributes || '') + '>' + UI.esc(value) + '</text>';
  };
  UI.svgLine = function (x1, y1, x2, y2, attributes) {
    return '<line x1="' + Number(x1) + '" y1="' + Number(y1) + '" x2="' + Number(x2) + '" y2="' + Number(y2) + '" ' + (attributes || '') + '/>';
  };
})(window.MonitorUI);
