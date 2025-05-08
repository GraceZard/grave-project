from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Grave
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

@app.before_first_request
def create_example_graves():
    # Check if there are already graves in the database
    if Grave.query.count() == 0:
        graves_data = [
            Grave(name="Ahmad bin Ali", date_of_birth="01-01-1950", date_of_death="01-01-2020", lot_number="L001", section="A1", picture_url="/static/images/ahmad.jpg", family_details="Wife: Aisha, 2 Children", notes="Veteran of the army"),
            Grave(name="Fatimah binti Zain", date_of_birth="15-05-1985", date_of_death="10-12-2022", lot_number="L002", section="B3", picture_url="/static/images/fatimah.jpg", family_details="Husband: Zain, 1 Child", notes="Loving mother"),
            Grave(name="Ibrahim bin Yusuf", date_of_birth="20-07-1975", date_of_death="05-09-2015", lot_number="L003", section="C5", picture_url="/static/images/ibrahim.jpg", family_details="Father: Sarah, 3 Children", notes="Spiritual leader"),
            Grave(name="Nurul Huda", date_of_birth="10-03-1990", date_of_death="11-11-2021", lot_number="L004", section="A2", picture_url="/static/images/nurul_huda.jpg", family_details="Mother: Sofia, 1 Child", notes="Teacher at local school"),
            Grave(name="Khadijah binti Omar", date_of_birth="25-08-1960", date_of_death="12-06-2018", lot_number="L005", section="B1", picture_url="/static/images/khadijah.jpg", family_details="Husband: Omar, 3 Children", notes="Charity worker")
        ]
        
        db.session.add_all(graves_data)
        db.session.commit()
        print("Example graves added to the database!")

@app.route('/')
def home():
    query = request.args.get('query', '')
    graves = []
    if query:
        graves = Grave.query.filter(
            (Grave.name.contains(query)) | (Grave.section.contains(query))
        ).all()
    return render_template('home.html', graves=graves, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        access_reason = request.form.get('access_reason')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or access your account.')
            return redirect(url_for('register'))

        # Generate a simple access code (in real app, use secure method)
        import random, string
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        new_user = User(
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            access_reason=access_reason,
            access_granted=False,
            access_code=access_code
        )
        db.session.add(new_user)
        db.session.commit()

        # Redirect to payment page with user id
        return redirect(url_for('payment', user_id=new_user.id))
    return render_template('register.html')

@app.route('/payment/<int:user_id>', methods=['GET', 'POST'])
def payment(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # In real app, integrate payment gateway here
        # For now, simulate successful payment
        user.access_granted = True
        db.session.commit()
        flash('Payment successful! Your access code is: ' + user.access_code)
        return redirect(url_for('login'))
    return render_template('payment.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        access_code = request.form.get('access_code')
        user = User.query.filter_by(email=email, access_code=access_code, access_granted=True).first()
        if user:
            session['user_id'] = user.id
            flash('Login successful. You can now view detailed grave information.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or access code.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/grave/<int:grave_id>')
def grave_detail(grave_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view detailed grave information. Please login or register.')
        return redirect(url_for('login'))
    grave = Grave.query.get_or_404(grave_id)
    return render_template('grave_detail.html', grave=grave)

if __name__ == "__main__":
    app.run(debug=True)
