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

# Get the latest 3 sales invoices
cursor.execute("SELECT invoice_no, sale_datetime FROM sales ORDER BY id DESC LIMIT 3")
invoices = cursor.fetchall()

print("Latest invoice numbers:")
for inv in invoices:
    print(f"Invoice: {inv['invoice_no']}, Date: {inv['sale_datetime']}")

cursor.close()
conn.close()
