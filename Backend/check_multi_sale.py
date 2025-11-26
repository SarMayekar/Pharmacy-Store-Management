import mysql.connector

# Connect to DB
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)
cursor = conn.cursor(dictionary=True)

# Get the latest sale
cursor.execute("SELECT id, invoice_no, total_amount FROM sales ORDER BY id DESC LIMIT 1")
sale = cursor.fetchone()
print(f"Latest Sale: ID {sale['id']}, Invoice {sale['invoice_no']}, Total {sale['total_amount']}")

# Get items for this sale
cursor.execute("SELECT si.*, m.name FROM sales_items si JOIN medicines m ON si.product_id = m.id WHERE si.sale_id = %s", (sale['id'],))
items = cursor.fetchall()
print("Items in sale:")
for item in items:
    print(f"  - {item['name']}: Qty {item['quantity']}, Amount {item['amount']}")

# Check stock updates for items with medicine_id
print("Stock updates:")
for item in items:
    if item['medicine_id']:
        cursor.execute("SELECT name, stock_qty FROM medicines WHERE id = %s", (item['medicine_id'],))
        med = cursor.fetchone()
        if med:
            print(f"  - {med['name']}: Stock now {med['stock_qty']}")
    else:
        print(f"  - {item['name']}: No medicine_id, stock not updated")

cursor.close()
conn.close()
