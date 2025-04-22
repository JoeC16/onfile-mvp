from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onfile.db'  # or use os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = '/app/uploaded_files'

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.main import main  # Delayed import to avoid circular reference
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
