from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    daftar_kematian = db.relationship('DaftarKematian', back_populates='grave', uselist=False)

class DaftarKematian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grave_id = db.Column(db.Integer, db.ForeignKey('grave.id'), unique=True)
    deceased_name = db.Column(db.String(100), nullable=False)
    stone_number = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    age_at_death = db.Column(db.Integer, nullable=False)
    heir_name = db.Column(db.String(100), nullable=False)
    heir_contact = db.Column(db.String(200), nullable=False)
    grave = db.relationship('Grave', back_populates='daftar_kematian')
