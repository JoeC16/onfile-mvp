from .. import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
