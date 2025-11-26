// UI utilities shared across pages
window.ui = (function() {
  function applyFilters(tableId, clearBtnId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const filterInputs = table.querySelectorAll('.filter-input');
    const rows = table.querySelectorAll('tbody tr');

    function filterRows() {
      const filters = {};
      filterInputs.forEach(input => {
        const idx = input.dataset.column;
        const val = input.value.trim().toLowerCase();
        if (val) filters[idx] = val;
      });
      rows.forEach(row => {
        let show = true;
        Object.entries(filters).forEach(([colIdx, filterVal]) => {
          const cell = row.cells[colIdx];
          if (cell && !cell.textContent.toLowerCase().includes(filterVal)) {
            show = false;
          }
        });
        row.style.display = show ? '' : 'none';
      });
    }

    filterInputs.forEach(input => {
      const eventType = (input.type === 'date' || input.tagName.toLowerCase() === 'select') ? 'change' : 'input';
      input.addEventListener(eventType, filterRows);
    });

    const clearBtn = document.getElementById(clearBtnId);
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        filterInputs.forEach(input => (input.value = ''));
        filterRows();
      });
    }

    // initial pass
    filterRows();
  }

  return {
    applyFilters
  };
})();
