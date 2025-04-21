from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import uuid
import os
from models import db, User, Document, CustomDocumentType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onfile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# Create tables on startup
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return redirect(url_for('dashboard', user_id=user.id))
    flash("Login failed. Try again.")
    return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    if User.query.filter_by(email=email).first():
        flash("Email already registered.")
        return redirect(url_for('home'))
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('dashboard', user_id=new_user.id))

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get_or_404(user_id)
    docs = Document.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, documents=docs)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        doc_type = request.form['doc_type']
        requires_signature = request.form.get('requires_signature') == 'on'
        is_view_only = request.form.get('is_view_only') == 'on'
        content = request.form['content']
        user_id = request.form['user_id']
        doc_id = str(uuid.uuid4())[:8]
        doc = Document(doc_id=doc_id, title=title, doc_type=doc_type, content=content,
                       requires_signature=requires_signature, is_view_only=is_view_only, user_id=user_id)
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('dashboard', user_id=user_id))
    user_id = request.args.get('user_id')
    return render_template('create_document.html', user_id=user_id)

@app.route('/view/<doc_id>', methods=['GET', 'POST'])
def view(doc_id):
    doc = Document.query.filter_by(doc_id=doc_id).first_or_404()
    if request.method == 'POST' and doc.requires_signature:
        doc.is_signed = True
        db.session.commit()
        return render_template('signed_confirmation.html')
    return render_template('view_document.html', doc=doc)

@app.route('/create_type/<int:user_id>', methods=['GET', 'POST'])
def create_type(user_id):
    if request.method == 'POST':
        name = request.form['name']
        requires_signature = request.form.get('requires_signature') == 'on'
        is_view_only = request.form.get('is_view_only') == 'on'
        new_type = CustomDocumentType(name=name, requires_signature=requires_signature,
                                      is_view_only=is_view_only, user_id=user_id)
        db.session.add(new_type)
        db.session.commit()
        return redirect(url_for('dashboard', user_id=user_id))
    return render_template('create_custom_type.html', user_id=user_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
