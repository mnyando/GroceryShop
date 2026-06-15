from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    email = StringField('Your Email Address', validators=[DataRequired(), Email()])
    username = StringField('Enter your username', validators=[DataRequired()])
    firstname = StringField('Enter your first name', validators=[DataRequired()])
    lastname = StringField('Enter your last name', validators=[DataRequired()])
    role = SelectField('Account Type', choices=[('customer', 'Customer'), ('admin', 'Store Admin')], default='customer')
    admin_code = PasswordField('Admin Passcode (Only if registering as Store Admin)')
    password = PasswordField('Password', validators=[
        DataRequired(), 
        EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')
 
    def validate_email(self, data_field):
        if User.get_by_email(data_field.data):
            raise ValidationError('There is an account with that email')

    def validate_username(self, data_field):
        from ..database import query_documents
        if query_documents('users', 'username', '==', data_field.data):
            raise ValidationError('That username is taken')


class LoginForm(FlaskForm):
    email = StringField('Your Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')