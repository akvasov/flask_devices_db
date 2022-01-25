"""
This module contains signup and login forms model definitions
to parse user's input from signup or login Web pages.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """Flask login form definition to login a user"""
    username = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Confirm')


class SignUPForm(FlaskForm):
    """Flask signup form definition to create a new user"""
    username = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    act_passwd = PasswordField('Activation Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')




