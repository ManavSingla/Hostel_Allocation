from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import email_validator

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    sid = IntegerField('sid', validators=[DataRequired(), Length(min=8, max=8, message="SID must be 8 characters long!")])
    email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long!")])
    phone = IntegerField('phone', validators=[DataRequired(), Length(min=10, max=10, message="Phone number must be 10 characters long!")])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=20, message="Password need to be 8-20 characters long!")])
    confirm_password = PasswordField('confirmpass', validators=[DataRequired(), EqualTo('password', message="Field must be equal to password!")])
    submit = SubmitField('SIGNUP')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long")])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('LOGIN')


class ForgotForm(FlaskForm):
   email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address")])
   submit = SubmitField("Request OTP")


class ResetForm(FlaskForm):
    otp = StringField('otp', validators=[DataRequired()])
    submit = SubmitField("Verify OTP")


class NewPForm(FlaskForm):
    newpassword = PasswordField('newpassword', validators=[DataRequired(), Length(min=8, max=20, message="Password need to be 8-20 characters long!")])
    confirmnewpassword = PasswordField('confirmnewpass', validators=[DataRequired(), EqualTo('newpassword')])
    submit = SubmitField("Submit")
