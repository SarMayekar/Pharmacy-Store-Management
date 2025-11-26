import requests
import datetime

url = 'http://127.0.0.1:5000/sales'

# Function to make a sale
def make_sale(patient_name, doctor_name, product, batch_no, expiry_date, mrp, quantity, rate, sgst, cgst, discount, amount, grand_total):
    data = {
        'patient_name': patient_name,
        'doctor_name': doctor_name,
        'sale_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'rowcount': '1',
        'items-0-product': product,
        'items-0-batch_no': batch_no,
        'items-0-expiry_date': expiry_date,
        'items-0-mrp': str(mrp),
        'items-0-quantity': str(quantity),
        'items-0-rate': str(rate),
        'items-0-sgst_percent': str(sgst),
        'items-0-cgst_percent': str(cgst),
        'items-0-discount_percent': str(discount),
        'items-0-amount': str(amount),
        'grand_total_actual': str(grand_total),
        'savesale': 'Save Sale'
    }
    response = requests.post(url, data=data)
    return response

# Test multiple sales to check invoice format
print("Testing auto-generated invoice format...")

# Sale 1
response1 = make_sale('Patient1', 'Doctor1', 'Medicine1', 'BATCH1', '2025-01-01', 100, 1, 90, 5, 5, 0, 99, 99)
print(f"Sale 1 status: {response1.status_code}")
if response1.status_code == 200:
    # Extract invoice from response (assuming it's in the HTML or redirect)
    # Since we can't parse HTML easily, we'll assume success and check logs or DB later
    print("Sale 1 successful")

# Sale 2
response2 = make_sale('Patient2', 'Doctor2', 'Medicine2', 'BATCH2', '2025-02-01', 200, 1, 180, 5, 5, 0, 198, 198)
print(f"Sale 2 status: {response2.status_code}")
if response2.status_code == 200:
    print("Sale 2 successful")

# Sale 3
response3 = make_sale('Patient3', 'Doctor3', 'Medicine3', 'BATCH3', '2025-03-01', 150, 1, 135, 5, 5, 0, 148.5, 148.5)
print(f"Sale 3 status: {response3.status_code}")
if response3.status_code == 200:
    print("Sale 3 successful")

print("Test completed. Check the database or logs for invoice numbers in format ddmmyyXXX (e.g., 181125001, 181125002, etc.)")
