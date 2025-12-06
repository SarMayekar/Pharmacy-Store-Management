// Shared calculations utilities for rows and totals
window.calc = (function() {
  function toFloat(val) { var num = parseFloat(val); return isNaN(num) ? 0 : num; }

  function calcRow(index, container = document) {
    const qtyEl = container.querySelector(`[name="items-${index}-quantity"]`);
    if (!qtyEl) return; // no row
    let qty = toFloat(qtyEl.value);
    let free = toFloat(container.querySelector(`[name="items-${index}-free"]`)?.value || 0);
    let rate = toFloat(container.querySelector(`[name="items-${index}-rate"]`)?.value || 0);
    let amountInput = container.querySelector(`[name="items-${index}-amount"]`);
    if (amountInput) {
      const form = container.closest('form');
      // detect purchases or purchase-returns routes (both hyphen and underscore variants)
      const action = (form && form.action) ? form.action : '';
      const isPurchases = action.includes('purchases') || action.includes('purchase_returns') || action.includes('purchase-returns');
      let row_final_amount;
      if (isPurchases) {
        let gst = toFloat(container.querySelector(`[name="items-${index}-gst_percent"]`)?.value || 0);
        row_final_amount = qty * rate * (1 + gst / 100);
        amountInput.value = row_final_amount > 0 ? row_final_amount.toFixed(2) : "";
        amountInput.dataset.locked = true;
      } else {
        if (!amountInput.dataset.locked || amountInput.value.trim() === "") {
          // Apply discount (if any) to sales rows: Amount = (Qty + Free) * Rate - Discount%
          let discount = toFloat(container.querySelector(`[name="items-${index}-discount_percent"]`)?.value || 0);
          // Base row amount before discount
          let base_row = (qty + free) * rate;
          let discount_amt = base_row * (discount / 100.0);
          row_final_amount = base_row - discount_amt;
          amountInput.value = row_final_amount > 0 ? row_final_amount.toFixed(2) : "";
          amountInput.dataset.locked = true;
        }
      }
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
    const form = container.closest('form');
    const isSales = form && form.action.includes('sales');
    const rows = container.querySelectorAll('[name^="items-"][name$="-quantity"]');
    let total_mrp = 0, total_actual = 0;
    // Detect header-level discount_percent (used for purchases and purchase returns)
    const headerDiscountEl = container.querySelector('[name="discount_percent"]');
    let useHeaderDiscount = !!headerDiscountEl;
    rows.forEach((qtyInput, idx) => {
      calcRow(idx, container);
      let mrp = toFloat(container.querySelector(`[name="items-${idx}-mrp"]`)?.value);
      let qty = toFloat(qtyInput.value);
      let free = toFloat(container.querySelector(`[name="items-${idx}-free"]`)?.value || 0);
      let amount = toFloat(container.querySelector(`[name="items-${idx}-amount"]`)?.value);
      let item_mrp_total = mrp * (qty + free); // for display
      total_mrp += item_mrp_total;

      total_actual += amount;
    });

    // try commonly named grand inputs
    const mrpInput = container.querySelector('[name="grand_total_mrp"]');
    const actualInput = container.querySelector('[name="grand_total_actual"]') || container.querySelector('[name="grand_total"]');
    const savingsInput = container.querySelector('[name="savings_total"]');
    if (mrpInput) {
      mrpInput.value = total_mrp > 0 ? total_mrp.toFixed(2) : "";
      mrpInput.dataset.locked = true;
    }
    if (useHeaderDiscount) {
      let headerDiscount = toFloat(headerDiscountEl.value);
      let headerDiscountValue = total_actual * (headerDiscount / 100.0);
      let finalTotal = total_actual - headerDiscountValue;
      if (actualInput) {
        actualInput.value = finalTotal > 0 ? finalTotal.toFixed(2) : "";
        actualInput.dataset.locked = true;
      }
      if (savingsInput) {
        savingsInput.value = (total_mrp - finalTotal > 0) ? (total_mrp - finalTotal).toFixed(2) : "";
        savingsInput.dataset.locked = true;
      }
    } else {
      if (actualInput) {
        actualInput.value = total_actual > 0 ? total_actual.toFixed(2) : "";
        actualInput.dataset.locked = true;
      }
      if (savingsInput) {
        savingsInput.value = (total_mrp - total_actual > 0) ? (total_mrp - total_actual).toFixed(2) : "";
        savingsInput.dataset.locked = true;
      }
    }
  }

  function attachRowListeners(idx, container = document) {
    // support both discount field names used across templates
    ['quantity','free','rate','gst_percent','sgst_percent','cgst_percent','sale_discount_percent','discount_percent','mrp'].forEach(field => {
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
    // header discount percent (purchases/purchase_returns) should also trigger recalculation
    const headerDiscount = container.querySelector('[name="discount_percent"]');
    if (headerDiscount) headerDiscount.addEventListener('input', function(){ recalcAll(container); });
  }

  return {
    toFloat, calcRow, recalcAll, attachRowListeners, attachTotalListeners
  };
})();
