import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, name, batch_no, expiry_date FROM medicines WHERE name IN ('MedicineC', 'MedicineD')")
medicines = cursor.fetchall()
for m in medicines:
    print(f"ID: {m['id']}, Name: {m['name']}, Batch: {m['batch_no']}, Expiry: {m['expiry_date']}")
cursor.close()
conn.close()
