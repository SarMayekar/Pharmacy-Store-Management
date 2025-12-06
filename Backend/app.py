import os
import sys
import datetime
import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash

# Minimal, clean copy of backend app for iterative reconstruction.
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    template_dir = os.path.join(base_path, 'templates')
    static_dir = os.path.join(base_path, 'static')
else:
    base_path = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_path, '..', 'Frontend', 'templates')
    static_dir = os.path.join(base_path, '..', 'Frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'your_unique_secret_key_here_12345'


def get_db_connection():
    return mysql.connector.connect(host='localhost', user='root', password='$@&Thak0', database='pharmacy_db', port=3306)


@app.route('/')
def home():
    return render_template('index.html') if os.path.isdir(template_dir) else 'Pharmacy Backend (fixed)'


@app.route('/test')
def test():
    return 'Server is working!'


@app.route('/api/medicine')
def api_medicine():
    q = request.args.get('q', '').strip()
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    try:
        if q:
            like = f"%{q}%"
            cur.execute("SELECT id,name,batch_no,expiry_date,hsn_code,mrp,sgst_percent,cgst_percent,packing FROM medicines WHERE name LIKE %s OR batch_no LIKE %s ORDER BY name LIMIT 50", (like, like))
        else:
            cur.execute("SELECT id,name,batch_no,expiry_date,hsn_code,mrp,sgst_percent,cgst_percent,packing FROM medicines ORDER BY name LIMIT 100")
        rows = cur.fetchall(); return jsonify(rows)
    finally:
        cur.close(); conn.close()


@app.route('/api/distributor')
def api_distributor():
    q = request.args.get('q', '').strip()
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    try:
        if q:
            like = f"%{q}%"
            cur.execute("SELECT id,name,contact_number FROM distributors WHERE name LIKE %s ORDER BY name LIMIT 50", (like,))
        else:
            cur.execute("SELECT id,name,contact_number FROM distributors ORDER BY name LIMIT 100")
        rows = cur.fetchall(); return jsonify(rows)
    finally:
        cur.close(); conn.close()


@app.route('/api/patient')
def api_patient():
    q = request.args.get('q', '').strip()
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    try:
        if q:
            like = f"%{q}%"
            cur.execute("SELECT id,name,contact_number FROM patients WHERE name LIKE %s ORDER BY name LIMIT 50", (like,))
        else:
            cur.execute("SELECT id,name,contact_number FROM patients ORDER BY name LIMIT 100")
        rows = cur.fetchall(); return jsonify(rows)
    finally:
        cur.close(); conn.close()


@app.route('/api/doctor')
def api_doctor():
    q = request.args.get('q', '').strip()
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    try:
        if q:
            like = f"%{q}%"
            cur.execute("SELECT id, name, contact_number FROM doctors WHERE name LIKE %s ORDER BY name LIMIT 50", (like,))
        else:
            cur.execute("SELECT id, name, contact_number FROM doctors ORDER BY name LIMIT 100")
        rows = cur.fetchall()
        return jsonify([{'id': r.get('id'), 'name': r.get('name'), 'contact_number': r.get('contact_number')} for r in rows])
    finally:
        cur.close()
        conn.close()


# Placeholder views so templates can be served until full logic is reconstructed
@app.route('/sales')
def sales_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Load helpers and master data
        cursor.execute("SELECT * FROM patients ORDER BY name;")
        patients = cursor.fetchall()
        cursor.execute("SELECT * FROM doctors ORDER BY name;")
        doctors = cursor.fetchall()
        cursor.execute("SELECT * FROM medicines ORDER BY name;")
        medicines = cursor.fetchall()

        # sales history with item counts
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
            today = datetime.datetime.now().strftime('%y%m%d')
            cursor.execute("SELECT MAX(CAST(RIGHT(invoice_no, 3) AS UNSIGNED)) as max_serial FROM sales WHERE LEFT(invoice_no, 6) = %s", (today,))
            data = cursor.fetchone()
            serial = (data['max_serial'] + 1) if data and data.get('max_serial') else 1
            return f"{today}{serial:03d}"

        rowcount = 1
        invoice_no = generate_invoice_no()
        sale_date = datetime.datetime.now().strftime('%Y-%m-%d')
        patient_name = doctor_name = ''
        grand_total_mrp = grand_total_actual = savings_total = ''
        items = []
        bill_data = None
        show_bill = False

        if request.method == 'POST':
            # handle add/del rows and edit commands
            if 'addrow' in request.form:
                rowcount = int(request.form.get('rowcount', 1)) + 1
                items = [{} for _ in range(rowcount)]
                return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines, rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date, items=items, sales_history=sales_history)

            if 'delrow' in request.form:
                del_idx = int(request.form.get('delrow'))
                rowcount = int(request.form.get('rowcount', 1))
                items = []
                for i in range(rowcount):
                    if i == del_idx:
                        continue
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
                        'amount': request.form.get(f'items-{i}-amount', ''),
                    })
                rowcount = max(1, len(items))
                return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines, rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date, items=items, sales_history=sales_history)

            # Start edit flow: populate form with existing sale
            if 'startedit_sale_id' in request.form:
                edit_id = int(request.form.get('startedit_sale_id'))
                cursor.execute("""
                    SELECT s.*, p.name as patient_name, p.contact_number as patient_contact, d.name as doctor_name, d.contact_number as doctor_contact
                    FROM sales s
                    LEFT JOIN patients p ON s.patient_id = p.id
                    LEFT JOIN doctors d ON s.doctor_id = d.id
                    WHERE s.id = %s
                """, (edit_id,))
                editing_sale = cursor.fetchone()
                cursor.execute("""
                    SELECT si.*, m.name as product, m.packing FROM sales_items si
                    JOIN medicines m ON si.product_id = m.id
                    WHERE si.sale_id = %s
                """, (edit_id,))
                item_list = cursor.fetchall()
                items = []
                for item in item_list:
                    gst_percent = (item.get('sgst_percent') or 0) + (item.get('cgst_percent') or 0)
                    items.append({
                        'product': item.get('product'),
                        'batch_no': item.get('batch_no'),
                        'expiry_date': item.get('expiry_date'),
                        'hsn_code': item.get('hsn_code'),
                        'mrp': item.get('mrp'),
                        'quantity': item.get('quantity'),
                        'rate': item.get('price'),
                        'gst_percent': gst_percent,
                        'discount_percent': item.get('discount_percent', ''),
                        'amount': item.get('amount'),
                        'packing': item.get('packing', ''),
                    })
                rowcount = len(items) if items else 1
                return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines, rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date, items=items, sales_history=sales_history)

            # Save sale (new or edit)
            if 'savesale' in request.form:
                try:
                    edit_sale_id = request.form.get('edit_sale_id')
                    rowcount = int(request.form.get('rowcount', 1))
                    invoice_no = request.form.get('invoice_no') or generate_invoice_no()
                    sale_date = request.form.get('sale_date', '') or datetime.datetime.now().strftime('%Y-%m-%d')
                    patient_name = request.form.get('patient_name', '').strip()
                    doctor_name = request.form.get('doctor_name', '').strip()

                    # Resolve or create patient/doctor
                    patient_id = None
                    for p in patients:
                        if p.get('name', '').strip().lower() == patient_name.lower():
                            patient_id = p.get('id')
                            break
                    if not patient_id and patient_name:
                        cursor.execute("INSERT INTO patients (name) VALUES (%s)", (patient_name,))
                        patient_id = cursor.lastrowid

                    doctor_id = None
                    for d in doctors:
                        if d.get('name', '').strip().lower() == doctor_name.lower():
                            doctor_id = d.get('id')
                            break
                    if not doctor_id and doctor_name:
                        cursor.execute("INSERT INTO doctors (name) VALUES (%s)", (doctor_name,))
                        doctor_id = cursor.lastrowid

                    grand_total_actual = request.form.get('grand_total_actual', '0')

                    if edit_sale_id:
                        sale_id = int(edit_sale_id)
                        # restore stock from old items
                        cursor.execute("SELECT product_id, quantity FROM sales_items WHERE sale_id=%s", (sale_id,))
                        items_to_restore = cursor.fetchall()
                        for item in items_to_restore:
                            cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (item.get('quantity'), item.get('product_id')))
                        cursor.execute("DELETE FROM sales_items WHERE sale_id=%s", (sale_id,))
                        cursor.execute("""
                            UPDATE sales SET patient_id=%s, doctor_id=%s, invoice_no=%s, sale_datetime=%s, total_amount=%s
                            WHERE id=%s
                        """, (patient_id, doctor_id, invoice_no, datetime.datetime.now(), float(grand_total_actual or 0), sale_id))
                    else:
                        cursor.execute("""
                            INSERT INTO sales (patient_id, doctor_id, invoice_no, sale_datetime, discount_value, gst_value, total_amount)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (patient_id, doctor_id, invoice_no, datetime.datetime.now(), 0, 0, float(grand_total_actual or 0)))
                        sale_id = cursor.lastrowid

                    total_item_mrp = total_actual_amt = total_savings = 0.0
                    for i in range(rowcount):
                        prod_name = request.form.get(f'items-{i}-product', '').strip()
                        if not prod_name:
                            continue
                        batch_no = request.form.get(f'items-{i}-batch_no', '')
                        expiry_date = request.form.get(f'items-{i}-expiry_date', None)
                        packing = request.form.get(f'items-{i}-packing', '')
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
                            discount_amt = base * dis / 100
                            amount = base - discount_amt

                        medicine_id = None
                        for m in medicines:
                            if m.get('name','').strip().lower() == prod_name.lower() and m.get('batch_no') == batch_no and str(m.get('expiry_date')) == str(expiry_date) and str(m.get('packing') or '') == str(packing or ''):
                                medicine_id = m.get('id')

                        if not medicine_id and prod_name:
                            cursor.execute("""
                                INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty, packing)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (prod_name, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, 0, packing))
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

                    cursor.execute("UPDATE sales SET total_amount=%s WHERE id=%s", (float(grand_total_actual or 0), sale_id))
                    conn.commit()
                    flash("Sale saved successfully", "success")
                except Exception as e:
                    conn.rollback()
                    flash(f"Error saving sale: {e}", "danger")

        # For GET or after POST handling, prepare defaults
        rowcount = rowcount or 1
        if not items:
            items = [{}]
        return render_template('sales.html', patients=patients, doctors=doctors, medicines=medicines,
                               rowcount=rowcount, invoice_no=invoice_no, sale_date=sale_date,
                               patient_name=patient_name, doctor_name=doctor_name,
                               grand_total_mrp=grand_total_mrp, grand_total_actual=grand_total_actual,
                               savings_total=savings_total, items=items,
                               show_bill=show_bill, bill_data=bill_data, sales_history=sales_history, enumerate=enumerate)
    finally:
        cursor.close()
        conn.close()


@app.route('/purchases')
def purchases_view():
    if os.path.isdir(template_dir):
        return render_template('purchases.html')
    return jsonify({'status': 'ok', 'message': 'purchases view placeholder'})


@app.route('/sales-returns', methods=['GET', 'POST'])
def sales_returns_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY name;")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM distributors ORDER BY name;")
    distributors = cursor.fetchall()
    cursor.execute("SELECT * FROM medicines ORDER BY name;")
    medicines = cursor.fetchall()

    cursor.execute("""
        SELECT sr.id, sr.invoice_no, sr.return_datetime as return_datetime, p.name as patient_name,
               COALESCE(cnt.item_qty, 0) as item_count, sr.total_amount
        FROM sales_returns sr
        LEFT JOIN patients p ON sr.patient_id = p.id
        LEFT JOIN (
            SELECT sales_return_id, SUM(quantity) AS item_qty
            FROM sales_return_items
            GROUP BY sales_return_id
        ) cnt ON cnt.sales_return_id = sr.id
        ORDER BY sr.return_datetime DESC, sr.id DESC
    """)
    sales_returns_history = cursor.fetchall()

    cursor.execute("""
        SELECT pr.id, pr.invoice_no, pr.return_datetime as return_datetime, d.name as distributor_name,
               COALESCE(cnt.item_qty, 0) as item_count, pr.total_amount
        FROM purchase_returns pr
        LEFT JOIN distributors d ON pr.distributor_id = d.id
        LEFT JOIN (
            SELECT purchase_return_id, SUM(quantity) AS item_qty
            FROM purchase_return_items
            GROUP BY purchase_return_id
        ) cnt ON cnt.purchase_return_id = pr.id
        ORDER BY pr.return_datetime DESC, pr.id DESC
    """)
    purchase_returns_history = cursor.fetchall()

    def generate_return_invoice_no():
        today = datetime.datetime.now().strftime('%y%m%d')
        cursor.execute("SELECT MAX(CAST(RIGHT(invoice_no, 3) AS UNSIGNED)) as max_serial FROM sales_returns WHERE LEFT(invoice_no, 6) = %s", (today,))
        data = cursor.fetchone()
        serial = (data['max_serial'] + 1) if data and data.get('max_serial') else 1
        return f"{today}{serial:03d}"

    sales_return_invoice_no = generate_return_invoice_no()
    sales_return_date = datetime.datetime.now().strftime('%Y-%m-%d')
    sales_rowcount = 1
    sales_items = [{}]
    sales_grand_total_mrp = sales_grand_total_actual = sales_savings_total = ''

    editing_sales_return = None
    edit_sales_return_id = None

    if request.method == 'POST':
        sales_rowcount = int(request.form.get('rowcount', 1))
        sales_return_date = request.form.get('return_date', '') or datetime.datetime.now().strftime('%Y-%m-%d')
        sales_return_invoice_no = request.form.get('invoice_no', sales_return_invoice_no)
        patient_name = request.form.get('patient_name', '').strip()
        grand_total_actual = request.form.get('grand_total_actual', '').strip()
        grand_total_mrp = request.form.get('grand_total_mrp', '').strip()
        savings_total = request.form.get('savings_total', '').strip()

        edit_sales_return_id = request.form.get('edit_sales_return_id')
        # Start editing sales return
        if 'startedit_salesreturn_id' in request.form:
            edit_id = int(request.form.get('startedit_salesreturn_id'))
            cursor.execute("""
                SELECT sr.*, p.name as patient_name
                FROM sales_returns sr
                LEFT JOIN patients p ON sr.patient_id = p.id
                WHERE sr.id = %s
            """, (edit_id,))
            editing_sales_return = cursor.fetchone()
            cursor.execute("""
                SELECT sri.*, m.name as product FROM sales_return_items sri
                JOIN medicines m ON sri.product_id = m.id
                WHERE sri.sales_return_id = %s
            """, (edit_id,))
            item_list = cursor.fetchall()
            sales_items = []
            for item in item_list:
                gst_percent = (item.get('sgst_percent') or 0) + (item.get('cgst_percent') or 0)
                sales_items.append({
                    'product': item.get('product'),
                    'batch_no': item.get('batch_no'),
                    'expiry_date': item.get('expiry_date'),
                    'hsn_code': item.get('hsn_code'),
                    'mrp': item.get('mrp'),
                    'quantity': item.get('quantity'),
                    'rate': item.get('price'),
                    'gst_percent': gst_percent,
                    'discount_percent': item.get('discount_percent'),
                    'amount': item.get('amount'),
                })
            sales_rowcount = len(sales_items) if sales_items else 1
            return render_template('sale_returns.html', patients=patients, sales_rowcount=sales_rowcount, sales_items=sales_items,
                                   sales_grand_total_actual=editing_sales_return['total_amount'], sales_grand_total_mrp='', sales_savings_total='',
                                   sales_returns_history=sales_returns_history, purchase_rowcount=1, purchase_items=[{}],
                                   purchase_returns_history=purchase_returns_history, distributors=distributors, medicines=medicines,
                                   editing_sales_return=editing_sales_return, edit_sales_return_id=edit_id,
                                   sales_return_invoice_no=editing_sales_return['invoice_no'],
                                   sales_return_date=editing_sales_return['return_datetime'].strftime('%Y-%m-%d'), patient_name=editing_sales_return['patient_name'])

        # Handle delete sales return record
        if 'delsalesreturn_id' in request.form:
            del_id = int(request.form.get('delsalesreturn_id'))
            # Get items to revert stock
            cursor.execute("SELECT product_id, quantity FROM sales_return_items WHERE sales_return_id=%s", (del_id,))
            items_to_revert = cursor.fetchall()
            for item in items_to_revert:
                # Reduce stock_qty by quantity (removing the returned stock)
                cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (item.get('quantity'), item.get('product_id')))
            cursor.execute("DELETE FROM sales_return_items WHERE sales_return_id=%s", (del_id,))
            cursor.execute("DELETE FROM sales_returns WHERE id=%s", (del_id,))
            conn.commit()
            return redirect(url_for('sales_returns_view'))

        # Add row to form
        if 'addrow' in request.form:
            sales_items = [
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
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(sales_rowcount)
            ]
            sales_rowcount += 1
            sales_items.append({})
            flash("Row added", "info")

        # Delete row from form
        if 'delrow' in request.form:
            del_idx = int(request.form['delrow'])
            sales_items = [
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
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(sales_rowcount) if i != del_idx
            ]
            sales_rowcount = max(1, len(sales_items))
            flash("Row deleted", "info")

        # Save sales return
        if 'savesalesreturn' in request.form:
            errors = []
            if not patient_name:
                errors.append("Patient name is required.")
            if sales_rowcount == 0:
                errors.append("At least one returned item is required.")
            valid_items = 0
            for i in range(sales_rowcount):
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
                errors.append("At least one complete returned item is required.")
            if not grand_total_actual:
                errors.append("Grand total is required.")

            if errors:
                for error in errors:
                    flash(error, "danger")
                sales_items = [
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
                        'amount': request.form.get(f'items-{i}-amount', ''),
                    }
                    for i in range(sales_rowcount)
                ]
                sales_grand_total_actual = grand_total_actual
                sales_grand_total_mrp = grand_total_mrp
                sales_savings_total = savings_total
                return render_template('sale_returns.html', patients=patients, sales_rowcount=sales_rowcount, sales_items=sales_items,
                                       sales_grand_total_actual=sales_grand_total_actual, sales_grand_total_mrp=sales_grand_total_mrp,
                                       sales_savings_total=sales_savings_total, sales_returns_history=sales_returns_history,
                                       purchase_rowcount=1, purchase_items=[{}], purchase_returns_history=[],
                                       distributors=[], medicines=[])

            try:
                # Patient ID resolution or insertion if new
                patient_id = None
                for p in patients:
                    if p.get('name','').strip().lower() == patient_name.lower():
                        patient_id = p.get('id')
                        break
                if not patient_id and patient_name:
                    cursor.execute("INSERT INTO patients (name) VALUES (%s)", (patient_name,))
                    cursor.execute("INSERT INTO patients (name, contact_number) VALUES (%s, %s)", (patient_name, ''))
                    patient_id = cursor.lastrowid

                # Insert sales return record
                return_datetime = datetime.datetime.now()

                if edit_sales_return_id:
                    # This is an update
                    sales_return_id = int(edit_sales_return_id)
                    # Revert stock for old items
                    cursor.execute("SELECT product_id, quantity FROM sales_return_items WHERE sales_return_id=%s", (sales_return_id,))
                    items_to_revert = cursor.fetchall()
                    for item in items_to_revert:
                        cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (item.get('quantity'), item.get('product_id')))
                    
                    # Delete old items
                    cursor.execute("DELETE FROM sales_return_items WHERE sales_return_id=%s", (sales_return_id,))

                    # Update sales return header
                    cursor.execute("""
                        UPDATE sales_returns SET patient_id=%s, invoice_no=%s, return_datetime=%s, total_amount=%s
                        WHERE id=%s
                    """, (patient_id, sales_return_invoice_no, sales_return_date, float(grand_total_actual), sales_return_id))
                else:
                    # This is a new sales return
                    cursor.execute("""
                    INSERT INTO sales_returns (patient_id, invoice_no, return_datetime, total_amount)
                    VALUES (%s, %s, %s, %s)
                """, (patient_id, sales_return_invoice_no, return_datetime, float(grand_total_actual)))
                sales_return_id = cursor.lastrowid

                for i in range(sales_rowcount):
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
                        discount_amt = base * dis / 100
                        amount = base - discount_amt

                    medicine_id = None
                    for m in medicines:
                        if m.get('name','').strip().lower() == prod_name.lower() and m.get('batch_no') == batch_no and str(m.get('expiry_date')) == str(expiry_date):
                            medicine_id = m.get('id')

                    if not medicine_id and prod_name:
                        cursor.execute("""
                            INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (prod_name, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, 0))
                        medicine_id = cursor.lastrowid

                    if medicine_id:
                        # On sales return, add stock_qty by qty (returns increase stock)
                        cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (qty, medicine_id))

                    cursor.execute("""
                        INSERT INTO sales_return_items (sales_return_id, product_id, quantity, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (sales_return_id, medicine_id, qty, rate, amount, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, dis))

                conn.commit()
                flash("Sales return saved successfully", "success")
                if edit_sales_return_id:
                    flash("Sales return updated successfully", "success")
                else:
                    flash("Sales return saved successfully", "success")
                return redirect(url_for('sales_returns_view'))
            except Exception as e:
                flash(f"Error saving sales return: {str(e)}", "danger")
                # Re-render with current data
                sales_items = [
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
                        'amount': request.form.get(f'items-{i}-amount', ''),
                    }
                    for i in range(sales_rowcount)
                ]
                return render_template('sale_returns.html', patients=patients, sales_rowcount=sales_rowcount, sales_items=sales_items,
                                       sales_grand_total_actual=grand_total_actual, sales_grand_total_mrp=grand_total_mrp,
                                       sales_savings_total=savings_total, sales_returns_history=sales_returns_history,
                                       purchase_rowcount=1, purchase_items=[{}], purchase_returns_history=purchase_returns_history,
                                       distributors=distributors, medicines=medicines)
            finally:
                cursor.close()
                conn.close()

    if not sales_items:
        sales_items = [{}]

    return render_template('sale_returns.html', patients=patients, sales_rowcount=sales_rowcount, sales_items=sales_items,
                           sales_grand_total_actual=sales_grand_total_actual, sales_grand_total_mrp=sales_grand_total_mrp,
                           sales_savings_total=sales_savings_total, sales_returns_history=sales_returns_history,
                           purchase_rowcount=1, purchase_items=[{}], purchase_returns_history=purchase_returns_history,
                           distributors=distributors, medicines=medicines)


@app.route('/purchase-returns', methods=['GET', 'POST'])
def purchase_returns_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributors ORDER BY name;")
    distributors = cursor.fetchall()
    cursor.execute("SELECT * FROM medicines ORDER BY name;")
    medicines = cursor.fetchall()

    cursor.execute("""
        SELECT pr.id, pr.invoice_no, pr.return_datetime as return_datetime, d.name as distributor_name, 
               COALESCE(cnt.item_qty, 0) as item_count, pr.total_amount
        FROM purchase_returns pr
        LEFT JOIN distributors d ON pr.distributor_id = d.id
        LEFT JOIN (
            SELECT purchase_return_id, SUM(quantity) AS item_qty
            FROM purchase_return_items
            GROUP BY purchase_return_id
        ) cnt ON cnt.purchase_return_id = pr.id
        ORDER BY pr.return_datetime DESC, pr.id DESC
    """)
    purchase_returns_history = cursor.fetchall()

    def generate_return_invoice_no():
        today = datetime.datetime.now().strftime('%y%m%d')
        cursor.execute("SELECT MAX(CAST(RIGHT(invoice_no, 3) AS UNSIGNED)) as max_serial FROM purchase_returns WHERE LEFT(invoice_no, 6) = %s", (today,))
        data = cursor.fetchone()
        serial = (data['max_serial'] + 1) if data and data.get('max_serial') else 1
        return f"{today}{serial:03d}"

    purchase_return_invoice_no = generate_return_invoice_no()
    purchase_return_date = datetime.datetime.now().strftime('%Y-%m-%d')
    purchase_rowcount = 1
    purchase_items = [{}]
    purchase_grand_total = ''

    editing_purchase_return = None
    edit_purchase_return_id = None

    if request.method == 'POST':
        purchase_rowcount = int(request.form.get('rowcount', 1))
        purchase_return_date = request.form.get('return_date', '') or datetime.datetime.now().strftime('%Y-%m-%d')
        purchase_return_invoice_no = request.form.get('invoice_no', purchase_return_invoice_no)
        distributor_name = request.form.get('distributor_name', '').strip()
        distributor_contact = request.form.get('distributor_contact', '').strip()
        grand_total = request.form.get('grand_total', '').strip()
        edit_purchase_return_id = request.form.get('edit_purchase_return_id')

        # Start editing purchase return
        if 'startedit_purchasereturn_id' in request.form:
            edit_id = int(request.form.get('startedit_purchasereturn_id'))
            cursor.execute("""
                SELECT pr.*, d.name as distributor_name
                FROM purchase_returns pr
                LEFT JOIN distributors d ON pr.distributor_id = d.id
                WHERE pr.id = %s
            """, (edit_id,))
            editing_purchase_return = cursor.fetchone()
            cursor.execute("""
                SELECT pri.*, m.name as product FROM purchase_return_items pri
                JOIN medicines m ON pri.product_id = m.id
                WHERE pri.purchase_return_id = %s
            """, (edit_id,))
            item_list = cursor.fetchall()
            purchase_items = []
            for item in item_list:
                purchase_items.append({
                    'product': item.get('product'),
                    'batch_no': item.get('batch_no'),
                    'expiry_date': item.get('expiry_date'),
                    'quantity': item.get('quantity'),
                    'rate': item.get('price'),
                    'amount': item.get('amount'),
                })
            purchase_rowcount = len(purchase_items) if purchase_items else 1
            return render_template('purchase_returns.html', distributors=distributors, purchase_rowcount=purchase_rowcount, purchase_items=purchase_items,
                                   purchase_grand_total=editing_purchase_return['total_amount'], purchase_returns_history=purchase_returns_history,
                                   medicines=medicines, editing_purchase_return=editing_purchase_return, edit_purchase_return_id=edit_id)

        # Handle delete purchase return record
        if 'delpurchasereturn_id' in request.form:
            del_id = int(request.form.get('delpurchasereturn_id'))
            # Get items to revert stock (include free units)
            cursor.execute("SELECT product_id, quantity, `free` FROM purchase_return_items WHERE purchase_return_id=%s", (del_id,))
            items_to_revert = cursor.fetchall()
            for item in items_to_revert:
                revert_qty = int(item.get('quantity') or 0) + int(item.get('free') or 0)
                # Increase stock_qty by quantity + free (revert stock removal)
                cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (revert_qty, item.get('product_id')))
            cursor.execute("DELETE FROM purchase_return_items WHERE purchase_return_id=%s", (del_id,))
            cursor.execute("DELETE FROM purchase_returns WHERE id=%s", (del_id,))
            conn.commit()
            return redirect(url_for('purchase_returns_view'))

        # Add row to form
        if 'addrow' in request.form:
            purchase_items = [
                {
                    'product': request.form.get(f'items-{i}-product', ''),
                    'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                    'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                    'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                    'mrp': request.form.get(f'items-{i}-mrp', ''),
                    'quantity': request.form.get(f'items-{i}-quantity', ''),
                    'rate': request.form.get(f'items-{i}-rate', ''),
                    'sale_discount_percent': request.form.get(f'items-{i}-sale_discount_percent', ''),
                    'sale_rate': request.form.get(f'items-{i}-sale_rate', ''),
                    'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                    'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(purchase_rowcount)
            ]
            purchase_rowcount += 1
            purchase_items.append({})
            flash("Row added", "info")

        # Delete row from form
        if 'delrow' in request.form:
            del_idx = int(request.form['delrow'])
            purchase_items = [
                {
                    'product': request.form.get(f'items-{i}-product', ''),
                    'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                    'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                    'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                    'mrp': request.form.get(f'items-{i}-mrp', ''),
                    'quantity': request.form.get(f'items-{i}-quantity', ''),
                    'rate': request.form.get(f'items-{i}-rate', ''),
                    'sale_discount_percent': request.form.get(f'items-{i}-sale_discount_percent', ''),
                    'sale_rate': request.form.get(f'items-{i}-sale_rate', ''),
                    'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                    'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                    'amount': request.form.get(f'items-{i}-amount', ''),
                }
                for i in range(purchase_rowcount) if i != del_idx
            ]
            purchase_rowcount = max(1, len(purchase_items))
            flash("Row deleted", "info")

        # Save purchase return
        if 'savepurchasereturn' in request.form:
            errors = []
            if not distributor_name:
                errors.append("Distributor name is required.")
            if purchase_rowcount == 0:
                errors.append("At least one returned item is required.")
            valid_items = 0
            for i in range(purchase_rowcount):
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
                errors.append("At least one complete returned item is required.")
            if not grand_total:
                errors.append("Grand total is required.")

            invoice_no = request.form.get('invoice_no') or generate_return_invoice_no()
            # Check for duplicate invoice_no
            cursor.execute("SELECT COUNT(*) as count FROM purchase_returns WHERE invoice_no = %s", (invoice_no,))
            if cursor.fetchone().get('count', 0) > 0:
                errors.append("Invoice number already exists. Please try again.")

            if errors:
                for error in errors:
                    flash(error, "danger")
                purchase_grand_total = grand_total
                return render_template('purchase_returns.html', distributors=distributors, purchase_rowcount=purchase_rowcount,
                                       purchase_items=purchase_items, purchase_grand_total=purchase_grand_total,
                                       purchase_returns_history=purchase_returns_history,
                                       sales_rowcount=1, sales_items=[{}], sales_returns_history=[],
                                       patients=[], medicines=[])

            try:
                # Distributor ID resolution or insert new distributor
                distributor_id = None
                for d in distributors:
                    if d.get('name','').strip().lower() == distributor_name.lower():
                        distributor_id = d.get('id')
                        break
                if not distributor_id and distributor_name:
                    cursor.execute("INSERT INTO distributors (name) VALUES (%s)", (distributor_name,))
                    distributor_id = cursor.lastrowid
                return_datetime = datetime.datetime.now()

                if edit_purchase_return_id:
                    # This is an update
                    purchase_return_id = int(edit_purchase_return_id)
                    # Revert stock for old items
                    cursor.execute("SELECT product_id, quantity, `free` FROM purchase_return_items WHERE purchase_return_id=%s", (purchase_return_id,))
                    items_to_revert = cursor.fetchall()
                    for item in items_to_revert:
                        revert_qty = int(item.get('quantity') or 0) + int(item.get('free') or 0)
                        cursor.execute("UPDATE medicines SET stock_qty = stock_qty + %s WHERE id = %s", (revert_qty, item.get('product_id')))
                    
                    # Delete old items
                    cursor.execute("DELETE FROM purchase_return_items WHERE purchase_return_id=%s", (purchase_return_id,))

                    # Update purchase return header
                    cursor.execute("""
                        UPDATE purchase_returns SET distributor_id=%s, invoice_no=%s, return_datetime=%s, total_amount=%s
                        WHERE id=%s
                    """, (distributor_id, purchase_return_invoice_no, purchase_return_date, float(grand_total), purchase_return_id))
                else:
                    # This is a new purchase return
                    return_datetime = datetime.datetime.now()
                    cursor.execute("""
                    INSERT INTO purchase_returns (distributor_id, invoice_no, return_datetime, total_amount)
                    VALUES (%s, %s, %s, %s)
                """, (distributor_id, purchase_return_invoice_no, return_datetime, float(grand_total)))
                purchase_return_id = cursor.lastrowid
                for i in range(purchase_rowcount):
                    prod_name = request.form.get(f'items-{i}-product', '').strip()
                    if not prod_name:
                        continue
                    batch_no = request.form.get(f'items-{i}-batch_no', '')
                    expiry_date = request.form.get(f'items-{i}-expiry_date', None)
                    packing = request.form.get(f'items-{i}-packing', '')
                    hsn_code = request.form.get(f'items-{i}-hsn_code', '')
                    mrp_str = request.form.get(f'items-{i}-mrp', '').strip()
                    mrp = float(mrp_str) if mrp_str else 0.0
                    qty_str = request.form.get(f'items-{i}-quantity', '').strip()
                    qty = int(qty_str) if qty_str else 0
                    free_str = request.form.get(f'items-{i}-free', '').strip()
                    free = int(free_str) if free_str else 0
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
                        discount_amt = base * dis / 100
                        amount = base - discount_amt
                    medicine_id = None
                    for m in medicines:
                        if m.get('name','').strip().lower() == prod_name.lower() and m.get('batch_no') == batch_no and str(m.get('expiry_date')) == str(expiry_date) and str(m.get('packing') or '') == str(packing or ''):
                            medicine_id = m.get('id')
                    if not medicine_id and prod_name:
                        cursor.execute("""
                            INSERT INTO medicines (name, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, stock_qty, packing)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (prod_name, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, 0))
                        medicine_id = cursor.lastrowid
                    if medicine_id:
                        # On purchase return, reduce stock_qty by qty + free (returned items include free units)
                        cursor.execute("UPDATE medicines SET stock_qty = stock_qty - %s WHERE id = %s", (qty + free, medicine_id))
                    cursor.execute("""
                        INSERT INTO purchase_return_items (purchase_return_id, product_id, quantity, `free`, price, amount, batch_no, expiry_date, hsn_code, mrp, sgst_percent, cgst_percent, discount_percent)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (purchase_return_id, medicine_id, qty, free, rate, amount, batch_no, expiry_date, hsn_code, mrp, sgst, cgst, dis))
                conn.commit()
                flash("Purchase return saved successfully", "success")
                if edit_purchase_return_id:
                    flash("Purchase return updated successfully", "success")
                else:
                    flash("Purchase return saved successfully", "success")
                return redirect(url_for('purchase_returns_view'))
            except Exception as e:
                flash(f"Error saving purchase return: {str(e)}", "danger")
                # Re-render with current data
                purchase_items = [
                    {
                        'product': request.form.get(f'items-{i}-product', ''),
                        'batch_no': request.form.get(f'items-{i}-batch_no', ''),
                        'expiry_date': request.form.get(f'items-{i}-expiry_date', ''),
                        'hsn_code': request.form.get(f'items-{i}-hsn_code', ''),
                        'mrp': request.form.get(f'items-{i}-mrp', ''),
                        'quantity': request.form.get(f'items-{i}-quantity', ''),
                        'rate': request.form.get(f'items-{i}-rate', ''),
                        'sale_discount_percent': request.form.get(f'items-{i}-sale_discount_percent', ''),
                        'sale_rate': request.form.get(f'items-{i}-sale_rate', ''),
                        'sgst_percent': request.form.get(f'items-{i}-sgst_percent', ''),
                        'cgst_percent': request.form.get(f'items-{i}-cgst_percent', ''),
                        'amount': request.form.get(f'items-{i}-amount', ''),
                    }
                    for i in range(purchase_rowcount)
                ]
                return render_template('purchase_returns.html', distributors=distributors, purchase_rowcount=purchase_rowcount, purchase_items=purchase_items,
                                       purchase_grand_total=grand_total, purchase_returns_history=purchase_returns_history,
                                       sales_rowcount=1, sales_items=[{}], sales_returns_history=[],
                                       patients=[], medicines=[])
            finally:
                cursor.close()
                conn.close()

    cursor.close()
    conn.close()

    if not purchase_items:
        purchase_items = [{}]

    return render_template('purchase_returns.html', distributors=distributors, purchase_rowcount=purchase_rowcount, purchase_items=purchase_items,
                           purchase_grand_total=purchase_grand_total, purchase_returns_history=purchase_returns_history,
                           sales_rowcount=1, sales_items=[{}], sales_returns_history=[],
                           patients=[], medicines=medicines, editing_purchase_return=editing_purchase_return,
                           edit_purchase_return_id=edit_purchase_return_id)


if __name__ == '__main__':
    # When running locally, open the app on 127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)
