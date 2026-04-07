// Shared navigation + shell rendering.
(function renderShell() {
  const links = [
    ['Dashboard', 'index.html'],
    ['Office Overview', 'office-overview.html'],
    ['Training Flow', 'training-flow.html'],
    ['Systems', 'systems.html'],
    ['Responsibilities', 'responsibilities.html'],
    ['Case Handling', 'case-handling.html'],
    ['Sanctions', 'sanctions.html'],
    ['Parent Letters', 'parent-letters.html'],
    ['Templates', 'templates.html'],
    ['Escalation', 'escalation.html'],
    ['Quick Reference', 'quick-reference.html']
  ];

  const shell = document.getElementById('portal-shell');
  if (!shell) return;

  const path = location.pathname.split('/').pop() || 'index.html';

  const sidebarLinks = links.map(([label, href]) => `
    <li>
      <a class="nav-link ${path === href ? 'active' : ''}" href="${href}">
        <span>•</span><span>${label}</span>
      </a>
    </li>`).join('');

  shell.innerHTML = `
    <aside class="sidebar" id="sidebar">
      <div class="brand">
        <h1>GA Training Portal</h1>
        <p>Office of Student Conduct</p>
      </div>
      <ul class="nav-list">${sidebarLinks}</ul>
    </aside>
    <section class="main-panel">
      <header class="topbar">
        <div class="meta">
          <button class="nav-toggle" id="nav-toggle">☰</button>
          <div>
            <strong id="page-title">Graduate Assistant Training</strong>
            <p style="font-size:0.8rem;">Internal onboarding and operations guide</p>
          </div>
        </div>
        <div class="meta">
          <span class="badge info">Spring 2026 Cohort</span>
          <span class="badge alert">FERPA Sensitive</span>
        </div>
      </header>
      <main id="page-content"></main>
    </section>
  `;

  const toggle = document.getElementById('nav-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }
})();
