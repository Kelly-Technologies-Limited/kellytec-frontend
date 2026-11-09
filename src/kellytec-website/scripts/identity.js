/* Central cookies stay HttpOnly; this page stores no identity or access token. */
(() => {
  const origin = 'https://auth.kellytec.io';
  window.Identity = Object.freeze({
    async session() {
      const response = await fetch(origin + '/session', {credentials: 'include', cache: 'no-store', signal: AbortSignal.timeout(15000)});
      if (response.status === 401) return null;
      if (!response.ok) throw new Error('Identity is unavailable');
      const value = await response.json();
      if (!Array.isArray(value.services) || typeof value.user?.name !== 'string' || typeof value.csrf !== 'string') throw new Error('Invalid identity response');
      return value;
    },
    async logout(csrf) {
      const response = await fetch(origin + '/logout', {
        method: 'POST', credentials: 'include', body: '{}', signal: AbortSignal.timeout(15000),
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf},
      });
      if (!response.ok && response.status !== 401) throw new Error('Sign out could not be confirmed');
    },
  });
  if (document.querySelector('[data-page="login"]')) {
    const flow = new URLSearchParams(location.search).get('flow');
    const login = document.querySelector('.login-google');
    const continuation = /^[A-Za-z0-9_-]{43}$/.test(flow || '');
    if (continuation) {
      const destination = new URL(login.href);
      destination.searchParams.set('flow', flow);
      destination.hash = location.hash;
      login.href = destination.href;
    }
    Identity.session().then(value => {
      if (value) location.replace(continuation ? login.href : '/services/');
    }).catch(() => {
      const status = document.querySelector('#login-status');
      status.dataset.en = 'Login is temporarily unavailable. Please try again.';
      status.dataset.zh = '登录暂时不可用，请稍后重试。';
      status.textContent = document.documentElement.lang.startsWith('zh') ? status.dataset.zh : status.dataset.en;
    });
  }
})();
