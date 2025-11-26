import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='$@&Thak0',
        database='pharmacy_db',
        port=3306
    )

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT name, batch_no, expiry_date, purchase_rate, sale_rate, sale_discount_percent, stock_qty FROM medicines WHERE name IN ('MedicineC', 'MedicineD') ORDER BY name")
medicines = cursor.fetchall()

print(f"Total medicines: {len(medicines)}")
for m in medicines:
    print(f"Name: {m['name']}, Batch: {m['batch_no']}, Expiry: {m['expiry_date']}, Purchase Rate: {m['purchase_rate']}, Sale Rate: {m['sale_rate']}, Sale Discount %: {m['sale_discount_percent']}, Stock: {m['stock_qty']}")

cursor.close()
conn.close()
