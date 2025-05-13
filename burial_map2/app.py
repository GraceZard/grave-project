from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Grave, DaftarKematian
import os
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

from sqlalchemy import or_

@app.route('/')
def home():
    query = request.args.get('query', '')
    graves = []
    daftar_kematian_records = []
    if query:
        like_pattern = f"%{query}%"
        graves = Grave.query.filter(
            or_(
                Grave.name.ilike(like_pattern),
                Grave.section.ilike(like_pattern)
            )
        ).all()
        daftar_kematian_records = DaftarKematian.query.filter(
            or_(
                DaftarKematian.deceased_name.ilike(like_pattern),
                DaftarKematian.stone_number.ilike(like_pattern),
                DaftarKematian.heir_name.ilike(like_pattern),
                DaftarKematian.heir_contact.ilike(like_pattern)
            )
        ).all()
        print(f"Search query: {query}")
        print(f"Graves found: {len(graves)}")
        print(f"Daftar Kematian records found: {len(daftar_kematian_records)}")
    return render_template('home.html', graves=graves, daftar_kematian_records=daftar_kematian_records, query=query)

@app.route('/daftar_kematian', methods=['GET', 'POST'])
def daftar_kematian():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to access this page. Please login or register.')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user.access_granted:
        flash('You must complete payment to access this information.')
        return redirect(url_for('payment', user_id=user.id))

    if request.method == 'POST':
        deceased_name = request.form.get('deceased_name')
        stone_number = request.form.get('stone_number')
        date_of_birth = request.form.get('date_of_birth')
        age_at_death = request.form.get('age_at_death')
        heir_name = request.form.get('heir_name')
        heir_contact = request.form.get('heir_contact')

        if not all([deceased_name, stone_number, date_of_birth, age_at_death, heir_name, heir_contact]):
            flash('Please fill in all fields.')
            return redirect(url_for('daftar_kematian'))

        new_record = DaftarKematian(
            deceased_name=deceased_name,
            stone_number=stone_number,
            date_of_birth=date_of_birth,
            age_at_death=int(age_at_death),
            heir_name=heir_name,
            heir_contact=heir_contact
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Daftar Kematian record added successfully.')
        return redirect(url_for('daftar_kematian'))

    records = DaftarKematian.query.all()
    return render_template('daftar_kematian.html', records=records)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or access your account.')
            return redirect(url_for('register'))

        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        new_user = User(
            email=email,
            access_granted=False,
            access_code=access_code
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in immediately after registration
        session['user_id'] = new_user.id

        return redirect(url_for('payment', user_id=new_user.id))
    return render_template('register.html')

@app.route('/payment/<int:user_id>', methods=['GET', 'POST'])
def payment(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        amount = request.form.get('amount')
        try:
            amount_value = float(amount)
            if amount_value < 1:
                flash('Minimum payment amount is RM1.')
                return redirect(url_for('payment', user_id=user.id))
        except (ValueError, TypeError):
            flash('Invalid payment amount.')
            return redirect(url_for('payment', user_id=user.id))

        user.access_granted = True
        db.session.commit()
        flash(f'Payment of RM{amount_value} successful! Your access code is: {user.access_code}')
        return redirect(url_for('login'))
    return render_template('payment.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, access_granted=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful. You can now view detailed grave information.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been loggeded out.')
    return redirect(url_for('home'))

@app.route('/grave/<int:grave_id>')
def grave_detail(grave_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view detailed grave information. Please login or register.')
        return redirect(url_for('login'))
    grave = Grave.query.get_or_404(grave_id)
    return render_template('grave_detail.html', grave=grave)


@app.route('/test_data')
def test_data():
    graves = Grave.query.all()
    daftar_kematian_records = DaftarKematian.query.all()
    graves_list = [f"{g.name} ({g.section})" for g in graves]
    daftar_list = [f"{d.deceased_name} (Stone: {d.stone_number})" for d in daftar_kematian_records]
    return f"Graves: {graves_list}<br>Daftar Kematian: {daftar_list}"

if __name__ == '__main__':
    app.run(debug=True)
