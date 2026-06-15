from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..email import mail_message

ADMIN_REGISTRATION_PASSCODE = "admin123" # Passcode to authorize registering as a store admin

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.index'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.get_by_email(login_form.email.data)
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.index'))

        flash('Invalid email or password')

    title = "Mama Mboga Login"
    return render_template('auth/login.html', login_form=login_form, title=title)


@auth.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        role = form.role.data
        if role == 'admin':
            if form.admin_code.data != ADMIN_REGISTRATION_PASSCODE:
                flash('Invalid admin registration passcode. Contact the owner for the passcode.')
                return render_template('auth/register.html', registration_form=form)

        user, err = User.create_user(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=role
        )
        
        if err:
            flash(err)
            return render_template('auth/register.html', registration_form=form)

        try:
            mail_message("Welcome to Mama Mboga App", "email/welcome_user", user.email, user=user)
        except Exception as e:
            # Silently log if SMTP variables aren't configured
            print(f"[MAIL] Safe Warning: Could not send email welcome notice. Reason: {e}")

        flash('Registration successful! Please sign in.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', registration_form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))