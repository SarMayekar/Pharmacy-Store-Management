import requests

BASE_URL = "http://127.0.0.1:5000"

def test_create_new_medicine_purchase():
    # Test Data: New medicine entry with purchase and sale rates
    data = {
        'rowcount': '1',
        'invoice_no': 'TEST-10001',
        'purchase_date': '2024-06-15',
        'distributor_name': 'Test Distributor',
        'distributor_contact': '1234567890',
        'trade_type': 'Retail',
        'grand_total': '150.00',

        'items-0-product': 'Test Medicine',
        'items-0-batch_no': 'BATCHTEST',
        'items-0-expiry_date': '2025-12-31',
        'items-0-hsn_code': '1234',
        'items-0-mrp': '200.00',
        'items-0-quantity': '10',
        'items-0-rate': '140.00',  # purchase rate
        'items-0-sale_rate': '160.00', # sale rate
        'items-0-sale_discount_percent': '5.0',
        'items-0-sgst_percent': '5.0',
        'items-0-cgst_percent': '5.0',
        'items-0-discount_percent': '0.0',
        'items-0-amount': '1500.00',
    }

    # Make POST request to save purchase
    response = requests.post(f"{BASE_URL}/purchases", data=data)

    assert response.status_code == 200 or response.status_code == 302, "Purchase creation failed"

    # Verify the medicine entry has purchase_rate and sale_rate updated
    meds_response = requests.get(f"{BASE_URL}/api/medicine/{data['items-0-product']}")
    assert meds_response.status_code == 200, "Failed to fetch medicine details"
    meds = meds_response.json()

    print("Medicines from API:", meds)  # Debug print to check API response

    matched_med = None
    for med in meds:
        if med['batch_no'] == data['items-0-batch_no'] and med['expiry_date'].split(" ")[0] == data['items-0-expiry_date']:
            matched_med = med
            break

    assert matched_med is not None, "Medicine batch not found"
    assert float(matched_med['purchase_rate']) == float(data['items-0-rate']), "Purchase rate mismatch"
    assert float(matched_med['sale_rate']) == float(data['items-0-sale_rate']), "Sale rate mismatch"
    assert float(matched_med['sale_discount_percent']) == float(data['items-0-sale_discount_percent']), "Sale discount percent mismatch"

    print("Test create_new_medicine_purchase passed.")

if __name__ == "__main__":
    test_create_new_medicine_purchase()
