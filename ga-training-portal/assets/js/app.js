// Core interactions used by multiple pages.
(function initInteractions() {
  document.addEventListener('click', (e) => {
    const collapseBtn = e.target.closest('[data-collapse]');
    if (collapseBtn) {
      const id = collapseBtn.getAttribute('data-collapse');
      const panel = document.getElementById(id);
      if (panel) {
        const hidden = panel.hasAttribute('hidden');
        panel.toggleAttribute('hidden', !hidden);
      }
    }

    const check = e.target.closest('[data-check]');
    if (check) {
      check.classList.toggle('done');
      const box = check.querySelector('input[type="checkbox"]');
      if (box) box.checked = !box.checked;
    }

    const copyBtn = e.target.closest('[data-copy]');
    if (copyBtn) {
      const id = copyBtn.getAttribute('data-copy');
      const source = document.getElementById(id);
      if (source) {
        navigator.clipboard.writeText(source.value || source.textContent || '');
        const prev = copyBtn.textContent;
        copyBtn.textContent = 'Copied';
        setTimeout(() => (copyBtn.textContent = prev), 1200);
      }
    }

    const filter = e.target.closest('[data-filter]');
    if (filter) {
      const type = filter.getAttribute('data-filter');
      document.querySelectorAll('[data-filter]').forEach(ch => ch.classList.remove('active'));
      filter.classList.add('active');
      document.querySelectorAll('.template-card').forEach(card => {
        const matches = type === 'All' || card.dataset.type === type;
        card.style.display = matches ? '' : 'none';
      });
    }
  });
})();
