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
