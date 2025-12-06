import requests
import json
import time

# Test script to verify multiple rows are saved correctly in sales and purchase returns

def test_multiple_rows():
    base_url = 'http://127.0.0.1:5000'

    print("Testing multiple rows functionality...")

    # Test data for sales return with 3 rows
    sales_return_data = {
        'rowcount': '3',
        'invoice_no': '240101001',
        'return_date': '2024-01-01',
        'patient_name': 'Test Patient',
        'grand_total_actual': '300.00',
        'grand_total_mrp': '350.00',
        'savings_total': '50.00',
        'savesalesreturn': '1',
        # Row 1
        'items-0-product': 'Paracetamol',
        'items-0-batch_no': 'BATCH001',
        'items-0-expiry_date': '2025-01-01',
        'items-0-hsn_code': 'HSN001',
        'items-0-mrp': '50.00',
        'items-0-quantity': '2',
        'items-0-rate': '40.00',
        'items-0-sgst_percent': '6.00',
        'items-0-cgst_percent': '6.00',
        'items-0-amount': '80.00',
        # Row 2
        'items-1-product': 'Ibuprofen',
        'items-1-batch_no': 'BATCH002',
        'items-1-expiry_date': '2025-02-01',
        'items-1-hsn_code': 'HSN002',
        'items-1-mrp': '100.00',
        'items-1-quantity': '1',
        'items-1-rate': '90.00',
        'items-1-sgst_percent': '6.00',
        'items-1-cgst_percent': '6.00',
        'items-1-amount': '90.00',
        # Row 3
        'items-2-product': 'Aspirin',
        'items-2-batch_no': 'BATCH003',
        'items-2-expiry_date': '2025-03-01',
        'items-2-hsn_code': 'HSN003',
        'items-2-mrp': '200.00',
        'items-2-quantity': '1',
        'items-2-rate': '180.00',
        'items-2-sgst_percent': '6.00',
        'items-2-cgst_percent': '6.00',
        'items-2-amount': '180.00'
    }

    # Test data for purchase return with 2 rows
    purchase_return_data = {
        'rowcount': '2',
        'invoice_no': '240101002',
        'return_date': '2024-01-01',
        'distributor_name': 'Test Distributor',
        'grand_total': '500.00',
        'savepurchasereturn': '1',
        # Row 1
        'items-0-product': 'Paracetamol',
        'items-0-batch_no': 'BATCH001',
        'items-0-expiry_date': '2025-01-01',
        'items-0-hsn_code': 'HSN001',
        'items-0-mrp': '50.00',
        'items-0-quantity': '5',
        'items-0-rate': '30.00',
        'items-0-sgst_percent': '6.00',
        'items-0-cgst_percent': '6.00',
        'items-0-amount': '150.00',
        # Row 2
        'items-1-product': 'Ibuprofen',
        'items-1-batch_no': 'BATCH002',
        'items-1-expiry_date': '2025-02-01',
        'items-1-hsn_code': 'HSN002',
        'items-1-mrp': '100.00',
        'items-1-quantity': '2',
        'items-1-rate': '80.00',
        'items-1-sgst_percent': '6.00',
        'items-1-cgst_percent': '6.00',
        'items-1-amount': '160.00'
    }

    try:
        # Test sales return
        print("Testing sales return with 3 rows...")
        response = requests.post(f'{base_url}/sales-returns', data=sales_return_data)
        print(f"Sales return response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Sales return submitted successfully")
        else:
            print(f"✗ Sales return failed: {response.text}")

        # Test purchase return
        print("Testing purchase return with 2 rows...")
        response = requests.post(f'{base_url}/purchase-returns', data=purchase_return_data)
        print(f"Purchase return response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Purchase return submitted successfully")
        else:
            print(f"✗ Purchase return failed: {response.text}")

        # Check if records were saved by querying the history endpoints
        print("\nChecking if records appear in history...")

        # Check sales returns history
        response = requests.get(f'{base_url}/sales-returns')
        if '240101001' in response.text:
            print("✓ Sales return with 3 items appears in history")
        else:
            print("✗ Sales return not found in history")

        # Check purchase returns history
        response = requests.get(f'{base_url}/purchase-returns')
        if '240101002' in response.text:
            print("✓ Purchase return with 2 items appears in history")
        else:
            print("✗ Purchase return not found in history")

        print("\nTest completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == '__main__':
    test_multiple_rows()
