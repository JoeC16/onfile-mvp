
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Document, CustomDocumentType
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///onfile.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(email=request.form['email'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', documents=documents)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_document():
    custom_types = CustomDocumentType.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        doc_type = request.form['doc_type']
        requires_signature = 'requires_signature' in request.form
        view_only = 'view_only' in request.form
        new_doc = Document(
            title=request.form['title'],
            content=request.form['content'],
            doc_type=doc_type,
            requires_signature=requires_signature,
            view_only=view_only,
            user_id=current_user.id
        )
        db.session.add(new_doc)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_document.html', custom_types=custom_types)

@app.route('/document/<doc_id>', methods=['GET', 'POST'])
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.view_only:
        return render_template('view_document.html', document=doc)
    if request.method == 'POST' and not doc.signed_name:
        doc.signed_name = request.form['name']
        doc.signed_at = datetime.utcnow()
        db.session.commit()
        return render_template('signed_confirmation.html', document=doc)
    return render_template('view_document.html', document=doc)

@app.route('/custom-types/create', methods=['GET', 'POST'])
@login_required
def create_custom_type():
    if request.method == 'POST':
        name = request.form['name']
        requires_signature = 'requires_signature' in request.form
        view_only = 'view_only' in request.form
        new_type = CustomDocumentType(
            name=name,
            requires_signature=requires_signature,
            view_only=view_only,
            user_id=current_user.id
        )
        db.session.add(new_type)
        db.session.commit()
        return redirect(url_for('create_document'))
    return render_template('create_custom_type.html')
