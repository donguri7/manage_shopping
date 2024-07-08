from datetime import datetime, timedelta
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates

class PurchaseListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PurchaseListItem {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    items = db.relationship('Item', backref='owner', lazy='dynamic')
    purchase_list_items = db.relationship('PurchaseListItem', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(passw