// Unified autofill utilities for medicines, patients, doctors and distributors
// Provides a `fillMedicineFields(rowIndex, med)` function and helper fetchers
window.autofill = (function() {
  function getIdCandidates(rowIndex, field) {
    return [
      `items-${rowIndex}-${field}`,
      `items-${rowIndex}-${field}-sales`,
      `items-${rowIndex}-${field}-purchase`
    ];
  }

  function setFirstExisting(rowIndex, field, value) {
    if (value === undefined || value === null) return;
    const ids = getIdCandidates(rowIndex, field);
    for (const id of ids) {
      const el = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
      if (el) { el.value = value; el.classList.add('autofilled'); return true; }
    }
    return false;
  }

  function setByName(rowIndex, field, value) {
    if (value === undefined || value === null) return;
    const name = `items-${rowIndex}-${field}`;
    const el = document.querySelector(`[name="${name}"]`);
    if (el) { el.value = value; el.classList.add('autofilled'); return true; }
    // fallback: try suffixes
    const el2 = document.querySelector(`[name="${name}-sales"]`) || document.querySelector(`[name="${name}-purchase"]`);
    if (el2) { el2.value = value; return true; }
    return false;
  }

  function fillMedicineFields(rowIndex, med) {
    // Fill generic fields (batch, expiry, hsn, mrp, gst fields)
    setFirstExisting(rowIndex, 'batch_no', med.batch_no);
    setFirstExisting(rowIndex, 'expiry_date', med.expiry_date);
    setFirstExisting(rowIndex, 'hsn_code', med.hsn_code);
    setFirstExisting(rowIndex, 'mrp', med.mrp);
    setFirstExisting(rowIndex, 'sgst_percent', med.sgst_percent);
    setFirstExisting(rowIndex, 'cgst_percent', med.cgst_percent);

    // Fill sale_rate if a dedicated sale_rate field exists
    if (med.sale_rate !== undefined) {
      // Try exact name first
      setByName(rowIndex, 'sale_rate', med.sale_rate);
    }

    // For the main `rate` field (name="items-<i>-rate") we pick the best candidate:
    // - If the page has a separate sale_rate field (name exists), we assume `rate` is purchase rate (purchases)
    // - Otherwise, treat `rate` as the sale rate (sales pages / returns where relevant)
    const rateEl = document.querySelector(`[name="items-${rowIndex}-rate"]`);
    const saleRateEl = document.querySelector(`[name="items-${rowIndex}-sale_rate"]`);
    if (rateEl) {
      if (saleRateEl) {
        // This is likely a purchases page (has both fields). Use purchase_rate when available
        if (med.purchase_rate !== undefined && med.purchase_rate !== null) rateEl.value = med.purchase_rate;
        else if (med.sale_rate !== undefined && med.sale_rate !== null) rateEl.value = med.sale_rate;
      } else {
        // No dedicated sale_rate field — treat `rate` as sale rate first
        if (med.sale_rate !== undefined && med.sale_rate !== null) rateEl.value = med.sale_rate;
        else if (med.purchase_rate !== undefined && med.purchase_rate !== null) rateEl.value = med.purchase_rate;
      }
    }

    // After autofill, trigger a custom event so page-specific code can react (recalc or similar)
    try {
      const evt = new CustomEvent('autofill:medicine', { detail: { rowIndex, med } });
      document.dispatchEvent(evt);
    } catch (e) {
      // ignore
    }
  }

// Remove autofill visual marker when user edits a field manually
document.addEventListener('input', function(e) {
  try {
    const el = e.target;
    if (!el) return;
    const name = el.name || el.id || '';
    if (/^items-/.test(name)) {
      el.classList.remove('autofilled');
    }
  } catch (err) {}
});

  // Fetch helpers
  function fetchMedicine(name) {
    return fetch(`/api/medicine/${encodeURIComponent(name)}`).then(r => r.json());
  }

  function fetchPatient(name) {
    return fetch(`/api/patient/${encodeURIComponent(name)}`).then(r => r.json());
  }

  function fetchDistributor(name) {
    return fetch(`/api/distributor/${encodeURIComponent(name)}`).then(r => r.json());
  }

  function fetchDoctor(name) {
    return fetch(`/api/doctor/${encodeURIComponent(name)}`).then(r => r.json());
  }

  // Helper to autofill contact number into a field (if present)
  function fillContact(targetId, data) {
    try {
      if (!data) return;
      const el = document.getElementById(targetId) || document.querySelector(`[name="${targetId}"]`);
      if (el && data.contact_number) el.value = data.contact_number;
    } catch (e) {}
  }

  return {
    fillMedicineFields,
    fetchMedicine,
    fetchPatient,
    fetchDistributor,
    fetchDoctor,
    fillContact
  };
})();

// When other page code may expect plain fillMedicineFields in global scope, expose directly
window.fillMedicineFields = window.autofill.fillMedicineFields;
