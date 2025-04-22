# app/routes/main.py

from flask import render_template, request, redirect, url_for, session, flash
from app.models import db, User

def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                flash('Account already exists. Please log in instead.')
                return redirect(url_for('login'))

            new_user = User(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            return redirect(url_for('dashboard'))

        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials. Please try again.')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')
