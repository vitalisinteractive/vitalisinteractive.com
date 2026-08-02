(() => {
  const logoUrl = 'https://raw.githack.com/vitalisinteractive/vitalisinteractive.com/website-v4-polish/assets/vitalis-logo-v2.jpg';
  document.querySelectorAll('.brand img, .footer img').forEach((image) => {
    image.src = logoUrl;
  });

  if (!document.querySelector('link[href^="hero-v5.css"]')) {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = 'hero-v5.css?v=1';
    document.head.appendChild(stylesheet);
  }

  const hero = document.querySelector('.hero');
  if (hero) {
    hero.innerHTML = `
      <div class="container hero-grid">
        <div class="hero-copy reveal">
          <div class="overline">Family Office Simulator · Now in Early Access</div>
          <h1>Build the institution<em>behind the wealth.</em></h1>
          <p class="lead">Acquire property. Structure debt. Hire a team. Govern the family office. Prepare the next generation.</p>
          <p class="plain">A deep management simulation for players who want to understand how the system actually works—not just watch a number climb.</p>
          <div class="actions">
            <a class="button" href="https://store.steampowered.com/app/4820790/Family_Office_Simulator/" target="_blank" rel="noreferrer">Play on Steam</a>
            <a class="ghost" href="#game">See how the game works</a>
          </div>
        </div>
        <div class="hero-showcase reveal delay">
          <a class="hero-shot" href="https://store.steampowered.com/app/4820790/Family_Office_Simulator/" target="_blank" rel="noreferrer" aria-label="View Family Office Simulator on Steam">
            <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/4820790/09ceb92d4cbcee87ec4dc9e4f730e2940b0c1c99/ss_09ceb92d4cbcee87ec4dc9e4f730e2940b0c1c99.1920x1080.jpg?t=1785250839" width="1920" height="1080" alt="Family Office Simulator property management gameplay">
            <span class="shot-cta">Explore on Steam →</span>
          </a>
          <div class="hero-gameplate">
            <div><span>Vitalis Interactive presents</span><strong>Family Office Simulator</strong></div>
            <span class="release-live"><i></i> Available now</span>
          </div>
          <div class="hero-system-tags" aria-label="Featured game systems">
            <span>Real Estate</span><span>Debt &amp; Liquidity</span><span>Governance</span><span>Succession</span>
          </div>
        </div>
      </div>
      <div class="container hero-proof" aria-label="Family Office Simulator facts">
        <div><strong>Live in Early Access</strong><span>Available now on Steam</span></div>
        <div><strong>Actively developed</strong><span>Player feedback shapes updates</span></div>
        <div><strong>Windows</strong><span>Steam Cloud supported</span></div>
      </div>`;
  }

  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-nav]');

  const setHeader = () => header?.classList.toggle('scrolled', window.scrollY > 22);
  const closeMenu = () => {
    nav?.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
  };

  setHeader();
  window.addEventListener('scroll', setHeader, { passive: true });

  toggle?.addEventListener('click', () => {
    const open = nav?.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(Boolean(open)));
  });

  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  document.querySelectorAll('[data-year]').forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  const items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    items.forEach((item) => observer.observe(item));
  } else {
    items.forEach((item) => item.classList.add('is-visible'));
  }
})();
