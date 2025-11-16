import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='$@&Thak0',
    database='pharmacy_db',
    port=3306
)

cursor = conn.cursor()
cursor.execute("ALTER TABLE sales CHANGE sale_date sale_datetime DATETIME;")
conn.commit()
cursor.close()
conn.close()
print("Table altered successfully.")
