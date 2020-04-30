from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from wtforms.widgets import TextArea
import email_validator

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    sid = IntegerField('sid', validators=[DataRequired(), NumberRange(min=10000000, max=99999999, message="SID must be 8 characters long!")])
    email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long!")])
    phone = IntegerField('phone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=20, message="Password need to be 8-20 characters long!")])
    guardianname = StringField('guardianname', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    guardianphone = IntegerField('guardianphone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    address = StringField('address', validators=[DataRequired(), Length(max=50, message="Too Long")])
    batch = SelectField(u"Batch:", choices=[('1',"1"),('2','2'),('3','3'),('4','4')])
    submit = SubmitField('SIGNUP')

class StaffForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    staffid = IntegerField('staffid', validators=[DataRequired(), NumberRange(min=10000, max=99999, message="SID must be 5 characters long!")])
    email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long!")])
    phone = IntegerField('phone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=20, message="Password need to be 8-20 characters long!")])
    hostel = StringField('hostel')
    designation = StringField('designation', validators=[DataRequired()])
    submit = SubmitField('SIGNUP')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long")])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('LOGIN')


class UpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    picture = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    sid = IntegerField('SID', validators=[DataRequired(), NumberRange(min=10000000, max=99999999, message="sid must be 5 characters long!")])
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40,message="Email Address too long!")])
    phone = IntegerField('Phone', validators=[DataRequired(), NumberRange(min=1000000000,max=9999999999,message="Phone number must 10 digits long!")])
    guardianname = StringField("Guardian's Name", validators=[DataRequired(), Length(max=20, message="Name too long!")])
    guardianphone = IntegerField('guardianphone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    address = StringField('address', validators=[DataRequired(), Length(max=50, message="Too Long")])
    batch = SelectField(u"Batch:", choices=[('1',"1"),('2','2'),('3','3'),('4','4')])
    submit = SubmitField("Update")

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    # picture = FileField('Upload Profile Picture', validators=[FileAllowed('jpg, png', 'Images only!')])
    sid = IntegerField('SID', validators=[DataRequired(), NumberRange(min=10000000, max=99999999, message="sid must be 5 characters long!")])
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40,message="Email Address too long!")])
    phone = IntegerField('Phone', validators=[DataRequired(), NumberRange(min=1000000000,max=9999999999,message="Phone number must 10 digits long!")])
    guardianname = StringField("Guardian's Name", validators=[DataRequired(), Length(max=20, message="Name too long!")])
    guardianphone = IntegerField('guardianphone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    address = StringField('address', validators=[DataRequired(), Length(max=50, message="Too Long")])
    batch = SelectField(u"Batch:", choices=[('','---'),('1',"1"),('2','2'),('3','3'),('4','4')])
    hostel = SelectField(u"Hostel:", choices=[('','---'),('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')])
    roomnum = IntegerField("Room Number", validators=[DataRequired(), NumberRange(min=100, max=999, message="Room number must be of 3 digits!")]) 
    blacklist = SubmitField("Blacklist")


class UpdateStaffForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20, message="Name too long!")])
    picture = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    staffid = IntegerField('Staff ID', validators=[DataRequired(), NumberRange(min=10000, max=99999, message="SID must be 5 characters long!")])
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email Address"), Length(max=40, message="Email Id too long!")])
    phone = IntegerField('Phone', validators=[DataRequired(), NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 characters long!")])
    hostel = StringField("Hostel")
    designation = SelectField("Designation", choices=[('','---'),('Warden','WARDEN'),('Attendant','ATTENDANT'),('Admin','ADMIN')])
    submit = SubmitField('Update')


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


class ChangePass(FlaskForm):
    oldpassword = PasswordField('oldpassword', validators=[DataRequired()])
    newpassword = PasswordField('newpassword', validators=[DataRequired(), Length(min=8, max=20, message="Password need to be 8-20 characters long!")])
    confirmnewpassword = PasswordField('confirmnewpass', validators=[DataRequired(), EqualTo('newpassword')])
    submit = SubmitField("Submit")

class CheckProfile(FlaskForm):
    sid = IntegerField("Enter Student's ID", validators=[DataRequired(), NumberRange(min=10000000, max=99999999, message="SID must be 8 digits long!")])
    submit = SubmitField('Submit')


class AnnouncementForm(FlaskForm):
    hostel = SelectField(u"Hostel:", choices=[('','---'),('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')], validators=[DataRequired()])
    type = SelectField(u"Type:", choices=[('','---'),('General','GENERAL'),('Mess','MESS'),('Fees','FEES')], validators=[DataRequired()])
    title = StringField("Title:", validators=[DataRequired(), Length(max=30, message="Title too long!")], widget=TextArea())
    content = StringField("Content:", validators=[DataRequired(), Length(max=500, message="Limit to 500 words only!")], widget=TextArea())
    submit = SubmitField('Post')

class UAnnouncementForm(FlaskForm):
    hostel = SelectField(u"Hostel:", choices=[('','---'),('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')])
    type = SelectField(u"Type:", choices=[('','---'),('General','GENERAL'),('Mess','MESS'),('Fees','FEES')])
    title = StringField("Title:", validators=[DataRequired(), Length(max=30, message="Title too long!")], widget=TextArea())
    content = StringField("Content:", validators=[DataRequired(), Length(max=500, message="Limit to 500 words only!")], widget=TextArea())
    submit = SubmitField('Update')


class ComplaintForm(FlaskForm):
    hostel = SelectField(u"Hostel:", choices=[('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')])
    to = SelectField(u"To:", choices=[('Warden','WARDEN'),('Attendant','ATTENDANT'),('Admin','ADMIN')])
    title = StringField("Title:", validators=[DataRequired(), Length(max=30, message="Title too long!")], widget=TextArea())
    content = StringField("Content:", validators=[DataRequired(), Length(max=500, message="Limit to 500 words only!")], widget=TextArea())
    submit = SubmitField('Post')


class UComplaintForm(FlaskForm):
    hostel = SelectField(u"Hostel:", choices=[('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')])
    to = SelectField(u"To:", choices=[('Warden','WARDEN'),('Attendant','ATTENDANT'),('Admin','ADMIN')])
    title = StringField("Title:", validators=[DataRequired(), Length(max=30, message="Title too long!")], widget=TextArea())
    content = StringField("Content:", validators=[DataRequired(), Length(max=500, message="Limit to 500 words only!")], widget=TextArea())
    update = SubmitField('Update')


class RoomForm(FlaskForm):
    hostel = SelectField(u"Hostel", choices=[('','---'),('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')])
    floor = SelectField(u"Floor", choices=[('','---'),('0','Ground Floor'),('1','First Floor'),('2','Second Floor')])
    capacity = SelectField(u"Capacity", choices=[('','---'),('1','1'),('2','2'),('3','3')])
    batch = SelectField(u"Allotting Rooms for", choices=[('','---'),('1','First Year'),('2','Second Year'),('3','Third Year'),('4','Fourth Year')])
    reset = SubmitField("Reset All")


class UploadForm(FlaskForm):
    hostel = SelectField(u"Hostel", choices=[('','---'),('Himalaya','HIMALAYA'),('Shivalik','SHIVALIK')], validators=[DataRequired()])
    file = FileField('Upload excel file of list of students.', validators=[DataRequired(), FileAllowed(['xlsx'], message='.xlsx files only')])
    post = SubmitField('Upload')