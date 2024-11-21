from flask import Blueprint, render_template, request, flash, redirect, url_for 
from .models import user, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        User = user.query.filter_by(email = email).first()
        
        if User:
            if check_password_hash(User.password, password):
                query= text('UPDATE user SET online = :val WHERE id = :ID')
                db.session.execute(query, {'val': 1, 'ID': User.id} )
                db.session.commit()
                flash('Logged in successfully.', category='success')
                login_user(User, remember=True)

                return  redirect(url_for('views.home'))
            else:
                flash('Password is incorrect, try again!', category='error')
        else:
            flash('User with that email does not exist!', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/signup', methods=['POST', 'GET'] )
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        fullname = request.form.get('fullname')
        country = request.form.get('country')
        school = request.form.get('school')
        programme = request.form.get('programme')
        year = request.form.get('year')
        mobilenumber = request.form.get('mobilenumber')
        occupation = request.form.get('occupation')
        organisation = request.form.get('organisation')
        
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
  
        User = user.query.filter_by(email=email).first()
        
        if User:
            flash('Email already exists', category='error')

        if len(email) < 4:
            flash('Email must be longer than 3 characters!', category='error')
        elif len(fullname) < 2:
            flash('Fullname must be longer than 2 characters!', category='error')
        elif len(school) <=      3:
            flash('School must be longer than 3 characters!', category='error')
        elif len(programme) < 3:
            flash('Programme must be longer than 3 characters!', category='error')
        elif len(year) < 3:
            flash('Year must be longer than 3 characters!', category='error')
        elif len(mobilenumber) < 3: 
            flash('Number must be longer than 3 characters!', category='error') 
        elif len(occupation) < 3:
            flash('Occupation must be longer than 3 characters!', category='error')  
        elif len(organisation) < 3:
            flash('Organisation must be longer than 3 characters!', category='error')  
        elif len(country) < 3:
            flash('Country must be longer than 3 characters!', category='error')                                              
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(password1) < 7:
            flash('Password must be longer than 7 characters!', category='error')
        else:
            newuser = user(fullname=fullname, country=country, school=school, programme=programme, mobilenumber=mobilenumber,
                    email=email, occupation=occupation, organisation=organisation, year=year, password=generate_password_hash(password1, method='pbkdf2:sha256'))

            db.session.add(newuser)
            db.session.commit()

            flash('Account created!', category='success')
            login_user(newuser, remember=True)  

            return  redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    db.session.execute(text('UPDATE user SET online = :val WHERE id = :ID'), {'val': 0, 'ID': current_user.id})
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))