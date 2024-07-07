from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User
import logging

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('receipt.upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        logger.info(f"User {user.username} logged in successfully")
        return redirect(url_for('receipt.upload'))
    return render_template('login.html', title='Sign In', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('receipt.upload'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            logger.info(f"New user registered: {user.username}")
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering new user: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('register.html', title='Register', form=form)