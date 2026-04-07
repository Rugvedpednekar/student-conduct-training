// Shared interactive behaviors.
(function initPortalInteractions() {
  document.addEventListener('click', async (event) => {
    const collapseButton = event.target.closest('[data-collapse]');
    if (collapseButton) {
      const targetId = collapseButton.getAttribute('data-collapse');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        const isHidden = targetPanel.hasAttribute('hidden');
        targetPanel.toggleAttribute('hidden', !isHidden);
      }
    }

    const checkItem = event.target.closest('[data-check]');
    if (checkItem) {
      checkItem.classList.toggle('done');
      const input = checkItem.querySelector('input[type="checkbox"]');
      if (input) input.checked = !input.checked;
    }

    const copyButton = event.target.closest('[data-copy]');
    if (copyButton) {
      const sourceId = copyButton.getAttribute('data-copy');
      const sourceElement = document.getElementById(sourceId);
      if (sourceElement) {
        const text = sourceElement.value || sourceElement.textContent || '';
        try {
          await navigator.clipboard.writeText(text);
          const originalLabel = copyButton.textContent;
          copyButton.textContent = 'Copied';
          setTimeout(() => { copyButton.textContent = originalLabel; }, 1200);
        } catch {
          copyButton.textContent = 'Copy blocked';
        }
      }
    }

    const filterButton = event.target.closest('[data-filter]');
    if (filterButton) {
      const filterType = filterButton.getAttribute('data-filter');
      document.querySelectorAll('[data-filter]').forEach((chip) => chip.classList.remove('active'));
      filterButton.classList.add('active');
      document.querySelectorAll('.template-card').forEach((card) => {
        const show = filterType === 'All' || card.dataset.type === filterType;
        card.style.display = show ? '' : 'none';
      });
    }
  });
})();
