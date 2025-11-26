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

cursor.execute("SELECT * FROM purchases ORDER BY purchase_date DESC")
purchases = cursor.fetchall()

print(f"Total purchases: {len(purchases)}")
for p in purchases:
    print(f"ID: {p['id']}, Invoice: {p['invoice_no']}, Distributor ID: {p['distributor_id']}, Date: {p['purchase_date']}, Total: {p['total_amount']}")

cursor.close()
conn.close()
