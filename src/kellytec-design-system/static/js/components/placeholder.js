/* Shared placeholder card renderer. */
(function (UI) {
  UI.registerRenderer("placeholder", {
    render: function (card) {
      return {
        className: "card-muted",
        html: '<div class="card-placeholder">' + UI.esc(card.description || "Pending") + "</div>"
      };
    }
  });
})(window.UI);
