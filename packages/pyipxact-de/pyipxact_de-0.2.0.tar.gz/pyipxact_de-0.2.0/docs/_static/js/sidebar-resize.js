// Enable dragging the left RTD sidebar width on desktop.
(function () {
  if (typeof window === 'undefined') return;
  const mq = window.matchMedia('(min-width: 769px)');
  if (!mq.matches) return;

  const side = document.querySelector('.wy-nav-side');
  const contentWrap = document.querySelector('.wy-nav-content-wrap');
  if (!side || !contentWrap) return;

  const min = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-min')) || 180;
  const max = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-max')) || 520;

  let startX = 0;
  let startWidth = 0;
  const handle = document.createElement('div');
  handle.style.width = '6px';
  handle.style.cursor = 'col-resize';
  handle.style.position = 'absolute';
  handle.style.top = '0';
  handle.style.right = '0';
  handle.style.bottom = '0';
  handle.style.zIndex = '5';
  handle.style.background = 'transparent';
  side.style.position = 'relative';
  side.appendChild(handle);

  function onMouseDown(e) {
    startX = e.clientX;
    startWidth = side.getBoundingClientRect().width;
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    e.preventDefault();
  }

  function onMouseMove(e) {
    const dx = e.clientX - startX;
    let newWidth = Math.min(max, Math.max(min, startWidth + dx));
    side.style.width = newWidth + 'px';
    contentWrap.style.marginLeft = newWidth + 'px';
  }

  function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
    // persist to localStorage
    const w = side.getBoundingClientRect().width;
    try { localStorage.setItem('rtd_sidebar_width', String(Math.round(w))); } catch (_) {}
  }

  // Restore saved width
  try {
    const saved = parseInt(localStorage.getItem('rtd_sidebar_width'));
    if (saved && saved >= min && saved <= max) {
      side.style.width = saved + 'px';
      contentWrap.style.marginLeft = saved + 'px';
    }
  } catch (_) {}

  handle.addEventListener('mousedown', onMouseDown);
})();
