import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)

cursor = conn.cursor()
cursor.execute("DESCRIBE sales;")
columns = cursor.fetchall()
for col in columns:
    print(col)
cursor.close()
conn.close()
