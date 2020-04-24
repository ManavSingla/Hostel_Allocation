from flask import Flask, render_template, request, flash, url_for, redirect, sessions, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm, ForgotForm, ResetForm, NewPForm
import sms
import random
from datetime import date


app = Flask(__name__)

app.config['SECRET_KEY'] = 'AjJ0lXaX5K9tai8QsUhwwQ'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html', title="Home")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             cur = mysql.connection.cursor()
#             user_details = request.form
#             name = user_details['name']
#             sid = user_details['sid']
#             email = user_details['email']
#             phone = user_details['phone']
#             password = user_details['password']
#             confirm_password = user_details['confirm_password']
#             hashed_pass = bcrypt.generate_password_hash(user_details['password']).decode('utf-8')
#             values = (name, sid, email, phone, hashed_pass)

#             if password == confirm_password:
#                 try:
#                     sql_formula = "INSERT INTO students (name, sid, email, phone, password) VALUES (%s, %s, %s, %s, %s)"
#                     cur.execute(sql_formula, values)
#                 except:
#                     flash("Account already exists",'info')
#                     return redirect(url_for('slogin'))
#                 else:
#                     mysql.connection.commit()
#                     flash("Thanks for Registering", 'success')
#                 cur.close()
#                 return redirect(url_for('slogin'))
#             else:
#                 flash("Password didnt match", 'danger')
#                 return redirect(url_for('register'))
#     return render_template('register.html', title="register",form = form)


@app.route('/studentlogin', methods=['GET', 'POST'])
def slogin():
    if session.get('user'):
        session.pop('user', None)
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            user_details = request.form
            email = user_details['email']
            password = user_details['password']
            cur.execute(f"SELECT password FROM students where email = '{email}'")
            fetch = cur.fetchone()
            if fetch == None:
                flash("This account is not valid! Please enter valid credentials.", 'danger')
                return redirect(url_for('slogin'))
            else:
                if (bcrypt.check_password_hash(fetch[0], password)):
                    session['user'] = email
                    cur.execute(f"SELECT name FROM students where email = '{email}'")
                    fetch = cur.fetchone()
                    flash(f"Welcome {fetch[0]}", 'success')
                    cur.close()
                    return redirect(url_for('index'))
                else:
                    flash("WRONG PASSWORD", 'danger')
                    cur.close()
                    return redirect(url_for('slogin'))
    return render_template('studentlogin.html', title="Login", form=form)



@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            details = request.form
            email = details['email']
            cur.execute(f"SELECT phone FROM students where email = '{email}'")
            fetch = cur.fetchone()
            cur.close()
            if fetch == None:
                flash("This Email address is invalid! Please enter valid one.",'danger')
                return redirect(url_for('forgot'))
            else:
                session['email'] = email
                session['phone'] = fetch[0]
                return redirect(url_for('resetpass'))

    return render_template('forgot.html',form=form)          



@app.route('/reset', methods=['GET', 'POST'])
def resetpass():
    form = ResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            otp_check = form.data['otp']
            if otp_check == session['otp']:
                return redirect(url_for('newpass'))
            else:
                flash('INVALID OTP', 'danger')
                return redirect(url_for('resetpass'))

    otp = str(random.randrange(100000, 999999))
    print(otp)
    URL = 'https://www.sms4india.com/api/v1/sendCampaign'
    session['otp']=otp
    # sms.sendPostRequest(URL, 'C23FTIDPYUYZVP7UV238S0QC1POBFWMR', 'N1AY9Q2S52NHUADE', 'stage', phone, '9781396442', f"Your OTP (One Time Password) to change your password is: {otp1} Do not share this with anyone!   Team college+")

    return render_template('verifyotp.html',form=form)



@app.route('/newpass', methods=['GET', 'POST'])
def newpass():
    form = NewPForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            newpass = form.data['newpassword']
            c_newpass = form.data['confirmnewpassword']
            if newpass == c_newpass:
                hashed_pass = bcrypt.generate_password_hash(newpass).decode('utf-8')
                cur = mysql.connection.cursor()
                cur.execute(f"UPDATE students set password = '{hashed_pass}' where email = '{session['email']}'")
                mysql.connection.commit()
                flash("Password Changed Successfully", 'success')
                return redirect(url_for('login'))
            else:
                flash("passwords didnt match", 'danger')
                return redirect(url_for('newpass'))
    return render_template('newpass.html', form=form)



@app.route('/facultylogin', methods=['GET', 'POST'])
def flogin():
    # if session.get('user'):
    #     session.pop('user', None)
    # if request.method == POST:
    #     cur = mysql.connection.cursor()
    #     user_details = request.form
    #     email = user_details['logid']
    #     password = user_details['password']
    #     cur.execute(f"SELECT password FROM faculty where email = '{email}'")
    #     fetch = cur.fetchone()
    #     if fetch == None:
    #         flash("Only Faculty can Login. Contact admin if you think this is a mistake.",'danger')
    #         return redirect(url_for('index'))
    #     if (bcrypt.check_password_hash(fetch[0], password)):
    #         session['user'] = email
    #         return redirect(url_for('flogin'))
    #     else:
    #         flash('Invalid Username or Password', 'danger')
    #         return redirect(url_for('flogin'))

    return render_template('facultylogin.html', title="Login")



@app.route('/announcement')
def announcement():

    return render_template('announcement.html')



@app.route('/postcomplaint')
def postcomplaint():

    return render_template('postcomplaint.html')


@app.route('/uploadfile')
def uploadfile():

    return render_template('uploadfile.html')

if __name__ == "__main__":
    app.run(debug = True)
