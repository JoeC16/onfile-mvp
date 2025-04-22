from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploaded_files')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
