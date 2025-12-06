from Backend import app as flask_app
from flask import render_template
import os

# Mock sale and items
sale = {
    'invoice_no': 'TEST001',
    'sale_datetime': '2025-12-02 10:00:00',
}

items = [
    {
        'name': 'Paracetamol 500mg',
        'batch_no': 'B001',
        'expiry_date': '2026-06-30',
        'hsn_code': '3004',
        'quantity': 2,
        'price': 118.0,  # Inclusive of 12% GST for example
        'mrp': 150.0,
        'sgst_percent': 6.0,
        'cgst_percent': 6.0,
    },
    {
        'name': 'Cough Syrup',
        'batch_no': 'B010',
        'expiry_date': '2027-01-31',
        'hsn_code': '3005',
        'quantity': 1,
        'price': 105.0,  # Inclusive of 5% GST for example
        'mrp': 120.0,
        'sgst_percent': 2.5,
        'cgst_percent': 2.5,
    }
]

# Compute gst_summary using reverse calculation (same logic as app.bill_view)
gst_summary = {
    5:  {'gross': 0.0, 'taxable': 0.0, 'sgst': 0.0, 'cgst': 0.0, 'total_gst': 0.0},
    12: {'gross': 0.0, 'taxable': 0.0, 'sgst': 0.0, 'cgst': 0.0, 'total_gst': 0.0},
    'other': {'gross': 0.0, 'taxable': 0.0, 'sgst': 0.0, 'cgst': 0.0, 'total_gst': 0.0},
    'total': {'gross': 0.0, 'taxable': 0.0, 'sgst': 0.0, 'cgst': 0.0, 'total_gst': 0.0}
}
mrp_total = 0.0

for item in items:
    qty = float(item.get('quantity', 0) or 0)
    rate = float(item.get('price', item.get('rate', 0)) or 0)
    mrp = float(item.get('mrp', 0) or 0)
    sgst_p = float(item.get('sgst_percent', 0) or 0)
    cgst_p = float(item.get('cgst_percent', 0) or 0)
    gst_rate = sgst_p + cgst_p

    row_gross = rate * qty
    mrp_total += mrp * qty

    if gst_rate > 0:
        taxable = row_gross / (1 + (gst_rate / 100))
        total_tax = row_gross - taxable
    else:
        taxable = row_gross
        total_tax = 0.0

    sgst_amt = total_tax / 2
    cgst_amt = total_tax / 2

    if abs(gst_rate - 5.0) < 1e-9:
        bucket = 5
    elif abs(gst_rate - 12.0) < 1e-9:
        bucket = 12
    else:
        bucket = 'other'

    gst_summary[bucket]['gross'] += row_gross
    gst_summary[bucket]['taxable'] += taxable
    gst_summary[bucket]['sgst'] += sgst_amt
    gst_summary[bucket]['cgst'] += cgst_amt
    gst_summary[bucket]['total_gst'] += total_tax

    gst_summary['total']['gross'] += row_gross
    gst_summary['total']['taxable'] += taxable
    gst_summary['total']['sgst'] += sgst_amt
    gst_summary['total']['cgst'] += cgst_amt
    gst_summary['total']['total_gst'] += total_tax

sale['mrp_total'] = round(mrp_total, 2)
sale['sub_total'] = round(gst_summary['total']['taxable'], 2)
# For test, grand total matches sum of gross
sale['total_amount'] = round(gst_summary['total']['gross'], 2)
sale['savings'] = round(sale['mrp_total'] - sale['total_amount'], 2)

# Render template
with flask_app.test_request_context('/'):
    html = render_template('bill.html', sale=sale, items=items, gst_summary=gst_summary, amount_in_words='Rupees One Hundred')

out_dir = os.path.join(os.path.dirname(__file__), '..', 'Output')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

out_path = os.path.join(out_dir, 'test_bill.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Rendered bill saved to:', out_path)
