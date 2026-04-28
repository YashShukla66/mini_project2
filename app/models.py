from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    gender = db.Column(db.String(20))
    race = db.Column(db.String(50))
    parental_education = db.Column(db.String(100))
    lunch = db.Column(db.String(50))
    test_prep = db.Column(db.String(50))
    math_score = db.Column(db.Integer)
    coding_score = db.Column(db.Integer)
    iot_score = db.Column(db.Integer)
    result = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())