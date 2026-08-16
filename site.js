(() => {
  if (!window.__vitalisMetricoolTrackerLoaded) {
    window.__vitalisMetricoolTrackerLoaded = true;
    const metricoolScript = document.createElement('script');
    metricoolScript.src = 'https://tracker.metricool.com/resources/be.js';
    metricoolScript.async = true;
    metricoolScript.addEventListener('load', () => {
      window.beTracker.t({ hash: 'f0e9f7ba2d868aa7d04d28c28366f0ec' });
    });
    document.head.append(metricoolScript);
  }

  const menu = document.querySelector('[data-menu]');
  const nav = document.querySelector('[data-nav]');
  menu?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('open');
    menu?.setAttribute('aria-expanded','false');
  }));
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

  if (!document.querySelector('#footer-contact-styles')) {
    const style = document.createElement('style');
    style.id = 'footer-contact-styles';
    style.textContent = `
      .footer-links{gap:15px!important}
      .footer-contact{display:grid;gap:2px}
      .footer-contact-label{color:#71868b;font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
      .footer-contact a{color:#c2d0d2;text-decoration:none}
      .footer-contact a:hover{color:#fff}
      @media(max-width:980px){.footer-links{gap:14px!important}}
    `;
    document.head.append(style);
  }

  document.querySelectorAll('.footer-links').forEach(group => {
    const links = Array.from(group.querySelectorAll('a[href^="mailto:"]'));
    const labels = [
      'Business, creators, press & partnerships',
      'Player support & bug reports'
    ];
    links.forEach((link, index) => {
      if (link.parentElement?.classList.contains('footer-contact')) return;
      const item = document.createElement('div');
      item.className = 'footer-contact';
      const label = document.createElement('span');
      label.className = 'footer-contact-label';
      label.textContent = labels[index] || 'Contact';
      link.before(item);
      item.append(label, link);
    });
  });

  document.querySelectorAll('.copyright').forEach(el => {
    if (el.querySelector('a[href="privacy.html"]')) return;
    const separator = document.createTextNode(' · ');
    const privacy = document.createElement('a');
    privacy.href = 'privacy.html';
    privacy.textContent = 'Privacy';
    privacy.className = 'footer-legal-link';
    privacy.style.color = '#d7a936';
    privacy.style.textDecoration = 'none';
    el.append(separator, privacy);
  });
})();
