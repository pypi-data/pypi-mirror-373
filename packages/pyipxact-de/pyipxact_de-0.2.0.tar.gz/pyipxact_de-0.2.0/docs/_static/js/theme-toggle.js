// Add a light/dark theme toggle that sticks across reloads using localStorage.
(function () {
  if (typeof window === 'undefined') return;

  const key = 'theme_preference';
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(key, theme); } catch (_) {}
  }

  function currentTheme() {
    const stored = localStorage.getItem(key);
    if (stored === 'light' || stored === 'dark') return stored;
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  }

  function ensureButton() {
    let container = document.querySelector('.wy-nav-top .theme-toggle-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'theme-toggle-container';
      const top = document.querySelector('.wy-nav-top');
      if (!top) return null;
      top.style.position = 'relative';
      top.appendChild(container);
    }
    let btn = container.querySelector('button.theme-toggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.className = 'theme-toggle';
      btn.type = 'button';
      btn.setAttribute('aria-live', 'polite');
      container.appendChild(btn);
    }
    return btn;
  }

  function label(theme) {
    return theme === 'dark' ? 'Light mode' : 'Dark mode';
  }

  function render(btn, theme) {
    const nextLabel = label(theme);
    const icon = theme === 'dark' ? '☀️' : '🌙';
    btn.innerHTML = `${icon} <span class="theme-toggle-text">${nextLabel}</span>`;
    btn.setAttribute('aria-label', `Switch to ${nextLabel}`);
    btn.setAttribute('title', `Switch to ${nextLabel}`);
    btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  }

  const initTheme = currentTheme();
  applyTheme(initTheme);

  const btn = ensureButton();
  if (!btn) return;
  render(btn, initTheme);

  btn.addEventListener('click', function () {
    const next = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
    applyTheme(next);
    render(btn, next);
  });
})();
