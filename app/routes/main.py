from app.models.document import Document

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db

main = Blueprint("main", __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Account already exists. Please log in instead.')
            return redirect(url_for('main.login'))

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('main.dashboard'))

    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

import os
from flask import current_app, request, redirect, url_for, render_template, flash
from flask_login import login_required

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file.save(save_path)
            flash('File uploaded successfully.')
            return redirect(url_for('main.dashboard'))
    return render_template('upload.html')

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_document():
    if request.method == 'POST':
        title = request.form['title']
        doc_type = request.form['type']
        html_content = request.form['body']

        new_doc = Document(title=title, type=doc_type, html=html_content)
        db.session.add(new_doc)
        db.session.commit()

        flash('Document created successfully.')
        return redirect(url_for('main.dashboard'))

    return render_template('create.html')

@main.route('/ping')
def ping():
    return "Pong!"

@main.route('/debug/users')
def debug_users():
    from app.models.user import User
    users = User.query.all()
    return "<br>".join([f"{u.id} – {u.email}" for u in users])


