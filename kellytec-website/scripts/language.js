// Footer year (re-run after lang switch since innerHTML replaces the span)
function setYear() {
  const el = document.getElementById('year');
  if (el) el.textContent = new Date().getFullYear();
}

function updateLanguageToggle(lang) {
  const btn = document.querySelector('[data-lang-toggle]');
  if (!btn) return;
  const nextLang = lang === 'zh' ? 'en' : 'zh';
  btn.dataset.lang = nextLang;
  btn.textContent = nextLang === 'zh' ? '中文' : 'EN';
  btn.setAttribute('aria-label', nextLang === 'zh' ? '切换到中文' : 'Switch to English');
}

function applyLang(lang) {
  document.documentElement.lang = lang === 'zh' ? 'zh-Hans' : 'en';
  document.querySelectorAll('[data-en][data-zh]').forEach(el => {
    const val = el.dataset[lang];
    if (val != null) el.innerHTML = val;
  });
  setYear();
  updateLanguageToggle(lang);
  try { localStorage.setItem('kellytec-lang', lang); } catch (e) {}
}

(function initLanguage() {
  const savedLang = (() => {
    try { return localStorage.getItem('kellytec-lang'); } catch (e) { return null; }
  })();
  const initialLang = savedLang || 'zh';
  applyLang(initialLang);

  document.querySelectorAll('[data-lang-toggle]').forEach(btn => {
    btn.addEventListener('click', () => applyLang(btn.dataset.lang));
  });
})();
