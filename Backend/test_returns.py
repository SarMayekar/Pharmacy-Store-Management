import mysql.connector
import datetime

# Connect to DB
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)
cursor = conn.cursor(dictionary=True)

print("Testing Returns Functionality...")

# Test Sales Returns
print("\n=== Testing Sales Returns ===")

# Get a medicine with stock
cursor.execute("SELECT id, name, stock_qty FROM medicines WHERE stock_qty > 0 LIMIT 1")
med = cursor.fetchone()
if not med:
    print("No medicine with stock found. Please add some stock first.")
else:
    med_id = med['id']
    med_name = med['name']
    initial_stock = med['stock_qty']
    print(f"Selected medicine: {med_name}, Initial Stock: {initial_stock}")

    # Create a sales return
    return_qty = 2
    cursor.execute("""
        INSERT INTO sales_returns (patient_id, invoice_no, return_datetime, total_amount)
        VALUES (1, 'TESTSR001', NOW(), 100.00)
    """, ())
    sr_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO sales_return_items (sales_return_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
        VALUES (%s, %s, %s, 50.00, 100.00, 'BATCH001', '2025-12-31', 'HSN001', 60.00, 5.00, 5.00, 0.00)
    """, (sr_id, med_id, return_qty))

    # Check stock after return
    cursor.execute("SELECT stock_qty FROM medicines WHERE id = %s", (med_id,))
    updated_stock = cursor.fetchone()['stock_qty']
    expected_stock = initial_stock + return_qty
    print(f"Stock after sales return: {updated_stock}, Expected: {expected_stock}")
    if updated_stock == expected_stock:
        print("✓ Sales return inventory update: PASS")
    else:
        print("✗ Sales return inventory update: FAIL")

    # Clean up test data
    cursor.execute("DELETE FROM sales_return_items WHERE sales_return_id = %s", (sr_id,))
    cursor.execute("DELETE FROM sales_returns WHERE id = %s", (sr_id,))
    cursor.execute("UPDATE medicines SET stock_qty = %s WHERE id = %s", (initial_stock, med_id))

# Test Purchase Returns
print("\n=== Testing Purchase Returns ===")

# Get a medicine with stock
cursor.execute("SELECT id, name, stock_qty FROM medicines WHERE stock_qty > 0 LIMIT 1")
med = cursor.fetchone()
if not med:
    print("No medicine with stock found. Please add some stock first.")
else:
    med_id = med['id']
    med_name = med['name']
    initial_stock = med['stock_qty']
    print(f"Selected medicine: {med_name}, Initial Stock: {initial_stock}")

    # Create a purchase return
    return_qty = 1
    cursor.execute("""
        INSERT INTO purchase_returns (distributor_id, invoice_no, return_datetime, total_amount)
        VALUES (1, 'TESTPR001', NOW(), 50.00)
    """, ())
    pr_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO purchase_return_items (purchase_return_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
        VALUES (%s, %s, %s, 50.00, 50.00, 'BATCH001', '2025-12-31', 'HSN001', 60.00, 5.00, 5.00, 0.00)
    """, (pr_id, med_id, return_qty))

    # Check stock after return
    cursor.execute("SELECT stock_qty FROM medicines WHERE id = %s", (med_id,))
    updated_stock = cursor.fetchone()['stock_qty']
    expected_stock = initial_stock - return_qty
    print(f"Stock after purchase return: {updated_stock}, Expected: {expected_stock}")
    if updated_stock == expected_stock:
        print("✓ Purchase return inventory update: PASS")
    else:
        print("✗ Purchase return inventory update: FAIL")

    # Clean up test data
    cursor.execute("DELETE FROM purchase_return_items WHERE purchase_return_id = %s", (pr_id,))
    cursor.execute("DELETE FROM purchase_returns WHERE id = %s", (pr_id,))
    cursor.execute("UPDATE medicines SET stock_qty = %s WHERE id = %s", (initial_stock, med_id))

conn.commit()
cursor.close()
conn.close()

print("\nReturns testing completed.")
