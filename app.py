from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime

from config import Config
from models import db, User, Document

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=10000)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "email" in request.form and "password" in request.form:
            user = User.query.filter_by(email=request.form["email"]).first()
            if user and check_password_hash(user.password, request.form["password"]):
                login_user(user)
                return redirect(url_for("dashboard"))
            else:
                return "Invalid credentials"
    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    if User.query.filter_by(email=email).first():
        return "Email already registered"
    hashed_pw = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=session["_user_id"]).all()
    return render_template("dashboard.html", documents=documents)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_document():
    if request.method == "POST":
        title = request.form["title"]
        doc_type = request.form["doc_type"]
        content = request.form["content"]
        signature_required = "signature_required" in request.form
        view_only = "view_only" in request.form
        doc = Document(
            title=title,
            content=content,
            doc_type=doc_type,
            signature_required=signature_required,
            view_only=view_only,
            user_id=session["_user_id"],
            created_at=datetime.utcnow()
        )
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("create_document.html")


@app.route("/document/<int:doc_id>")
def view_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    return render_template("view_document.html", document=document)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
