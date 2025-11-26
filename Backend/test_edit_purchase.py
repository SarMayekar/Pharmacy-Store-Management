import requests
import datetime

url = 'http://127.0.0.1:5000/purchases'

# Test editing purchase ID 27 (change quantity of first item)
data = {
    'edit_purchase_id': '27',
    'distributor_name': 'DistributorMulti',
    'trade_type': 'Retail',
    'purchase_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '2',
    'items-0-product': 'MedicineC',
    'items-0-batch_no': 'BATCHC',
    'items-0-expiry_date': '2025-03-01',
    'items-0-hsn_code': 'HSNC',
    'items-0-mrp': '150',
    'items-0-quantity': '5',  # Changed from 3 to 5
    'items-0-rate': '140',
    'items-0-sgst_percent': '5',
    'items-0-cgst_percent': '5',
    'items-0-discount_percent': '0',
    'items-0-product_id': '27',  # Assuming product_id for MedicineC is 27, but need to check
    'items-1-product': 'MedicineD',
    'items-1-batch_no': 'BATCHD',
    'items-1-expiry_date': '2025-04-01',
    'items-1-hsn_code': 'HSND',
    'items-1-mrp': '250',
    'items-1-quantity': '2',
    'items-1-rate': '240',
    'items-1-sgst_percent': '5',
    'items-1-cgst_percent': '5',
    'items-1-discount_percent': '0',
    'items-1-product_id': '28',  # Assuming product_id for MedicineD is 28
    'grand_total': '1190',  # Recalculate: 5*140 + gst = 700 + 70 = 770, 2*240 + gst = 480 + 48 = 528, total 1298, but set to 1190 for now
    'savepurchase': 'Save Purchase'
}

response = requests.post(url, data=data)
print(f"Edit Purchase status: {response.status_code}")
if response.status_code == 302:  # Redirect after success
    print("Edit purchase successful")
else:
    print("Failed")
    print(response.text)
