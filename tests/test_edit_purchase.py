import requests
import json

# Test script to edit the existing purchase (ID 1) by adding a third row and modifying quantities
# This tests the edit functionality, addrow during edit, and inventory updates

def test_edit_purchase():
    base_url = 'http://127.0.0.1:5000'

    print("Testing purchase editing with third row addition...")

    # First, start editing the purchase (ID 1)
    edit_data = {
        'startedit_id': '1'
    }

    try:
        # Get the edit form
        response = requests.post(f'{base_url}/purchases', data=edit_data)
        print(f"Edit form load status: {response.status_code}")

        if response.status_code == 200:
            print("Edit form loaded successfully")

            # Now submit the edited purchase with 3 rows (adding a third row)
            # Original 2 rows + 1 new row
            edit_purchase_data = {
                'rowcount': '3',
                'invoice_no': 'TEST001',
                'purchase_date': '2024-01-15',
                'distributor_name': 'Test Distributor',
                'distributor_contact': '1234567890',
                'trade_type': 'Retail',
                'grand_total': '350.00',  # Updated total
                'discount_percent': '0',
                'edit_purchase_id': '1',

                # Row 1 (modified quantities)
                'items-0-product': 'Test Medicine 1',
                'items-0-batch_no': 'BATCH001',
                'items-0-expiry_date': '2025-01-01',
                'items-0-packing': '10x10',
                'items-0-free': '3',  # Changed from 2 to 3
                'items-0-sgst_percent': '5',
                'items-0-cgst_percent': '5',
                'items-0-gst_percent': '10',
                'items-0-hsn_code': '123456',
                'items-0-mrp': '50.00',
                'items-0-quantity': '15',  # Changed from 10 to 15
                'items-0-rate': '15.00',
                'items-0-discount_percent': '0',
                'items-0-amount': '225.00',  # 15 * 15
                'items-0-sale_rate': '20.00',
                'items-0-sale_discount_percent': '0',
                'items-0-product_id': '1',  # Existing product

                # Row 2 (modified quantities)
                'items-1-product': 'Test Medicine 2',
                'items-1-batch_no': 'BATCH002',
                'items-1-expiry_date': '2025-02-01',
                'items-1-packing': '5x5',
                'items-1-free': '2',  # Changed from 1 to 2
                'items-1-sgst_percent': '6',
                'items-1-cgst_percent': '6',
                'items-1-gst_percent': '12',
                'items-1-hsn_code': '654321',
                'items-1-mrp': '30.00',
                'items-1-quantity': '8',  # Changed from 5 to 8
                'items-1-rate': '10.00',
                'items-1-discount_percent': '0',
                'items-1-amount': '80.00',  # 8 * 10
                'items-1-sale_rate': '15.00',
                'items-1-sale_discount_percent': '0',
                'items-1-product_id': '2',  # Existing product

                # Row 3 (new row)
                'items-2-product': 'Test Medicine 3',
                'items-2-batch_no': 'BATCH003',
                'items-2-expiry_date': '2025-03-01',
                'items-2-packing': '20x1',
                'items-2-free': '1',
                'items-2-sgst_percent': '9',
                'items-2-cgst_percent': '9',
                'items-2-gst_percent': '18',
                'items-2-hsn_code': '987654',
                'items-2-mrp': '40.00',
                'items-2-quantity': '5',
                'items-2-rate': '12.00',
                'items-2-discount_percent': '0',
                'items-2-amount': '60.00',  # 5 * 12
                'items-2-sale_rate': '18.00',
                'items-2-sale_discount_percent': '0',

                'savepurchase': 'Save Purchase'
            }

            # Submit the edited purchase
            response = requests.post(f'{base_url}/purchases', data=edit_purchase_data)
            print(f"Edit save status: {response.status_code}")

            if response.status_code == 302:  # Redirect indicates success
                print("Purchase edited successfully!")
            else:
                print(f"Edit failed. Response: {response.text[:500]}")

        else:
            print(f"Failed to load edit form. Status: {response.status_code}")

    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == '__main__':
    test_edit_purchase()
