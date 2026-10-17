/* Canonical cell shell. */
(function (UI) {
  UI.cell = function (body, options) {
    const config = options || {};
    const tag = config.tag === "article" ? "article" : "div";
    const classes = ["monitor-cell"];
    if (config.head) classes.push("monitor-cell-head");
    if (config.className) classes.push(config.className);
    const role = config.role ? ' role="' + UI.esc(config.role) + '"' : "";
    const title = config.title ? ' title="' + UI.esc(config.title) + '"' : "";
    const typography = ' data-ui-type="' + UI.esc(config.typography || "table-cell") + '"';
    const attributes = Object.keys(config.attributes || {}).map(function (name) {
      if (!/^data-[a-z0-9-]+$/.test(name)) return "";
      return ' ' + name + '="' + UI.esc(config.attributes[name]) + '"';
    }).join("");
    return '<' + tag + ' class="' + classes.join(" ") + '" data-ui="cell"' + role + title + typography + attributes + '>' +
      (body == null ? "" : String(body)) + "</" + tag + ">";
  };
})(window.MonitorUI);
