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

  function initializePage(container = document) {
    // Attach general input listener to lock fields when manually inputted
    container.addEventListener('input', function(event) {
      const el = event.target;
      if (el && el.tagName === 'INPUT' && el.type !== 'submit' && el.type !== 'button') {
        if (!el.dataset.locked) {
          el.dataset.locked = true;
        }
      }
    });

    // Attach autofill listeners for medicine product inputs
    container.addEventListener('input', function(event) {
      if (event.target.matches('[id^="items-"][id$="-product"]')) {
        const productInput = event.target;
        const rowIndex = productInput.id.match(/items-(\d+)-product/)[1];
        const medicineName = productInput.value.trim();
        if (medicineName && window.autofill && window.autofill.fetchMedicine) {
          window.autofill.fetchMedicine(medicineName)
            .then(data => {
              if (data && data.length > 0) {
                // For simplicity, we'll just use the first result.
                // A more advanced implementation could show a batch selector.
                window.autofill.fillMedicineFields(rowIndex, data[0]);
              }
            })
            .catch(error => console.error('Error fetching medicine data:', error));
        }
      }
    });

    // Attach autofill listeners for patient name
    const patientNameEl = container.querySelector('#patient_name');
    if (patientNameEl) {
      patientNameEl.addEventListener('input', function() {
        const patientName = this.value.trim();
        if (patientName && window.autofill && window.autofill.fetchPatient) {
          window.autofill.fetchPatient(patientName)
            .then(data => {
              if (data && data.contact_number) {
                window.autofill.fillContact('patient_contact', data);
              }
            })
            .catch(error => console.error('Error fetching patient data:', error));
        }
      });
    }

    // Attach autofill listeners for doctor name
    const doctorNameEl = container.querySelector('#doctor_name');
    if (doctorNameEl) {
      doctorNameEl.addEventListener('input', function() {
        const doctorName = this.value.trim();
        if (doctorName && window.autofill && window.autofill.fetchDoctor) {
          window.autofill.fetchDoctor(doctorName)
            .then(data => {
              if (data && data.contact_number) {
                window.autofill.fillContact('doctor_contact', data);
              }
            })
            .catch(error => console.error('Error fetching doctor data:', error));
        }
      });
    }

    // Attach autofill listeners for distributor name
    const distributorNameEl = container.querySelector('#distributor_name');
    if (distributorNameEl) {
      distributorNameEl.addEventListener('input', function() {
        const distributorName = this.value.trim();
        if (distributorName && window.autofill && window.autofill.fetchDistributor) {
          window.autofill.fetchDistributor(distributorName)
            .then(data => {
              if (data && data.length > 0) {
                window.autofill.fillContact('distributor_contact', data[0]);
              }
            })
            .catch(error => console.error('Error fetching distributor data:', error));
        }
      });
    }

    // Attach calculation listeners to all item rows
    const rows = container.querySelectorAll('[name^="items-"][name$="-quantity"]');
    for (let i = 0; i < rows.length; i++) {
      if (window.calc) window.calc.attachRowListeners(i, container);
    }
    if (window.calc) window.calc.attachTotalListeners(container);
    if (window.calc) window.calc.recalcAll(container); // Initial calculation
  }

  return {
    applyFilters,
    initializePage
  };
})();
