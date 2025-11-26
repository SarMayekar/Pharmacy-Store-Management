import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)

cursor = conn.cursor()

# Add columns to purchase_items
try:
    cursor.execute("ALTER TABLE purchase_items ADD COLUMN sale_rate DECIMAL(10, 2) DEFAULT 0.00;")
    print("Added sale_rate to purchase_items")
except mysql.connector.Error as err:
    print(f"Error adding sale_rate to purchase_items: {err}")

try:
    cursor.execute("ALTER TABLE purchase_items ADD COLUMN sale_discount_percent DECIMAL(5, 2) DEFAULT 0.00;")
    print("Added sale_discount_percent to purchase_items")
except mysql.connector.Error as err:
    print(f"Error adding sale_discount_percent to purchase_items: {err}")

# Add columns to medicines
try:
    cursor.execute("ALTER TABLE medicines ADD COLUMN purchase_rate DECIMAL(10, 2) DEFAULT 0.00;")
    print("Added purchase_rate to medicines")
except mysql.connector.Error as err:
    print(f"Error adding purchase_rate to medicines: {err}")

try:
    cursor.execute("ALTER TABLE medicines ADD COLUMN sale_rate DECIMAL(10, 2) DEFAULT 0.00;")
    print("Added sale_rate to medicines")
except mysql.connector.Error as err:
    print(f"Error adding sale_rate to medicines: {err}")

try:
    cursor.execute("ALTER TABLE medicines ADD COLUMN sale_discount_percent DECIMAL(5, 2) DEFAULT 0.00;")
    print("Added sale_discount_percent to medicines")
except mysql.connector.Error as err:
    print(f"Error adding sale_discount_percent to medicines: {err}")

conn.commit()
cursor.close()
conn.close()
print("Migration completed.")
