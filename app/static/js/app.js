// Shared interactive behaviors.
(function initPortalInteractions() {
  document.addEventListener('click', async (event) => {
    const collapseButton = event.target.closest('[data-collapse]');
    if (collapseButton) {
      const targetId = collapseButton.getAttribute('data-collapse');
      const targetPanel = document.getElementById(targetId);

      if (targetPanel) {
        const isHidden = targetPanel.hasAttribute('hidden');

        // Optional accordion behavior for case-step cards
        const parentCard = collapseButton.closest('.case-step-card');
        if (parentCard) {
          document.querySelectorAll('.case-step-card').forEach((card) => {
            const button = card.querySelector('[data-collapse]');
            const panelId = button?.getAttribute('data-collapse');
            const panel = panelId ? document.getElementById(panelId) : null;
            const arrow = card.querySelector('.case-step-arrow');

            if (card !== parentCard && panel) {
              panel.setAttribute('hidden', '');
              card.classList.remove('is-open');
              if (arrow) arrow.textContent = '+';
            }
          });
        }

        targetPanel.toggleAttribute('hidden', !isHidden);

        const arrow = collapseButton.querySelector('.case-step-arrow');
        if (!isHidden) {
          parentCard?.classList.remove('is-open');
          if (arrow) arrow.textContent = '+';
        } else {
          parentCard?.classList.add('is-open');
          if (arrow) arrow.textContent = '−';
        }
      }
      return;
    }

    const checkItem = event.target.closest('[data-check]');
    if (checkItem) {
      // Avoid double toggle when clicking the actual checkbox
      if (event.target.matches('input[type="checkbox"]')) {
        checkItem.classList.toggle('done', event.target.checked);
      } else {
        checkItem.classList.toggle('done');
        const input = checkItem.querySelector('input[type="checkbox"]');
        if (input) input.checked = !input.checked;
      }
      return;
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
          setTimeout(() => {
            copyButton.textContent = originalLabel;
          }, 1200);
        } catch {
          copyButton.textContent = 'Copy blocked';
          setTimeout(() => {
            copyButton.textContent = 'Copy Template';
          }, 1200);
        }
      }
      return;
    }

    const filterButton = event.target.closest('[data-filter]');
    if (filterButton) {
      const filterType = filterButton.getAttribute('data-filter');

      document.querySelectorAll('[data-filter]').forEach((chip) => {
        chip.classList.remove('active');
      });
      filterButton.classList.add('active');

      document.querySelectorAll('.template-card').forEach((card) => {
        const show = filterType === 'All' || card.dataset.type === filterType;
        card.style.display = show ? '' : 'none';
      });
    }
  });

  // Sync checklist styles on initial load
  document.querySelectorAll('[data-check]').forEach((item) => {
    const input = item.querySelector('input[type="checkbox"]');
    if (input?.checked) {
      item.classList.add('done');
    }
  });
})();
