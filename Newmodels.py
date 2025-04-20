
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('Document', backref='owner', lazy=True)
    custom_types = db.relationship('CustomDocumentType', backref='creator', lazy=True)

class CustomDocumentType(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    requires_signature = db.Column(db.Boolean, default=False)
    view_only = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)

class Document(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    doc_type = db.Column(db.String(100), nullable=False)
    requires_signature = db.Column(db.Boolean, default=False)
    view_only = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    signed_name = db.Column(db.String(120))
    signed_at = db.Column(db.DateTime)
