// Shared calculations utilities for rows and totals
window.calc = (function() {
  function toFloat(val) { var num = parseFloat(val); return isNaN(num) ? 0 : num; }

  function calcRow(index, container = document) {
    const qtyEl = container.querySelector(`[name="items-${index}-quantity"]`);
    if (!qtyEl) return; // no row
    let qty = toFloat(qtyEl.value);
    let rate = toFloat(container.querySelector(`[name="items-${index}-rate"]`)?.value);
    let sgst = toFloat(container.querySelector(`[name="items-${index}-sgst_percent"]`)?.value);
    let cgst = toFloat(container.querySelector(`[name="items-${index}-cgst_percent"]`)?.value);
    let amountInput = container.querySelector(`[name="items-${index}-amount"]`);
    if (amountInput && (!amountInput.dataset.locked || amountInput.value.trim() === "")) {
      let base = qty * rate;
      let gst_sgst = base * sgst / 100;
      let gst_cgst = base * cgst / 100;
      let amount = base + gst_sgst + gst_cgst;
      amountInput.value = amount > 0 ? amount.toFixed(2) : "";
    }

    // sale rate calculation if applicable
    let mrp = toFloat(container.querySelector(`[name="items-${index}-mrp"]`)?.value);
    let saleDiscountEl = container.querySelector(`[name="items-${index}-sale_discount_percent"]`) || container.querySelector(`[name="items-${index}-discount_percent"]`);
    let saleDiscount = toFloat(saleDiscountEl?.value);
    let saleRateInput = container.querySelector(`[name="items-${index}-sale_rate"]`);
    if (saleRateInput && saleDiscount > 0) {
      let sRate = mrp - (mrp * saleDiscount / 100);
      saleRateInput.value = sRate.toFixed(2);
    }
  }

  function recalcAll(container = document) {
    const rows = container.querySelectorAll('[name^="items-"][name$="-quantity"]');
    let total_mrp = 0, total_actual = 0;
    rows.forEach((qtyInput, idx) => {
      calcRow(idx, container);
      let mrp = toFloat(container.querySelector(`[name="items-${idx}-mrp"]`)?.value);
      let sgst = toFloat(container.querySelector(`[name="items-${idx}-sgst_percent"]`)?.value);
      let cgst = toFloat(container.querySelector(`[name="items-${idx}-cgst_percent"]`)?.value);
      let qty = toFloat(qtyInput.value);
      let amount = toFloat(container.querySelector(`[name="items-${idx}-amount"]`)?.value);
      let item_mrp_total = (mrp * qty) + ((mrp*qty)*sgst/100) + ((mrp*qty)*cgst/100);
      total_mrp += item_mrp_total;
      total_actual += amount;
    });

    // try commonly named grand inputs
    const mrpInput = container.querySelector('[name="grand_total_mrp"]');
    const actualInput = container.querySelector('[name="grand_total_actual"]') || container.querySelector('[name="grand_total"]');
    const savingsInput = container.querySelector('[name="savings_total"]');
    if (mrpInput && (!mrpInput.dataset.locked || mrpInput.value.trim() === "")) mrpInput.value = total_mrp > 0 ? total_mrp.toFixed(2) : "";
    if (actualInput && (!actualInput.dataset.locked || actualInput.value.trim() === "")) actualInput.value = total_actual > 0 ? total_actual.toFixed(2) : "";
    if (savingsInput && (!savingsInput.dataset.locked || savingsInput.value.trim() === "")) savingsInput.value = (total_mrp - total_actual > 0) ? (total_mrp - total_actual).toFixed(2) : "";
  }

  function attachRowListeners(idx, container = document) {
    // support both discount field names used across templates
    ['quantity','rate','sgst_percent','cgst_percent','sale_discount_percent','discount_percent','mrp'].forEach(field => {
      const el = container.querySelector(`[name="items-${idx}-${field}"]`);
      if (el) el.addEventListener('input', function(){ calcRow(idx, container); recalcAll(container); });
    });
    const amount = container.querySelector(`[name="items-${idx}-amount"]`);
    if (amount) amount.addEventListener('input', function(){ amount.dataset.locked = (amount.value.trim() !== ''); recalcAll(container); });
  }

  function attachTotalListeners(container = document) {
    const mrpInput = container.querySelector('[name="grand_total_mrp"]');
    const actualInput = container.querySelector('[name="grand_total_actual"]') || container.querySelector('[name="grand_total"]');
    const savingsInput = container.querySelector('[name="savings_total"]');
    function handleMrp(){ if (!mrpInput) return; mrpInput.dataset.locked = (mrpInput.value.trim() !== ''); if (!savingsInput?.dataset.locked) { let v = toFloat(mrpInput.value) - toFloat(actualInput?.value); if (savingsInput) savingsInput.value = v>0? v.toFixed(2):''; } }
    function handleActual(){ if (!actualInput) return; actualInput.dataset.locked = (actualInput.value.trim() !== ''); if (!savingsInput?.dataset.locked) { let v = toFloat(mrpInput?.value) - toFloat(actualInput.value); if (savingsInput) savingsInput.value = v>0? v.toFixed(2):''; } }
    function handleSavings(){ if (!savingsInput) return; savingsInput.dataset.locked = (savingsInput.value.trim() !== ''); if (!actualInput?.dataset.locked) { let v = toFloat(mrpInput?.value) - toFloat(savingsInput.value); if (actualInput) actualInput.value = v>0? v.toFixed(2):''; } }
    if (mrpInput) mrpInput.addEventListener('input', handleMrp);
    if (actualInput) actualInput.addEventListener('input', handleActual);
    if (savingsInput) savingsInput.addEventListener('input', handleSavings);
  }

  return {
    toFloat, calcRow, recalcAll, attachRowListeners, attachTotalListeners
  };
})();
