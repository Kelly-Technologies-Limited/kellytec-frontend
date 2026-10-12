/* Shared placeholder card renderer. */
(function (UI) {
  UI.registerRenderer("placeholder", {
    render: function (card) {
      return {
        className: "monitor-card-muted",
        html: '<div class="monitor-card-placeholder">' + UI.esc(card.description || "Pending") + "</div>"
      };
    }
  });
})(window.MonitorUI);
