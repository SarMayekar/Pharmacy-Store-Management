import requests

url = 'http://127.0.0.1:5000/sales'

# Data for first sale
data1 = {
    'patient_name': 'Test Patient',
    'doctor_name': 'Test Doctor',
    'invoice_no': 'TEST001',
    'sale_date': '2023-10-01',
    'rowcount': '1',
    'items-0-product': 'Test Medicine',
    'items-0-batch_no': 'BATCH1',
    'items-0-expiry_date': '2025-01-01',
    'items-0-mrp': '100',
    'items-0-quantity': '1',
    'items-0-rate': '90',
    'items-0-sgst_percent': '5',
    'items-0-cgst_percent': '5',
    'items-0-discount_percent': '0',
    'items-0-amount': '99',
    'grand_total_actual': '99',
    'savesale': 'Save Sale'
}

# Post first sale
response1 = requests.post(url, data=data1)
print("First sale response status:", response1.status_code)
print("First sale response contains 'saved successfully':", 'saved successfully' in response1.text.lower())

# Data for second sale with same invoice
data2 = {
    'patient_name': 'Test Patient2',
    'doctor_name': 'Test Doctor2',
    'invoice_no': 'TEST001',
    'sale_date': '2023-10-02',
    'rowcount': '1',
    'items-0-product': 'Test Medicine2',
    'items-0-batch_no': 'BATCH2',
    'items-0-expiry_date': '2025-02-01',
    'items-0-mrp': '200',
    'items-0-quantity': '1',
    'items-0-rate': '180',
    'items-0-sgst_percent': '5',
    'items-0-cgst_percent': '5',
    'items-0-discount_percent': '0',
    'items-0-amount': '198',
    'grand_total_actual': '198',
    'savesale': 'Save Sale'
}

# Post second sale
response2 = requests.post(url, data=data2)
print("Second sale response status:", response2.status_code)
print("Second sale response contains 'already exists':", 'already exists' in response2.text.lower())
