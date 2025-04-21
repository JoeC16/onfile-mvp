from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
CORS(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Define models (move to models.py in production)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    doc_type = db.Column(db.String(100), nullable=False)
    signature_required = db.Column(db.Boolean, default=False)
    view_only = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Clear database and recreate tables (TEMPORARY FOR RESET)
@app.before_first_request
def reset_db():
    db.drop_all()
    db.create_all()

# Routes
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        return "Invalid login credentials"
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    if User.query.filter_by(email=email).first():
        return "Email already exists"
    hashed_pw = generate_password_hash(password, method="sha256")
    user = User(email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", documents=documents)

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_document():
    if request.method == "POST":
        doc = Document(
            title=request.form["title"],
            content=request.form["content"],
            doc_type=request.form["doc_type"],
            signature_required="signature_required" in request.form,
            view_only="view_only" in request.form,
            user_id=current_user.id
        )
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("create_document.html")

@app.route("/document/<int:doc_id>")
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template("view_document.html", document=doc)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
