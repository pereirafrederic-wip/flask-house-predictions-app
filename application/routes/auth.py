from flask import Blueprint, flash, redirect, render_template, url_for
from application.forms.login import Login
from application.forms.add_user import  AddUser
from application.database.users import User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user

auth = Blueprint('auth', __name__, url_prefix='/')

@auth.route('/')
def home():
    return render_template('home.html')

@auth.route("/login", methods=["GET","POST"])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            print('un user est dorénavant connecté')
            flash("Logged in with success", category="success")
            return redirect(url_for('auth.home'))
        else:
            flash("Mail address or password invalid", category="danger")
    return render_template('login.html', form=form)


@auth.route('/add_user', methods= ['GET', 'POST'])
def add_user():
    form = AddUser()
    if form.validate_on_submit():
        if form.password_hash.data == form.password_hash2.data:

            check = User.query.filter_by(email = form.email.data).first()
            if check : 
                flash('Email already exists', category='error')
                return redirect(url_for('auth.login'))
            User(lastname = form.lastname.data, firstname = form.firstname.data, email = form.email.data, password_hash = generate_password_hash(form.password_hash.data, method='sha256')).save_to_db()
            flash('Nouvel utilisateur ajouté ', category='secondary')
            return redirect(url_for('auth.login'))
        else:
            flash('Please enter same password')
    return render_template('add_user.html', form=form)

@auth.route('/logout')
def logout_page():
    logout_user()
    flash('Vous êtes correctement déconnecté',category="success")
    return redirect(url_for('auth.login'))
