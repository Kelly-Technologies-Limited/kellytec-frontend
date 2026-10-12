/* Canonical DOM and renderer registry for every monitor. */
(function (global) {
  const UI = global.MonitorUI = global.MonitorUI || {};
  const renderers = UI.renderers = UI.renderers || {};

  UI.EMPTY = "—";

  UI.esc = function (value) {
    const el = document.createElement("div");
    el.textContent = value == null ? "" : String(value);
    return el.innerHTML.replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  };

  UI.firstPresent = function (row, keys) {
    if (!row || typeof row !== "object") return null;
    for (let i = 0; i < keys.length; i++) {
      if (row[keys[i]] !== null && row[keys[i]] !== undefined) return row[keys[i]];
    }
    return null;
  };

  UI.registerRenderer = function (name, renderer) {
    if (!name || !renderer || typeof renderer.render !== "function") {
      throw new TypeError("renderer requires a name and render function");
    }
    renderers[name] = renderer;
  };

  UI.rendererFor = function (card) {
    return renderers[(card || {}).renderer] || renderers[(card || {}).kind] || renderers.unknown;
  };
})(window);
