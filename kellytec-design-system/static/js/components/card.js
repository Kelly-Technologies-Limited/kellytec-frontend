/* Canonical card shell and lifecycle. */
(function (UI) {
  UI.card = UI.renderCardShell = function (card, body, extraClass) {
    const id = card.id || "";
    const hideTitle = card.hide_title || card.hideTitle;
    const classes = "monitor-card" + (hideTitle ? " monitor-card-no-title" : "") +
      (extraClass ? " " + extraClass : "");
    return '<section class="' + classes + '" data-ui="card" data-card="' + UI.esc(id) + '">' +
      (hideTitle ? "" : '<div class="monitor-card-head" data-ui="card-head"><h2 data-ui-type="card-title">' + UI.esc(card.title || "") + "</h2></div>") +
      body + "</section>";
  };

  UI.renderCard = function (card, context) {
    const renderer = UI.rendererFor(card);
    const output = renderer && renderer.render ? renderer.render(card || {}, context || {}) : "";
    const body = typeof output === "string" ? output : (output && output.html) || "";
    const className = typeof output === "string" ? "" : (output && output.className) || "";
    return UI.card(card || {}, body, className);
  };

  UI.loadingCard = function (title, id) {
    return UI.card(
      { id: id || "loading", title: title || "", hide_title: !title },
      '<div class="monitor-loading-placeholder" aria-busy="true" aria-label="Loading content">' +
        '<span></span><span></span><span></span></div>',
      "monitor-card-loading"
    );
  };

  UI.errorCard = function (title, message, id) {
    return UI.card(
      { id: id || "error", title: title || "Unable to load" },
      '<div class="monitor-card-error" data-ui-type="supporting">' + UI.esc(message || "Unable to load") + "</div>",
      "monitor-card-error-shell"
    );
  };

  const bindings = new Map();
  let removalObserver;
  UI.bindCard = function (card, context) {
    const renderer = UI.rendererFor(card);
    if (!UI.bindChartText || !UI.bindTooltip || typeof document.querySelector !== "function") {
      if (renderer && renderer.bind) renderer.bind(card || {}, context || {});
      return;
    }
    const root = Array.from(document.querySelectorAll('[data-ui="card"]')).find(function (node) { return node.dataset.card === card.id; });
    if (!root) return;
    if (bindings.has(root)) bindings.get(root)();
    let textCleanup, tipCleanup, rendererCleanup;
    function bindShared() {
      if (textCleanup) textCleanup();
      if (tipCleanup) tipCleanup();
      textCleanup = UI.bindChartText(root);
      tipCleanup = UI.bindTooltip(root);
    }
    function dispose() {
      root.removeEventListener('monitor-chart-layout', bindShared);
      if (typeof rendererCleanup === 'function') rendererCleanup();
      if (textCleanup) textCleanup();
      if (tipCleanup) tipCleanup();
      bindings.delete(root);
    }
    root.addEventListener('monitor-chart-layout', bindShared);
    try {
      if (renderer && renderer.bind) rendererCleanup = renderer.bind(card || {}, context || {});
      bindShared();
    } catch (error) {
      dispose();
      throw error;
    }
    bindings.set(root, dispose);
    if (!removalObserver) {
      removalObserver = new MutationObserver(function () {
        bindings.forEach(function (dispose, node) { if (!node.isConnected) dispose(); });
      });
      removalObserver.observe(document.body, {childList: true, subtree: true});
    }
  };

  UI.registerRenderer("unknown", {
    render: function (card) {
      return '<div class="empty">No renderer for ' + UI.esc(card.renderer || card.kind || card.id || "card") + "</div>";
    }
  });
})(window.MonitorUI);
