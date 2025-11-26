import mysql.connector
import datetime
import requests

# Test the returns functionality by simulating a POST request
def test_sales_returns():
    print("Testing Sales Returns Frontend...")

    # First, ensure we have a medicine with stock
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='$@&Thak0',
        database='pharmacy_db',
        port=3306
    )
    cursor = conn.cursor(dictionary=True)

    # Get a medicine with stock
    cursor.execute("SELECT id, name, stock_qty, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent FROM medicines WHERE stock_qty > 0 LIMIT 1")
    med = cursor.fetchone()
    if not med:
        print("No medicine with stock found. Adding test medicine...")
        cursor.execute("""
            INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty, purchase_rate, sale_rate)
            VALUES ('Test Medicine', 'TEST001', '2025-12-31', 'HSN001', 10.00, 5.00, 5.00, 10, 8.00, 9.00)
        """)
        med_id = cursor.lastrowid
        med_name = 'Test Medicine'
        initial_stock = 10
        batch_no = 'TEST001'
        expiry_date = '2025-12-31'
        hsn_code = 'HSN001'
        mrp = 10.00
        sgst = 5.00
        cgst = 5.00
    else:
        med_id = med['id']
        med_name = med['name']
        initial_stock = med['stock_qty']
        batch_no = med['batch_no']
        expiry_date = str(med['expiry_date'])
        hsn_code = med['hsn_code']
        mrp = med['mrp']
        sgst = med['sgst_percent']
        cgst = med['cgst_percent']

    print(f"Using medicine: {med_name}, Initial Stock: {initial_stock}")
    print(f"batch_no: {batch_no}, expiry_date: {expiry_date}")

    # Test data for sales return
    test_data = {
        'invoice_no': 'TESTSR001',
        'return_date': '2024-01-15',
        'patient_name': 'Test Patient',
        'rowcount': '1',
        'items-0-product': med_name,
        'items-0-batch_no': batch_no,
        'items-0-expiry_date': expiry_date,
        'items-0-hsn_code': hsn_code,
        'items-0-mrp': str(mrp),
        'items-0-quantity': '2',
        'items-0-rate': '8.00',
        'items-0-sgst_percent': str(sgst),
        'items-0-cgst_percent': str(cgst),
        'items-0-amount': '17.60',
        'grand_total_mrp': '21.00',
        'grand_total_actual': '17.60',
        'savings_total': '3.40',
        'savesalesreturn': '1'
    }

    try:
        # Make POST request to sales-returns endpoint
        response = requests.post('http://localhost:5000/sales-returns', data=test_data, timeout=10)

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            print("✓ Sales return POST request successful")

            # Check if the record was saved in database
            cursor.execute("SELECT COUNT(*) as count FROM sales_returns WHERE invoice_no = 'TESTSR001'")
            sr_count = cursor.fetchone()['count']
            print(f"Sales returns with invoice TESTSR001: {sr_count}")

            if sr_count > 0:
                print("✓ Sales return record saved successfully")

                # Check inventory update (should increase stock)
                cursor.execute("SELECT stock_qty FROM medicines WHERE id = %s", (med_id,))
                updated_stock = cursor.fetchone()['stock_qty']
                expected_stock = initial_stock + 2  # Return 2 items
                print(f"Stock after return: {updated_stock}, Expected: {expected_stock}")

                if updated_stock == expected_stock:
                    print("✓ Inventory updated correctly (stock increased)")
                else:
                    print("✗ Inventory update failed")

                # Check sales return items
                cursor.execute("SELECT COUNT(*) as count FROM sales_return_items WHERE sales_return_id = (SELECT id FROM sales_returns WHERE invoice_no = 'TESTSR001')")
                sri_count = cursor.fetchone()['count']
                print(f"Sales return items count: {sri_count}")

                if sri_count > 0:
                    print("✓ Sales return items saved successfully")
                else:
                    print("✗ Sales return items not saved")

            else:
                print("✗ Sales return record not saved")
                print("Response content:")
                print(response.text[:500])  # First 500 chars

        else:
            print(f"✗ POST request failed with status {response.status_code}")
            print("Response content:")
            print(response.text[:500])

    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")

    # Clean up test data
    try:
        cursor.execute("DELETE FROM sales_return_items WHERE sales_return_id IN (SELECT id FROM sales_returns WHERE invoice_no = 'TESTSR001')")
        cursor.execute("DELETE FROM sales_returns WHERE invoice_no = 'TESTSR001'")
        cursor.execute("UPDATE medicines SET stock_qty = %s WHERE id = %s", (initial_stock, med_id))
        conn.commit()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"Warning: Could not clean up test data: {e}")

    conn.close()

if __name__ == "__main__":
    test_sales_returns()
