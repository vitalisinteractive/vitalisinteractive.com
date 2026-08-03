(() => {
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