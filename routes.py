import secrets
import os
from PIL import Image
from flask import Flask, render_template, request, flash, url_for, redirect, sessions, session, send_file
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm, ForgotForm, ResetForm, NewPForm, CheckProfile, ChangePass, UpdateForm, StaffForm, AnnouncementForm, ComplaintForm, RoomForm, UComplaintForm, ProfileForm, UpdateStaffForm, UAnnouncementForm, UploadForm
import sms
import random
from datetime import datetime
from werkzeug.utils import secure_filename



app = Flask(__name__)

app.config['SECRET_KEY'] = 'AjJ0lXaX5K9tai8QsUhwwQ'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)
bcrypt = Bcrypt(app)








################################################################################################## INDEX ###############


@app.route('/')
def index():
    return render_template('index.html', title="Home")



############################################################################## STUDENT PART #########


############################################################################## STUDENT REGISTRATION ###########

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            user_details = request.form
            name = user_details['name']
            sid = user_details['sid']
            email = user_details['email']
            phone = user_details['phone']
            password = user_details['password']
            guardianname = user_details['guardianname']
            guardianphone = user_details['guardianphone']
            address = user_details['address']
            batch = user_details['batch']
            hashed_pass = bcrypt.generate_password_hash(user_details['password']).decode('utf-8')
            values = (name, sid, email, phone, hashed_pass, guardianname,guardianphone,address,batch)
            sql_formula = "INSERT INTO studentinfo (name, sid, email, phone, password, guardianname, guardianphone, address, batch) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql_formula, values)
            mysql.connection.commit()
            flash("Thanks for Registering", 'success')
            cur.close()
            return redirect(url_for('slogin'))
        else:
            flash("Password didnt match", 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', title="register",form = form)




########################################################################### STUDENT LOGIN ###############

@app.route('/studentlogin', methods=['GET', 'POST'])
def slogin():
    session.pop('faculty', None)    
    if session.get('user'):
        flash("You're already logged in!", 'info')
        return redirect(url_for('shome'))
    else:
        form = LoginForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                cur = mysql.connection.cursor()
                user_details = request.form
                email = user_details['email']
                password = user_details['password']
                cur.execute(f"SELECT password FROM studentinfo where email = '{email}'")
                fetch = cur.fetchone()
                if fetch == None:
                    flash("This account is not valid! Please enter valid credentials.", 'danger')
                    return redirect(url_for('slogin'))
                else:
                    if (bcrypt.check_password_hash(fetch[0], password)):
                        session['email'] = email
                        cur.execute(f"SELECT name, sid FROM studentinfo where email = '{email}'")
                        fetch = cur.fetchone()
                        session['user'] = fetch[0]
                        session['sid'] = fetch[1]
                        flash(f"Welcome {fetch[0]}", 'success')
                        cur.close()
                        return redirect(url_for('shome'))
                    else:
                        flash("WRONG PASSWORD", 'danger')
                        cur.close()
                        return redirect(url_for('slogin'))
        return render_template('studentlogin.html', title="Login", form=form)





################################################################################# STUDENT HOME ###############


@app.route('/studenthome')
def shome():
    if session.get('user'):
        profile = session['user']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT  hostel from studentinfo where email = '{session['email']}'")
        fetch=cur.fetchone()
        hostel=fetch[0]
        if hostel == None:
            flash("Please Select a Room First!", 'danger')
            return redirect(url_for('selectroom'))
        cur.execute(f"SELECT * from announcements where hostel = '{hostel}' and datediff(current_timestamp,postdate)<7 order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('studenthome.html', post=fetch, name=profile)
        else:
            flash("No Announcements Yet!",'info')
            return render_template('studenthome.html', name=profile)

    else:
        flash("You need to log in first!", 'danger')
        return redirect(url_for('slogin'))





###################################################################################### ALL ANNOUNCEMENT #############


@app.route('/announcements')
def watchannouncement():
    if session.get('user'):
        profile = session['user']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT hostel from studentinfo where email='{session['email']}'")
        fetch= cur.fetchone()
        cur.execute(f"SELECT * from announcements where hostel='{fetch[0]}' order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('watchannouncement.html', post=fetch, name=profile)
        else:
            flash("No Announcement Posted Yet!", "info")
            return render_template('watchannouncement.html', name=profile)
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))






################################################################################### COMPLAINTS ################


@app.route('/postcomplaint', methods=['GET', 'POST'])
def postcomplaint():
    if session.get('user'):
        profile = session['user']
        form = ComplaintForm()
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT hostel from studentinfo where email='{session['email']}'")
        fetch= cur.fetchone()
        if fetch[0] == None:
            flash("Please Select a Room First to post complaints!", 'danger')
            return redirect(url_for('selectroom'))
        
        else:
            form.hostel.data = fetch[0]
            hostel = fetch[0]
        if request.method == 'POST':
            if form.validate_on_submit():
                details = request.form
                to = details['to']
                title = details['title']
                postdate = datetime.now()
                content = details['content']
                cur.execute(f"SELECT sid, name from studentinfo where email = '{session['email']}'")
                fetch=cur.fetchone()
                sid = fetch[0]
                name = fetch[1]
                values = (sid, name, content, title, postdate, to, hostel)
                sql_formula = "INSERT INTO studentqueries (sid, name, content, title, postdate, reciever, hostel) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql_formula, values)
                cur.execute(f"SELECT picture from studentinfo where sid = '{session['sid']}'")
                picture=cur.fetchone()
                cur.execute(f"UPDATE studentqueries set picture = '{picture[0]}' where sid = '{session['sid']}'")
                mysql.connection.commit()
                flash("Complaint Posted Successfully!", 'success')
                return redirect(url_for('postcomplaint'))
            else:
                flash("Unsuccessfull", 'danger')

                   
        cur.execute(f"SELECT * from studentqueries where hostel='{hostel}' and sid = '{session['sid']}' order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('postcomplaint.html', form=form, post=fetch, name=profile)
        else:
            flash("No complaints added yet!", 'success')
            return render_template('postcomplaint.html', form=form, name=profile)

    else:
        flash("Please Log In First!", 'danger')
        return redirect(url_for('slogin'))




@app.route('/complaint<int:queryno>')
def complaint(queryno):
    if session.get('user'):
        profile = session['user']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT name from studentqueries where qno = {queryno}")
        fetch = cur.fetchone()
        if fetch:
            if session['user'] == fetch[0]:
                cur.execute(f"SELECT * from studentqueries where qno = {queryno} ")
                fetch = cur.fetchone()
                return render_template('showcomplaint.html', post = fetch, name=profile)
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('shome'))
        else:
            flash("Complaint not available!", 'info')
            return redirect(url_for('shome'))
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))


@app.route('/updatecomplaint<int:queryno>', methods=['GET', 'POST'])
def updatecomplaint(queryno):
    if session.get('user'):
        form = UComplaintForm()
        profile = session['user']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT name from studentqueries where qno = {queryno}")
        fetch = cur.fetchone()
        if fetch:
            if session['user'] == fetch[0]:
                cur.execute(f"SELECT hostel from studentqueries where qno = {queryno}")
                fetch = cur.fetchone()
                form.hostel.data = fetch[0]
                if request.method == 'POST':
                    print(form.hostel.data)
                    if form.validate_on_submit():
                        cur.execute(f"UPDATE studentqueries set reciever='{form.to.data}', title= '{form.title.data}', content= '{form.content.data}' where qno = {queryno}")
                        mysql.connection.commit()
                        flash("Update Successfull!", 'success')
                        return redirect(url_for('postcomplaint'))
                    else:
                        flash('failed','danger')
                cur.execute(f"SELECT * from studentqueries where qno = {queryno}")
                fetch = cur.fetchone()
                form.to.data = fetch[4]
                form.title.data = fetch[5]
                form.content.data = fetch[2]

                return render_template('updatecomplaint.html', form=form, name=profile)
            
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('shome'))
        else:
            flash(f"Complaint not available!", 'info')
            return redirect(url_for('shome'))

    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))


@app.route('/deletecomplaint<int:queryno>')
def deletecomplaint(queryno):
    if session.get('user'):
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT name from studentqueries where qno = {queryno}")
        fetch = cur.fetchone()
        if fetch:
            if session['user'] == fetch[0]:
                cur.execute(f"DELETE from studentqueries where qno = {queryno}")
                mysql.connection.commit()
                flash("Complaint Successfully Deleted!", 'success')
                return redirect('postcomplaint')
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('shome'))
        else:
            flash(f"Complaint not available!", 'info')
            return redirect(url_for('shome'))   
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))





##################################################################################### ROOM SELECTION #############


@app.route('/selectroom', methods=['GET','POST'])
def selectroom():
    if session.get('user'):
        form = RoomForm()
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT hostel from studentinfo where email = '{session['email']}'")
        hostel = cur.fetchone()
        if hostel[0] == None:
            profile = session['user']
            rooms=[]
            vacant=[]
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT batch from studentinfo where email='{session['email']}'")
            batch = cur.fetchone()
            cur.execute(f"SELECT * from rooms where year = {batch[0]} and status <> 1")
            fetch = cur.fetchall()
            if fetch:
                if request.method == 'POST':
                    cur.execute(f"SELECT * from rooms where year = {batch[0]} and hostel='{form.hostel.data}' and status <> 1")
                    fetch = cur.fetchall()
                    if fetch:
                        if hostel != '':
                            hostel = form.hostel.data
                            floor = form.floor.data
                            capacity = form.capacity.data
                            if floor != '' and capacity != '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel}' and floor = {floor} and year = {batch[0]} and capacity = {capacity} order by roomnum ")
                            elif floor != '' and capacity == '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel}' and floor = {floor} and year = {batch[0]} order by roomnum ")
                            elif floor == '' and capacity != '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel}' and capacity = {capacity} and year = {batch[0]} order by roomnum ") 
                            elif floor =='' and capacity =='':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel}' and year = {batch[0]} order by roomnum ")
                            fetch = cur.fetchall()
                            for i in fetch:
                                if i[8]==0:
                                    vacant.append(i[0])
                                rooms.append(i[0])
                            l = len(rooms)//10
                            r = len(rooms)%10
                            return render_template('selectroom.html',form=form, rooms=rooms, vacant=vacant,l=l,r=r, name=profile)
                    else:
                        flash(f"Allotment Criteria is not released for {form.hostel.data} yet! or All rooms are filled!", 'info')
                        return redirect(url_for('selectroom'))
                return render_template('selectroom.html',form=form, rooms=rooms, vacant=vacant, name=profile)
            
            else:
                flash("Allotment Criteria is not released yet! or All rooms are filled! Contact Attendant.", 'info')
                return render_template('noroom.html', name=profile)

        else:
            flash("You already have a room!", 'info')
            return redirect(url_for('shome'))
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))



@app.route("/selected<hostelname>s<int:roomnum>")
def selected(roomnum=None,hostelname=None):
    if session.get('user'):
        profile = session['user']
        form = RoomForm()
        cur =  mysql.connection.cursor()
        cur.execute(f"SELECT hostel,batch from studentinfo where email = '{session['email']}'")
        fetch = cur.fetchone()
        batch = fetch[1]
        if fetch[0] == None:
            cur.execute(f"SELECT year,status from rooms where roomnum = {roomnum}")
            fetch = cur.fetchone()
            year = fetch[0]
            status = fetch[1]
            if year == batch:
                if status == 0:
                    cur.execute(f"UPDATE studentinfo set hostel= '{hostelname}', roomnum = '{roomnum}' where email= '{session['email']}'")
                    cur.execute(f"SELECT capacity, totalin from rooms where hostel ='{hostelname}' and roomnum={roomnum}")
                    fetch = cur.fetchone()
                    capacity = fetch[0]
                    totalin = fetch[1]
                    temp = totalin+1
                    cur.execute(f"SELECT sid from studentinfo where email ='{session['email']}'")
                    fetch=cur.fetchone()
                    cur.execute(f"UPDATE rooms set seater{temp}='{fetch[0]}' where hostel='{hostelname}' and roomnum={roomnum}")
                    totalin=totalin+1
                    if totalin == capacity:
                        cur.execute(f"UPDATE rooms set status=1 where hostel='{hostelname}' and roomnum={roomnum}")
                    cur.execute(f"UPDATE rooms set totalin={totalin} where hostel='{hostelname}' and roomnum={roomnum}")
                    flash(" Room Successfully Registered!",'success')
                    mysql.connection.commit()


                    cur.execute(f"SELECT floor, capacity from rooms where hostel='{hostelname}' and roomnum={roomnum}")
                    fetch = cur.fetchone()
                    floor = fetch[0]
                    form.hostel.data= hostelname
                    form.floor.data = str(floor)
                    form.capacity.data = str(capacity)
                    cur.execute(f"SELECT batch from studentinfo where email='{session['email']}'")
                    fetch = cur.fetchone()
                    batch=fetch[0]
                    cur.execute(f"SELECT * from rooms where hostel = '{hostelname}' and floor = {floor} and year = {batch} order by roomnum ")
                    fetch = cur.fetchall()
                    rooms=[]
                    vacant=[]
                    for i in fetch:
                        if i[8]==0:
                            vacant.append(i[0])
                        rooms.append(i[0])
                    l = len(rooms)//10
                    r = len(rooms)%10
                    return render_template('selected.html',form=form,roomnum=roomnum,rooms=rooms,vacant=vacant,l=l,r=r, name=profile)
                else:
                    flash("This Room is already filled!", 'info')
                    return redirect('selectroom')
            else:
                flash("Room not available for you!", 'danger')
                return redirect('selectroom')
        else:
            flash("You already have a room!", 'info')
            return redirect(url_for('shome'))

    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))



############################################################################# UPDATE PROFILE ##############


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_fn)
    print (picture_path)

    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn



@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if session.get('user'):
        form = UpdateForm()
        email = session['email']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT picture from studentinfo where email = '{session['email']}'")
        pic = cur.fetchone()
        image_file = url_for('static', filename=f"img/profile_pics/{pic[0]}" )
        print (image_file)
        cur.execute(f"SELECT batch from studentinfo where email = '{session['email']}'")
        fetch = cur.fetchone()
        form.batch.data = str(fetch[0])
        if request.method == 'POST':
            print(form.batch.data)
            if form.validate_on_submit():
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    cur.execute(f"UPDATE studentinfo set picture = '{picture_file}' where email = '{session['email']}'")
                    cur.execute(f"UPDATE studentqueries set picture = '{picture_file}' where sid = '{session['sid']}'")
                print(form.name.data)
                cur.execute(f"UPDATE studentinfo set phone = '{form.phone.data}', batch = {form.batch.data}, guardianname = '{form.guardianname.data}', guardianphone = {form.guardianphone.data}, address = '{form.address.data}' where email = '{email}'")
                mysql.connection.commit()
                cur.close()
                flash("Update Successfull!", 'success')
                return redirect(url_for('updateprofile'))

        cur.execute(f"SELECT name, sid, email, phone, guardianname, guardianphone, address, batch from studentinfo where email = '{session['email']}'")
        fetch = cur.fetchone()
        print(fetch)
        form.name.data = fetch[0]
        form.sid.data = fetch[1]
        form.email.data = fetch[2]
        form.phone.data = fetch[3]
        form.guardianname.data = fetch[4]
        form.guardianphone.data = fetch[5]
        form.address.data = fetch[6]
        cur.close()
        return render_template('updateprofile.html',form=form, image_file=image_file)

    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('slogin'))






######################################################################################### ALLOTMENT STATUS ##########


@app.route('/allotmentstatus')
def allotmentstatus():
    if session.get('user'):
        profile = session['user']
        cur = mysql.connection.cursor()
        rooms=[]
        vacant=[]
        cur.execute(f"SELECT hostel, roomnum from studentinfo where email='{session['email']}'")
        fetch = cur.fetchone()
        if fetch[0] != None:
            roomnum = fetch[1]
            cur.execute(f"SELECT * from rooms where hostel = '{fetch[0]}'")
            fetch = cur.fetchall()
            for i in fetch:
                rooms.append(i[0])
                if i[8]==0:
                    vacant.append(i[0])
            l = len(rooms)//10
            r = len(rooms)%10
            return render_template('allotmentstatus.html',rooms=rooms,vacant= vacant,l=l,r=r, name=profile, roomnum = roomnum)
        else:
            flash("No room is allocated to you. Select a room first!", 'danger')
            return redirect(url_for('selectroom'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('slogin'))






############################################################################## STUDENT CHANGE PASSWORD #############



@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            details = request.form
            email = details['email']
            cur.execute(f"SELECT phone FROM studentinfo where email = '{email}'")
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
    sms.sendPostRequest(URL, 'NF6N0V2YKJIB72BZ9NEYI706Z4Y8BGJ5', 'HXCL4DM4TI2MCPWM', 'stage', session['phone'], '9592260601', f"Your OTP (One Time Password) to change your password is: {otp} Do not share this with anyone!   PEC")

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
                cur.execute(f"UPDATE studentinfo set password = '{hashed_pass}' where email = '{session['email']}'")
                mysql.connection.commit()
                flash("Password Changed Successfully", 'success')
                return redirect(url_for('slogin'))
            else:
                flash("passwords didnt match", 'danger')
                return redirect(url_for('newpass'))
    return render_template('newpass.html', form=form)


@app.route('/changepass',methods=['GET','POST'])
def changepass():
    form=ChangePass()
    if request.method=='POST':
        if form.validate_on_submit():
            oldp=form.oldpassword.data
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT password from studentinfo where email = '{session['email']}' ")
            fetch = cur.fetchone()
            if (bcrypt.check_password_hash(fetch[0], oldp)):
                newpassworda = bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
                cur.execute(f" UPDATE  studentinfo  set password = '{newpassworda}' where email= '{session['email']}' ")
                mysql.connection.commit()
                flash('Update successfull', 'success')
                return redirect(url_for('shome'))
            else:
                flash('Enter Correct old password', 'danger')
                return redirect(url_for('changepass'))
    print (session['email'])
    return render_template('changepass.html',form=form,title="Change Password")





















########################################################################################### FACULTY SIDE ##########



######################################################################################## FACULTY REGISTER ###########
 
@app.route('/staffregister', methods=['GET', 'POST'])
def sregister():
    form = StaffForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            user_details = request.form
            name = user_details['name']
            staffid = user_details['staffid']
            email = user_details['email']
            phone = user_details['phone']
            password = user_details['password']
            hostel = user_details['hostel']
            designation = user_details['designation']
            hashed_pass = bcrypt.generate_password_hash(user_details['password']).decode('utf-8')
            if hostel != "":
                values = (name, staffid, email, phone, hashed_pass, hostel, designation)
                sql_formula = "INSERT INTO staffinfo (name, staffid, email, phone, password, hostel, designation) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            else:
                values = (name, staffid, email, phone, hashed_pass, designation)
                sql_formula = "INSERT INTO staffinfo (name, staffid, email, phone, password, designation) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql_formula, values)
            mysql.connection.commit()
            flash("Thanks for Registering", 'success')
            cur.close()
            return redirect(url_for('sregister'))
    return render_template('sregister.html', title="register",form = form)





####################################################################################### FACULTY LOGIN ###############


@app.route('/facultylogin', methods=['GET', 'POST'])
def flogin():
    form = LoginForm()
    if session.get('user'):
        session.pop('user', None)
    if session.get('faculty'):
        flash("You are already logged in!", 'info')
        return redirect(url_for('facultyhome'))
    else:
        if request.method == 'POST':
            if form.validate_on_submit():
                cur = mysql.connection.cursor()
                user_details = request.form
                email = user_details['email']
                password = user_details['password']
                cur.execute(f"SELECT password FROM staffinfo where email = '{email}'")
                fetch = cur.fetchone()
                if fetch == None:
                    flash("Only Faculty can Login. Contact admin if you think this is a mistake.",'danger')
                    return redirect(url_for('flogin'))
                else:
                    if (bcrypt.check_password_hash(fetch[0], password)):
                        session['email'] = email
                        cur.execute(f"SELECT name, staffid, designation from staffinfo where email ='{email}'")
                        fetch = cur.fetchone()
                        session['faculty'] = fetch[0]
                        session['staffid'] = fetch[1]
                        session['designation'] = fetch[2]
                        flash(f"Welcome {fetch[0]}", 'success')
                        cur.close()
                        return redirect(url_for('facultyhome'))
                    else:
                        flash('Invalid Username or Password', 'danger')
                        cur.close()
                        return redirect(url_for('flogin'))

        return render_template('facultylogin.html', title="Login", form=form)





######################################################################################## FACULTY HOME ##############


@app.route('/facultyhome', methods=['GET', 'POST'])
def facultyhome():
    if session.get('faculty'):
        profile = session['faculty']
        form = CheckProfile()
        cur = mysql.connection.cursor()
        if request.method == 'POST':
            if form.validate_on_submit():
                cur.execute(f"SELECT sid from studentinfo where sid = '{form.data['sid']}'")
                temp = cur.fetchone()
                if temp == None:
                    flash("Enter a valid SID", 'danger')
                    return redirect(url_for('facultyhome'))
                else:
                    cur.execute(f"SELECT hostel from studentinfo where sid = '{form.data['sid']}'")
                    fetch = cur.fetchone()
                    if fetch[0]==None:
                        if session['designation'] == 'Admin':
                            return redirect(url_for('profile',studentid=temp[0]))
                        else:
                            flash("Student is not from this hostel!",'info')
                            return redirect(url_for('facultyhome'))
                    else:
                        print (temp[0])
                        return redirect(url_for('profile',studentid=temp[0]))
        cur.execute(f"SELECT designation from staffinfo where email = '{session['email']}'")
        fetch = cur.fetchone()
        cur.execute(f"SELECT * from studentqueries where reciever= '{fetch[0]}' and datediff(current_timestamp, postdate)<7 order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('facultyhome.html', form=form, post=fetch, name=profile)
        else:
            flash("No Complaint By Students yet!", 'info')
            return render_template('facultyhome.html', form=form, name=profile)
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))





####################################################################################### UPDATE PROFILE ################



@app.route('/updatefacultyprofile', methods=['GET','POST'])
def facultyprofile():
    if session.get('faculty'):
        profile = session['faculty']
        form = UpdateStaffForm()
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT picture from staffinfo where email = '{session['email']}'")
        pic = cur.fetchone()
        image_file = url_for('static', filename=f"img/profile_pics/{pic[0]}" )
        cur.execute(f"SELECT hostel, designation from staffinfo where email = '{session['email']}'")
        fetch = cur.fetchone()
        form.designation.data = str(fetch[1])
        if request.method == 'POST':
            if form.validate_on_submit():
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    cur.execute(f"UPDATE staffinfo set picture = '{picture_file}' where email = '{session['email']}'")
                    cur.execute(f"UPDATE announcements set picture = '{picture_file}' where authorid = '{session['staffid']}'")
                cur.execute(f"UPDATE staffinfo set phone = {form.phone.data} where email = '{session['email']}'")
                mysql.connection.commit()
                flash('Successfully Updated', 'success')
                return redirect(url_for('facultyprofile'))

        cur.execute(f"SELECT * from staffinfo where email='{session['email']}'")
        fetch = cur.fetchone()
        form.name.data = fetch[1]
        form.staffid.data = fetch[0]
        form.email.data = fetch[2]
        form.phone.data = fetch[5]
        if fetch[4]!=None:
            form.hostel.data= fetch[4]
        else:
            form.hostel.data = '---'
        return render_template('updatefaculty.html', form=form, name=profile, image_file=image_file)
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))





######################################################################################### FACULTY ANNOUNCEMENT #######


@app.route('/facultyannouncement', methods=['GET', 'POST'])
def announcement():
    if session.get('faculty'):
        profile = session['faculty']
        form = AnnouncementForm()
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT hostel from staffinfo where email='{session['email']}'")
        fetch= cur.fetchone()
        if fetch[0] != None:
            form.hostel.data = fetch[0]
            hostel = fetch[0]

        if request.method == 'POST':
            if form.validate_on_submit():
                details = request.form
                type = details['type']
                title = details['title']
                postdate = datetime.now()
                content = details['content']
                cur.execute(f"SELECT staffid, name from staffinfo where email = '{session['email']}'")
                fetch=cur.fetchone()
                authorid = fetch[0]
                author = fetch[1]
                try:
                    values = (authorid, content, postdate, title, type, hostel, author)
                except:
                    hostel = form.hostel.data
                    values = (authorid, content, postdate, title, type, hostel, author)
                sql_formula = "INSERT INTO announcements (authorid, content, postdate, title, type, hostel, author) VALUES (%s,%s, %s, %s, %s, %s, %s)"
                cur.execute(sql_formula, values)
                cur.execute(f"SELECT picture from staffinfo where email = '{session['email']}'")
                picture=cur.fetchone()
                cur.execute(f"UPDATE announcements set picture = '{picture[0]}' where authorid='{session['staffid']}'")
                mysql.connection.commit()
                flash("Announcement Posted Successfully!", 'success')
                return redirect(url_for('announcement'))
            else:
                flash("Announcement Posted unSuccessfully!", 'success')


        cur.execute(f"SELECT staffid from staffinfo where email='{session['email']}'")
        fetch= cur.fetchone()
        cur.execute(f"SELECT * from announcements where authorid={fetch[0]} order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('facultyannouncement.html',form=form,post=fetch, name=profile)
        else:
            flash("No Announcement Posted Yet!", "info")
            return render_template('facultyannouncement.html',form=form, name=profile)
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))



@app.route('/announcement<int:ano>')
def openannouncement(ano):
    if session.get('faculty'):
        profile = session['faculty']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT staffid from staffinfo where email = '{session['email']}'")
        staffid = cur.fetchone()
        cur.execute(f"SELECT authorid from announcements where ano = {ano}")
        fetch = cur.fetchone()
        if fetch:
            if staffid[0] == fetch[0]:
                cur.execute(f"SELECT * from announcements where ano = {ano} ")
                fetch = cur.fetchone()
                return render_template('showannouncement.html', post = fetch, name=profile)
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('fhome'))
        else:
            flash("Announcement not available!", 'info')
            return redirect(url_for('fhome'))
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))



@app.route('/updateannouncement<int:ano>', methods=['GET', 'POST'])
def updateannouncement(ano):
    if session.get('faculty'):
        form = UAnnouncementForm()
        profile = session['faculty']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT staffid from staffinfo where email = '{session['email']}'")
        staffid = cur.fetchone()
        cur.execute(f"SELECT authorid from announcements where ano = {ano}")
        fetch = cur.fetchone()
        if fetch:
            if staffid[0] == fetch[0]:
                cur.execute(f"SELECT hostel from announcements where ano = {ano}")
                fetch = cur.fetchone()
                if fetch[0] != None:
                    form.hostel.data = str(fetch[0])
                if request.method == 'POST':
                    if form.validate_on_submit():
                        cur.execute(f"UPDATE announcements set type='{form.type.data}', title= '{form.title.data}', content= '{form.content.data}' where ano = {ano}")
                        mysql.connection.commit()
                        flash("Update Successfull!", 'success')
                        return redirect(url_for('announcement'))
                    else:
                        flash('failed','danger')
                cur.execute(f"SELECT * from announcements where ano = {ano}")
                fetch = cur.fetchone()
                form.type.data = fetch[6]
                form.title.data = fetch[5]
                form.content.data = fetch[3]
                if fetch[7] != None:
                    form.hostel.data = fetch[7]

                return render_template('updateannouncement.html', form=form, name=profile)
            
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('fhome'))
        else:
            flash(f"Announcement not available!", 'info')
            return redirect(url_for('fhome'))

    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))


@app.route('/deleteannouncement<int:ano>')
def deleteannouncement(ano):
    if session.get('faculty'):
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT staffid from staffinfo where email = '{session['email']}'")
        staffid = cur.fetchone()
        cur.execute(f"SELECT authorid from announcements where ano = {ano}")
        fetch = cur.fetchone()
        if fetch:
            if staffid[0] == fetch[0]:
                cur.execute(f"DELETE from announcements where ano = {ano}")
                mysql.connection.commit()
                flash("Announcement Successfully Deleted!", 'success')
                return redirect(url_for('announcement'))
            else:
                flash("You cannot access that!",'danger')
                return redirect(url_for('fhome'))
        else:
            flash(f"Announcement not available!", 'info')
            return redirect(url_for('fhome'))   
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))




############################################################################################ BLACKLIST STUDENT ##########


@app.route('/student<studentid>', methods=['GET', 'POST'])
def profile(studentid):
    if session.get('faculty'):
        profile = session['faculty']
        cur = mysql.connection.cursor()
        form = ProfileForm()
        cur.execute(f"SELECT name from studentinfo where sid = '{studentid}'")
        name = cur.fetchone()
        if name:
            cur.execute(f"SELECT * from studentinfo where sid = '{studentid}'")
            fetch = cur.fetchone()
            form.name.data = fetch[1]
            form.sid.data = fetch[0]
            form.email.data = fetch[2]
            form.phone.data = fetch[4]
            form.guardianname.data = fetch[5]
            form.guardianphone.data = fetch[6]
            form.address.data = fetch [7]
            form.batch.data = str(fetch[8])
            if fetch[9] == None:
                form.hostel.data = "None"
            else:
                form.hostel.data = fetch[9]
            if fetch[10] == None:
                form.roomnum.data = "---"
            else:
                form.roomnum.data = fetch[10]
            if request.method == 'POST':
                cur.execute(f"DELETE from studentqueries where sid = '{studentid}'")
                cur.execute(f"SELECT roomnum from studentinfo where sid = '{studentid}'")
                roomnum = cur.fetchone()
                if roomnum[0] != None:
                    cur.execute(f"SELECT seater1, seater2, seater3, capacity from rooms where roomnum={roomnum[0]}")
                    fetch = cur.fetchone()
                    if fetch[3] == 1:
                        cur.execute(f"UPDATE rooms set seater1=null, totalin=0, status=0 where roomnum={roomnum[0]}")
                    elif fetch[3] == 2:
                        if fetch[0]==studentid:
                            if fetch[1]!=None:
                                cur.execute(f"UPDATE rooms set seater1 = '{fetch[1]}', seater2=null, totalin = 1, status=0 where roomnum={roomnum[0]}")
                            else:
                                cur.execute(f"UPDATE rooms set seater1 = null, totalin=0 where roomnum={roomnum[0]}")
                        elif fetch[1] == studentid:
                            cur.execute(f"UPDATE rooms set seater2 = null, totalin=1,status=0 where roomnum={roomnum[0]}")
                    elif fetch[3] == 3:
                        if fetch[0]==studentid:
                            if fetch[1] != None and fetch[2] != None:
                                cur.execute(f"UPDATE rooms set seater1 = '{fetch[1]}', seater2 = '{fetch[2]}', seater3= null, totalin = 2, status=0 where roomnum={roomnum[0]}")
                            elif fetch[1] != None and fetch[2] == None:
                                cur.execute(f"UPDATE rooms set seater1 = '{fetch[1]}', seater2 = null, totalin=1 where roomnum={roomnum[0]}")
                            elif fetch[1]==None:
                                cur.execute(f"UPDATE rooms set seater1=null, totalin=0 where roomnum={roomnum[0]}")
                        elif fetch[1] == studentid:
                            if fetch[2]!=None:
                                cur.execute(f"UPDATE rooms set seater2 = '{fetch[2]}',seater3=null,totalin=2,status=0 where roomnum={roomnum[0]}")
                            elif fetch[2]==None:
                                cur.execute(f"UPDATE rooms set seater2=null, totalin=1 where roomnum={roomnum[0]}")
                        elif fetch[2]==studentid:
                            cur.execute(f"UPDATE rooms set seater3=null, totalin=2,status=0 where roomnum={roomnum[0]}")
                cur.execute(f"DELETE FROM studentinfo where sid = '{studentid}'")
                mysql.connection.commit()
                flash(f"{name[0]} is blacklisted!", 'success')
                cur.close()
                return redirect(url_for('facultyhome'))

            cur.close()
            return render_template('profile.html', form=form, name=profile)
        else:
            flash("No student with that sid. Enter correct one!", 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First!",'danger')
        return redirect(url_for('flogin'))




##################################################################################### ALLOTMENT CRITERIA #############


@app.route('/allotmentcriteria', methods=['GET', 'POST'])
def allotmentcriteria():
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            profile = session['faculty']
            form = RoomForm()
            cur = mysql.connection.cursor()
            rooms = []
            first=[]
            second=[]
            third=[]
            fourth=[]
            cur.execute(f"SELECT hostel from staffinfo where email = '{session['email']}'")
            hostel = cur.fetchone()
            form.hostel.data = hostel[0]
            cur.execute(f"SELECT * from rooms where year is null and hostel = '{hostel[0]}'")
            fetch = cur.fetchall()
            print(hostel[0])
            if len(fetch) == 0:
                flash("All rooms have been allotted!",'info')


            if request.method == 'POST':
                if form.batch.data != '':
                    cur = mysql.connection.cursor()
                    floor = form.floor.data
                    capacity = form.capacity.data
                    if form.floor.data == '' and form.capacity.data == '':
                        cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' order by roomnum ")
                    elif form.floor.data != '' and form.capacity.data == '':
                        cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and floor = {floor} order by roomnum ")
                    elif form.floor.data == '' and form.capacity.data != '':
                        cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and capacity = {capacity} order by roomnum ")
                    elif form.floor.data != '' and form.capacity.data != '':
                        cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and floor = {floor} and capacity = {capacity} order by roomnum ")
                    fetch = cur.fetchall()
                    for i in fetch:
                        rooms.append(i[0])
                        if i[9] == 1:
                            first.append(i[0])
                        elif i[9] == 2:
                            second.append(i[0])
                        elif i[9] == 3:
                            third.append(i[0])
                        elif i[9] == 4:
                            fourth.append(i[0])
                    l = len(rooms)//10
                    r = len(rooms)%10
                    return render_template('allotment.html',form=form, rooms=rooms, first=first,second=second,third=third,fourth=fourth, l=l, r=r, name=profile)


            return render_template('allotment.html', form=form, rooms=rooms, name=profile)
        else:
            flash("You cannot access that!", 'danger')
            return redirect(url_for("facultyhome"))
    else:
        flash("Please Login First!",'danger')
        return redirect(url_for('flogin'))  



@app.route('/allotted<roomnum>s<batch>',methods=['GET', 'POST'])
def allotted(roomnum, batch):
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            profile = session['faculty']
            form = RoomForm()
            rooms=[]
            first=[]
            second=[]
            third=[]
            fourth=[]
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * from rooms where roomnum={roomnum}")
            fetch = cur.fetchone()
            if len(fetch) == 0:
                flash("Invaild Room Number", 'danger')
            cur.execute(f"SELECT hostel from staffinfo where email='{session['email']}'")
            hostel = cur.fetchone()
            form.hostel.data = hostel[0]
            cur.execute(f"SELECT * from rooms where roomnum={roomnum} and hostel = '{hostel[0]}'")
            fetch = cur.fetchone()
            if fetch:
                if int(batch)>=1 and int(batch)<=4:
                    if request.method == 'POST':
                        if form.batch.data != '':
                            cur = mysql.connection.cursor()
                            cur.execute(f"SELECT batch from studentinfo where email='{session['email']}'")
                            batch = cur.fetchone()
                            floor = form.floor.data
                            capacity = form.capacity.data
                            if form.floor.data == '' and form.capacity.data == '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' order by roomnum ")
                            elif form.floor.data != '' and form.capacity.data == '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and floor = {floor} order by roomnum ")
                            elif form.floor.data == '' and form.capacity.data != '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and capacity = {capacity} order by roomnum ")
                            elif form.floor.data != '' and form.capacity.data != '':
                                cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' and floor = {floor} and capacity = {capacity} order by roomnum ")
                            fetch = cur.fetchall()
                            for i in fetch:
                                rooms.append(i[0])
                                if i[9] == 1:
                                    first.append(i[0])
                                elif i[9] == 2:
                                    second.append(i[0])
                                elif i[9] == 3:
                                    third.append(i[0])
                                elif i[9] == 4:
                                    fourth.append(i[0])

                            l = len(rooms)//10
                            r = len(rooms)%10
                            return render_template('allotment.html',form=form, rooms=rooms, first=first,second=second,third=third,fourth=fourth, l=l, r=r, name=profile)

                    cur.execute(f"SELECT floor, capacity from rooms where hostel = '{hostel[0]}' and roomnum = {roomnum}")
                    fetch = cur.fetchone()
                    cur.execute(f"UPDATE rooms set year = {batch} where hostel = '{hostel[0]}' and roomnum = {roomnum}")
                    mysql.connection.commit()
                    form.hostel.data = hostel[0]
                    form.batch.data = str(batch)
                    cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}' order by roomnum ")
                    fetch = cur.fetchall()
                    for i in fetch:
                        rooms.append(i[0])
                        if i[9] == 1:
                            first.append(i[0])
                        elif i[9] == 2:
                            second.append(i[0])
                        elif i[9] == 3:
                            third.append(i[0])
                        elif i[9] == 4:
                            fourth.append(i[0])


                    
                    l = len(rooms)//10
                    r = len(rooms)%10
                    return render_template("allotted.html", form=form, rooms=rooms,first=first,second=second,third=third,fourth=fourth,l=l,r=r, name=profile)

                else:
                    flash("Enter valid batch!", 'danger')
                    return redirect(url_for('allotmentcriteria'))
            else:
                flash("Invaild Room Number!", 'danger')
                return redirect(url_for('allotmentcriteria'))
        else:
            flash('You cannot access that!' , 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))




######################################################################################### SHOW ROOMS ####################


@app.route('/rooms', methods=['GET', 'POST'])
def showrooms():
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            profile = session['faculty']
            form = RoomForm()
            cur = mysql.connection.cursor()
            if request.method == 'POST':
                cur.execute(f"UPDATE rooms set year = null")
                mysql.connection.commit()
                flash("Allotment Criteria Resetting, Successfully Done!",'success')
            rooms=[]
            first=[]
            second=[]
            third=[]
            fourth=[]
            cur.execute(f"SELECT hostel from staffinfo where email='{session['email']}'")
            hostel = cur.fetchone()
            cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}'")
            fetch = cur.fetchall()
            for i in fetch:
                rooms.append(i[0])
                if i[9] == 1:
                    first.append(i[0])
                elif i[9] == 2:
                    second.append(i[0])
                elif i[9] == 3:
                    third.append(i[0])
                elif i[9] == 4:
                    fourth.append(i[0])
            l = len(rooms)//10
            r = len(rooms)%10
            return render_template('showroom.html',form=form,rooms=rooms,first=first,second=second,third=third,fourth=fourth,l=l,r=r, name=profile)
        else:
            flash('You cannot access that!' , 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))



@app.route('/deallocaterooms')
def deallocaterooms():
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            flash('Click on room number to dealloate!', 'info')
            profile = session['faculty']
            cur = mysql.connection.cursor()
            rooms=[]
            vacant=[]
            cur.execute(f"SELECT hostel from staffinfo where email='{session['email']}'")
            hostel = cur.fetchone()
            cur.execute(f"SELECT * from rooms where hostel = '{hostel[0]}'")
            fetch = cur.fetchall()
            for i in fetch:
                rooms.append(i[0])
                if i[8] == 0:
                    vacant.append(i[0])
            l = len(rooms)//10
            r = len(rooms)%10
            return render_template('deallocaterooms.html',rooms=rooms, vacant=vacant,l=l,r=r, name=profile)
        else:
            flash('You cannot access that!', 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))




############################################################################################ DEALLOCATE ALL ##############


@app.route('/deallocateall')
def deallocateall():
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT hostel from staffinfo where email = '{session['email']}'")
            hostel = cur.fetchone()
            cur.execute(f"UPDATE studentinfo set hostel = null, roomnum = null where hostel = '{hostel[0]}'")
            cur.execute(f"UPDATE rooms set seater1 = null, seater2 = null, seater3 = null, totalin = 0, status = 0 where hostel='{hostel[0]}'")
            cur.execute(f"DELETE from studentqueries where hostel='{hostel[0]}'")
            mysql.connection.commit()
            flash("Successfully Dealloacated!", 'success')
            return redirect(url_for('showrooms'))
        else:
            flash('You cannot access that!', 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))






########################################################################################### DEALLOCATE ONE ##################



@app.route('/deallocate<int:roomnum>')
def deallocate(roomnum):
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * from rooms where roomnum={roomnum}")
            fetch = cur.fetchone()
            if fetch[0] != None:
                cur.execute(f"SELECT hostel from staffinfo where email = '{session['email']}'")
                hostel = cur.fetchone()
                cur.execute(f"SELECT sid from studentinfo where hostel = '{hostel[0]}' and roomnum = {roomnum}")
                sid = cur.fetchall()
                if len(sid) == 0:
                    flash(f"Room Number {roomnum} is already deallocated!", 'info')
                    return redirect(url_for('showrooms'))
                cur.execute(f"UPDATE studentinfo set hostel = null, roomnum = null where hostel = '{hostel[0]}' and roomnum = {roomnum}")
                cur.execute(f"UPDATE rooms set seater1 = null, seater2 = null, seater3 = null, totalin = 0, status = 0 where hostel='{hostel[0]}' and roomnum = {roomnum}")
                for s in sid:
                    if s[0] != None:
                        cur.execute(f"DELETE from studentqueries where sid = '{s[0]}'")
                mysql.connection.commit()
                flash(f"Successfully Dealloacated Room Number {roomnum}!", 'success')
                return redirect(url_for('deallocate'))
            else:
                flash("Invalid Room Number!",'danger')
                return redirect(url_for('showrooms'))
        else:
            flash('You cannot access that!', 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))




######################################################################################## SHOW QUERIES ###############


@app.route('/showstudentqueries')
def showqueries():
    if session.get('faculty'):
        profile = session['faculty']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT designation from staffinfo where email='{session['email']}'")
        fetch = cur.fetchone()
        cur.execute(f"SELECT * from studentqueries where reciever='{fetch[0]}' order by postdate desc")
        fetch = cur.fetchall()
        if fetch:
            return render_template('showqueries.html', post=fetch, name=profile)
        else:
            flash("No complaints added yet!", 'success')
            return render_template('showqueries.html', name=profile)
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))






#################################################################################### FACULTY CHANGE PASSWORD ###########



@app.route('/facultychangepass',methods=['GET','POST'])
def fchangepass():
    if session.get('faculty'):
        form=ChangePass()
        if request.method=='POST':
            if form.validate_on_submit():
                oldp=form.oldpassword.data
                cur = mysql.connection.cursor()
                cur.execute(f"SELECT password from staffinfo where email = '{session['email']}' ")
                fetch = cur.fetchone()
                if (bcrypt.check_password_hash(fetch[0], oldp)):
                    newpassworda = bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
                    cur.execute(f" UPDATE  staffinfo  set password = '{newpassworda}' where email= '{session['email']}' ")
                    mysql.connection.commit()
                    flash('Password Changed Successfullyly!', 'success')
                    return redirect(url_for('facultyhome'))
                else:
                    flash('Enter Correct old password', 'danger')
                    return redirect(url_for('fchangepass'))
        print (session['email'])
        return render_template('changepass.html',form=form,title="Change Password")
    else:
        flash("Please Login First", 'danger')
        return redirect(url_for('flogin'))





@app.route('/facultyforgot', methods=['GET', 'POST'])
def facultyforgot():
    form = ForgotForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cur = mysql.connection.cursor()
            details = request.form
            email = details['email']
            cur.execute(f"SELECT phone FROM staffinfo where email = '{email}'")
            fetch = cur.fetchone()
            cur.close()
            if fetch == None:
                flash("This Email address is invalid! Please enter valid one.",'danger')
                return redirect(url_for('facultyforgot'))
            else:
                session['email'] = email
                session['phone'] = fetch[0]
                return redirect(url_for('fresetpass'))
    return render_template('forgot.html',form=form)

@app.route('/facultyreset', methods=['GET', 'POST'])
def fresetpass():
    form = ResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            otp_check = form.data['otp']
            if otp_check == session['otp']:
                return redirect(url_for('fnewpass'))
            else:
                flash('INVALID OTP', 'danger')
                return redirect(url_for('fresetpass'))

    otp = str(random.randrange(100000, 999999))
    print(otp)
    URL = 'https://www.sms4india.com/api/v1/sendCampaign'
    session['otp']=otp
    sms.sendPostRequest(URL, 'NF6N0V2YKJIB72BZ9NEYI706Z4Y8BGJ5', 'HXCL4DM4TI2MCPWM', 'stage', session['phone'], '9592260601', f"Your OTP (One Time Password) to change your password is: {otp} Do not share this with anyone!   PEC")

    return render_template('verifyotp.html',form=form)


@app.route('/facultynewpass', methods=['GET', 'POST'])
def fnewpass():
    form = NewPForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            newpass = form.data['newpassword']
            c_newpass = form.data['confirmnewpassword']
            if newpass == c_newpass:
                hashed_pass = bcrypt.generate_password_hash(newpass).decode('utf-8')
                cur = mysql.connection.cursor()
                cur.execute(f"UPDATE staffinfo set password = '{hashed_pass}' where email = '{session['email']}'")
                mysql.connection.commit()
                flash("Password Changed Successfully", 'success')
                return redirect(url_for('flogin'))
            else:
                flash("passwords didnt match", 'danger')
                return redirect(url_for('fnewpass'))
    return render_template('newpass.html', form=form)





#################################################################################### UPLOAD LIST #############


@app.route('/uploadfile', methods=['GET', 'POST'])
def uploadfile():
    if session.get('faculty'):
        if session['designation'] != 'Admin':
            form = UploadForm()
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT hostel from staffinfo where email='{session['email']}'")
            fetch = cur.fetchone()
            hostel = fetch[0]
            form.hostel.data = str(fetch[0])
            profile = session['faculty']
            if request.method == 'POST':
                if form.validate_on_submit():
                    file = form.file.data
                    filename = secure_filename(file.filename)
                    _, f_ext = os.path.splitext(file.filename)
                    f =  'list' + f_ext
                    print (f)
                    file.save(os.path.join(app.root_path, f"static/uploads/{hostel}",f))
                    flash("File Uploaded Successfully!", 'success')
                    return redirect(url_for('facultyhome'))
            return render_template('uploadfile.html', name=profile, form=form)
        else:
            flash('You cannot access that!', 'danger')
            return redirect(url_for('facultyhome'))
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))



@app.route('/downloadfile')
def download():
    if session.get('user'):
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT hostel from studentinfo where sid = '{session['sid']}'")
        hostel = cur.fetchone()
        if hostel[0] != None:
            path = os.path.join(app.root_path, f"static/uploads/{hostel[0]}")
            list=[]
            for r, d, f in os.walk(path):
                for file in f:
                    if '.xlsx' in file:
                        list.append(os.path.join(r,file))
            print (len(list))
            if len(list) == 0:
                flash("List is not uploaded Yet!", 'info')
                return redirect(url_for('shome'))
            else:
                return redirect(url_for('static', filename=f"uploads/{hostel[0]}/list.xlsx"))
            return redirect(url_for('shome'))
        else:
            flash("Please Select a room first!", 'danger')
            return redirect(url_for('selectroom'))
    else:
        flash("Please Login First!", 'success')
        return redirect(url_for('slogin'))




@app.route('/downloadlist<hostel>')
def downloadlist(hostel):
    if session.get('faculty'):
        if session['designation'] == 'Admin':
            path = os.path.join(app.root_path, f"static/uploads/{hostel}")
            list=[]
            for r, d, f in os.walk(path):
                for file in f:
                    if '.xlsx' in file:
                        list.append(os.path.join(r,file))
            print (len(list))
            if len(list) == 0:
                flash("List is not uploaded Yet!", 'info')
                return redirect(url_for('facultyhome'))
            else:
                flash('Successfully Downloaded!', 'success')
                return redirect(url_for('static', filename=f"uploads/{hostel}/list.xlsx"))
        else:
            flash('You cannot Access that!', 'danger')
            return redirect('facultyhome')
    else:
        flash("Please Login First!", 'danger')
        return redirect(url_for('flogin'))




###################################################################################### LOGOUT ###################


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user',None)
    session.pop('email', None)
    session.pop('faculty', None)
    session.pop('sid', None)
    session.pop('staffid', None)
    session.pop('designation', None)
    session.pop('phone', None)
    flash("You are successfully logged out!", 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)

