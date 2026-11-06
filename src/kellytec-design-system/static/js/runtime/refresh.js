/* One refresh lifecycle: explicit policy, no overlapping work, hidden pages pause. */
(function(UI) {
  UI.refreshController = ({refresh, onError = () => {}}) => {
    let interval = null, timer = null, active = null, started = false, closed = false;
    function clear() { clearTimeout(timer); timer = null; }
    function schedule() {
      clear();
      if (started && !closed && interval !== null && !active && document.visibilityState !== 'hidden') {
        timer = setTimeout(tick, interval * 1000);
      }
    }
    function tick() {
      if (started && !closed && interval !== null && document.visibilityState !== 'hidden') run().catch(onError);
    }
    function run() {
      if (closed) return Promise.reject(new Error('Refresh controller is closed'));
      if (active) return active;
      clear();
      active = Promise.resolve().then(refresh).finally(() => { active = null; schedule(); });
      return active;
    }
    function configure(policy) {
      clear(); interval = null;
      if (!policy || !['manual', 'interval'].includes(policy.mode) ||
          (policy.mode === 'manual' && policy.interval_seconds !== null) ||
          (policy.mode === 'interval' && (!Number.isInteger(policy.interval_seconds) ||
            policy.interval_seconds < 60 || policy.interval_seconds > 86400))) {
        throw new Error('Invalid refresh policy');
      }
      interval = policy.interval_seconds;
      schedule();
    }
    function visible() {
      clear();
      tick();
    }
    function close() {
      closed = true; clear();
      document.removeEventListener('visibilitychange', visible);
      window.removeEventListener('pagehide', close);
    }
    document.addEventListener('visibilitychange', visible);
    window.addEventListener('pagehide', close);
    return {refresh: run, configure, start() { if (!closed) { started = true; schedule(); } }, close};
  };
})(window.UI);
