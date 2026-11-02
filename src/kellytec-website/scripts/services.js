/* Render only server-authorized service links; empty slots have no text or actions. */
(() => {
  let pending = false;
  const slots = [...document.querySelectorAll('[data-service]')];
  const status = document.querySelector('#access-status');
  function clear() {
    slots.forEach(slot => { slot.replaceChildren(); slot.setAttribute('aria-hidden', 'true'); });
  }
  async function refresh() {
    if (pending) return;
    pending = true;
    try {
      const session = await Identity.session();
      clear();
      if (!session) { location.replace('/login/'); return; }
      document.querySelector('#account-name').textContent = session.user.name;
      const grants = new Set(session.services);
      slots.forEach(slot => {
        if (!grants.has(slot.dataset.service)) return;
        const template = document.querySelector('#service-' + slot.dataset.service);
        slot.append(template.content.cloneNode(true));
        slot.removeAttribute('aria-hidden');
      });
      if (typeof applyLang === 'function') applyLang(document.documentElement.lang.startsWith('zh') ? 'zh' : 'en');
      status.textContent = ''; delete status.dataset.en; delete status.dataset.zh;
      const logout = document.querySelector('#sign-out'); logout.hidden = false;
      logout.onclick = async () => {
        logout.disabled = true;
        try { await Identity.logout(session.csrf); clear(); location.assign('/login/'); }
        catch (_) { unavailable(); logout.disabled = false; }
      };
    } catch (_) { clear(); unavailable(); }
    finally { pending = false; }
  }
  function unavailable() {
    status.dataset.en = 'Services are temporarily unavailable. Please try again.';
    status.dataset.zh = '服务暂时不可用，请稍后重试。';
    status.textContent = document.documentElement.lang.startsWith('zh') ? status.dataset.zh : status.dataset.en;
  }
  window.addEventListener('focus', refresh);
  refresh();
})();
