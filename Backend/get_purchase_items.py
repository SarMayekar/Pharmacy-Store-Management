import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM purchase_items WHERE purchase_id = 27")
items = cursor.fetchall()
for item in items:
    print(item)
cursor.close()
conn.close()
