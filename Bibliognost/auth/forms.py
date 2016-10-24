from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Email, DataRequired, Length, EqualTo

from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[
        DataRequired('Please provide a valid email address'),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired('please provide a valid password')
    ])
    remember_me = BooleanField('Remember me')


class RegistrationForm(Form):
    name = StringField('Full Name', validators=[
        DataRequired('Please provide your Full name')
    ])
    email = StringField('Email', validators=[
        DataRequired('Please provide a valid email address'),
        Email(),
        Length(1, 64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired('please provide a password'),
        Length(min=6),
        EqualTo('confirm_password', 'passwords must match')
    ])
    confirm_password = PasswordField('Confirm password', validators=[
        DataRequired('please confirm your password'),
    ])

    def validate_email(self, field):
        if User.get(email=field.data):
            raise ValidationError('Email already exists')

    def validate_username(self, field):
        if User.get(username=field.data):
            raise ValidationError('Username already exists')
