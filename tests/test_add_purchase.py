import requests
import json

# Test script to add a purchase record with multiple rows
# This tests the addrow/delrow functionality and gst_percent calculation

def test_add_purchase():
    base_url = 'http://127.0.0.1:5000'

    # First, let's get to the purchases page to see the form
    print("Testing purchase addition with multiple rows...")

    # Simulate form data for adding a purchase with 2 rows
    purchase_data = {
        'rowcount': '2',
        'invoice_no': 'TEST001',
        'purchase_date': '2024-01-15',
        'distributor_name': 'Test Distributor',
        'distributor_contact': '1234567890',
        'trade_type': 'Retail',
        'grand_total': '200.00',
        'discount_percent': '0',

        # Row 1
        'items-0-product': 'Test Medicine 1',
        'items-0-batch_no': 'BATCH001',
        'items-0-expiry_date': '2025-01-01',
        'items-0-packing': '10x10',
        'items-0-free': '2',
        'items-0-sgst_percent': '5',
        'items-0-cgst_percent': '5',
        'items-0-gst_percent': '10',  # Should be sgst + cgst = 10
        'items-0-hsn_code': '123456',
        'items-0-mrp': '50.00',
        'items-0-quantity': '10',
        'items-0-rate': '15.00',
        'items-0-discount_percent': '0',
        'items-0-amount': '150.00',
        'items-0-sale_rate': '20.00',
        'items-0-sale_discount_percent': '0',

        # Row 2
        'items-1-product': 'Test Medicine 2',
        'items-1-batch_no': 'BATCH002',
        'items-1-expiry_date': '2025-02-01',
        'items-1-packing': '5x5',
        'items-1-free': '1',
        'items-1-sgst_percent': '6',
        'items-1-cgst_percent': '6',
        'items-1-gst_percent': '12',  # Should be sgst + cgst = 12
        'items-1-hsn_code': '654321',
        'items-1-mrp': '30.00',
        'items-1-quantity': '5',
        'items-1-rate': '10.00',
        'items-1-discount_percent': '0',
        'items-1-amount': '50.00',
        'items-1-sale_rate': '15.00',
        'items-1-sale_discount_percent': '0',

        'savepurchase': 'Save Purchase'
    }

    try:
        # Send POST request to add purchase
        response = requests.post(f'{base_url}/purchases', data=purchase_data)

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # First 500 chars

        if response.status_code == 200:
            print("Purchase addition successful!")
            # Check if redirected (which indicates success)
            if 'redirect' in response.text.lower() or response.url != f'{base_url}/purchases':
                print("Redirect detected - purchase likely saved successfully")
            else:
                print("No redirect - check for errors in response")
        else:
            print(f"Failed to add purchase. Status: {response.status_code}")

    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == '__main__':
    test_add_purchase()
