import requests
import datetime

url = 'http://127.0.0.1:5000/sales'

# Test sale with 2 items
data = {
    'patient_name': 'PatientMulti',
    'doctor_name': 'DoctorMulti',
    'sale_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '2',
    'items-0-product': 'MedicineA',
    'items-0-batch_no': 'BATCHA',
    'items-0-expiry_date': '2025-01-01',
    'items-0-mrp': '100',
    'items-0-quantity': '2',
    'items-0-rate': '90',
    'items-0-sgst_percent': '5',
    'items-0-cgst_percent': '5',
    'items-0-discount_percent': '0',
    'items-1-product': 'MedicineB',
    'items-1-batch_no': 'BATCHB',
    'items-1-expiry_date': '2025-02-01',
    'items-1-mrp': '200',
    'items-1-quantity': '1',
    'items-1-rate': '180',
    'items-1-sgst_percent': '5',
    'items-1-cgst_percent': '5',
    'items-1-discount_percent': '0',
    'grand_total_actual': '360',
    'savesale': 'Save Sale'
}

response = requests.post(url, data=data)
print(f"Sale status: {response.status_code}")
if response.status_code == 200:
    print("Multi-item sale successful")
else:
    print("Failed")
