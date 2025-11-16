import os
import mysql.connector
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash

# Paths for Flask template and static folders
project_root = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.abspath(os.path.join(project_root, '../Frontend/templates'))
static_dir = os.path.abspath(os.path.join(project_root, '../Frontend/static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'your_unique_secret_key_here_12345'

# ---------- MySQL DB Connection ----------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='$@&Thak0',
        database='pharmacy_db',
        port=3306
    )

# ---------- ROOT/UTILITY ----------
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # Total number of sales today
    cursor.execute("SELECT COUNT(*) as total_sales FROM sales WHERE DATE(sale_datetime) = %s", (today,))
    total_sales = cursor.fetchone()['total_sales']
    # Total items sold today
    cursor.execute("""
        SELECT COALESCE(SUM(si.quantity), 0) as total_items
        FROM sales_items si
        JOIN sales s ON si.sale_id = s.id
        WHERE DATE(s.sale_datetime) = %s
    """, (today,))
    total_items = cursor.fetchone()['total_items']
    # Total amount of sales today
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total_amount FROM sales WHERE DATE(sale_datetime) = %s", (today,))
    total_amount = cursor.fetchone()['total_amount']
    cursor.close()
    conn.close()
    return render_template('index.html', total_sales=total_sales, total_items=total_items, total_amount=total_amount)

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES;')
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'tables': [table[0] for table in tables]})

# ---------- WEB INTERFACE ----------
@app.route('/sales', methods=['GET', 'POST'])
def sales_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch dropdown data
    cursor.execute("SELECT * FROM patients ORDER BY name;")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM doctors ORDER BY name;")
    doctors = cursor.fetchall()
    cursor.execute("SELECT * FROM medicines ORDER BY name;")
    medicines = cursor.fetchall()

    # Fetch sales history with item counts
    cursor.execute("""
        SELECT s.id, s.invoice_no, s.sale_datetime, s.total_amount, p.name AS patient_name,
               COALESCE(cnt.item_qty, 0) AS item_count
          FROM sales s
          LEFT JOIN patients p ON s.patient_id = p.id
          LEFT JOIN (
            SELECT sale_id, SUM(quantity) AS item_qty
              FROM sales_items
             GROUP BY sale_id
          ) cnt ON cnt.sale_id = s.id
         ORDER BY s.sale_datetime DESC, s.id DESC
    """)
    sales_history = cursor.fetchall()

    def generate_invoice_no():
        today = datetime.datetime.now().strftime('%d%m%y')
        cursor.execute("SELECT COUNT(*) as count FROM sales WHERE DATE(sale_datetime) = CURDATE()")
        data = cursor.fetchone()
        serial = (data['count'] + 1) if data else 1
        return f"{today}{serial:03d}"

    rowcount = 1
    invoice_no = generate_invoice_no()
    sale_date = datetime.datetime.now().strftime('%Y-%m-%d')
    patient_name = doctor_name = grand_total_mrp = grand_total_actual = savings_total = ''
    items = []
    bill_data = None
    show_bill = False

    if request.method == 'POST':
        rowcount = int(request.form.get('rowcount', 1))
        invoice_no = request.form.get('invoice_no') or generate_invoice_no()
        sale_date = request.form.get('sale_date', '') or datetime.datetime.now().strftime('%Y-%m-%d')
        patient_name = request.form.get('patient_name', '').strip()
        patient_contact = request.form.get('patient_contact', '').strip()
        doctor_name = request.form.get('doctor_name', '').strip()
        doctor_contact = request.form.get('doctor_contact', '').strip()
        grand_total_mrp = request.form.get('grand_total_mrp', '')
        grand_total_actual = request.form.get('grand_total_actual', '')
        savings_total = request.form.get('savings_total', '')

        if 'delrow' in request.form:
            del_idx = int(request.form['delrow'])
            items = [
                {
                    'product': request.form.get(f'items-{i}-product', ''),
                    'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                    'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                    'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                    'mrp': request.form.get(f'items-{i}-mrp', ''),
                    'quantity': request.form.get(f'items-{i}-quantity', ''),
                    'rate': request.form.get(f'items-{i}-rate', ''),
                    'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                    'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                    'discount_percent': request.form.get(f'items-{i}-discount_percent', ''),
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(rowcount) if i != del_idx
            ]
            rowcount = max(1, len(items))
            return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                                   rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date,
                                   patient_name=patient_name, doctor_name=doctor_name,
                                   grand_total_mrp=grand_total_mrp, grand_total_actual=grand_total_actual,
                                   savings_total=savings_total, items=items,
                                   show_bill=show_bill, bill_data=bill_data, sales_history=sales_history,
                                   enumerate=enumerate)

        if 'addrow' in request.form:
            items = [
                {
                    'product': request.form.get(f'items-{i}-product', ''),
                    'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                    'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                    'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                    'mrp': request.form.get(f'items-{i}-mrp', ''),
                    'quantity': request.form.get(f'items-{i}-quantity', ''),
                    'rate': request.form.get(f'items-{i}-rate', ''),
                    'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                    'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                    'discount_percent': request.form.get(f'items-{i}-discount_percent', ''),
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(rowcount)
            ]
            rowcount += 1
            items.append({})
            return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                                   rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date,
                                   patient_name=patient_name, doctor_name=doctor_name,
                                   grand_total_mrp=grand_total_mrp, grand_total_actual=grand_total_actual,
                                   savings_total=savings_total, items=items,
                                   show_bill=show_bill, bill_data=bill_data, sales_history=sales_history,
                                   enumerate=enumerate)

        if 'showbill_id' in request.form:
            sale_id = request.form.get('showbill_id')
            cursor.execute("""
                SELECT s.*, p.name as patient_name, d.name as doctor_name
                FROM sales s
                LEFT JOIN patients p ON s.patient_id = p.id
                LEFT JOIN doctors d ON s.doctor_id = d.id
                WHERE s.id = %s
            """, (sale_id,))
            sale = cursor.fetchone()
            cursor.execute("""
                SELECT si.*, m.name
                FROM sales_items si
                JOIN medicines m ON si.product_id = m.id
                WHERE si.sale_id = %s
            """, (sale_id,))
            items_bill = cursor.fetchall()
            bill_data = {'sale': sale, 'items': items_bill}
            show_bill = True
            return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                                   rowcount=1, invoice_no='', sale_date='',
                                   patient_name='', doctor_name='',
                                   grand_total_mrp='', grand_total_actual='',
                                   savings_total='', items=[{}],
                                   show_bill=show_bill, bill_data=bill_data, sales_history=sales_history,
                                   enumerate=enumerate)

        # Delete sale
        elif 'delsale_id' in request.form:
            del_id = int(request.form.get('delsale_id'))
            # First, get the items to restore stock
            cursor.execute("SELECT product_id, quantity FROM sales_items WHERE sale_id=%s", (del_id,))
            items_to_restore = cursor.fetchall()
            for item in items_to_restore:
                cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (item['quantity'], item['product_id']))
            # Delete sales items and sale
            cursor.execute("DELETE FROM sales_items WHERE sale_id=%s", (del_id,))
            cursor.execute("DELETE FROM sales WHERE id=%s", (del_id,))
            conn.commit()
            # Refresh history
            cursor.execute("""
                SELECT s.id, s.invoice_no, s.sale_datetime, s.total_amount, p.name AS patient_name,
                       COALESCE(cnt.item_qty, 0) AS item_count
                  FROM sales s
                  LEFT JOIN patients p ON s.patient_id = p.id
                  LEFT JOIN (
                    SELECT sale_id, SUM(quantity) AS item_qty
                      FROM sales_items
                     GROUP BY sale_id
                  ) cnt ON cnt.sale_id = s.id
                 ORDER BY s.sale_datetime DESC, s.id DESC
            """)
            sales_history = cursor.fetchall()
            return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                                   rowcount=1, invoice_no='', sale_date='',
                                   patient_name='', doctor_name='',
                                   grand_total_mrp='', grand_total_actual='',
                                   savings_total='', items=[{}],
                                   show_bill=False, bill_data=None, sales_history=sales_history,
                                   enumerate=enumerate)

        if 'savesale' in request.form:
            # Validation
            errors = []
            if not patient_name.strip():
                errors.append("Patient name is required.")
            if rowcount == 0:
                errors.append("At least one item is required.")
            valid_items = 0
            for i in range(rowcount):
                prod_name = request.form.get(f'items-{i}-product', '').strip()
                qty = request.form.get(f'items-{i}-quantity', '').strip()
                rate = request.form.get(f'items-{i}-rate', '').strip()
                if prod_name and qty and rate:
                    try:
                        qty_val = int(qty)
                        rate_val = float(rate)
                        if qty_val <= 0 or rate_val <= 0:
                            errors.append(f"Item {i+1}: Quantity and rate must be positive.")
                        else:
                            valid_items += 1
                    except ValueError:
                        errors.append(f"Item {i+1}: Invalid quantity or rate.")
                elif prod_name or qty or rate:
                    errors.append(f"Item {i+1}: Incomplete item data.")
            if valid_items == 0:
                errors.append("At least one complete item is required.")
            if not grand_total_actual.strip():
                errors.append("Grand total is required.")
            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                                       rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date,
                                       patient_name=patient_name, doctor_name=doctor_name,
                                       grand_total_mrp=grand_total_mrp, grand_total_actual=grand_total_actual,
                                       savings_total=savings_total, items=items,
                                       show_bill=show_bill, bill_data=bill_data, sales_history=sales_history,
                                       enumerate=enumerate)

            patient_id = None
            doctor_id = None
            for p in patients:
                if p['name'].strip().lower() == patient_name.lower():
                    patient_id = p['id']
            if not patient_id and patient_name:
                cursor.execute("INSERT INTO patients (name, contact_number) VALUES (%s, %s)", (patient_name, patient_contact))
                patient_id = cursor.lastrowid

            for d in doctors:
                if d['name'].strip().lower() == doctor_name.lower():
                    doctor_id = d['id']
            if not doctor_id and doctor_name:
                cursor.execute("INSERT INTO doctors (name) VALUES (%s)", (doctor_name,))
                doctor_id = cursor.lastrowid

            # Use current datetime for sale_datetime to include time
            sale_datetime = datetime.datetime.now()
            cursor.execute("""
                INSERT INTO sales (patient_id, doctor_id, invoice_no, sale_datetime, discount_value, gst_value, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, invoice_no, sale_datetime, 0, 0, float(grand_total_actual or 0)))
            sale_id = cursor.lastrowid

            total_item_mrp = total_actual_amt = total_savings = 0.0

            for i in range(rowcount):
                prod_name = request.form.get(f'items-{i}-product', '').strip()
                if not prod_name:
                    continue
                batch_no = request.form.get(f'items-{i}-batch_no', '')
                expiry_date = request.form.get(f'items-{i}-expiry_date', None)
                hsn_code = request.form.get(f'items-{i}-hsn_code', '')
                mrp_str = request.form.get(f'items-{i}-mrp', '').strip()
                mrp = float(mrp_str) if mrp_str else 0.0
                qty_str = request.form.get(f'items-{i}-quantity', '').strip()
                qty = int(qty_str) if qty_str else 0
                rate_str = request.form.get(f'items-{i}-rate', '').strip()
                rate = float(rate_str) if rate_str else 0.0
                sgst_str = request.form.get(f'items-{i}-sgst_percent', '').strip()
                sgst = float(sgst_str) if sgst_str else 0.0
                cgst_str = request.form.get(f'items-{i}-cgst_percent', '').strip()
                cgst = float(cgst_str) if cgst_str else 0.0
                dis_str = request.form.get(f'items-{i}-discount_percent', '').strip()
                dis = float(dis_str) if dis_str else 0.0

                amount_input = request.form.get(f'items-{i}-amount', '').strip()
                if amount_input:
                    amount = float(amount_input)
                else:
                    base = qty * rate
                    gst_sgst = base * sgst / 100
                    gst_cgst = base * cgst / 100
                    discount_amt = base * dis / 100
                    amount = base + gst_sgst + gst_cgst - discount_amt

                medicine_id = None
                for m in medicines:
                    if m['name'].strip().lower() == prod_name.lower() and m['batch_no'] == batch_no and str(m['expiry_date']) == str(expiry_date):
                        medicine_id = m['id']

                if not medicine_id and prod_name:
                    cursor.execute("""
                        INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (prod_name, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, 0))
                    medicine_id = cursor.lastrowid

                if medicine_id:
                    cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (qty, medicine_id))

                item_mrp_total = (mrp * qty) + ((mrp*qty)*sgst/100) + ((mrp*qty)*cgst/100)
                total_item_mrp += item_mrp_total
                total_actual_amt += amount
                total_savings += item_mrp_total - amount

                cursor.execute("""
                    INSERT INTO sales_items (sale_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (sale_id, medicine_id, qty, rate, amount, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, dis))

            cursor.execute("UPDATE sales SET total_amount=%s WHERE id=%s", (total_actual_amt, sale_id))
            conn.commit()

            cursor.execute("""
                SELECT s.*, p.name as patient_name, d.name as doctor_name
                FROM sales s
                LEFT JOIN patients p ON s.patient_id = p.id
                LEFT JOIN doctors d ON s.doctor_id = d.id
                WHERE s.id = %s
            """, (sale_id,))
            sale = cursor.fetchone()
            cursor.execute("""
                SELECT si.*, m.name
                FROM sales_items si
                JOIN medicines m ON si.product_id = m.id
                WHERE si.sale_id = %s
            """, (sale_id,))
            items_bill = cursor.fetchall()
            bill_data = {'sale': sale, 'items': items_bill}
            show_bill = True

            rowcount = 1
            invoice_no = generate_invoice_no()
            sale_date = datetime.datetime.now().strftime('%Y-%m-%d')
            patient_name = doctor_name = ''
            grand_total_mrp, grand_total_actual, savings_total = total_item_mrp, total_actual_amt, total_savings
            items = [{}]

    cursor.close()
    conn.close()

    if not items:
        items = [{}]

    return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                           rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date,
                           patient_name=patient_name, doctor_name=doctor_name,
                           grand_total_mrp=grand_total_mrp, grand_total_actual=grand_total_actual,
                           savings_total=savings_total, items=items,
                           show_bill=show_bill, bill_data=bill_data, sales_history=sales_history, enumerate=enumerate)

@app.route('/purchases', methods=['GET', 'POST'])
def purchases_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicines ORDER BY name;")
    medicines = cursor.fetchall()
    cursor.execute("SELECT * FROM distributors ORDER BY name;")
    distributors = cursor.fetchall()

    cursor.execute("""
        SELECT p.id, p.invoice_no, p.purchase_date, d.name as distributor_name, d.trade_type, 
            p.total_amount
        FROM purchases p
        LEFT JOIN distributors d ON p.distributor_id = d.id
        ORDER BY p.purchase_date DESC, p.id DESC;
    """)
    purchases_history = cursor.fetchall()

    rowcount = 1
    invoice_no = purchase_date = datetime.datetime.now().strftime('%Y-%m-%d')
    distributor_name = trade_type = grand_total = ''
    distributor_id = None
    items = []
    show_detail = False
    purchase_detail = None

    if request.method == 'POST':
        rowcount = int(request.form.get('rowcount', 1))
        invoice_no = request.form.get('invoice_no', '')
        purchase_date = request.form.get('purchase_date', '') or ''
        distributor_name = request.form.get('distributor_name', '').strip()
        trade_type = request.form.get('trade_type', '')
        grand_total = request.form.get('grand_total', '')
        
        items = []
        for i in range(rowcount):
            items.append({
                'product': request.form.get(f'items-{i}-product', ''),
                'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                'mrp': request.form.get(f'items-{i}-mrp', ''),
                'quantity': request.form.get(f'items-{i}-quantity', ''),
                'rate': request.form.get(f'items-{i}-rate', ''),
                'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                'discount_percent': request.form.get(f'items-{i}-discount_percent', ''),
                'amount': request.form.get(f'items-{i}-amount', ''),
            })

        # Delete purchase
        if "delpurchase_id" in request.form:
            del_id = int(request.form.get("delpurchase_id"))
            # First, get the items to restore stock
            cursor.execute("SELECT product_id, quantity FROM purchase_items WHERE purchase_id=%s", (del_id,))
            items_to_restore = cursor.fetchall()
            for item in items_to_restore:
                cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (item['quantity'], item['product_id']))
            # Delete purchase items and purchase
            cursor.execute("DELETE FROM purchase_items WHERE purchase_id=%s", (del_id,))
            cursor.execute("DELETE FROM purchases WHERE id=%s", (del_id,))
            conn.commit()
            # Refresh history
            cursor.execute("""
                SELECT p.id, p.invoice_no, p.purchase_date, d.name as distributor_name, d.trade_type,
                    p.total_amount
                FROM purchases p
                LEFT JOIN distributors d ON p.distributor_id = d.id
                ORDER BY p.purchase_date DESC, p.id DESC;
            """)
            purchases_history = cursor.fetchall()
            return render_template('purchases.html', purchases_history=purchases_history, medicines=medicines,
                                  distributors=distributors, rowcount=1, invoice_no='', purchase_date='',
                                  distributor_name='', trade_type='', grand_total='', items=[{}],
                                  show_detail=False, purchase_detail=None)

        # Show detail for purchase
        if "showdetail_id" in request.form:
            show_id = int(request.form.get("showdetail_id"))
            cursor.execute("""
                SELECT p.*, d.name as distributor_name, d.trade_type, d.contact_number
                FROM purchases p
                LEFT JOIN distributors d ON p.distributor_id = d.id
                WHERE p.id = %s
            """, (show_id,))
            purchase = cursor.fetchone()
            cursor.execute("""
                SELECT pi.*, m.name FROM purchase_items pi
                JOIN medicines m ON pi.product_id = m.id
                WHERE pi.purchase_id = %s
            """, (show_id,))
            item_list = cursor.fetchall()
            purchase_detail = {'purchase': purchase, 'items': item_list}
            show_detail = True
            return render_template('purchases.html', purchases_history=purchases_history, medicines=medicines,
                                  distributors=distributors, rowcount=1, invoice_no='', purchase_date='',
                                  distributor_name='', trade_type='', grand_total='', items=[{}],
                                  show_detail=show_detail, purchase_detail=purchase_detail)
            
        # Remove Row
        if "delrow" in request.form:
            del_idx = int(request.form['delrow'])
            items = [item for idx, item in enumerate(items) if idx != del_idx]
            rowcount = max(1, len(items))
            return render_template('purchases.html', purchases_history=purchases_history, medicines=medicines,
                                  distributors=distributors, rowcount=rowcount, invoice_no=invoice_no,
                                  purchase_date=purchase_date, distributor_name=distributor_name,
                                  trade_type=trade_type, grand_total=grand_total, items=items)
        
        # Add Row
        if "addrow" in request.form:
            rowcount += 1
            items.append({})
            return render_template('purchases.html', purchases_history=purchases_history, medicines=medicines,
                                  distributors=distributors, rowcount=rowcount, invoice_no=invoice_no,
                                  purchase_date=purchase_date, distributor_name=distributor_name,
                                  trade_type=trade_type, grand_total=grand_total, items=items)
        
        # Save Purchase
        if "savepurchase" in request.form:
            distributor_id = None
            for d in distributors:
                if d['name'].strip().lower() == distributor_name.lower() and d['trade_type'] == trade_type:
                    distributor_id = d['id']
            if not distributor_id and distributor_name:
                cursor.execute(
                    "INSERT INTO distributors (name, trade_type) VALUES (%s, %s)",
                    (distributor_name, trade_type or "Retail")
                )
                distributor_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO purchases (distributor_id, invoice_no, purchase_date, total_amount, gst_value, discount_value, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (distributor_id, invoice_no, purchase_date, float(grand_total or 0), 0, 0, ''))
            purchase_id = cursor.lastrowid

            for idx, row in enumerate(items):
                prod_name = row['product'].strip()
                if not prod_name:
                    continue
                batch_no = row['batch_no'] or ''
                expiry = row['expiry_date'] or None
                hsn = row['hsn_code'] or ''
                mrp = float(row['mrp'] or 0)
                qty = int(row['quantity'] or 0)
                rate = float(row['rate'] or 0)
                sgst = float(row['sgst_percent'] or 0)
                cgst = float(row['cgst_percent'] or 0)
                discount = float(row['discount_percent'] or 0)
                amount_input = row.get('amount', '').strip()
                if amount_input:
                    amount = float(amount_input)
                else:
                    base = qty * rate
                    gst_sgst = base * sgst / 100
                    gst_cgst = base * cgst / 100
                    discount_amt = base * discount / 100
                    amount = base + gst_sgst + gst_cgst - discount_amt

                medicine_id = None
                cursor.execute(
                    "SELECT id FROM medicines WHERE name=%s AND batch_no=%s AND expiry_date=%s LIMIT 1",
                    (prod_name, batch_no, expiry)
                )
                med_exist = cursor.fetchone()
                if med_exist:
                    medicine_id = med_exist['id']
                    cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (qty, medicine_id))
                else:
                    cursor.execute("""
                        INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (prod_name, batch_no, expiry, hsn, mrp, sgst, cgst, qty))
                    medicine_id = cursor.lastrowid

                if medicine_id:
                    cursor.execute("""
                        INSERT INTO purchase_items (purchase_id, product_id, sr_no, hsn_code, batch_no, expiry_date, quantity, mrp, rate, sgst_percent, cgst_percent, discount_percent, amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (purchase_id, medicine_id, idx + 1, hsn, batch_no, expiry, qty, mrp, rate, sgst, cgst, discount, amount))

            conn.commit()
            flash("Purchase saved successfully.", "success")
            return redirect(url_for('purchases_view'))

    cursor.close()
    conn.close()
    if not items:
        items = [{}]
    return render_template('purchases.html', purchases_history=purchases_history, medicines=medicines,
                          distributors=distributors, rowcount=rowcount, invoice_no=invoice_no,
                          purchase_date=purchase_date, distributor_name=distributor_name,
                          trade_type=trade_type, grand_total=grand_total, items=items,
                          show_detail=show_detail, purchase_detail=purchase_detail)

@app.route('/medicines', methods=['GET', 'POST'])
def medicines_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Delete medicine
    if request.method == 'POST' and "delmedicine_id" in request.form:
        mid = int(request.form.get('delmedicine_id'))
        # Check for sales or purchases
        cursor.execute("SELECT COUNT(*) as cnt FROM sales_items WHERE product_id=%s", (mid,))
        sales_cnt = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM purchase_items WHERE product_id=%s", (mid,))
        purch_cnt = cursor.fetchone()['cnt']
        if sales_cnt > 0 or purch_cnt > 0:
            flash("Cannot delete medicine: linked to sales/purchases.", "danger")
        else:
            cursor.execute("DELETE FROM medicines WHERE id=%s", (mid,))
            conn.commit()

    # Add new medicine
    if request.method == 'POST' and "addmedicine" in request.form:
        name = request.form.get("name", "").strip()
        hsn_code = request.form.get("hsn_code", "")
        batch_no = request.form.get("batch_no", "")
        expiry_date = request.form.get("expiry_date", "")
        mrp = float(request.form.get("mrp") or 0)
        price = float(request.form.get("price") or 0)
        purchase_price = float(request.form.get("purchase_price") or 0)
        stock_qty = int(request.form.get("stock_qty") or 0)
        sgst_percent = float(request.form.get("sgst_percent") or 0)
        cgst_percent = float(request.form.get("cgst_percent") or 0)
        supplier_name = request.form.get("supplier_name", "")
        supplier_contact = request.form.get("supplier_contact", "")

        cursor.execute("""
            INSERT INTO medicines (name, hsn_code, batch_no, expiry_date, mrp, price, purchase_price, stock_qty,
                                   sgst_percent, cgst_percent, supplier_name, supplier_contact)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, hsn_code, batch_no, expiry_date, mrp, price, purchase_price, stock_qty, sgst_percent, cgst_percent, supplier_name, supplier_contact))
        conn.commit()

    # Fetch all inventory
    cursor.execute("""
        SELECT * FROM medicines
        ORDER BY name, batch_no, expiry_date
    """)
    medicines = cursor.fetchall()

    # View medicine sales/purchases history: separate button triggers
    show_sales = show_purchases = False
    sales_history = purchases_history = []
    medicine_detail = None

    if request.method == 'POST' and "view_sales_id" in request.form:
        mid = int(request.form.get('view_sales_id'))
        cursor.execute("SELECT name FROM medicines WHERE id=%s", (mid,))
        med = cursor.fetchone()
        if med:
            name = med['name']
            cursor.execute("SELECT * FROM medicines WHERE id=%s", (mid,))
            medicine_detail = cursor.fetchone()
            show_sales = True
            cursor.execute("""
                SELECT m.batch_no, m.expiry_date, SUM(si.quantity) as total_quantity, SUM(si.amount) as total_amount, COUNT(DISTINCT s.id) as num_sales
                FROM sales_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN medicines m ON si.product_id = m.id
                WHERE m.name = %s
                GROUP BY m.batch_no, m.expiry_date
                ORDER BY m.expiry_date DESC
            """, (name,))
            sales_history = cursor.fetchall()

    if request.method == 'POST' and "view_purchases_id" in request.form:
        mid = int(request.form.get('view_purchases_id'))
        cursor.execute("SELECT name FROM medicines WHERE id=%s", (mid,))
        med = cursor.fetchone()
        if med:
            name = med['name']
            cursor.execute("SELECT * FROM medicines WHERE id=%s", (mid,))
            medicine_detail = cursor.fetchone()
            show_purchases = True
            cursor.execute("""
                SELECT pu.invoice_no, pu.purchase_date, pi.quantity, pi.amount, d.name as distributor_name, m.batch_no, m.expiry_date
                FROM purchase_items pi
                JOIN purchases pu ON pi.purchase_id = pu.id
                LEFT JOIN distributors d ON pu.distributor_id = d.id
                JOIN medicines m ON pi.product_id = m.id
                WHERE m.name = %s
                ORDER BY pu.purchase_date DESC
            """, (name,))
            purchases_history = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('medicines.html', medicines=medicines,
                           show_sales=show_sales, sales_history=sales_history,
                           show_purchases=show_purchases, purchases_history=purchases_history,
                           medicine_detail=medicine_detail)

@app.route('/patients', methods=['GET', 'POST'])
def patients_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all patients in DB
    cursor.execute("SELECT * FROM patients ORDER BY name;")
    patients = cursor.fetchall()

    # To handle editing existing patient or viewing sale history
    editing_patient = None
    show_history = False
    sale_history = []

    if request.method == 'POST':
        # Add new patient
        if 'addpatient' in request.form:
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            address = request.form.get('address', '').strip()
            if name:
                cursor.execute("""
                    INSERT INTO patients (name, contact_number, medical_history_notes)
                    VALUES (%s, %s, %s)
                """, (name, contact_number, address))
                conn.commit()

        # Edit patient
        elif 'editpatient_id' in request.form:
            edit_id = int(request.form['editpatient_id'])
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            address = request.form.get('address', '').strip()
            cursor.execute("""
                UPDATE patients SET name=%s, contact_number=%s, medical_history_notes=%s WHERE id=%s
            """, (name, contact_number, address, edit_id))
            conn.commit()

        # Start editing show form
        elif 'startedit_id' in request.form:
            edit_id = int(request.form['startedit_id'])
            cursor.execute("SELECT * FROM patients WHERE id=%s", (edit_id,))
            editing_patient = cursor.fetchone()

        # Show patient records (sales history)
        elif 'viewpurchase_id' in request.form:
            pid = int(request.form['viewpurchase_id'])
            cursor.execute("""
                SELECT s.id as id, s.invoice_no, s.sale_datetime, s.total_amount, COALESCE(SUM(si.quantity), 0) as item_count
                FROM sales s
                LEFT JOIN sales_items si ON s.id = si.sale_id
                WHERE s.patient_id = %s
                GROUP BY s.id, s.invoice_no, s.sale_datetime, s.total_amount
                ORDER BY s.sale_datetime DESC
            """, (pid,))
            sale_history = cursor.fetchall()
            show_history = True

        # Delete patient
        elif 'delpatient_id' in request.form:
            del_id = int(request.form.get('delpatient_id'))
            # Check for sales existence
            cursor.execute("SELECT COUNT(*) as count FROM sales WHERE patient_id=%s", (del_id,))
            sales_count = cursor.fetchone()['count']
            if sales_count > 0:
                # Show error, flash message, or handle gracefully (not deleting)
                flash("Cannot delete patient: sales records exist.", "danger")
            else:
                # Safe to delete
                cursor.execute("DELETE FROM patients WHERE id=%s", (del_id,))
                conn.commit()

        # Refresh list of patients after any operation
        cursor.execute("SELECT * FROM patients ORDER BY name;")
        patients = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('patients.html', patients=patients, editing_patient=editing_patient,
                           show_history=show_history, sale_history=sale_history)

@app.route('/doctors', methods=['GET', 'POST'])
def doctors_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all doctors
    cursor.execute("SELECT * FROM doctors ORDER BY name;")
    doctors = cursor.fetchall()

    editing_doctor = None
    show_history = False
    sale_history = []
    doctor_detail = None

    if request.method == 'POST':
        # Add new doctor
        if 'adddoctor' in request.form:
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            address = request.form.get('address', '').strip()
            if name:
                cursor.execute("""
                    INSERT INTO doctors (name, contact_number, address)
                    VALUES (%s, %s, %s)
                """, (name, contact_number, address))
                conn.commit()

        # Edit doctor
        elif 'editdoctor' in request.form:
            edit_id = int(request.form['editdoctor_id'])
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            address = request.form.get('address', '').strip()
            cursor.execute("""
                UPDATE doctors SET name=%s, contact_number=%s, address=%s WHERE id=%s
            """, (name, contact_number, address, edit_id))
            conn.commit()

        # Start edit
        elif 'startedit_id' in request.form:
            edit_id = int(request.form['startedit_id'])
            cursor.execute("SELECT * FROM doctors WHERE id=%s", (edit_id,))
            editing_doctor = cursor.fetchone()

        # View sales history for doctor
        elif 'viewsales_id' in request.form:
            did = int(request.form['viewsales_id'])
            cursor.execute("SELECT * FROM doctors WHERE id=%s", (did,))
            doctor_detail = cursor.fetchone()
            show_history = True
            cursor.execute("""
                SELECT s.invoice_no, s.sale_datetime, p.name as patient_name, s.total_amount
                FROM sales s
                LEFT JOIN patients p ON s.patient_id = p.id
                WHERE s.doctor_id = %s
                ORDER BY s.sale_datetime DESC
            """, (did,))
            sale_history = cursor.fetchall()

        # Delete sale
        elif 'delsale_id' in request.form:
            del_id = int(request.form.get('delsale_id'))
            # Get the doctor_id from the sale
            cursor.execute("SELECT doctor_id FROM sales WHERE id=%s", (del_id,))
            sale = cursor.fetchone()
            if sale:
                doctor_id = sale['doctor_id']
                # First, get the items to restore stock
                cursor.execute("SELECT product_id, quantity FROM sales_items WHERE sale_id=%s", (del_id,))
                items_to_restore = cursor.fetchall()
                for item in items_to_restore:
                    cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (item['quantity'], item['product_id']))
                # Delete sales items and sale
                cursor.execute("DELETE FROM sales_items WHERE sale_id=%s", (del_id,))
                cursor.execute("DELETE FROM sales WHERE id=%s", (del_id,))
                conn.commit()
                # Refresh history for the doctor
                cursor.execute("SELECT * FROM doctors WHERE id=%s", (doctor_id,))
                doctor_detail = cursor.fetchone()
                show_history = True
                cursor.execute("""
                    SELECT s.invoice_no, s.sale_datetime, p.name as patient_name, s.total_amount
                    FROM sales s
                    LEFT JOIN patients p ON s.patient_id = p.id
                    WHERE s.doctor_id = %s
                    ORDER BY s.sale_datetime DESC
                """, (doctor_id,))
                sale_history = cursor.fetchall()
                return render_template('doctors.html', doctors=doctors, editing_doctor=editing_doctor,
                                       show_history=show_history, sale_history=sale_history, doctor_detail=doctor_detail)

        # Delete doctor (add your constraint checks as needed)
        elif 'deldoctor_id' in request.form:
            del_id = int(request.form.get('deldoctor_id'))
            try:
                # Check if doctor has sales
                cursor.execute("SELECT COUNT(*) as cnt FROM sales WHERE doctor_id=%s", (del_id,))
                if cursor.fetchone()['cnt'] > 0:
                    flash("Cannot delete doctor: sales records exist.", "danger")
                else:
                    cursor.execute("DELETE FROM doctors WHERE id=%s", (del_id,))
                    conn.commit()
            except Exception as e:
                pass

        # Refresh after any action
        cursor.execute("SELECT * FROM doctors ORDER BY name;")
        doctors = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('doctors.html', doctors=doctors, editing_doctor=editing_doctor,
                           show_history=show_history, sale_history=sale_history, doctor_detail=doctor_detail)

@app.route('/bill/<int:sale_id>')
def bill_view(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, p.name as patient_name, d.name as doctor_name
        FROM sales s
        LEFT JOIN patients p ON s.patient_id = p.id
        LEFT JOIN doctors d ON s.doctor_id = d.id
        WHERE s.id = %s
    """, (sale_id,))
    sale = cursor.fetchone()
    if not sale:
        return "Bill not found", 404
    cursor.execute("""
        SELECT si.*, m.name
        FROM sales_items si
        JOIN medicines m ON si.product_id = m.id
        WHERE si.sale_id = %s
    """, (sale_id,))
    items = cursor.fetchall()

    # Calculate MRP total and savings
    mrp_total = sum((item['mrp'] or 0) * item['quantity'] for item in items)
    actual_total = sum(item['amount'] for item in items)
    savings = mrp_total - actual_total

    cursor.close()
    conn.close()
    return render_template('bill.html', sale=sale, items=items, mrp_total=mrp_total, savings=savings, enumerate=enumerate)

@app.route('/distributors', methods=['GET', 'POST'])
def distributors_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all distributors
    cursor.execute("SELECT * FROM distributors ORDER BY name;")
    distributors = cursor.fetchall()

    editing_distributor = None
    show_history = False
    purchase_history = []
    distributor_detail = None

    if request.method == 'POST':
        # Add new distributor
        if 'adddistributor' in request.form:
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            trade_type = request.form.get('trade_type', 'Retail')
            if name:
                cursor.execute("""
                    INSERT INTO distributors (name, contact_number, trade_type)
                    VALUES (%s, %s, %s)
                """, (name, contact_number, trade_type))
                conn.commit()

        # Edit distributor
        elif 'editdistributor' in request.form:
            edit_id = int(request.form['editdistributor_id'])
            name = request.form.get('name', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            trade_type = request.form.get('trade_type', 'Retail')
            cursor.execute("""
                UPDATE distributors SET name=%s, contact_number=%s, trade_type=%s WHERE id=%s
            """, (name, contact_number, trade_type, edit_id))
            conn.commit()

        # Start edit
        elif 'startedit_id' in request.form:
            edit_id = int(request.form['startedit_id'])
            cursor.execute("SELECT * FROM distributors WHERE id=%s", (edit_id,))
            editing_distributor = cursor.fetchone()

        # View purchase history for distributor
        elif 'viewpurchases_id' in request.form:
            did = int(request.form['viewpurchases_id'])
            cursor.execute("SELECT * FROM distributors WHERE id=%s", (did,))
            distributor_detail = cursor.fetchone()
            show_history = True
            cursor.execute("""
                SELECT * FROM purchases
                WHERE distributor_id = %s
                ORDER BY purchase_date DESC
            """, (did,))
            purchase_history = cursor.fetchall()

        # Delete distributor (do not allow delete if linked purchases exist)
        elif 'deldistributor_id' in request.form:
            del_id = int(request.form.get('deldistributor_id'))
            try:
                cursor.execute("SELECT COUNT(*) AS cnt FROM purchases WHERE distributor_id=%s", (del_id,))
                if cursor.fetchone()['cnt'] > 0:
                    # Optional: flash a message
                    pass
                else:
                    cursor.execute("DELETE FROM distributors WHERE id=%s", (del_id,))
                    conn.commit()
            except Exception as e:
                pass

        # Refresh distributor list after any operation
        cursor.execute("SELECT * FROM distributors ORDER BY name;")
        distributors = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('distributors.html', distributors=distributors, editing_distributor=editing_distributor,
                           show_history=show_history, purchase_history=purchase_history,
                           distributor_detail=distributor_detail)

# ---------- API Endpoints for Autofill ----------
@app.route('/api/medicine/<name>')
def get_medicine_details(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT batch_no, DATE_FORMAT(expiry_date, '%Y-%m-%d') as expiry_date, hsn_code, mrp, sgst_percent, cgst_percent FROM medicines WHERE name = %s ORDER BY expiry_date DESC", (name,))
    meds = cursor.fetchall()
    conn.close()
    return jsonify(meds)

@app.route('/api/distributor/<name>')
def get_distributor_details(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT trade_type, contact_number FROM distributors WHERE name = %s", (name,))
    dist = cursor.fetchone()
    conn.close()
    return jsonify(dist or {})

@app.route('/api/patient/<name>')
def get_patient_details(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT contact_number FROM patients WHERE name = %s", (name,))
    pat = cursor.fetchone()
    conn.close()
    return jsonify(pat or {})

@app.route('/api/doctor/<name>')
def get_doctor_details(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT contact_number FROM doctors WHERE name = %s", (name,))
    doc = cursor.fetchone()
    conn.close()
    return jsonify(doc or {})

if __name__ == '__main__':
    app.run(debug=True)
