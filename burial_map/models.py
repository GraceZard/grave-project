from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    access_reason = db.Column(db.String(200))
    access_granted = db.Column(db.Boolean, default=False)
    access_code = db.Column(db.String(50), unique=True)

class Grave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(20))
    date_of_death = db.Column(db.String(20))
    lot_number = db.Column(db.String(50))
    section = db.Column(db.String(50))
    picture_url = db.Column(db.String(200))
    family_details = db.Column(db.Text)
    notes = db.Column(db.Text)
