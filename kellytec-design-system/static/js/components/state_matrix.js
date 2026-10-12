/* Canonical dense state matrix geometry, interaction and accessibility. */
(function (UI) {
  function attr(value) {
    return UI.esc(value).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function cssSize(value, fallback) {
    const text = String(value || fallback || "");
    return /^\d+(?:\.\d+)?(?:px|rem|vh|vw|%)$/.test(text) ? text : fallback;
  }

  function dataAttributes(values) {
    return Object.keys(values || {}).map(function (name) {
      if (!/^data-[a-z0-9-]+$/.test(name)) return "";
      return " " + name + '="' + attr(values[name]) + '"';
    }).join("");
  }

  function matrixCell(cell, rowIndex, columnIndex, active) {
    const tone = String(cell.tone || "neutral");
    const title = String(cell.title || cell.ariaLabel || "");
    const classes = "state-matrix-cell state-matrix-cell-tone-" + attr(tone) +
      (cell.className ? " " + attr(cell.className) : "");
    const attributes = Object.assign({}, cell.attributes || {}, {
      "data-state-row": rowIndex,
      "data-state-column": columnIndex,
      "data-state-active": active ? "1" : "0"
    });
    return '<div class="' + classes + '" role="gridcell" tabindex="' + (active ? "0" : "-1") + '"' +
      ' title="' + attr(title) + '" aria-label="' + attr(cell.ariaLabel || title) + '"' +
      dataAttributes(attributes) + '></div>';
  }

  UI.stateMatrix = function (config) {
    const columns = config.columns || [];
    const rows = config.rows || [];
    if (!rows.length) {
      return '<div class="state-matrix-empty" data-ui-type="supporting">' +
        UI.esc(config.emptyText || "No data") + "</div>";
    }
    const active = config.active || { row: 0, column: 0 };
    const style = [
      "--state-matrix-column-count:" + columns.length,
      "--state-matrix-label-width:" + cssSize(config.labelWidth, "280px"),
      "--state-matrix-column-width:" + cssSize(config.columnWidth, "28px"),
      "--state-matrix-header-height:" + cssSize(config.headerHeight, "78px"),
      "--state-matrix-row-height:" + cssSize(config.rowHeight, "26px"),
      "--state-matrix-grid-line:" + String(config.gridLine || "var(--monitor-matrix-grid)")
    ].join(";") + ";";
    const head = '<div class="state-matrix-head" role="row">' +
      '<div class="state-matrix-corner" role="columnheader" aria-label="' +
      attr(config.cornerAriaLabel || config.cornerLabel || "Rows") + '">' +
      String(config.cornerHtml || UI.esc(config.cornerLabel || "")) + "</div>" +
      columns.map(function (column) {
        const label = String(column.label || "");
        return '<div class="state-matrix-column-head" role="columnheader" title="' +
          attr(column.title || label) + '" aria-label="' + attr(column.ariaLabel || label) + '">' +
          '<span class="state-matrix-column-label">' + UI.esc(label) + "</span></div>";
      }).join("") + (!columns.length ? '<div class="state-matrix-columns-empty" role="status">' +
        UI.esc(config.emptyColumnsText || "No columns") + '</div>' : "") + "</div>";
    const body = rows.map(function (row, rowIndex) {
      const label = String(row.label || "");
      return '<div class="state-matrix-row" role="row"' + dataAttributes(row.attributes) + '>' +
        '<div class="state-matrix-row-head' + (row.className ? " " + attr(row.className) : "") +
        '" role="rowheader" title="' + attr(row.title || label) + '" aria-label="' +
        attr(row.ariaLabel || label) + '">' + String(row.headerHtml || UI.esc(label)) + "</div>" +
        (row.cells || []).map(function (cell, columnIndex) {
          return matrixCell(cell || {}, rowIndex, columnIndex,
            rowIndex === active.row && columnIndex === active.column);
        }).join("") + (!columns.length ? '<div class="state-matrix-row-empty" aria-hidden="true"></div>' : "") + "</div>";
    }).join("");
    return '<div class="state-matrix-viewport' + (!columns.length ? " state-matrix-no-columns" : "") +
      (config.className ? " " + attr(config.className) : "") +
      '" tabindex="-1" role="grid" aria-label="' + attr(config.ariaLabel || "State matrix") + '"' +
      ' aria-rowcount="' + attr(rows.length + 1) + '" aria-colcount="' + attr(columns.length + 1) + '"' +
      dataAttributes(config.attributes) + '><div class="state-matrix-canvas" style="' + attr(style) + '">' +
      head + body + "</div></div>";
  };

  function ensureVisible(viewport, cell) {
    const viewportRect = viewport.getBoundingClientRect();
    const cellRect = cell.getBoundingClientRect();
    const stickyLeft = viewport.querySelector(".state-matrix-corner");
    const stickyHeader = viewport.querySelector(".state-matrix-head");
    const leftBoundary = viewportRect.left + (stickyLeft ? stickyLeft.getBoundingClientRect().width : 0);
    const topBoundary = viewportRect.top + (stickyHeader ? stickyHeader.getBoundingClientRect().height : 0);
    let nextLeft = viewport.scrollLeft;
    let nextTop = viewport.scrollTop;
    if (cellRect.left < leftBoundary) nextLeft -= leftBoundary - cellRect.left;
    else if (cellRect.right > viewportRect.right) nextLeft += cellRect.right - viewportRect.right;
    if (cellRect.top < topBoundary) nextTop -= topBoundary - cellRect.top;
    else if (cellRect.bottom > viewportRect.bottom) nextTop += cellRect.bottom - viewportRect.bottom;
    viewport.scrollLeft = Math.max(0, nextLeft);
    viewport.scrollTop = Math.max(0, nextTop);
  }

  UI.bindStateMatrix = function (viewport, options) {
    if (!viewport) return;
    const rows = Array.from(viewport.querySelectorAll(".state-matrix-row")).map(function (row) {
      return Array.from(row.querySelectorAll(".state-matrix-cell"));
    }).filter(function (row) { return row.length; });
    if (!rows.length) return;
    const config = options || {};
    let active = viewport.querySelector('.state-matrix-cell[data-state-active="1"]') || rows[0][0];
    const activate = function (cell, focus) {
      if (!cell) return;
      if (active && active !== cell) {
        active.tabIndex = -1;
        active.setAttribute("data-state-active", "0");
      }
      active = cell;
      active.tabIndex = 0;
      active.setAttribute("data-state-active", "1");
      if (typeof config.onActivate === "function") config.onActivate(active);
      if (focus) {
        try { active.focus({ preventScroll: true }); }
        catch (_error) { active.focus(); }
      }
      ensureVisible(viewport, active);
    };
    viewport.addEventListener("focusin", function (event) {
      const cell = event.target.closest && event.target.closest(".state-matrix-cell");
      if (cell && viewport.contains(cell)) activate(cell, false);
    });
    viewport.addEventListener("click", function (event) {
      const cell = event.target.closest && event.target.closest(".state-matrix-cell");
      if (cell && viewport.contains(cell)) activate(cell, true);
    });
    viewport.addEventListener("keydown", function (event) {
      const cell = event.target.closest && event.target.closest(".state-matrix-cell");
      if (!cell || !viewport.contains(cell)) return;
      let rowIndex = Number(cell.getAttribute("data-state-row"));
      let columnIndex = Number(cell.getAttribute("data-state-column"));
      if (event.key === "ArrowLeft") columnIndex -= 1;
      else if (event.key === "ArrowRight") columnIndex += 1;
      else if (event.key === "ArrowUp") rowIndex -= 1;
      else if (event.key === "ArrowDown") rowIndex += 1;
      else if (event.key === "Home") {
        if (event.ctrlKey || event.metaKey) rowIndex = 0;
        columnIndex = 0;
      } else if (event.key === "End") {
        if (event.ctrlKey || event.metaKey) rowIndex = rows.length - 1;
        columnIndex = rows[Math.max(0, Math.min(rows.length - 1, rowIndex))].length - 1;
      } else return;
      rowIndex = Math.max(0, Math.min(rows.length - 1, rowIndex));
      columnIndex = Math.max(0, Math.min(rows[rowIndex].length - 1, columnIndex));
      event.preventDefault();
      activate(rows[rowIndex][columnIndex], true);
    });
    if (config.restoreFocus) activate(active, true);
  };
})(window.MonitorUI);
