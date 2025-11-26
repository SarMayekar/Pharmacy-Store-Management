import requests
import datetime

url = 'http://127.0.0.1:5000/purchases'

# Test purchase with 2 items
data = {
    'distributor_name': 'DistributorMulti',
    'trade_type': 'Retail',
    'purchase_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '2',
    'items-0-product': 'MedicineC',
    'items-0-batch_no': 'BATCHC',
    'items-0-expiry_date': '2025-03-01',
    'items-0-hsn_code': 'HSNC',
    'items-0-mrp': '150',
    'items-0-quantity': '3',
    'items-0-rate': '140',
    'items-0-sgst_percent': '5',
    'items-0-cgst_percent': '5',
    'items-0-discount_percent': '0',
    'items-0-sale_rate': '145',
    'items-0-sale_discount_percent': '2',
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
    'items-1-sale_rate': '250',
    'items-1-sale_discount_percent': '5',
    'grand_total': '1020',  # 3*140 + 2*240 = 420 + 480 = 900, but with GST? Wait, calculate properly.
    # Actually, in the code, amount is calculated as qty*rate + gst - discount
    # For item0: 3*140 + (3*140*5/100)*2 - 0 = 420 + 42 = 462
    # Item1: 2*240 + (2*240*5/100)*2 = 480 + 48 = 528
    # Total 462+528=990, but let's set grand_total to 990
    'grand_total': '990',
    'savepurchase': 'Save Purchase'
}

response = requests.post(url, data=data)
print(f"Purchase status: {response.status_code}")
if response.status_code == 200:
    print("Multi-item purchase successful")
else:
    print("Failed")
    print(response.text)
