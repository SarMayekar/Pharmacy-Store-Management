import requests
import datetime
import mysql.connector
import sys

# DB Connection to verify
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='$@&Thak0',
        database='pharmacy_db',
        port=3306
    )

url = 'http://127.0.0.1:5000/purchases'

def log(msg):
    print(msg, flush=True)

# 1. Add Branded Purchase
data_branded = {
    'invoice_no': 'TEST_BRANDED_002',
    'distributor_name': 'TestDistributor',
    'trade_type': 'Retail',
    'purchase_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '1',
    'items-0-product': 'TestBrandedMed',
    'items-0-batch_no': 'B002',
    'items-0-expiry_date': '2026-01-01',
    'items-0-hsn_code': '1234',
    'items-0-mrp': '100',
    'items-0-quantity': '10',
    'items-0-rate': '50',
    'items-0-sgst_percent': '0',
    'items-0-cgst_percent': '0',
    'items-0-sale_discount_percent': '10',
    'items-0-sale_rate': '90', 
    'grand_total': '500',
    'savepurchase': '1'
}

log("Testing Branded Purchase...")
try:
    response = requests.post(url, data=data_branded)
    log(f"Branded Status: {response.status_code}")
    if response.status_code != 200 and response.status_code != 302:
        log(f"Branded Response: {response.text}")
except Exception as e:
    log(f"Branded Request failed: {e}")

# 2. Add Generic Purchase
data_generic = {
    'invoice_no': 'TEST_GENERIC_002',
    'distributor_name': 'TestDistributor',
    'trade_type': 'Retail',
    'purchase_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '1',
    'items-0-product': 'TestGenericMed',
    'items-0-batch_no': 'G002',
    'items-0-expiry_date': '2026-01-01',
    'items-0-hsn_code': '5678',
    'items-0-mrp': '100',
    'items-0-quantity': '10',
    'items-0-rate': '40',
    'items-0-sgst_percent': '0',
    'items-0-cgst_percent': '0',
    'items-0-sale_discount_percent': '0',
    'items-0-sale_rate': '80', 
    'grand_total': '400',
    'savepurchase': '1'
}

log("Testing Generic Purchase...")
try:
    response = requests.post(url, data=data_generic)
    log(f"Generic Status: {response.status_code}")
    if response.status_code != 200 and response.status_code != 302:
        log(f"Generic Response: {response.text}")
except Exception as e:
    log(f"Generic Request failed: {e}")

# Verify DB
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

# Check Branded
cursor.execute("SELECT * FROM medicines WHERE name='TestBrandedMed'")
med = cursor.fetchone()
if med:
    log(f"Branded Med: Sale Rate={med['sale_rate']}, Discount={med['sale_discount_percent']}")
    if float(med['sale_rate']) == 90.0 and float(med['sale_discount_percent']) == 10.0:
        log("PASS: Branded Sale Rate Correct.")
    else:
        log("FAIL: Branded Sale Rate Incorrect.")
else:
    log("FAIL: Branded Med not found.")

# Check Generic
cursor.execute("SELECT * FROM medicines WHERE name='TestGenericMed'")
med = cursor.fetchone()
if med:
    log(f"Generic Med: Sale Rate={med['sale_rate']}, Discount={med['sale_discount_percent']}")
    if float(med['sale_rate']) == 80.0 and float(med['sale_discount_percent']) == 0.0:
        log("PASS: Generic Sale Rate Correct.")
    else:
        log("FAIL: Generic Sale Rate Incorrect.")
else:
    log("FAIL: Generic Med not found.")

# Cleanup
log("Cleaning up...")
cursor.execute("DELETE FROM purchase_items WHERE product_id IN (SELECT id FROM medicines WHERE name IN ('TestBrandedMed', 'TestGenericMed'))")
cursor.execute("DELETE FROM purchases WHERE invoice_no IN ('TEST_BRANDED_002', 'TEST_GENERIC_002')")
cursor.execute("DELETE FROM medicines WHERE name IN ('TestBrandedMed', 'TestGenericMed')")
conn.commit()
cursor.close()
conn.close()
log("Done.")
