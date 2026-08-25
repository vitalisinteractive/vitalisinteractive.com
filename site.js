(() => {
  if (!document.querySelector('link[data-vitalis-exact-logo]')) {
    const exactLogoStyles = document.createElement('link');
    exactLogoStyles.rel = 'stylesheet';
    exactLogoStyles.href = '/exact-logo-fix.css';
    exactLogoStyles.dataset.vitalisExactLogo = '';
    document.head.appendChild(exactLogoStyles);
  }

  if (!window.__vitalisMetricoolTrackerLoaded) {
    window.__vitalisMetricoolTrackerLoaded = true;
    const metricoolScript = document.createElement('script');
    metricoolScript.src = 'https://tracker.metricool.com/resources/be.js';
    metricoolScript.async = true;
    metricoolScript.addEventListener('load', () => {
      window.beTracker.t({ hash: 'f0e9f7ba2d868aa7d04d28c28366f0ec' });
    });
    document.head.appendChild(metricoolScript);
  }

  const menu = document.querySelector('[data-menu]');
  const nav = document.querySelector('[data-nav]');
  const setMenuState = open => {
    if (!menu || !nav) return;
    nav.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
  };

  menu?.addEventListener('click', () => setMenuState(!nav?.classList.contains('open')));
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    setMenuState(false);
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') setMenuState(false);
  });
  document.addEventListener('click', event => {
    if (!menu || !nav || !nav.classList.contains('open')) return;
    if (menu.contains(event.target) || nav.contains(event.target)) return;
    setMenuState(false);
  });

  document.querySelectorAll('[data-year]').forEach(el => {
    el.textContent = new Date().getFullYear();
  });
})();
