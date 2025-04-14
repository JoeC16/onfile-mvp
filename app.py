from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'onfile_secret'
UPLOAD_FOLDER = 'waivers'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# DB Setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS waivers (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title TEXT,
                    body TEXT,
                    link TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS signed_waivers (
                    id INTEGER PRIMARY KEY,
                    waiver_id INTEGER,
                    name TEXT,
                    email TEXT,
                    filename TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')
    return "Invalid login"

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM waivers WHERE user_id=?", (session['user_id'],))
    waivers = c.fetchall()
    conn.close()
    return render_template('dashboard.html', waivers=waivers)

@app.route('/create_waiver', methods=['GET', 'POST'])
def create_waiver():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        unique_link = os.urandom(4).hex()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO waivers (user_id, title, body, link) VALUES (?, ?, ?, ?)", 
                  (session['user_id'], title, body, unique_link))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('create_waiver.html')

@app.route('/waiver/<link>', methods=['GET', 'POST'])
def sign_waiver(link):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, title, body FROM waivers WHERE link=?", (link,))
    waiver = c.fetchone()
    if not waiver:
        return "Waiver not found"
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        filename = f"{name.replace(' ', '_')}_{waiver[0]}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        c_pdf = canvas.Canvas(filepath, pagesize=letter)
        c_pdf.drawString(50, 750, f"Waiver: {waiver[1]}")
        c_pdf.drawString(50, 730, f"Signed by: {name} ({email})")
        text_obj = c_pdf.beginText(50, 700)
        for line in waiver[2].splitlines():
            text_obj.textLine(line)
        c_pdf.drawText(text_obj)
        c_pdf.save()
        
        c.execute("INSERT INTO signed_waivers (waiver_id, name, email, filename) VALUES (?, ?, ?, ?)",
                  (waiver[0], name, email, filename))
        conn.commit()
        conn.close()
        return f"Thank you! Waiver signed and saved as {filename}."
    return render_template('sign_waiver.html', waiver=waiver)

@app.route('/signed')
def signed_list():
    if 'user_id' not in session:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT s.name, s.email, s.filename
                 FROM signed_waivers s
                 JOIN waivers w ON s.waiver_id = w.id
                 WHERE w.user_id=?''', (session['user_id'],))
    signed = c.fetchall()
    conn.close()
    return render_template('signed_waivers.html', signed=signed)

@app.route('/waivers/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
