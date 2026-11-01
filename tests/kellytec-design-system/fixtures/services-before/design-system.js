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
;
/* One semantic value contract for dates, numbers, money, quantities and status. */
(function (UI) {
  const EMPTY = UI.EMPTY || "—";
  const STATUS_LABELS = {
    healthy: "Healthy",
    warning: "Warning",
    critical: "Critical",
    unknown: "Unknown",
    inactive: "Inactive"
  };

  function missing(value) {
    return value === null || value === undefined || value === "";
  }

  function number(value) {
    if (missing(value)) return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function grouped(value, minimum, maximum) {
    const parsed = number(value);
    if (parsed === null) return EMPTY;
    // A rounded negative zero is never an adverse or negative economic value.
    const rounded = Math.abs(parsed) < 0.5 * Math.pow(10, -maximum) ? 0 : parsed;
    return rounded.toLocaleString("en-US", {
      minimumFractionDigits: minimum,
      maximumFractionDigits: maximum
    });
  }

  function precision(spec, minimum, maximum) {
    const digits = spec.fraction_digits;
    if (digits === undefined) return [minimum, maximum];
    return Number.isInteger(digits) && digits >= 0 && digits <= 20 ? [digits, digits] : null;
  }

  function numeric(spec, minimum, maximum) {
    const digits = precision(spec, minimum, maximum);
    return digits ? grouped(spec.value, digits[0], digits[1]) : EMPTY;
  }

  function percent(spec, scale) {
    const digits = spec.fraction_digits;
    if (digits !== undefined && (!Number.isInteger(digits) || digits < 0 || digits > 20)) return EMPTY;
    const parsed = number(spec.value);
    return parsed === null ? EMPTY : grouped(parsed * scale, digits === undefined ? 0 : digits, digits === undefined ? 1 : digits) + "%";
  }

  function etParts(value) {
    if (missing(value)) return null;
    const raw = String(value).trim();
    if (!/(?:z|[+-]\d{2}:?\d{2})$/i.test(raw)) {
      const match = raw.replace(/\s*ET$/i, "").replace("T", " ")
        .match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?(?:\.(\d+))?/);
      return match ? {
        year: match[1], month: match[2], day: match[3],
        hour: match[4], minute: match[5], second: match[6] || "00",
        fractionalSecond: ((match[7] || "") + "000").slice(0, 3)
      } : null;
    }
    const instant = new Date(raw);
    if (Number.isNaN(instant.getTime())) return null;
    return new Intl.DateTimeFormat("en-US", {
      timeZone: "America/New_York",
      hour12: false,
      hourCycle: "h23",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short",
      fractionalSecondDigits: 3
    }).formatToParts(instant).reduce(function (result, part) {
      result[part.type] = part.value;
      return result;
    }, {});
  }

  function zone(parts, spec) {
    return spec.show_timezone && parts.timeZoneName ? parts.timeZoneName : "ET";
  }

  function date(parts) {
    return parts.year + "-" + parts.month + "-" + parts.day;
  }

  function clock(parts, seconds, spec) {
    const fraction = seconds && spec.fractional_seconds === 3 ? "." + parts.fractionalSecond : "";
    return parts.hour + ":" + parts.minute + (seconds ? ":" + parts.second : "") + fraction;
  }

  const formatters = {
    text: function (spec) {
      return missing(spec.value) ? EMPTY : String(spec.value);
    },
    integer: function (spec) {
      return grouped(spec.value, 0, 0);
    },
    decimal: function (spec) {
      return numeric(spec, 0, 2);
    },
    quantity: function (spec) {
      const parsed = number(spec.value);
      if (parsed === null) return EMPTY;
      const formatted = numeric(spec, 0, 4);
      return formatted === EMPTY ? EMPTY : (parsed > 0 && spec.show_plus ? "+" : "") + formatted;
    },
    price: function (spec) {
      return numeric(spec, 2, 2);
    },
    money: function (spec) {
      const parsed = number(spec.value);
      if (parsed === null || !spec.currency) return EMPTY;
      const scaled = spec.compact === "millions" ? Math.abs(parsed) / 1000000 : Math.abs(parsed);
      const digits = precision(spec, spec.compact === "millions" ? 2 : 0, spec.compact === "millions" ? 2 : 0);
      if (!digits) return EMPTY;
      const abs = grouped(scaled, digits[0], digits[1]);
      const symbol = spec.currency === "USD" ? "$" : spec.currency + " ";
      return (parsed < 0 && scaled >= 0.5 * Math.pow(10, -digits[1]) ? "-" : "") + symbol + abs + (spec.compact === "millions" ? "M" : "");
    },
    percent_ratio: function (spec) {
      return percent(spec, 100);
    },
    percent_points: function (spec) {
      return percent(spec, 1);
    },
    bytes: function (spec) {
      let parsed = number(spec.value);
      if (parsed === null || parsed < 0) return EMPTY;
      const units = ["B", "KB", "MB", "GB", "TB"];
      let index = 0;
      while (parsed >= 1024 && index < units.length - 1) {
        parsed /= 1024;
        index += 1;
      }
      const formatted = index === 0 ? grouped(parsed, 0, 0) : grouped(parsed, parsed >= 10 ? 1 : 2, parsed >= 10 ? 1 : 2);
      return formatted + " " + units[index];
    },
    gigabytes: function (spec) {
      const parsed = number(spec.value);
      return parsed === null || parsed < 0
        ? EMPTY
        : grouped(parsed / 1000000000, 2, 2) + " GB";
    },
    duration_ms: function (spec) {
      const parsed = number(spec.value);
      if (parsed === null || parsed < 0) return EMPTY;
      if (parsed < 1000) return grouped(parsed, 0, 0) + " ms";
      if (parsed < 60000) return grouped(parsed / 1000, 0, 1) + " s";
      return grouped(parsed / 60000, 0, 1) + " min";
    },
    duration_seconds: function (spec) {
      const parsed = number(spec.value), formatted = numeric(spec, 2, 2);
      return parsed === null || parsed < 0 || formatted === EMPTY ? EMPTY : formatted + " s";
    },
    ratio: function (spec) {
      const formatted = numeric(spec, 2, 2);
      return formatted === EMPTY ? EMPTY : formatted + "×";
    },
    trading_date: function (spec) {
      if (missing(spec.value)) return EMPTY;
      const match = String(spec.value).match(/^(\d{4}-\d{2}-\d{2})/);
      return match ? match[1] : EMPTY;
    },
    datetime_et: function (spec) {
      const parts = etParts(spec.value);
      return parts ? date(parts) + " " + clock(parts, true, spec) + " " + zone(parts, spec) : EMPTY;
    },
    time_et: function (spec) {
      const parts = etParts(spec.value);
      return parts ? clock(parts, true, spec) + " " + zone(parts, spec) : EMPTY;
    },
    minute_et: function (spec) {
      const parts = etParts(spec.value);
      return parts ? clock(parts, false, spec) + " " + zone(parts, spec) : EMPTY;
    },
    status: function (spec) {
      const state = String(spec.value || "unknown").toLowerCase();
      return spec.label || STATUS_LABELS[state] || STATUS_LABELS.unknown;
    }
  };

  UI.value = function (spec) {
    if (!spec || typeof spec !== "object" || !formatters[spec.kind]) return EMPTY;
    return formatters[spec.kind](spec);
  };

  UI.statusText = function (value) {
    return UI.value({ kind: "status", value: value });
  };

})(window.MonitorUI);
;
/* Generic bubble construction. Callers own domain state → tone mapping. */
(function (UI) {
  UI.statusBadge = function (status, label, id) {
    const normalized = ["healthy", "warning", "critical", "unknown", "inactive"].includes(status) ? status : "unknown";
    return '<span class="badge ' + UI.esc(normalized) + '"' +
      (id ? ' id="' + UI.esc(id) + '"' : "") +
      ">" + UI.esc(label || UI.statusText(normalized)) + "</span>";
  };

  UI.compactBadge = function (tone, label, classes) {
    const allowed = ["neutral", "healthy", "warning", "critical", "unknown"];
    const safeTone = allowed.includes(tone) ? tone : "unknown";
    return '<span class="monitor-bubble monitor-bubble-compact ' + UI.esc(classes || "") + '" data-tone="' + safeTone + '" data-ui-type="badge-compact">' + UI.esc(label) + '</span>';
  };
  UI.metricBadge = function (label, value, tone, classes) {
    return '<span class="monitor-bubble monitor-bubble-metric ' + UI.esc(classes || "") + '" data-tone="' + UI.esc(["healthy", "critical", "unknown"].includes(tone) ? tone : "unknown") + '" data-ui-type="badge-metric"><span>' + UI.esc(label) + '</span><strong>' + UI.esc(value) + '</strong></span>';
  };
})(window.MonitorUI);
;
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
;
/* One tooltip per bound card. Never changes data, status or value formatting. */
(function (UI) {
  let nextId = 0;
  UI.bindTooltip = function (root) {
    const hits = Array.from(root.querySelectorAll('[data-ui-tooltip]'));
    if (!hits.length) return function () {};
    const tip = document.createElement('div');
    tip.className = 'monitor-tooltip'; tip.id = 'monitor-tooltip-' + (++nextId);
    tip.setAttribute('role', 'tooltip'); tip.setAttribute('data-ui-type', 'tooltip');
    tip.hidden = true; root.appendChild(tip);
    const controller = new AbortController();
    let active = null;
    function hide() {
      tip.hidden = true;
      if (active) active.removeAttribute('aria-describedby');
      active = null;
    }
    function show(hit, x, y) {
      if (active !== hit) hide();
      active = hit; tip.textContent = (hit.getAttribute('data-ui-tooltip') || hit.getAttribute('aria-label'));
      tip.hidden = false; hit.setAttribute('aria-describedby', tip.id);
      tip.style.left = Math.max(8, Math.min(window.innerWidth - tip.offsetWidth - 12, x + 14)) + 'px';
      tip.style.top = Math.max(8, Math.min(window.innerHeight - tip.offsetHeight - 12, y + 14)) + 'px';
    }
    function listen(target, name, fn) { target.addEventListener(name, fn, {signal: controller.signal}); }
    hits.forEach(function (hit) {
      if (!hit.hasAttribute('tabindex')) hit.setAttribute('tabindex', '0');
      if (!hit.hasAttribute('aria-label')) hit.setAttribute('aria-label', (hit.getAttribute('data-ui-tooltip') || hit.getAttribute('aria-label')));
    });
    listen(root, 'pointermove', function (event) {
      const hit = event.target.closest('[data-ui-tooltip]');
      if (hit && root.contains(hit)) show(hit, event.clientX, event.clientY); else hide();
    });
    listen(root, 'pointerleave', hide);
    listen(root, 'focusin', function (event) {
      const hit = event.target.closest('[data-ui-tooltip]');
      if (!hit) return;
      const r = hit.getBoundingClientRect(); show(hit, r.left + r.width / 2, r.top + r.height / 2);
    });
    listen(root, 'focusout', hide);
    listen(document, 'keydown', function (event) { if (event.key === 'Escape') hide(); });
    listen(window, 'resize', hide);
    listen(window, 'scroll', hide);
    return function () { hide(); controller.abort(); tip.remove(); };
  };
})(window.MonitorUI);
;
/* Small escaped SVG primitives; geometry belongs to the caller. */
(function (UI) {
  UI.svgText = function (x, y, value, attributes) {
    return '<text x="' + Number(x) + '" y="' + Number(y) + '" ' + (attributes || '') + '>' + UI.esc(value) + '</text>';
  };
  UI.svgLine = function (x1, y1, x2, y2, attributes) {
    return '<line x1="' + Number(x1) + '" y1="' + Number(y1) + '" x2="' + Number(x2) + '" y2="' + Number(y2) + '" ' + (attributes || '') + '/>';
  };
})(window.MonitorUI);
;
/* CSS font sizes describe screen pixels, including stretched and rotated SVGs. */
(function (UI) {
  const original = new WeakMap();
  UI.bindChartText = function (root) {
    const charts = Array.from(root.querySelectorAll('svg[data-ui-chart]'));
    function update() {
      charts.forEach(function (chart) {
        const m = chart.getScreenCTM();
        let zoom = 1;
        for (let node = chart; node; node = node.parentElement) zoom *= Number(getComputedStyle(node).zoom) || 1;
        if (!m || !chart.getBoundingClientRect().width || m.a <= 0 || m.d <= 0) return;
        chart.querySelectorAll('text').forEach(function (text) {
          if (!original.has(text)) original.set(text, text.getAttribute('transform') || '');
          const x = Number(text.getAttribute('x') || 0), y = Number(text.getAttribute('y') || 0);
          const rotate = text.hasAttribute('data-axis-vertical') ? 'rotate(-90 ' + x + ' ' + y + ')' : original.get(text);
          text.setAttribute('transform', 'translate(' + x + ' ' + y + ') scale(' + (zoom / m.a) + ' ' + (zoom / m.d) + ') translate(' + (-x) + ' ' + (-y) + ') ' + rotate);
        });
      });
    }
    const observer = new ResizeObserver(update);
    charts.forEach(function (chart) { observer.observe(chart); });
    update();
    let alive = true;
    if (document.fonts) document.fonts.ready.then(function () { if (alive) update(); });
    return function () { alive = false; observer.disconnect(); };
  };
})(window.MonitorUI);
;
/* Geometry follows its container; fonts and interaction keep shared ownership. */
(function (UI) {
  UI.bindResponsiveChart = function (root, selector, draw) {
    if (!root) return function () {};
    const hosts = Array.from(root.querySelectorAll(selector));
    const widths = new WeakMap();
    function update() {
      let changed = false;
      hosts.forEach(function (host) {
        const width = Math.floor(host.getBoundingClientRect().width);
        if (width <= 0 || widths.get(host) === width) return;
        host.innerHTML = draw(width);
        widths.set(host, width);
        changed = true;
      });
      // Replacing SVG nodes also replaces keyboard targets and text transforms.
      if (changed) root.dispatchEvent(new Event('monitor-chart-layout'));
    }
    const observer = new ResizeObserver(update);
    hosts.forEach(function (host) { observer.observe(host); });
    try {
      update();
    } catch (error) {
      observer.disconnect();
      throw error;
    }
    return function () { observer.disconnect(); };
  };
})(window.MonitorUI);
;
/* Opaque category keys keep their visual identity across cards and refreshes. */
(function (UI) {
  const assigned = new Map();

  UI.chartSeriesStyle = function (key, catalog) {
    (catalog || []).concat([key]).forEach(function (item) {
      if (!assigned.has(item)) assigned.set(item, assigned.size);
    });
    const index = assigned.get(key);
    return { key: key, index: index, role: 'series-' + (index % 4 + 1), pattern: Math.floor(index / 4) };
  };

  UI.chartSeriesFill = function (style, namespace) {
    return style.pattern ? 'url(#' + namespace + '-series-' + style.index + ')' : UI.chartSeriesColor(style.role);
  };

  UI.chartSeriesDefinitions = function (styles, namespace) {
    return '<defs>' + styles.filter(function (style) { return style.pattern; }).map(function (style) {
      const spacing = 4 + Math.floor((style.pattern - 1) / 3) * 2;
      const color = UI.chartSeriesColor(style.role);
      const direction = [45, -45, 0][(style.pattern - 1) % 3];
      return '<pattern id="' + UI.esc(namespace) + '-series-' + style.index + '" patternUnits="userSpaceOnUse" width="' + spacing + '" height="' + spacing + '" patternTransform="rotate(' + direction + ')">' +
        '<rect width="' + spacing + '" height="' + spacing + '" fill="' + color + '"/>' +
        '<line x1="0" y1="0" x2="0" y2="' + spacing + '" stroke="var(--monitor-surface-raised)" stroke-width="2"/></pattern>';
    }).join('') + '</defs>';
  };

  UI.chartSeriesSwatch = function (style) {
    const color = UI.chartSeriesColor(style.role);
    if (!style.pattern) return 'background:' + color;
    const spacing = 4 + Math.floor((style.pattern - 1) / 3) * 2;
    const angle = [45, -45, 0][(style.pattern - 1) % 3];
    return 'background:repeating-linear-gradient(' + angle + 'deg,var(--monitor-surface-raised) 0px,var(--monitor-surface-raised) 2px,' + color + ' 2px,' + color + ' ' + spacing + 'px)';
  };
})(window.MonitorUI);
;
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
;
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
;
/* Stateful checkbox selection shared by factor and strategy forms. */
(function (UI) {
  UI.selection = function (root, options) {
    const selected = new Set(options.selected || []);
    let query = '', selectedOnly = false, items = options.items || [];
    root.dataset.ui = 'selection';
    root.classList.toggle('selection-compact', !!options.compact);
    root.innerHTML = '<div class="selection-tools"><input data-ui="input" type="search" aria-label="Search choices" placeholder="Search">' +
      '<button data-ui="button" type="button" data-action="select">Select filtered</button><button data-ui="button" type="button" data-action="clear">Clear filtered</button>' +
      '<label><input type="checkbox" data-action="only"> Selected only</label></div>' +
      '<div class="selection-options" role="group" aria-label="' + UI.esc(options.label || 'Choices') + '"></div><div class="selection-count" aria-live="polite"></div>';
    const list = root.querySelector('.selection-options');
    function filtered() {
      return items.filter(x => (x.label || x.id).toLowerCase().includes(query) && (!selectedOnly || selected.has(x.id)));
    }
    function render() {
      const focus = list.contains(document.activeElement) ? document.activeElement.value : null;
      const scroll = list.scrollTop;
      list.innerHTML = filtered().map(x => '<label class="selection-option" title="' + UI.esc(x.label || x.id) + '">' +
        '<input type="checkbox" value="' + UI.esc(x.id) + '"' + (selected.has(x.id) ? ' checked' : '') + '><span>' + UI.esc(x.label || x.id) + '</span></label>').join('');
      root.querySelector('.selection-count').textContent = options.count ? options.count([...selected]) : selected.size + ' selected';
      if (focus) Array.from(list.querySelectorAll('input')).find(input => input.value === focus)?.focus({preventScroll:true});
      list.scrollTop = scroll;
    }
    function changed() { render(); if (options.onChange) options.onChange([...selected]); }
    root.querySelector('input[type="search"]').addEventListener('input', e => { query = e.target.value.toLowerCase(); render(); });
    root.querySelector('[data-action="only"]').addEventListener('change', e => { selectedOnly = e.target.checked; render(); });
    root.querySelector('[data-action="select"]').addEventListener('click', () => { filtered().forEach(x => selected.add(x.id)); changed(); });
    root.querySelector('[data-action="clear"]').addEventListener('click', () => { filtered().forEach(x => selected.delete(x.id)); changed(); });
    list.addEventListener('change', e => { if (e.target.checked) selected.add(e.target.value); else selected.delete(e.target.value); changed(); });
    render();
    return {values: () => [...selected], replace: function (next) { items = next; const ids = new Set(items.map(x => x.id)); [...selected].forEach(id => { if (!ids.has(id)) selected.delete(id); }); changed(); }};
  };
})(window.MonitorUI);
;
/* One request indicator for the whole monitor, including concurrent requests. */
(function (UI) {
  let pending = 0;
  function sync() {
    const indicator = document.getElementById("monitor-loading");
    if (indicator) indicator.setAttribute("aria-hidden", pending ? "false" : "true");
  }
  UI.withLoading = function (work) {
    pending += 1;
    sync();
    return Promise.resolve().then(work).finally(function () {
      pending -= 1;
      sync();
    });
  };
})(window.MonitorUI);
;
/* Canonical card shell and lifecycle. */
(function (UI) {
  UI.card = UI.renderCardShell = function (card, body, extraClass) {
    const id = card.id || "";
    const hideTitle = card.hide_title || card.hideTitle;
    const classes = "monitor-card" + (hideTitle ? " monitor-card-no-title" : "") +
      (extraClass ? " " + extraClass : "");
    return '<section class="' + classes + '" data-ui="card" data-card="' + UI.esc(id) + '">' +
      (hideTitle ? "" : '<div class="monitor-card-head" data-ui="card-head"><h2 data-ui-type="card-title">' + UI.esc(card.title || "") + "</h2>" +
        (card.status ? '<span class="card-status" role="status">' + UI.esc(card.status) + '</span>' : '') + "</div>") +
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
;
/* Canonical semantic table shell. */
(function (UI) {
  UI.table = function (headers, rows, emptyText, options) {
    if (!rows.length) return '<div class="empty">' + UI.esc(emptyText || "No data") + "</div>";
    const layout = options && options.equalColumns ? ' data-ui-column-layout="equal"' : '';
    const headerType = options && options.headerType || 'table-header';
    return '<div class="scroll"><table data-ui="table"' + layout + '><thead><tr>' +
      headers.map(function (heading) {
        const numeric = heading && typeof heading === "object" && heading.numeric;
        const label = heading && typeof heading === "object" ? heading.label : heading;
        const lines = heading && Array.isArray(heading.lines) ? heading.lines : null;
        const content = lines ? lines.map(function (line) {
          return '<span class="monitor-table-header-line">' + UI.esc(line) + '</span>';
        }).join(' ') : UI.esc(label);
        return '<th data-ui-type="' + UI.esc(headerType) + '"' + (numeric ? ' data-ui-numeric="true"' : '') + '>' + content + "</th>";
      }).join("") +
      "</tr></thead><tbody>" + rows.map(function (row) {
        return "<tr>" + row.map(function (value, index) {
          return '<td data-ui-type="table-cell"' + (headers[index] && headers[index].numeric ? ' data-ui-numeric="true"' : '') + '>' + value + "</td>";
        }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  };

  // Multiple measurements with distinct units share the same numeric anchor.
  UI.labelValues = function (items) {
    return '<span class="monitor-label-values">' + items.map(function (item) {
      return '<span class="monitor-label-value"><span data-ui-type="supporting">' + UI.esc(item.label || '') +
        '</span><span data-ui-type="value">' + UI.esc(UI.value(item.value)) + '</span></span>';
    }).join('') + '</span>';
  };
})(window.MonitorUI);
;
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
;
/* Generic log-table shell; each monitor owns its field mapping. */
(function (UI) {
  function attribute(value) {
    return UI.esc(value).replace(/"/g, "&quot;");
  }

  UI.logTable = function (rows, options) {
    const config = options || {};
    const headers = config.headers || [];
    if (!rows.length && !headers.length) return '<div class="empty">' + UI.esc(config.emptyText || "No logs") + "</div>";
    const attributes = Object.keys(config.attributes || {}).map(function (name) {
      if (!/^data-[a-z0-9-]+$/.test(name)) return "";
      return ' ' + name + '="' + attribute(config.attributes[name]) + '"';
    }).join("");
    if (headers.length) {
      const controls = config.headerControls || [];
      const controlRow = controls.length ? '<tr class="monitor-log-table-controls' +
        (config.controlsClassName ? ' ' + attribute(config.controlsClassName) : '') + '">' +
        controls.map(function (control) {
          const span = control.span || 1;
          if (!Number.isInteger(span) || span < 1) throw new TypeError('Header control span must be a positive integer');
          return '<td colspan="' + span + '">' + control.html + '</td>';
        }).join('') + '</tr>' : '';
      const body = rows.length ? rows.map(function (cells) {
        return '<tr>' + cells.map(function (body) {
          return '<td data-ui-type="table-cell">' + body + '</td>';
        }).join("") + '</tr>';
      }).join("") : '<tr><td colspan="' + headers.length + '"><div class="empty">' +
        UI.esc(config.emptyText || "No logs") + '</div></td></tr>';
      return '<div class="monitor-log-table monitor-log-table--headed' +
        (config.className ? " " + attribute(config.className) : "") +
        '" data-ui="log-table" role="region" aria-label="' + attribute(config.label || "Logs") +
        '" tabindex="0"' + attributes + '><table data-ui="table"><colgroup>' +
        headers.map(function () { return '<col>'; }).join('') + '</colgroup><thead>' + controlRow + '<tr>' +
        headers.map(function (heading) {
          return '<th scope="col" data-ui-type="' + attribute(config.headerTypography || "table-header") + '">' + UI.esc(heading) + '</th>';
        }).join("") + '</tr></thead><tbody>' + body + '</tbody></table></div>';
    }
    return '<div class="monitor-log-table' + (config.className ? " " + attribute(config.className) : "") + '" data-ui="log-table" role="table" tabindex="0"' + attributes + '>' +
      rows.map(function (cells) {
        return '<div class="monitor-log-table-row" role="row">' + cells.map(function (body) {
          return UI.cell(body, { className: "monitor-log-table-cell", role: "cell", typography: "table-cell" });
        }).join("") + "</div>";
      }).join("") + "</div>";
  };
})(window.MonitorUI);
;
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
;
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
