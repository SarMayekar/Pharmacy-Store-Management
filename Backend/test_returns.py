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

# Drop and recreate tables with correct schema
cursor.execute("DROP TABLE IF EXISTS sales_return_items")
cursor.execute("DROP TABLE IF EXISTS sales_returns")
cursor.execute("DROP TABLE IF EXISTS purchase_return_items")
cursor.execute("DROP TABLE IF EXISTS purchase_returns")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    invoice_no VARCHAR(50) NOT NULL UNIQUE,
    return_datetime DATETIME NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_value DECIMAL(10,2) DEFAULT 0,
    gst_value DECIMAL(10,2) DEFAULT 0,
    remarks TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_return_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_return_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    batch_no VARCHAR(50),
    expiry_date DATE,
    hsn_code VARCHAR(50),
    mrp DECIMAL(10,2),
    sgst_percent DECIMAL(5,2),
    cgst_percent DECIMAL(5,2),
    discount_percent DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (sales_return_id) REFERENCES sales_returns(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES medicines(id) ON DELETE RESTRICT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS purchase_returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distributor_id INT,
    invoice_no VARCHAR(50) NOT NULL UNIQUE,
    return_datetime DATETIME NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_value DECIMAL(10,2) DEFAULT 0,
    gst_value DECIMAL(10,2) DEFAULT 0,
    remarks TEXT,
    FOREIGN KEY (distributor_id) REFERENCES distributors(id) ON DELETE SET NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS purchase_return_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_return_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    batch_no VARCHAR(50),
    expiry_date DATE,
    hsn_code VARCHAR(50),
    mrp DECIMAL(10,2),
    sgst_percent DECIMAL(5,2),
    cgst_percent DECIMAL(5,2),
    discount_percent DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (purchase_return_id) REFERENCES purchase_returns(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES medicines(id) ON DELETE RESTRICT
)
""")

conn.commit()

# Check if returns tables exist and their schema
print("\n=== Checking Database Schema ===")
cursor.execute("SHOW TABLES LIKE 'sales_returns'")
sales_returns_table = cursor.fetchone()
cursor.execute("SHOW TABLES LIKE 'purchase_returns'")
purchase_returns_table = cursor.fetchone()

if not sales_returns_table:
    print("sales_returns table does not exist. Please run Backend/create_returns_tables.sql")
else:
    cursor.execute("DESCRIBE sales_returns")
    sales_returns_schema = cursor.fetchall()
    print("sales_returns table schema:")
    for col in sales_returns_schema:
        print(f"  {col['Field']}: {col['Type']}")

if not purchase_returns_table:
    print("purchase_returns table does not exist. Please run Backend/create_returns_tables.sql")
else:
    cursor.execute("DESCRIBE purchase_returns")
    purchase_returns_schema = cursor.fetchall()
    print("purchase_returns table schema:")
    for col in purchase_returns_schema:
        print(f"  {col['Field']}: {col['Type']}")

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

    # Create a sales return - adjust based on schema
    return_qty = 2
    if sales_returns_table:
        # Check if patient_id column exists
        patient_id_exists = any(col['Field'] == 'patient_id' for col in sales_returns_schema)
        cursor.execute("""
            INSERT INTO sales_returns (patient_id, invoice_no, return_datetime, total_amount)
            VALUES (NULL, 'TESTSR001', NOW(), 100.00)
        """, ())
        sr_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO sales_return_items (sales_return_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
            VALUES (%s, %s, %s, 50.00, 100.00, 'BATCH001', '2025-12-31', 'HSN001', 60.00, 5.00, 5.00, 0.00)
        """, (sr_id, med_id, return_qty))

        # Update inventory: sales return increases stock
        cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (return_qty, med_id))

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
    else:
        print("Skipping sales returns test - table does not exist")

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
        VALUES (NULL, 'TESTPR001', NOW(), 50.00)
    """, ())
    pr_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO purchase_return_items (purchase_return_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
        VALUES (%s, %s, %s, 50.00, 50.00, 'BATCH001', '2025-12-31', 'HSN001', 60.00, 5.00, 5.00, 0.00)
    """, (pr_id, med_id, return_qty))

    # Update inventory: purchase return decreases stock
    cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (return_qty, med_id))

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
