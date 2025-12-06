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


@app.route('/purchases')
def purchases_placeholder():
    return render_template('purchases.html') if os.path.isdir(template_dir) else jsonify({'status': 'ok', 'message': 'purchases placeholder (fixed file)'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
