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
