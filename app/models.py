from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login_date = db.Column(db.Date)
    streak = db.Column(db.Integer, default=0)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    gender = db.Column(db.String(20))
    sleep_hours = db.Column(db.Float)
    doom_scrolling_time = db.Column(db.Float)
    productive_screen_time = db.Column(db.Float)
    study_hours = db.Column(db.Float)
    medical_issue = db.Column(db.String(10))
    drug_addiction = db.Column(db.String(10))
    math_score = db.Column(db.Integer)
    physics_score = db.Column(db.Integer)
    chemistry_score = db.Column(db.Integer)
    biology_score = db.Column(db.Integer)
    english_score = db.Column(db.Integer)
    result = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())