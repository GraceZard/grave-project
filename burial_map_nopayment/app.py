from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Grave, DaftarKematian
import os
from sqlalchemy import or_

app = Flask(__name__)
import os
db_path = os.path.abspath('database.db')
print(f"Using database at: {db_path}")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

@app.route('/')
def home():
    query = request.args.get('query', '')
    print(f"Search query: {query}")
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
    print(f"Found graves: {len(graves)}, daftar_kematian_records: {len(daftar_kematian_records)}")
    return render_template('home.html', graves=graves, daftar_kematian_records=daftar_kematian_records, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Alamat email telah didaftarkan. Sila log masuk atau gunakan email lain.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            email=email
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Pendaftaran berjaya! Anda telah log masuk.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Log masuk berjaya. Anda kini boleh lihat maklumat terperinci.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email atau kata laluan tidak sah.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/daftar_kematian', methods=['GET', 'POST'])
def daftar_kematian():
    user_id = session.get('user_id')
    if not user_id:
        flash('Sila log masuk untuk mengakses halaman ini.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        deceased_name = request.form.get('deceased_name')
        stone_number = request.form.get('stone_number')
        date_of_birth = request.form.get('date_of_birth')
        age_at_death = request.form.get('age_at_death')
        heir_name = request.form.get('heir_name')
        heir_contact = request.form.get('heir_contact')

        if not all([deceased_name, stone_number, date_of_birth, age_at_death, heir_name, heir_contact]):
            flash('Sila isi semua maklumat.', 'error')
            return redirect(url_for('daftar_kematian'))

        # Check if grave exists by stone_number
        grave = Grave.query.filter_by(lot_number=stone_number).first()
        if not grave:
            grave = Grave(
                name=deceased_name,
                date_of_birth=date_of_birth,
                lot_number=stone_number,
                section='',  # Section can be updated later if needed
                picture_url='',
                family_details='',
                notes=''
            )
            db.session.add(grave)
            db.session.flush()  # To get grave.id for foreign key

        new_record = DaftarKematian(
            grave_id=grave.id,
            deceased_name=deceased_name,
            stone_number=stone_number,
            date_of_birth=date_of_birth,
            age_at_death=int(age_at_death),
            heir_name=heir_name,
            heir_contact=heir_contact
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Rekod kematian berjaya ditambah.', 'success')
        return redirect(url_for('daftar_kematian'))

    records = DaftarKematian.query.all()
    return render_template('daftar_kematian.html', records=records)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Anda telah log keluar.', 'success')
    return redirect(url_for('home'))

@app.route('/grave/<int:grave_id>')
def grave_detail(grave_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Sila log masuk untuk melihat maklumat kubur secara terperinci.', 'error')
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
    app.run(debug=True, host='0.0.0.0', port=5000)
