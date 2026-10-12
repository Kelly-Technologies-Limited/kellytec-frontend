/* Shared overview metric-grid renderer. */
(function (UI) {
  function fieldValue(field) {
    return UI.value(field.display || { kind: "text", value: field.value });
  }

  function renderField(field, className) {
    const tone = field.tone ? " monitor-metric-value-" + UI.esc(field.tone) : "";
    const multiline = field.multiline ? " monitor-metric-value-multiline" : "";
    const valueParts = Array.isArray(field.display_parts)
      ? field.display_parts.map(UI.value).filter(function (part) { return part !== UI.EMPTY; })
      : Array.isArray(field.value_parts)
      ? field.value_parts.map(function (part) { return UI.value({ kind: "text", value: part }); }).filter(function (part) { return part !== UI.EMPTY; })
      : [];
    const valueLines = valueParts.length > 1 ? " monitor-metric-value-lines" : "";
    const view = field.view || "";
    const title = field.title ? ' title="' + UI.esc(field.title) + '"' : "";
    const span = Math.max(1, Math.min(4, Number(field.span || 1)));
    const spanClass = !field.wide && span > 1 ? " " + className + "-span-" + span : "";
    const label = UI.esc(field.label || "");
    const mobileLabel = field.mobile_label ? UI.esc(field.mobile_label) : "";
    const labelHtml = mobileLabel ?
      '<span class="monitor-metric-label monitor-metric-label-desktop" data-ui-type="label">' + label + '</span>' +
      '<span class="monitor-metric-label monitor-metric-label-mobile" data-ui-type="label">' + mobileLabel + '</span>' :
      '<span class="monitor-metric-label" data-ui-type="label">' + label + '</span>';
    const value = valueParts.length
      ? valueParts.map(function (part) { return '<span data-ui-type="value">' + UI.esc(part) + '</span>'; }).join("")
      : UI.esc(fieldValue(field));
    const valueHtml = view ?
      '<a class="monitor-metric-value' + tone + multiline + valueLines + '" data-ui-type="value" href="#' + UI.esc(view) + '" data-monitor-view="' + UI.esc(view) + '"' + title + '>' + value + "</a>" :
      '<strong class="monitor-metric-value' + tone + multiline + valueLines + '" data-ui-type="value"' + title + '>' + value + "</strong>";
    return '<div class="' + className + (field.wide ? " " + className + "-wide" : "") + spanClass + '">' +
      labelHtml + valueHtml + "</div>";
  }

  function renderSection(section) {
    const fields = section.fields || [];
    const kind = section.kind ? ' data-monitor-section-kind="' + UI.esc(section.kind) + '"' : "";
    return '<section class="monitor-context-section"' + kind + '><div class="monitor-context-section-head"><h3 data-ui-type="section-title">' +
      UI.esc(section.title || "") + "</h3></div>" +
      '<div class="monitor-context-metrics">' +
      fields.map(function (field) { return renderField(field, "monitor-context-metric"); }).join("") +
      "</div></section>";
  }

  UI.renderField = renderField;
  UI.registerRenderer("metric_grid", {
    render: function (card) {
      const sections = card.sections || [];
      const interpretation = card.interpretation
        ? '<p class="monitor-card-note" data-ui-type="supporting">' + UI.esc(card.interpretation) + "</p>"
        : "";
      return {
        className: "monitor-card-metrics",
        html: '<div class="monitor-context-grid">' +
          sections.map(renderSection).join("") +
          "</div>" + interpretation
      };
    }
  });
})(window.MonitorUI);
