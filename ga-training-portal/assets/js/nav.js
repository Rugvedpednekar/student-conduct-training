// Shared layout shell (sidebar + topbar + footer).
(function renderPortalShell() {
  const links = [
    { label: 'Dashboard', href: 'index.html', icon: '⌂' },
    { label: 'Office Overview', href: 'office-overview.html', icon: 'ⓘ' },
    { label: 'Training Flow', href: 'training-flow.html', icon: '⤴' },
    { label: 'Systems', href: 'systems.html', icon: '🖥' },
    { label: 'Responsibilities', href: 'responsibilities.html', icon: '☑' },
    { label: 'Case Handling', href: 'case-handling.html', icon: '📁' },
    { label: 'Sanctions', href: 'sanctions.html', icon: '⚖' },
    { label: 'Parent Letters', href: 'parent-letters.html', icon: '✉' },
    { label: 'Templates', href: 'templates.html', icon: '🗂' },
    { label: 'Escalation', href: 'escalation.html', icon: '⚠' },
    { label: 'Quick Reference', href: 'quick-reference.html', icon: '⟡' }
  ];

  const shell = document.getElementById('portal-shell');
  if (!shell) return;

  const page = location.pathname.split('/').pop() || 'index.html';
  const navMarkup = links
    .map(
      (link) => `
      <li>
        <a class="nav-link ${page === link.href ? 'active' : ''}" href="${link.href}">
          <span class="nav-icon">${link.icon}</span>
          <span>${link.label}</span>
        </a>
      </li>`
    )
    .join('');

  shell.innerHTML = `
    <aside class="sidebar" id="sidebar">
      <div class="brand-card">
        <h1>GA Training Portal</h1>
        <p>Office of Student Conduct</p>
      </div>

      <nav aria-label="Sidebar Navigation">
        <ul class="nav-list">${navMarkup}</ul>
      </nav>

      <div class="profile-mini">
        <div class="avatar">GA</div>
        <div>
          <strong>Graduate Assistant</strong>
          <p>Training Cohort 2026</p>
        </div>
      </div>
    </aside>

    <section class="main-panel">
      <header class="topbar">
        <div class="topbar-left">
          <button class="nav-toggle" id="nav-toggle" aria-label="Open navigation">☰</button>
          <div>
            <h2 id="page-title">Graduate Assistant Training</h2>
            <p id="page-subtitle">Student Conduct internal operations portal</p>
          </div>
        </div>
        <div class="topbar-right">
          <span class="badge info">Internal Use</span>
          <span class="badge alert">FERPA Sensitive</span>
        </div>
      </header>

      <main id="page-content"></main>

      <footer class="shell-footer">
        <span>© 2026 Office of Student Conduct</span>
        <span>Use minimum necessary student information in all communications.</span>
      </footer>
    </section>
  `;

  document.getElementById('nav-toggle')?.addEventListener('click', () => {
    document.getElementById('sidebar')?.classList.toggle('open');
  });
})();
