import requests
import datetime
import mysql.connector
import sys

def log(msg):
    print(msg, flush=True)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='$@&Thak0',
        database='pharmacy_db',
        port=3306
    )

url = 'http://127.0.0.1:5000/purchases'

# Setup: Ensure a medicine exists with OLD rates
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("DELETE FROM medicines WHERE name='TestUpdateMed'")
cursor.execute("""
    INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty, purchase_rate, sale_rate, sale_discount_percent)
    VALUES ('TestUpdateMed', 'B_OLD', '2025-12-31', '1111', 100, 0, 0, 10, 40, 80, 0)
""")
conn.commit()
log("Setup: Created 'TestUpdateMed' with Rate=40, SaleRate=80")

# Test: Add a NEW purchase for the SAME medicine (same batch/expiry for simplicity of matching, or different to test general update?)
# The code matches by name, batch, expiry.
# If I use SAME batch/expiry, it hits the `med_exist` block.
# I want to update the rates even if it's the same batch.
# User said: "inventory should always reflect the most recent purchase and sale rates"

data_update = {
    'invoice_no': 'TEST_UPDATE_001',
    'distributor_name': 'TestDistributor',
    'trade_type': 'Retail',
    'purchase_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rowcount': '1',
    'items-0-product': 'TestUpdateMed',
    'items-0-batch_no': 'B_OLD',
    'items-0-expiry_date': '2025-12-31',
    'items-0-hsn_code': '1111',
    'items-0-mrp': '100',
    'items-0-quantity': '10',
    'items-0-rate': '50',       # NEW Purchase Rate (was 40)
    'items-0-sgst_percent': '0',
    'items-0-cgst_percent': '0',
    'items-0-sale_discount_percent': '10', # NEW Discount (was 0)
    'items-0-sale_rate': '90',  # NEW Sale Rate (was 80)
    'grand_total': '500',
    'savepurchase': '1'
}

log("Testing Update Purchase...")
try:
    response = requests.post(url, data=data_update)
    log(f"Status: {response.status_code}")
except Exception as e:
    log(f"Request failed: {e}")

# Verify DB
cursor.execute("SELECT * FROM medicines WHERE name='TestUpdateMed'")
med = cursor.fetchone()
if med:
    log(f"Med Rates: Purchase={med['purchase_rate']}, Sale={med['sale_rate']}, Discount={med['sale_discount_percent']}")
    if float(med['purchase_rate']) == 50.0 and float(med['sale_rate']) == 90.0 and float(med['sale_discount_percent']) == 10.0:
        log("PASS: Rates updated.")
    else:
        log("FAIL: Rates NOT updated.")
else:
    log("FAIL: Med not found.")

# Cleanup
cursor.execute("DELETE FROM purchase_items WHERE product_id IN (SELECT id FROM medicines WHERE name='TestUpdateMed')")
cursor.execute("DELETE FROM purchases WHERE invoice_no='TEST_UPDATE_001'")
cursor.execute("DELETE FROM medicines WHERE name='TestUpdateMed'")
conn.commit()
cursor.close()
conn.close()
