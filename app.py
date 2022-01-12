import datetime
import random
import string
import csv
from flask import Flask, request, session,Response
from flask import render_template, url_for, redirect, jsonify
from flask.helpers import send_file
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import io
import xlwt
import pymysql
from os.path import join, dirname, realpath
from fpdf import FPDF
from flask import session
from datetime import date

from flask_mail import Mail, Message

output = io.BytesIO()
#create WorkBook object
workbook = xlwt.Workbook()
#add a sheet

# Mysql Connection
mysql = MySQL()

app = Flask(__name__)

#mail configuration
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.ionos.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'testing@web-designpakistan.com'
app.config['MAIL_PASSWORD'] = 'Lawrence1234**'
app.config['MAIL_DEFAULT_SENDER'] = ('testing@web-designpakistan.com')

mail = Mail(app)


# Uplaod Images and Documents Folder
UPLOAD_FOLDER = join(dirname(realpath(__file__)), "static/userData")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# mysql config
app.config["MYSQL_DATABASE_USER"] = "root"
# app.config["MYSQL_DATABASE_PASSWORD"] = 'LAwrence1234**'
app.config["MYSQL_DATABASE_PASSWORD"] = ''
app.config["MYSQL_DATABASE_DB"] = "doc"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
mysql.init_app(app)
app.secret_key = '123456789'



def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@app.route("/testing")
def testing():
    return render_template("testing2.html")

# dashboard main page route
@app.route("/")
def home():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        if status != "admin":
            return redirect(url_for("dashboard"))

        return render_template("testing2.html",status=status)
    else:
        session['attempt'] = 3
        return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # try:
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        print(status,"status")
        role = session.get("role")
        print(role,"r1")
        role2 = session.get("role2")
        print(role2,"r2")
        username = session.get("username")
        loginuserid = session.get("userid")
        print(loginuserid,"id")
        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute(""" select * from rights where user_id =%s ;""",[loginuserid])
        right = cur.fetchone()
        print(right,"rr")
        if right == None:
            session["data_download"] = None
        else:

            data_download = session.get("data_download")
        # print(data_download)
        if status == "admin":

            cur.execute('''select count(user_id) from user where role=2;''')
            doctors = cur.fetchone()[0]
            cur.execute('''select count(user_id) from user where role=3;''')
            assist = cur.fetchone()[0]
            cur.execute('''select count(user_id) from user where role=4;''')
            represt = cur.fetchone()[0]
            cur.execute('''select count(form_id) from form;''')
            forms = cur.fetchone()[0]
            cur.execute('''select count(form_entry_id) from form_entry;''')
            totalforms = cur.fetchone()[0]
            cur.execute('''select count(patient_id) from patient;''')
            patients = cur.fetchone()[0]
            cur.close()
            connection.close()
            return render_template("indexadmin.html", status=status, message=message, doctors=doctors,
                                   assist=assist, represt=represt, forms=forms, role=role,
                                   username=username, totalforms=totalforms, patients=patients,role2=role2)
        else:
            role2 = session.get("role2")
            print(role2,"r2 again")
            cur.execute('''select count(form_id) from form_entry where user_id=%s;''',
                        [int(session.get("userid"))])
            totalformsubmission = cur.fetchone()[0]
            cur.execute('''select count(form_id) from user_form_permissions where user_id=%s;''',
                        [int(session.get("userid"))])
            totalforms = cur.fetchone()[0]

            # cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
            # auditt = cur.fetchone()
            # print(auditt,"audit")
            # # form_id = auditt[1]
            event = "Dashboard Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s,%s)''',[username, event])
            connection.commit()

            cur.close()
            connection.close()
            return render_template("indexadmin.html", status=status, message=message, role=role,
                                   totalformsubmission=totalformsubmission, totalforms=totalforms,
                                   username=username,role2=role2)
    else:
        return redirect(url_for("login"))
    # except Exception as e:
    #     error = str(e)
    #     status = session.get("status")
    #     role = session.get("role")
    #     username = session.get("username")
    #     return render_template("indexadmin.html", status=status, error=error, role=role,
    #                            username=username)

@app.route("/Doctor/add", methods=["GET","POST"])
def doctoradd():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            if request.method == "POST":
                role = session.get("role")
                name = request.form["name"]
                username = request.form["username"]
                password = request.form["password"]
                contactno = request.form["contactno"]
                address = request.form["address"]
                form = request.form.getlist("form")
                role2 = request.form["role2"]
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, user_name, password from user where user_name=%s;''', [username])
                user = cur.fetchone()
                if user is not None:
                    session["error"] = "User with this username already exist. Please try " \
                                       "with a different username."
                    session["a"] = name
                    session["b"] = contactno
                    session["c"] = address
                    return redirect(url_for("doctoradd"))
                else:
                    # hashpassword = generate_password_hash(password)
                    cur.execute('''insert into user (name, user_name, password, contact_number, address, 
                    rep_code, role, parent_id,role2) values(%s,%s, %s, %s, %s, %s, %s, %s, %s);''',
                                [name, username, password, contactno, address, 0, 2, int(role),role2])
                    connection.commit()
                    docid = cur.lastrowid
                    for eachcase in form:
                        cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                                    [int(docid), int(eachcase)])
                        connection.commit()
                    session["message"] = "User has been added successfully"
                    event = "User Added"
                    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                    connection.commit()

                cur.close()
                connection.close()
                return redirect(url_for("doctoradd"))
            else:
                connection = mysql.connect()
                cur = connection.cursor()
                event = "User Created"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
                cur.close()
                connection.close()

                message = ""
                a = b = c = ''
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                if session.get("a") and session.get("b") and session.get("c"):
                    a = session.get("a")
                    b = session.get("b")
                    c = session.get("c")
                    session.pop("a", None)
                    session.pop("b", None)
                    session.pop("c", None)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select form_id, title from form;''')
                forms = cur.fetchall()
                cur.execute('''select * from address;''')
                address = cur.fetchall()
                cur.close()
                connection.close()
            return render_template("doctoradd.html", status=status, message=message, error=error,
                                   forms=forms, role=role, username=username, a=a, b=b, c=c,address=address)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        return render_template("doctoradd.html", status=status, error=str(error), role=role,
                               username=username)


@app.route("/Doctor/list", methods=["GET", "POST"])
def doctorlist():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address.address, parent_id,role2 from user
                            inner join address on
                            address.sno = user.address
                            where role=2 and status='active';''')
            users = cur.fetchall()
            cur.execute('''select * from address''')
            address = cur.fetchall()
            event = "User List Viewed"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D","ROLE","EDIT", "DELETE"]
            return render_template("doctorlist.html", status=status, message=message, data=users,
                                   headers=headers, rolee=users[6],
                                   username=username,role=role,address=address)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address.address, parent_id ,role2 from user
                    inner join address on
                    address.sno = user.address
                    where role=2 and status='active';''')
        users = cur.fetchall()
        cur.execute('''select * from address''')
        address = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D","ROLE", "EDIT", "DELETE"]
        return render_template("doctorlist.html", status=status, data=users, headers=headers, error=error,
                               role=users[6], username=username,address=address)


@app.route("/Doctor/deactivate", methods=["GET", "POST"])
def doctordeactivate():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id,role2 from user
            where role=2 and status='active' and login_attempt = 'deactive';''')
            users = cur.fetchall()
            event = "Doctor Deactivate List Viewed"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ROLE",
                       "ACTIVATE"]
            return render_template("deactivated.html", status=status, message=message, data=users,
                                   headers=headers,
                                   username=username, role=role)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, parent_id ,role2 from user
                    where role=2 and status='active' and login_attempt='deactive';''')
        users = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ROLE", "ACTIVATE"]
        return render_template("deactivated.html", status=status, data=users, headers=headers, error=error,
                               username=username)

@app.route("/activate_user", methods=["GET","POST"])
def activate_user():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            id = request.args.get("id")
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute("""UPDATE user
                            SET login_attempt = 'activate'
                            WHERE user_id = %s;""",[id])
            connection.commit()
            username1 = session.get("username")
            event = "Users Activated"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])

            connection.commit()
            cur.close()
            connection.close()
            return redirect(url_for("doctordeactivate"))

        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        return render_template("deactivated.html", error=error)


@app.route("/Doctor/edit", methods=["POST"])
def doctoredit():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            iddoc = request.get_data("data")
            iddoc = str(iddoc).split("'")[1].split("=")[1]
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address.address, parent_id,role2,password from user
                            inner join address on
                            address.sno = user.address
                            where role=2 and user_id=%s and status='active';''', [int(iddoc)])
            users = cur.fetchone()
            print(users)
            cur.execute('''select * from address''')
            address = cur.fetchall()
            cur.execute('''select form_id, title from form;''')
            forms = cur.fetchall()
            cur.execute('''select form_id from user_form_permissions where user_id=%s;''', [int(iddoc)])
            formspermissions = cur.fetchall()
            permform = []
            for eachitem in formspermissions:
                permform.append(eachitem[0])
            username = session.get("username")
            event = "Edit User Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
            connection.commit()

            cur.close()
            connection.close()
            return render_template("usersdata.html", user="doctor", name=users[1], username=users[2],role=users[6],
                                   contactno=users[3], address=users[4], form=users[5], id=users[0],password=users[7],
                                   forms=forms, formspermissions=permform,address1=address)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        return render_template("doctoradd.html", error=error)


@app.route("/Doctor/update", methods=["POST"])
def doctorupdate():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            print(name,username)
            address = request.form['address']
            contactno = request.form['contactno']
            form = request.form['form']
            role2 = request.form['role2']
            print(role2)
            form = str(form).split(",")

            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select password from user where role=2 and user_id=%s;''',[int(docid)])
            data = cur.fetchone()[0]

            cur.execute('''Update user set name=%s, contact_number=%s, address=%s, password=%s,role2=%s where role=2 
            and user_id=%s;''', [name, contactno, address, password, role2, int(docid)])
            connection.commit()
            if data != password:
                username1 = session.get("username")
                event = "User Password Updated"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
                connection.commit()
            else:
                username1 = session.get("username")
                event = "User Data Updated"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
                connection.commit()

            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()

            for eachcase in form:
                cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                            [int(docid), int(eachcase)])
                connection.commit()

            cur.execute('''select user_id, name, user_name, contact_number,password, address, parent_id from user
                                where role=2 and status='active';''')
            users = cur.fetchall()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
            session["message"] = "User detail updated successfully!"
            return render_template("userstable.html", data=users, headers=headers)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                                        where role=2 and status='active';''')
        users = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
        return render_template("userstable.html", error=error, data=users, headers=headers)


@app.route("/Doctor/delete", methods=["POST"])
def doctordelete():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Update user set status='deactive' where role=2 and user_id=%s;''', [int(docid)])
            connection.commit()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                                where role=2 and status='active';''')
            users = cur.fetchall()

            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()
            username1 = session.get("username")
            event = "Delete Doctor Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
            session["message"] = "User Deleted successfully!"

            return render_template("userstable.html", data=users, headers=headers)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        # session["error"] = error
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                                        where role=2;''')
        users = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
        return render_template("userstable.html", error=error, data=users, headers=headers)


@app.route("/Assistant/add", methods=["GET", "POST"])
def assistantadd():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            if request.method == "POST":
                name = request.form["name"]
                username = request.form["username"]
                password = request.form["password"]
                contactno = request.form["contactno"]
                address = request.form["address"]
                role2 = request.form["role2"]
                form = request.form.getlist("form")
                doctor = request.form["doctor"]
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, user_name, password from user where user_name=%s;''', [username])
                user = cur.fetchone()
                if user is not None:
                    session["error"] = "This username is already used. Please try " \
                                       "with a different usernmae."
                    return redirect(url_for("assistantadd"))
                else:
                    hashpassword = generate_password_hash(password)
                    cur.execute('''insert into user (name, user_name, password, contact_number, address, 
                                    rep_code, role, parent_id,role2) values(%s,%s, %s, %s, %s, %s, %s, %s, %s);''',
                                [name, username, hashpassword, contactno, address, 0, 3, int(doctor),role2])
                    connection.commit()
                    assistantid = cur.lastrowid
                    if len(form) > 0:
                        for eachcase in form:
                            cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                                        [int(assistantid), int(eachcase)])
                            connection.commit()
                    session["message"] = "Assitant added successfully"
                cur.close()
                connection.close()
                return redirect(url_for("assistantadd"))
            else:
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, name from user where role=2 and status='active';''')
                users = cur.fetchall()
                cur.execute('''select form_id, title from form;''')
                forms = cur.fetchall()
                event = "Assistant Add Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
                cur.close()
                connection.close()
            return render_template("assistantadd.html", status=status, message=message, data=users,
                                   error=error, forms=forms, role=role,
                                   username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        return render_template("assistantadd.html", status=status, error=error, role=role,
                               username=username)


@app.route("/Assistant/list", methods=["GET", "POST"])
def assistantlist():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id, role2
             from user where role=3 and status='active';''')
            data = cur.fetchall()

            event = "Assistant List Viewed"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            connection.commit()

            
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "ASSISTASNT_OF","ROLE","EDIT", "DELETE"]
            return render_template("assistantlist.html", status=status, message=message, data=data,
                                   headers=headers, error=error, role=role,
                                   username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect() 
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, parent_id,role2
         from user where role=3;''')
        data = cur.fetchall()

        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "ASSISTASNT_OF","ROLE", "EDIT", "DELETE"]
        return render_template("assistantlist.html", status=status, data=data,
                               headers=headers, error=error, role=role, username=username)


@app.route("/Assistant/edit", methods=["POST"])
def assistantedit():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            iddoc = request.get_data("data")
            iddoc = str(iddoc).split("'")[1].split("=")[1]
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id,role2 from user
                                where role=3 and user_id=%s and status='active';''', [int(iddoc)])
            users = cur.fetchone()
            cur.execute('''select user_id, name from user where role=2 and status='active';''')
            doctors = cur.fetchall()
            cur.execute('''select form_id, title from form;''')
            forms = cur.fetchall()
            cur.execute('''select form_id from user_form_permissions where user_id=%s;''', [int(iddoc)])
            formspermissions = cur.fetchall()
            username1 = session.get("username")
            event = "Assistant Edit Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()

            permform = []
            for eachitem in formspermissions:
                permform.append(eachitem[0])
            cur.close()
            connection.close()
            return render_template("usersdata.html", user="assistant", name=users[1], username=users[2],role2=users[6],
                                   contactno=users[3], address=users[4], form=users[5], id=users[0],
                                   users=doctors, doctor=users[5], forms=forms, formspermissions=permform)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("assistantlist"))


@app.route("/Assistant/update", methods=["POST"])
def assistantupdate():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            name = request.form['name']
            username = request.form['username']
            address = request.form['address']
            contactno = request.form['contactno']
            form = request.form['form']
            role2 = request.form['role2']
            form = str(form).split(",")
            doctor = request.form['doctor']
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Update user set name=%s, contact_number=%s, address=%s,role2=%s, parent_id=%s where role=3 
            and user_id=%s;''', [name, contactno, address,role2, doctor, int(docid)])
            connection.commit()

            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()

            for eachcase in form:
                cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                            [int(docid), int(eachcase)])
                connection.commit()

            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                                where role=3 and status='active';''')
            users = cur.fetchall()
            username1 = session.get("username")
            event = "Assistant Update Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
            session["message"] = "Assistant detail updated successfully!"
            return render_template("userstable.html", data=users, headers=headers)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("assistantlist"))
        

@app.route("/Assistant/delete", methods=["POST"])
def assistantdelete():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Update user set status='deactive' where role=3 and user_id=%s;''', [int(docid)])
            connection.commit()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                                where role=3 and status='active';''')
            users = cur.fetchall()
            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()
            username1 = session.get("username")
            event = "Assistant Delete Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D", "ACTION"]
            message = "Doctor detail updated successfully!"
            return render_template("userstable.html", data=users, headers=headers, message=message)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("assistantlist"))


@app.route("/Representative/add", methods=["GET", "POST"])
def representativeadd():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            if request.method == "POST":
                name = request.form["name"]
                username = request.form["username"]
                password = request.form["password"]
                contactno = request.form["contactno"]
                address = request.form["address"]
                form = request.form.getlist("form")
                repcode = request.form["repcode"]
                role2 = request.form["role2"]
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, user_name, password from user where user_name=%s;''', [username])
                user = cur.fetchone()
                if user is not None:
                    session["error"] = "This username is already used. Please try " \
                                       "with a different usernmae."
                    return redirect(url_for("assistantadd"))
                else:
                    hashpassword = generate_password_hash(password)
                    cur.execute('''insert into user (name, user_name, password, contact_number, address, 
                                                    rep_code, role, parent_id,role2) values
                                                    (%s, %s, %s, %s, %s, %s, %s, %s,%s);''',
                                [name, username, hashpassword, contactno, address, repcode, 4, 1,role2])
                    connection.commit()
                    represetativeid = cur.lastrowid
                    if len(form) > 0:
                        for eachcase in form:
                            cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                                        [int(represetativeid), int(eachcase)])
                            connection.commit()
                    session["message"] = "Representative added successfully"
                cur.close()
                connection.close()
                return redirect(url_for("representativeadd"))
            else:
                message = ""
                error = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select form_id, title from form;''')
                forms = cur.fetchall()
                event = "Add Representative Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
                cur.close()
                connection.close()
                return render_template("representativeadd.html", status=status, message=message,
                                       error=error, forms=forms, role=role,
                                       username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        role = session.get("role")
        username = session.get("username")
        status = session.get("status")
        return render_template("representativeadd.html", status=status, error=error,
                               role=role, username=username)


@app.route("/Representative/list", methods=["GET", "POST"])
def representativelist():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address, parent_id,role2 from user where
            role=4 and status='active';''')
            data = cur.fetchall()
            event = "Representative List Viewed"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D","ROLE", "EDIT", "DELETE"]
            return render_template("representativelist.html", status=status, message=message, data=data,
                                   headers=headers, error=error, role=role,
                                   username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, rep_code from user where
                    role=4 and status='active';''')
        data = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "REPCODE", "EDIT", "DELETE"]
        return render_template("representativelist.html", status=status, data=data,
                               headers=headers, error=error)


@app.route("/Representative/edit", methods=["POST"])
def representativeedit():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            iddoc = request.get_data("data")
            iddoc = str(iddoc).split("'")[1].split("=")[1]
            iddoc = str(iddoc).split("'")[1].split("=")[1]
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select user_id, name, user_name, contact_number, address, rep_code,role2 from user
                                where role=4 and user_id=%s and status='active';''', [int(iddoc)])
            users = cur.fetchone()
            cur.execute('''select form_id, title from form;''')
            forms = cur.fetchall()
            cur.execute('''select form_id from user_form_permissions where user_id=%s;''', [int(iddoc)])
            formspermissions = cur.fetchall()
            username1 = session.get("username")
            event = "Edit Representative Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            permform = []
            for eachitem in formspermissions:
                permform.append(eachitem[0])
            cur.close()
            connection.close()
            return render_template("usersdata.html",role=users[6], user="representative", name=users[1], username=users[2],
                                   contactno=users[3], address=users[4], form=users[5], id=users[0],
                                   doctor=users[5], forms=forms, formspermissions=permform)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("representativelist"))


@app.route("/Representative/update", methods=["POST"])
def representativeupdate():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            name = request.form['name']
            contactno = request.form["contactno"]
            address = request.form["address"]
            repcode = request.form["repcode"]
            form = request.form["form"]
            role2 = request.form["role2"]
            form = str(form).split(",")
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Update user set name=%s, contact_number=%s, address=%s, rep_code=%s,role2=%s where role=4 
            and user_id=%s;''', [name, contactno, address, repcode,role2, int(docid)])
            connection.commit()
            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()

            for eachcase in form:
                cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                            [int(docid), int(eachcase)])
                connection.commit()
            cur.execute('''select user_id, name, user_name, contact_number, address, rep_code from user
                                where role=4 and status='active';''')
            users = cur.fetchall()
            username1 = session.get("username")
            event = "Update Representative Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "REPCODE", "ACTION"]
            message = "Representative detail updated successfully!"
            return render_template("userstable.html", data=users, headers=headers, message=message)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("representativelist"))


@app.route("/Representative/delete", methods=["POST"])
def representativedelete():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            docid = request.form['docid']
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Update user set status='deactive' where role=4 and user_id=%s;''', [int(docid)])
            connection.commit()
            cur.execute('''Delete from user_form_permissions where user_id=%s;''', [int(docid)])
            connection.commit()
            cur.execute('''select user_id, name, user_name, contact_number, address, rep_code from user
                                where role=4 and status='active';''')
            users = cur.fetchall()
            username1 = session.get("username")
            event = "Delete Representative Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "REPCODE", "ACTION"]
            message = "Doctor detail updated successfully!"
            return render_template("userstable.html", data=users, headers=headers, message=message)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("representativelist"))


@app.route("/Study/add", methods=["GET", "POST"])
def studyadd():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            if request.method == "POST":
                title = request.form["title"]
                status = request.form["status"]
                pid = request.form["pid"]
                labellist = request.form.getlist("label")
                fieldplaceholderlist = request.form.getlist("fieldplaceholder")
                fieldvaluelist = request.form.getlist("fieldvalue")
                fieldsortinglist = request.form.getlist("fieldsorting")
                fieldtypelist = request.form.getlist("fieldtype")
                fieldsizelist = request.form.getlist("fieldsize")
                isrequiredlist = request.form.getlist("isrequired")
                # print(title, status, labellist, fieldplaceholderlist, fieldvaluelist, fieldsortinglist,
                #       fieldtypelist, fieldsizelist, isrequiredlist)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute(''' select * from form where project_id=%s; ''',[pid])
                data = cur.fetchone()
                if data is not None:
                    session["error"] = f" This Project Id Is Already Exist {pid}"
                    error = ""
                    if session.get("error"):
                        error = session.get("error")
                        
                    return render_template("studyadd.html",error=error )
                else:
                    cur.execute('''Insert into form (title, status,project_id) values (%s, %s, %s)''',[title, status,pid])
                connection.commit()
                titleid = cur.lastrowid
                for i, eachfield in enumerate(labellist):
                    cur.execute(
                        '''Insert into form_fields (label, field_type, field_placeholder, field_value, 
                        class_column, sort_order, form_id, is_required) 
                        values (%s, %s, %s, %s, %s, %s, %s, %s)''',
                        [labellist[i], fieldtypelist[i], fieldplaceholderlist[i], fieldvaluelist[i],
                         fieldsizelist[i], fieldsortinglist[i], titleid, isrequiredlist[i]])
                    connection.commit()
                    event = "Study Form Added"
                    connection = mysql.connect()
                    cur = connection.cursor()
                    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                                [username, event])
                    connection.commit()
                cur.close()
                connection.close()
                session["message"] = "Case added successfully."
                return redirect(url_for("studyadd"))
            else:
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)

                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)

                event = "Study Add Opened"

                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                            [username, event])
                connection.commit()
                cur.close()
                connection.close()
                
            return render_template("studyadd.html", status=status, message=message, role=role,
                                   username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        return render_template("studyadd.html", status=status, role=role,
                               username=username, error=error)


@app.route("/Study/list", methods=["GET", "POST"])
def studylist():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message1 = request.args.get("message")
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = "Study Project list Openend"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select * from form;''')
            data = cur.fetchall()
            print(data)
            event =  "Study Project list Openend"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
            [username, event])
            connection.commit()
            cur.close()
            connection.close()
            headers = ["form_id", "TITLE", "CREATED ON", "STATUS","PROJECT ID","EDIT", "DELETE"]
            return render_template("studylist.html", status=status, message=message, data=data,
                                    headers=headers, role=role, username=username)

        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select * from form;''')
        data = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["form_id", "TITLE", "CREATED AT NUMBER", "STATUS", "EDIT", "DELETE"]
        return render_template("studylist.html", status=status, role=role, username=username,
                               error=error, data=data, headers=headers)

# @app.route('/viewform',methods=['GET','POST'])
# def viewform():


@app.route("/caseedit", methods=["GET", "POST"])
def studyedit():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        if request.method == "POST":
            caseids = request.form["caseids"]
            title = request.form["title"]
            status = request.form["status"]
            fieldids = request.form.getlist("fieldids")
            labellist = request.form.getlist("label")
            fieldplaceholderlist = request.form.getlist("fieldplaceholder")
            fieldvaluelist = request.form.getlist("fieldvalue")
            fieldsortinglist = request.form.getlist("fieldsorting")
            fieldtypelist = request.form.getlist("fieldtype")
            fieldsizelist = request.form.getlist("fieldsize")
            isrequiredlist = request.form.getlist("isrequired")
            print(isrequiredlist)
            previousfieldids = request.form["idfields"]

            previousfieldids = previousfieldids.replace('[', '')
            previousfieldids = previousfieldids.replace(']', '')
            previousfieldids = previousfieldids.split(", ")

            todelete = list(set(previousfieldids) - set(fieldids))

            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''update form set title=%s, status=%s where form_id=%s''',
                        [title, status, int(caseids)])
            connection.commit()
            if len(todelete) > 0:
                for i in todelete:
                    cur.execute('''delete from form_fields where form_fields_id=%s and form_id=%s''',
                                [int(i), int(caseids)])
                    connection.commit()
            if len(fieldids) > 0:
                for i, eachfield in enumerate(fieldids):
                    if fieldids[i] != "" or fieldids[i] != '':
                        cur.execute('''Update form_fields set label=%s, field_type=%s, field_placeholder=%s,
                             field_value=%s, class_column=%s, sort_order=%s, is_required=%s where 
                             form_fields_id=%s and form_id=%s''',
                                    [labellist[i], fieldtypelist[i], fieldplaceholderlist[i], fieldvaluelist[i],
                                     fieldsizelist[i], fieldsortinglist[i], isrequiredlist[i], int(fieldids[i]),
                                     int(caseids)])
                        connection.commit()
                    elif fieldids[i] == "" or fieldids[i] == '':
                        cur.execute(
                            '''Insert into form_fields (label, field_type, field_placeholder, field_value, 
                            class_column, sort_order, form_id, is_required) 
                            values (%s, %s, %s, %s, %s, %s, %s, %s)''',
                            [labellist[i], fieldtypelist[i], fieldplaceholderlist[i], fieldvaluelist[i],
                             fieldsizelist[i], fieldsortinglist[i], int(caseids), isrequiredlist[i]])
                        connection.commit()
            username1 = session.get("username")
            event = "Study Edited"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                        [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            session["message"] = "Case Updated successfully."
            return redirect(url_for("studyedit"))
        else:
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            caseid = request.cookies.get("case")
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''select * from form where form_id = %s;''', [int(caseid)])
            case = cur.fetchone()
            cur.execute('''select * from form_fields where form_id = %s order by sort_order;''',
                        [int(caseid)])
            casedetails = cur.fetchall()
            print(casedetails)
            idfields = []
            for i in casedetails:
                idfields.append(i[0])
            username1 = session.get("username")
            event = "Study Edit Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                        [username1, event])
            connection.commit()

            cur.close()
            connection.close()
            return render_template("studyedit.html", status=status, message=message, case=case,
                                   data=casedetails, idfields=idfields, role=role,
                                   username=username)
    else:
        return redirect(url_for("login"))


@app.route("/casedelete", methods=["GET", "POST"])
def studydelete():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        if request.method == "POST":
            caseids = request.form["caseid"]
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''delete from form_fields where form_id=%s''', [int(caseids)])
            connection.commit()
            cur.execute('''delete from form where form_id = %s''', [int(caseids)])
            connection.commit()
            username1 = session.get("username")
            event = "Study Delete Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                        [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            session["message"] = "Case Deleted successfully."
            return str(True)
        else:
            return str(True)


# 1 Tab 5: Show only forms
@app.route("/CaseReport/list", methods=["GET", "POST"])
def casereportlist():
    # try:
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        role2 = session.get("role2")
        username = session.get("username")
        loginuserid = session.get("userid")
        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        error = ""
        if session.get("error"):
            error = session.get("error")
            session.pop("error", None)

        connection = mysql.connect()
        cur = connection.cursor()
        if status == "admin":
            cur.execute('''select form_id, title, status, created_at,project_id from form where archive="no";''')
            data = cur.fetchall()

        else:
            cur.execute('''select form.form_id, form.title, form.status, form.created_at,project_id from form where 
            form.form_id in (select user_form_permissions.form_id from user_form_permissions 
            where user_form_permissions.user_id = %s);''', [int(loginuserid)])
            data = cur.fetchall()
        username1 = session.get("username")
        event = "Case Report List Viewed"
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        connection.commit()
        cur.close()
        connection.close()

        # else:
        #     cur.execute('''select form.form_id, form.title, form.status, form.created_at from form where
        #     form.form_id in, (select user_form_permissions.form_id from user_form_permissions
        #     where user_form_permissions.user_id = %s);''', [int(loginuserid)])
        #     data = cur.fetchall()
            # cur.execute(""" SELECT user_form_permissions_id , user_id, form_id ,(SELECT form.title FROM form where form.form_id = user_form_permissions.form_id)as "title",(select name FROM user WHERE user.user_id = user_form_permissions.form_id) as "user_id" FROM user_form_permissions WHERE user_id=%s; """,[loginuserid])
            # auditt = cur.fetchall()
            # print(auditt)
            # cur.execute(""" SELECT form_entry_id, project_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
            # auditt = cur.fetchone()
            # form_id = auditt[1]
            # event = "Case Report List Viewed"
            # cur.execute('''Insert into audittrail (username,form_id, event ) values (%s, %s,%s)''',[username,form_id, event])
            # connection.commit()

        headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT","PROJECT ID", "ACTION","Locked"]
        header2 = ["S.NO", "TITLE", "STATUS", "CREATED_AT","PROJECT ID", "ACTION"]
        return render_template("reportlist.html", status=status, message=message, data=data,
                               headers=headers, error=error, role=role, username=username,header2=header2,role2=role2)
    else:
        return redirect(url_for("login"))
    # except Exception as e:
    #     error = str(e)
    #     status = session.get("status")
    #     connection = mysql.connect()
    #     cur = connection.cursor()
    #     cur.execute('''select form_id, title, created_at, status from form;''')
    #     data = cur.fetchall()
    #     cur.close()
    #     connection.close()
    #
    #     headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
    #     message = ""
    #     if session.get("message"):
    #         message = session.get("message")
    #         session.pop("message", None)
    #     return render_template("reportlist.html", status=status, data=data,
    #                            headers=headers, error=error, role=role, username=username,message=message)

@app.route("/CaseReport/list/rights", methods=["GET", "POST"])
def casereportlist_rights():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            connection = mysql.connect()
            cur = connection.cursor()
            if status == "admin":
                cur.execute('''select form_id, title, status, created_at,project_id from form;''')
                data = cur.fetchall()
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
            elif username == "monitor":
                cur.execute('''select form_id, title, status, created_at from form;''')
                data = cur.fetchall()
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()

            else:
                cur.execute('''select form.form_id, form.title, form.status, form.created_at from form where 
                form.form_id in, (select user_form_permissions.form_id from user_form_permissions 
                where user_form_permissions.user_id = %s);''', [int(loginuserid)])
                data = cur.fetchall()
                # cur.execute(""" SELECT user_form_permissions_id , user_id, form_id ,(SELECT form.title FROM form where form.form_id = user_form_permissions.form_id)as "title",(select name FROM user WHERE user.user_id = user_form_permissions.form_id) as "user_id" FROM user_form_permissions WHERE user_id=%s; """,[loginuserid])
                # auditt = cur.fetchall()
                # print(auditt)
                cur.execute(""" SELECT form_entry_id, project_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
                auditt = cur.fetchone()
                form_id = auditt[1]
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username,form_id, event ) values (%s, %s,%s)''',[username,form_id, event])
                connection.commit()
                

            cur.close()
            connection.close()
            headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT","PROJECT ID", "ACTION"]
            header2 = ["S.NO", "TITLE", "STATUS", "CREATED_AT","PROJECT ID", "ACTION"]
            return render_template("reportlist-rights.html", status=status, message=message, data=data,
                                   headers=headers, error=error, role=role, username=username,header2=header2)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select form_id, title, created_at, status from form;''')
        data = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
        return render_template("reportlist.html", status=status, data=data,
                               headers=headers, error=error, role=role, username=username)



@app.route("/casedetail-rights", methods=["GET", "POST"])
def casedetail_rights():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            
            status = session.get("status")
            role = session.get("role")
            print(role)
            username = session.get("username")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            formid = request.cookies.get("formid")
            connection = mysql.connect()
            cur = connection.cursor()
            if status == "admin":
                cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
                form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
                patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
                user.user_id = form_entry.user_id limit 1), form_entry.created_at from form_entry where 
                form_id=%s group by user_id;''', [int(formid), int(formid)])
                data = cur.fetchall()
                event = "Case Listing for Patients Rights Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()

                cur.execute(''' select * from rights where user_id =%s ;''',[loginuserid])
                user = cur.fetchone()
                       
            else:
                cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
                form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
                patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
                user.user_id = form_entry.user_id limit 1), form_entry.created_at from form_entry where 
                form_id=%s and user_id=%s;''', [int(formid), int(formid), int(loginuserid)])
                data = cur.fetchall()
                # event = "Case Detail Opened"
                # cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                # connection.commit()


                cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
                auditt = cur.fetchone()
                form_id = auditt[1]
                event = "Case Listing for Patients Rights Opened"
                cur.execute('''Insert into audittrail (username,form_id, event ) values (%s, %s,%s)''',[username,form_id, event])
                connection.commit()

                cur.execute(''' select * from rights where user_id =%s ;''',[loginuserid])
                user = cur.fetchone()



            cur.close()
            connection.close()
            
            headers = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","RIGHTS"]
            edit_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","EDIT","DELETE","LOCK"]
            delete_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","DELETE"]
            lock_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","LOCK"]
        return render_template("reportdetails-rights.html", status=status, data=data, headers=headers,
                               message=message, error=error, formid=formid, role=role, username=username,user=user,edit=edit_header,delete=delete_header,lock=lock_header)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casedetail_rights"))





# 2 Tab 5: View form entries(patient name and doctor name wise.)
# /CaseReport/list/ casedetails
@app.route("/casedetail", methods=["GET", "POST"])
def casedetail():
    # try:
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        print(status,"i am status")
        role = session.get("role")
        role2 = session.get("role2")
        print(role2,"zohaib")
        username = session.get("username")
        loginuserid = session.get("userid")
        message1 = request.args.get("message")
        if message1 != None:
            connection = mysql.connect()
            cur = connection.cursor()
            event = message1
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
            connection.commit()

        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        error = ""
        if session.get("error"):
            error = session.get("error")
            session.pop("error", None)
        formid = request.cookies.get("formid")
        connection = mysql.connect()
        cur = connection.cursor()
        if status == "admin":
            cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
            form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
            patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
            user.user_id = form_entry.user_id limit 1), form_entry.created_at from form_entry where 
            form_id=%s group by user_id;''', [int(formid), int(formid)])
            data = cur.fetchall()
            event = "Case Detail Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            connection.commit()

            cur.execute(''' select * from rights where user_id = %s ;''',[loginuserid])
            user = cur.fetchone()

        elif role2 == "Query Receiver":
            cur.execute('''SELECT form.title,patient.patient_name,user.user_name,query,form_id,user_idd,patient_id,query_idd FROM query INNER JOIN form ON form.form_id = query.form_idd INNER JOIN patient ON patient.patient_id = query.patient_idd INNER JOIN user ON user_id = query.patient_idd WHERE form_idd=%s and query_status="no";''', [int(formid)])
            data = cur.fetchall()

        elif role2 == "Query Sender":
            cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
            form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
            patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
            user.user_id = form_entry.user_id limit 1), form_entry.created_at,form_id,user_id,patient_id from form_entry where 
            form_id=%s ;''', [int(formid), int(formid)])
            data = cur.fetchall()

        elif username == "monitor":
            cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
            form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
            patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
            user.user_id = form_entry.user_id limit 1), form_entry.created_at from form_entry where 
            form_id=%s group by user_id;''', [int(formid), int(formid)])
            data = cur.fetchall()
            event = "Case Detail Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            connection.commit()


        else:
            cur.execute('''select form_entry.form_entry_id, patient_id, user_id, (select form.title from 
            form where form.form_id = %s limit 1), (select patient.patient_name from patient where 
            patient.patient_id = form_entry.patient_id limit 1), (select user.name from user where 
            user.user_id = form_entry.user_id limit 1), form_entry.created_at,form_id,user_id,patient_id from form_entry where 
            form_id=%s and user_id=%s;''', [int(formid), int(formid),int(loginuserid)])
            data = cur.fetchall()
            # event = "Case Detail Opened"
            # cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
            # connection.commit()


            # cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
            # auditt = cur.fetchone()
            # form_id = auditt[1]
            event = "Case Detail Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s,%s)''',[username, event])
            connection.commit()

        cur.execute(''' select * from rights where user_id =%s ;''',[loginuserid])
        user = cur.fetchone()
        if user == None:
            data_download = None
        else:
            data_download = user[7]

        cur.close()
        connection.close()
        headers = ["form_entry_id", "patient_id", "user_id", "DOCTOR NAME", "CREATED AT", "EDIT", "View"]
        headers = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","VIEW","DELETE"]
        edit_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","EDIT","DELETE","LOCK","VIEW"]
        delete_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","DELETE"]
        lock_header = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT","LOCK"]
    return render_template("reportdetails.html", status=status, data=data, headers=headers,
                           message=message, error=error, formid=formid, role=role, username=username,user=user,edit=edit_header,delete=delete_header,lock=lock_header,data_download=data_download,role2=role2, form_id=formid)
    # except Exception as e:
    #     session["error"] = str(e)
    #     return redirect(url_for("casereportlist"))


@app.route("/case-patient-study", methods=["GET", "POST"])
def casepatientstudy():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            role2 = session.get("role2")
            username = session.get("username")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            formentryid = request.cookies.get("formentryid")
            patientid = request.cookies.get("patientid")
            doctorid = request.cookies.get("doctorid")
            actualformid = request.cookies.get("actualformid")
            print(formentryid, patientid, doctorid, actualformid)

            # print(formentryid, patientid, doctorid, actualformid)
            connection = mysql.connect()
            cur = connection.cursor()
            # cur.execute('''select form_entry_data.form_entry_data_id,
            # (select form_fields.label from form_fields where form_fields.form_fields_id=
            # form_entry_data.form_fields_id) as 'label', form_entry_data.value,
            # form_entry_data.created_at from form_entry_data where form_entry_data.form_entry_id=%s;;''',
            #             [int(formentryid)])
            # data1 = cur.fetchall()
            cur.execute('''select * from form_fields where form_id = %s order by sort_order;''',
                        [int(actualformid)])
            data = cur.fetchall()
            # cur.execute('''select * from patient;''')
            # patients = cur.fetchall()
            cur.execute('''select * from rights where user_id = %s''',
                        [int(loginuserid)])
            rights = cur.fetchone()
            username1 = session.get("username")
            event = "Case Patient Study Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()

            print(rights)
            cur.close()
            connection.close()
            headers = ["S.NO", "FORM", "PATIENT NAME", "DOCTOR NAME", "CREATED AT", "ACTION"]
            return render_template("reportcasedetail.html", status=status, data=data, headers=headers,
                                   message=message, error=error, doctorid=doctorid,
                                   actualformid=actualformid, patientid=patientid, role=role,
                                   username=username, formentryid=formentryid, rights=rights, role2=role2)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casedetail"))


@app.route("/casestudydeleteas", methods=["GET", "POST"])
def casestudydelete():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        if request.method == "POST":
            caseids = request.form["caseid"]
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''delete from form_fields where form_id=%s''', [int(caseids)])
            connection.commit()
            cur.execute('''delete from form where form_id = %s''', [int(caseids)])
            connection.commit()
            username1 = session.get("username")
            event = "Case Study Delete Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.close()
            connection.close()
            session["message"] = "Case Updated successfully."
            return str(True)
        else:
            return str(True)


@app.route("/CaseView/list", methods=["GET", "POST"])
def caseviewlist():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            role2 = session.get("role2")

            username = session.get("username")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            connection = mysql.connect()
            cur = connection.cursor()
            if session.get("status") == "admin":
                cur.execute('''select form_id, title, status, created_at from form;''')
                data = cur.fetchall()
                event = "Case View List Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
            else:
                cur.execute('''select form.form_id, form.title, form.status, form.created_at from form where 
                form.form_id in (select user_form_permissions.form_id from user_form_permissions 
                where user_form_permissions.user_id = %s);''', [int(loginuserid)])
                data = cur.fetchall()
                # event = "Case View List Opened"
                # cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                # connection.commit()

                # cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
                # auditt = cur.fetchone()
                # form_id = auditt[1]
                event = "Case View List Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s,%s)''',[username, event])
                connection.commit()

            cur.execute('select * from address')
            city = cur.fetchall()
            cur.close()
            connection.close()
            headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
            return render_template("caseviewlist.html", status=status, message=message, data=data,
                                   headers=headers, error=error, role=role,
                                   username=username,role2=role2,city=city)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        connection = mysql.connect()
        cur = connection.cursor()
        if session.get("status") == "admin":
            cur.execute('''select form_id, title, status, created_at from form;''')
            data = cur.fetchall()
        else:
            cur.execute('''select form.form_id, form.title, form.status, form.created_at from form where 
            form.form_id in (select user_form_permissions.form_id from user_form_permissions 
            where user_form_permissions.user_id = %s);''', [int(loginuserid)])
            data = cur.fetchall()
        cur.execute('select * from address')
        city = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
        return render_template("caseviewlist.html", error=error, data=data, headers=headers,
                               status=status, username=username, role=role, city=city)


@app.route("/CaseView", methods=["GET", "POST"])
def caseview():
    # try:
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        role2 = session.get("role2")
        patient_id = request.args.get("patientid")
        print(patient_id,"ppiidd")
        message = ""

        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        error = ""
        if session.get("error"):
            error = session.get("error")
            session.pop("error", None)

        formid = request.cookies.get("formid")
        print(formid,"id")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select * from form_fields where form_id = %s order by sort_order;''',
                    [formid])
        data = cur.fetchall()
        #sign data
        cur.execute("""select signature from digital_signature 
                    where user_id=%s and patient_id=%s;""",[loginuserid,patient_id])
        sign_data = cur.fetchone()
        if sign_data != None:
            sign_data = sign_data[0]
        # print(sign_data, "AAAAAAAAAAA")


        # Ek project open kren to usmn ek he project k patients show hon
        cur.execute('''select * from patient 
                inner join form_entry
                on form_entry.patient_id = patient.patient_id
                where created_by=%s and form_id=%s ;''', [loginuserid, formid])
        patients = cur.fetchall()
        print(patients)
        if role2 == "Query Receiver":
            cur.execute('''SELECT patient.patient_id,patient.patient_name FROM query INNER JOIN form ON form.form_id = query.form_idd INNER JOIN patient ON patient.patient_id = query.patient_idd INNER JOIN user ON user_id = query.patient_idd WHERE form_idd=12; ''')
            patients = cur.fetchall()

        cur.execute('''select * from form where form_id = %s;''', [formid])

        formname = cur.fetchone()[1]
        print(formname)

        cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
        auditt = cur.fetchone()
        if auditt == "":
            form_id = auditt[1]
            event = "Case View Opened"
            cur.execute('''Insert into audittrail (username,form_id, event ) values (%s, %s,%s)''',[username,form_id, event])
            connection.commit()

        cur.execute("select sign from rights where user_id=%s",[loginuserid])
        user_rights = cur.fetchone()[0]
        print(user_rights,"me rights hun")
        cur.close()
        connection.close()
        patientid = "NULL"
        print(role2,"here see")
        if request.args.get("patientid"):
            patientid = request.args.get("patientid")
            print(patientid)
        return render_template("reporttestview.html", status=status, message=message, data=data, error=error, patients=patients
                               , formid=formid, role=role,role2=role2,username=username, formname=formname,patientid=patientid,
                                 user_rights=user_rights,sign_data=sign_data)
    else:
        return redirect(url_for("login"))
    # except Exception as e:
    #     error = str(e)
    #     session["error"] = error
    #     return str(e)

@app.route("/addpatient", methods=["GET", "POST"])
def addpatient():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            if request.method == "POST":
                name = request.form["name"]
                contact = request.form["contact"]
                address = request.form["address"]
                createdby = session.get("userid")
                p_id = request.form["pid"]
                cnic = request.form["cnic"]
                print(p_id,address)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''Insert into patient (patient_name, contact, address, created_by,p_id,cnic)
                values(%s, %s, %s, %s, %s,%s);''', [name, contact, address, int(createdby),int(p_id),cnic])
                connection.commit()
                username1 = session.get("username")
                event = "Add Patient Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
                connection.commit()
                cur.close()
                connection.close()
                return redirect(url_for("caseview"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("caseview"))


@app.route("/addpatient2", methods=["GET", "POST"])
def addpatient2():
    # try:
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        if request.method == "POST":
            name = request.form["name"]
            contact = request.form["contact"]
            address = request.form["address"]
            createdby = session.get("userid")
            p_id = request.form["pid"]
            cnic = request.form["cnic"]
            print(p_id,address,name,contact,createdby)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Insert into patient (patient_name, contact, address, created_by,p_id,cnic)
            values(%s, %s, %s, %s, %s,%s);''', [name, contact, address, int(createdby),p_id,cnic])
            connection.commit()
            id = cur.lastrowid
            print(id , "this is id")
            username1 = session.get("username")
            event = "Add Patient Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])

            connection.commit()
            cur.close()
            connection.close()
            return redirect("/CaseView?patientid="+str(id))
    else:
        return redirect(url_for("login"))
    # except Exception as e:
    #     error = str(e)
    #     session["error"] = error
    #     return redirect(url_for("patient_list2"))


# Add study case data route.
@app.route("/casedataadd", methods=["GET", "POST"])
def casedataadd():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            print("i got called 1")
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            # patient_id = request.args.get("patientid")
            # print(patient_id,"me patient ki id hn")
            connection = mysql.connect()
            cur = connection.cursor()
            username1 = session.get("username")
            event = "Case Data Add Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()

            if request.method == "POST":
                print("i got called 2")
                return str(True)
            else:
                print("i got called 3")
                data = request.args.get('myFormData')
                data = str(data).split(',')
                patientid = request.args.get('patientid')
                print(patientid,"patinet id")
                studyprojectid = request.args.get('studyprojectid')
                # print(studyprojectid,"projectid")
                userid = session.get('userid')
                # print(userid,"userid")
                sign = request.args.get("sign")
                print(sign,"signature22")
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select * from digital_signature where user_id=%s and patient_id=%s;''',[userid,patientid])
                sign_data = cur.fetchone()
                print(sign_data,"mjhy dekho")
                if sign_data != None:
                    print("i am inserting data")
                    print(userid, patientid, sign, userid, patientid)

                    cur.execute('''update digital_signature set signature=%s
                                  where user_id=%s and patient_id=%s;''',
                                [sign, userid, patientid])
                    connection.commit()
                else:
                    print("i am inserting data else")
                    print(userid, patientid, sign)
                    cur.execute('''insert into digital_signature (user_id,patient_id,signature)
                                    values (%s,%s,%s);''', [userid, patientid, sign])
                    connection.commit()

                cur.execute('''Select * from form_entry where form_id=%s and user_id=%s and patient_id=%s;''',
                            [int(studyprojectid), int(userid), int(patientid)])
                record = cur.fetchone()
                if record is None:
                    print("i got called 4")
                    cur.execute('''Insert into form_entry (form_id, user_id, patient_id) values 
                    (%s, %s, %s);''', [studyprojectid, userid, patientid])
                    connection.commit()
                    formentryid = cur.lastrowid
                    for eachrecord in data:
                        fieldid = eachrecord.split('_&&_')[0]
                        value = eachrecord.split('_&&_')[1]
                        cur.execute('''Insert into form_entry_data (form_entry_id, form_fields_id, `value`)
                        values(%s, %s, %s);''', [formentryid, fieldid, value])
                        connection.commit()
                else:
                    print("i got called 5")
                    formentryid = record[0]
                    for eachrecord in data:
                        fieldid = eachrecord.split('_&&_')[0]
                        value = eachrecord.split('_&&_')[1]
                        cur.callproc("insertorupdateformvalue", [int(formentryid), fieldid, value]);
                        connection.commit()
                username1 = session.get("username")
                event = "Case Data Added"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
                connection.commit()
                cur.close()
                connection.close()

                return str(True)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        session["error"] = error
        return redirect(url_for("caseview"))

# Case patient details
@app.route("/casepatientdetail")
def casepatientdetials():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        if request.method == "POST":
            return str(True)
        else:
            patientid = request.args.get('patientid')
            studyprojectid = request.args.get('studyprojectid')
            # userid = session.get('userid')
            if request.args.get('doctorid') is not None:
                userid = request.args.get('doctorid')
            else:
                userid = session.get('userid')
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''Select * from form_entry where form_id=%s and patient_id=%s;''',
                        [int(studyprojectid), int(patientid)])
            record = cur.fetchone()
            mydict = {}
            mydict["success"] = False
            if record is not None:
                formentryid = record[0]
                mydict = {}
                cur.execute('''Select * from form_entry_data where form_entry_id=%s;''', [int(formentryid)])
                data = cur.fetchall()
                for eachfield in data:
                    mydict[str(eachfield[2])] = eachfield[3]
                mydict["success"] = True
            return jsonify(mydict)


@app.route("/test", methods=["GET", "POST"])
def test():
    status = session.get("status")
    role = session.get("role")
    username = session.get("username")
    message = session.get("message")
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute('''select user_id, name, user_name, contact_number, address, parent_id from user
                where role=2 and status='active';''')
    users = cur.fetchall()
    username1 = session.get("username")
    event = "List Opened"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()

    cur.close()
    connection.close()
    headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D"]
    return render_template("tetss.html", status=status, data=users,
                           headers=headers, role=role,
                           username=username)



@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            return redirect(url_for("home"))
        else:
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, user_name, password, role,role2 from user where user_name=%s
                and status='active' and login_attempt='active';''', [username])
                user = cur.fetchone()
                print(user,"user data")
                cur.close()
                connection.close()
                if user is not None:
                    date1 = date.today().strftime("%B %d, %Y")
                    today = datetime.datetime.now().strftime("%I:%M:%S %p")

                    if (check_password_hash(user[2], password)) or (user[2]== password) is True:
                        session["username"] = user[1]
                        if user[3] == 1:
                            session["status"] = "admin"
                        elif user[3] == 2:
                            session["status"] = "doctor"
                        elif user[3] == 3:
                            session["status"] = "assistant"
                        elif user[3] == 4:
                            session["status"] = "representative"
                        session["userid"] = user[0]
                        session["role"] = user[3]
                        session["role2"] = user[4]
                        # message = Message("Login In!", recipients=["mahruk@gmail.com"])
                        # message.html = """Hi, <br>Recent Login Status<br><br> <strong>Name: </strong>""" + str(
                        #     session['username']) + """ <br><br><strong>Date:  </strong>
                        #             """ + str(date1) + """
                        #             <br><br><strong>Time: </strong>
                        #             """ + str(today) + """
                        #                                 <br><br> Regards, <br>Metrics Research"""
                        # mail.send(message)
                        return redirect(url_for("home"))
                    else:
                        attempt = session.get('attempt')
                        print(attempt)
                        attempt -= 1
                        session['attempt'] = attempt
                        print(attempt)
                        if attempt > 1:
                            session["message"] = "Invalid credentials"
                        elif attempt == 1:
                            session["message"] = "Last attempt to login, your account will be deactivated"
                        elif attempt <= 0:
                            session["message"] = "Your account has been deactivated."
                            connection = mysql.connect()
                            cur = connection.cursor()
                            cur.execute('''UPDATE user
                                           SET login_attempt = 'deactive' 
                                           WHERE user_name=%s;''', [username])
                            connection.commit()
                            cur.close()
                            connection.close()
                        # else:
                        #     session["message"] = "the error is with the number."

                        session["usernameemail"] = username
                else:

                    session["message"] = "Invalid Account."
                    session["usernameemail"] = username
                return redirect(url_for("login"))
            else:
                message = ""
                usernameemail = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                if session.get("usernameemail"):
                    usernameemail = session["usernameemail"]
                    session.pop("usernameemail", None)
            return render_template("login.html", status="null", message=message, usernameemail=usernameemail)
    except Exception as e:
        message = str(e)
        return render_template("login.html", status="null", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        return redirect(url_for("dashboard"))
    else:
        if request.method == "Post":
            return redirect(url_for("register"))
        else:
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
        return render_template("register.html", status="null", message=message)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role") and session.get("role2"):
        session.pop("status", None)
        session.pop("attempt",None)
        session.pop("userid", None)
        session.pop("username", None)
        session.pop("role", None)
        session.pop("role2", None)
        session.clear()
        session['attempt'] = 3
    return render_template("login.html", status="null")


#AFTER UPDATE
@app.route('/patient-list',methods=["POST","GET"])
def patient_list():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
            message1 = request.args.get("message")
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = message1
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            formid = request.cookies.get("formid")
            connection = mysql.connect()
            cur = connection.cursor()
            if status == "admin":
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_id,patient.patient_id,user.user_id,user.name,patient.patient_name,form_entry.created_at FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where 
                user.user_id=%s;''', [int(user)])
            elif username == "monitor":
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_id,patient.patient_id,user.user_id,user.name,patient.patient_name,form_entry.created_at FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where 
                user.user_id=%s;''', [int(user)])
            else:
                cur.execute(''' SELECT form_entry.form_entry_id,patient.patient_id,user.user_id,user.name,patient.patient_name,form_entry.created_at  FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where 
                form_entry.form_id=%s and user.user_id=%s;''', [int(formid),int(loginuserid)])

            connection.commit()
            username1 = session.get("username")
            event = "Patient List Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()

            cur.close()
            data = cur.fetchall()
            print(data)
            header = ["S.NO","DR NAME","PATIENT NAME","CREATE AT","VIEW","DELETE"]
        return render_template("p.html",data=data,header=header,status=status,role=role,username=username)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))


@app.route("/audit/trail", methods=["GET", "POST"])
def audit_trail():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''SELECT * FROM `audittrail` ORDER BY date DESC ;''')
        data = cur.fetchall()
        cur.execute('''select form_id, title from form;''')
        forms = cur.fetchall()
        cur.close()
        connection.close()
        header = ["S.NO","USER NAME","id","EVENT TYPE","DATE TIME"]
        return render_template("audit-trail.html",headers=header,data=data,forms=forms,status=status,role=role)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))



@app.route('/audit/trail/delete',methods=["POST","GET"])
def audit_trail_delete():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            formid = request.cookies.get("formid")
            connection = mysql.connect()
            cur = connection.cursor()
            if status == "admin":
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''delete FROM `audittrail` ;''')
                connection.commit()
                cur.close()
                connection.close()
                return redirect(url_for("audit_trail"))
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))




# @app.route('/download/report/excel')
# def download_report():
#     conn = None
#     cursor = None
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         cursor.execute("""  SELECT user.name,patient.patient_name,form_entry.created_at FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id """)
#         result = cursor.fetchall()
#         print(result)
        
#         #add a sheet
#         sh = workbook.add_sheet('Case Report')
        
#         #add headers
#         sh.write(0, 0, 'DR NAME')
#         sh.write(0, 1, 'PATIENT NAME')
#         sh.write(0, 2, 'CREATED_AT')
        
        
#         idx = 0
#         for row in result:
#             sh.write(idx+1, 0, str(row['name']))
#             sh.write(idx+1, 1, row['patient_name'])
#             sh.write(idx+1, 2, str(row['created_at']))
            
#             idx += 1
        
#         workbook.save(output)
#         output.seek(0)
        
#         return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
#     except Exception as e:
#         return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
    
#     finally:
#         cursor.close() 
#         conn.close()


# @app.route('/case/report/list/download',methods=["POST","GET"])
# def download_case_report_list():
#     # try:
#     id = request.cookies.get("formid")
#     print(id,"zohaib")
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute("""  SELECT patient.patient_id,case when  v1.field_type = "radio" then (select form_fields.label from form_fields     where form_fields.form_fields_id = (v1.form_fields_id - 1))
#                     else v1.label end as "label",
#                     case when  v1.field_type = "radio" and form_entry_data.value = 1 then SUBSTRING_INDEX(v1.label, ',', 1)
#                     when  v1.field_type = "radio" and form_entry_data.value = 2 then SUBSTRING_INDEX(v1.label, ',', -1)
#                     else form_entry_data.value end as "Value"
#                     FROM `form_entry` INNER join user on user.user_id = form_entry.user_id
#                     INNER join  patient on form_entry.patient_id = patient.patient_id
#                     inner JOIN form_entry_data on form_entry_data.form_entry_id = form_entry.form_entry_id
#                     INNER JOIN form_fields as v1 on form_entry.form_id = v1.form_id and v1.form_fields_id = form_entry_data.form_fields_id where v1.form_id = %s;  """,[id])
#     result = cursor.fetchall()
#
#     cursor.execute("""SET @sql = NULL;
# SELECT
# GROUP_CONCAT(DISTINCT
# CONCAT(
#   'max(case when label= ''',
#   label,
#   ''' then Value end) '
#
# )
# ) INTO @sql
# FROM
# reportdata ;
#
# SET @sql = CONCAT('SELECT  patient_id, ', @sql, '
#               FROM    reportdata
#               GROUP   BY patient_id');
#
# PREPARE stmt FROM @sql;
# EXECUTE stmt;
# DEALLOCATE PREPARE stmt;""")
#
#     data = cursor.fetchall()
#     print("ASdsad")
#     print(data)
#
#     listt = ["Patient Id"]
#     data = []
#     userid = result[0][0]
#     userdata = []
#     for record in result:
#         if record[1] not in listt:
#                 listt.append(record[1])
#
#         if userid == record[0]:
#             if record[0] not in userdata:
#                 userdata.append(record[0])
#
#             userdata.append(record[2])
#         else:
#             userid = record[0]
#             data.append(userdata)
#             userdata = []
#             if record[0] not in userdata:
#                 userdata.append(record[0])
#
#
#             userdata.append(record[2])
#         print(userdata)
#
#     with open(os.path.join(app.config['UPLOAD_FOLDER'], 'newrecord.csv'), 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(listt)
#         for alldata in data:
#             writer.writerow(alldata)
#
#     cursor.close()
#     conn.close()
#
#     return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'newrecord.csv'), as_attachment=True)
#     # except Exception as e:
#     #     session["error"] = "this project has not data"
#     #     return redirect(url_for("casedetail_rights"))

@app.route('/case/report/list/download', methods=["POST", "GET"])
def download_case_report_list():
    try:
        # id = request.cookies.get("formid")
        id = int(request.args.get("formid"))
        print(id, "zohaib")
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select 1 from reportdata where form_id = %s", [id])
        checkData = cursor.fetchall()
        if len(checkData) > 0:
            cursor.callproc("REPORTLIST", [id])
            data = cursor.fetchall()
            header = cursor.description
        else:
            data = []
            header = []
        Headers = []
        print("this is header")
        print(header)
        for index, head in enumerate(header):
            print(head)
            if index > 0:
                headername = head[0].split("'")[1]
                Headers.append(headername)
            else:
                Headers.append(head[0])

        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'newrecord.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(Headers)
            for alldata in data:
                writer.writerow(alldata)

        cursor.close()
        conn.close()

        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'newrecord.csv'), as_attachment=True)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casedetail_rights"))


@app.route('/case/report/download3',methods=["POST","GET"])
def download_case_report_list3():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        user = request.args.get("id")
        formid = request.cookies.get("formid")
        
        
        cursor.execute('''select user.name,patient.patient_name,form_entry.created_at  FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where form_entry.form_id=%s and user.user_id=%s;''', [int(formid),int(loginuserid)])
        result = cursor.fetchall()
        print(result)       
        #add a sheet
        sh = workbook.add_sheet("Dr's Patient list")        
        #add headers
        sh.write(0, 0, 'DR NAME')
        sh.write(0, 1, 'PATIENT NAME')
        sh.write(0, 2, 'CREATED_AT')        
        active = "active"
        idx = 0
        for row in result:
            sh.write(idx+1, 0, str(row['name']))
            sh.write(idx+1, 1, str(row['patient_name']))
            sh.write(idx+1, 2, str(row['created_at']))
            
            idx += 1
        workbook.save(output)
        output.seek(0)
        
        
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
    except Exception as e:
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
        
    
    finally:
        cursor.close() 
        conn.close()
        


@app.route('/case/report/download2',methods=["POST","GET"])
def download_case_report_list2():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        user = request.args.get("id")
        formid = request.cookies.get("formid")
        
        cursor.execute('''select user.name,patient.patient_name,form_entry.created_at  FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where form_entry.form_id=%s and user.user_id=%s;''', [int(formid),int(loginuserid)])
        result = cursor.fetchall()
        print(result)       
        #add a sheet
        sh = workbook.add_sheet(" Patient")     
        #add headers
        sh.write(0, 0, 'DR NAME')
        sh.write(0, 1, 'PATIENT NAME')
        sh.write(0, 2, 'CREATED_AT')        
        active = "active"
        idx = 0
        for row in result:
            sh.write(idx+1, 0, str(row['name']))
            sh.write(idx+1, 1, str(row['patient_name']))
            sh.write(idx+1, 2, str(row['created_at']))
            idx += 1
        workbook.save(output)
        output.seek(0)
        
        
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
    # except Exception as e:
    #   print(e)
    
    finally:
        cursor.close() 
        conn.close()



@app.route('/dr/list/download',methods=["POST","GET"])
def dr_list_download():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        user = request.args.get("id")
        formid = request.cookies.get("formid")
        
        cursor.execute('''select name, user_name, contact_number, address, parent_id,role2 from user
            where role=2 and status='active';''')
        result = cursor.fetchall()
        print(result)       
        #add a sheet
        sh = workbook.add_sheet(" DR List ")        
        #add headers
        sh.write(0, 0, 'DR NAME')
        sh.write(0, 1, 'USER NAME')
        sh.write(0, 2, 'CONTACT NUMBER')        
        sh.write(0, 3, 'ADRESS')        
        sh.write(0, 4, 'PROJECT I.D')       
        sh.write(0, 5, 'ROLE')      
        idx = 0
        for row in result:
            sh.write(idx+1, 0, str(row['name']))
            sh.write(idx+1, 1, str(row['user_name']))
            sh.write(idx+1, 2, str(row['contact_number']))
            sh.write(idx+1, 3, str(row['adress']))
            sh.write(idx+1, 4, str(row['patient_id']))
            sh.write(idx+1, 5, str(row['role2']))
            idx += 1
        workbook.save(output)
        output.seek(0)
        username1 = session.get("username")
        event = "Doctor List Downloaded"
        cursor.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        conn.commit()

        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})
    except Exception as e:
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})


    finally:
        cursor.close() 
        conn.close()






#user setting

# @app.route('/setting',methods=["POST","GET"])
# def setting():
#     try:
#         if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
#             if request.method == "POST":
#                 status = session.get("status")
#                 role = session.get("role")
#                 username = session.get("username")
#                 loginuserid = session.get("userid")
#                 password = request.form.get("password")
#                 new_password = request.form.get("newpassword")
#                 message = ""
#                 if session.get("message"):
#                     message = session.get("message")
#                     session.pop("message", None)
#                 error = ""
#                 if session.get("error"):
#                     error = session.get("error")
#                     session.pop("error", None)
#                 formid = request.cookies.get("formid")
#                 connection = mysql.connect()
#                 cur = connection.cursor()
#                 cur.execute(""" SELECT * FROM `user` WHERE name=%s; """, [username])
#                 password1 = cur.fetchone()
#                 if password1[3] == password:
#                     hashpassword = generate_password_hash(password)
#                     cursor.execute("""update `user` set `password` =%s  where username=%s """, [hashpassword, username])
#                     connection.commit()
#                     cur.close()
#                     connection.close()
#                     return "true"
#                     #return redirect(url_for("setting"))
#             else:
#                 username = session.get("username")
#                 return render_template("setting.html",username=username)
#     except Exception as e:
#         session["error"] = str(e)
#         return redirect(url_for("casereportlist"))


@app.route("/monitoring/add", methods=["GET", "POST"])
def monitoring_add():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            if request.method == "POST":
                role = session.get("role")
                name = request.form["name"]
                username = request.form["username"]
                password = request.form["password"]
                contactno = request.form["contactno"]
                address = request.form["address"]
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select user_id, user_name, password from user where user_name=%s;''', [username])
                user = cur.fetchone()
                if user is not None:
                    session["error"] = "Doctor with this username already exist. Please try " \
                                       "with a different usernmae."
                    session["a"] = name
                    session["b"] = contactno
                    session["c"] = address
                    return redirect(url_for("monitoring_add"))
                else:
                    hashpassword = generate_password_hash(password)
                    cur.execute('''insert into user (name, user_name, password, contact_number, address, 
                    rep_code, role) values(%s, %s, %s, %s, %s, %s, %s);''',
                                [name, username, hashpassword, contactno, address, 0, 5])
                    connection.commit()
                    docid = cur.lastrowid
                    for eachcase in form:
                        cur.execute('''insert into user_form_permissions (user_id, form_id) values(%s, %s);''',
                                    [int(docid), int(eachcase)])
                        connection.commit()
                    session["message"] = "Doctor added successfully"
                cur.close()
                connection.close()
                return redirect(url_for("monitoring_add"))
            else:
                connection = mysql.connect()
                cur = connection.cursor()
                event = "Add Doctor Opened"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
                cur.close()
                connection.close()
                message = ""
                a = b = c = ''
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                if session.get("a") and session.get("b") and session.get("c"):
                    a = session.get("a")
                    b = session.get("b")
                    c = session.get("c")
                    session.pop("a", None)
                    session.pop("b", None)
                    session.pop("c", None)
                connection = mysql.connect()
                cur = connection.cursor()
                cur.execute('''select form_id, title from form;''')
                forms = cur.fetchall()
                cur.close()
                connection.close()
            return render_template("monitoring.html", status=status, message=message, error=error,
                                   forms=forms, role=role, username=username, a=a, b=b, c=c)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        return render_template("monitoring.html", status=status, error=str(error), role=role,
                               username=username)


#project-wise audit trail
@app.route("/project-wise-audittrail", methods=["GET", "POST"])
def projectwise_audit_trail():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
            message1 = request.args.get("message")
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = message1
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            connection = mysql.connect()
            cur = connection.cursor()
            if status == "admin":
                cur.execute('''select form_id,title from form;''')
                data = cur.fetchall()
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
            elif username == "monitor" :
                cur.execute('''select form_id, title  from form;''')
                data = cur.fetchall()
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()

            else:
                cur.execute('''select form.form_id, form.title, form.status, form.created_at from form where 
                form.form_id in (select user_form_permissions.form_id from user_form_permissions 
                where user_form_permissions.user_id = %s);''', [int(loginuserid)])
                data = cur.fetchall()
                event = "Case Report List Viewed"
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',[username, event])
                connection.commit()
                

            cur.close()
            connection.close()
            headers = ["S.NO", "TITLE",  "ACTION"]
            header2 = ["S.NO", "TITLE", "ACTION"]
            return render_template("projectwise-audit-trail.html", status=status, message=message, data=data,
                                   headers=headers, error=error, role=role, username=username,header2=header2)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select form_id, title, created_at, status from form;''')
        data = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
        return render_template("reportlist.html", status=status, data=data,
                               headers=headers, error=error, role=role, username=username)



#project wise audit trail detail

@app.route("/audit-trail-detail", methods=["GET", "POST"])
def audit_trail_detail():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
        user_id = request.args.get("id")
        message1 = request.args.get("message")
        if message1 != None:
            connection = mysql.connect()
            cur = connection.cursor()
            event = message1
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
            connection.commit()

        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''SELECT * FROM `audittrail` where form_id=%s ORDER BY date DESC  ;''',[user_id])
        data = cur.fetchall()
        cur.execute('''select form_id, title from form;''')
        forms = cur.fetchall()
        cur.close()
        connection.close()
        header = ["S.NO","USER NAME","id","EVENT TYPE","DATE TIME"]
        return render_template("audit-trail-detail.html",headers=header,data=data,forms=forms,status=status,role=role,username=username)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))



@app.route("/user-right", methods=["GET", "POST"])
def user_right():
    if request.method == "POST":
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute(''' select user_id from userid order by sno DESC limit 1''')
        zb = cur.fetchall()
        zb = str(zb)
        print(zb)

        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
  
        # Removing punctuations in string
        # Using loop + punctuation string
        for ele in zb: 
            if ele in punc: 
                zb = zb.replace(ele, "") 
  
        # printing result 
        print("The string after punctuation filter : " + zb)          
        cur.close()
        connection.close()
      
        delete = request.form.get("delete")
        edit = request.form.get("edit")
        add = request.form.get("add")
        view = request.form.get("view")
        lock = request.form.get("lock")
        data_download = request.form.get("data_download")
        query = request.form.get("query")
        print(delete,edit,add,view,lock)
        print(query)
        
        if session.get("status") and session.get("username") and session.get("userid"):
            username = session.get("username")
            loginuserid = session.get("userid")
            user_id = request.args.get("id")
            connection = mysql.connect()
            cur = connection.cursor()
            
            cur.execute(''' select * from rights where user_id=%s; ''',[int(zb)])
            data = cur.fetchone()
            if data is not None:
                print("this is exist")
                data = data[1]
                if str(data) == str(zb):
                    print("match")
                    connection = mysql.connect()
                    cur = connection.cursor()
                    cur.execute('''update rights set editt=%s, deletee=%s,addd=%s,vieww=%s,data_download=%s,lockk=%s,query=%s 
                    where user_id=%s;''',[edit,delete,add,view,data_download,lock,query,int(data)])
                    print("done")
                    connection.commit()
                    cur.close()
                    connection.close()
                    print("done2")
                    #return redirect("/casedetail")
                return redirect("/casedetail")
               
            else:
                cur.execute(""" SELECT form_entry_id,form_id , user_id FROM form_entry WHERE user_id=%s; """,[loginuserid])
                auditt = cur.fetchone()
                form_id = auditt[1]
                cur.execute('''insert into rights (user_id,editt, deletee,addd,vieww,lockk,form_id) values(%s,%s,%s,%s,%s,%s,%s);''',
                [zb, edit, delete,add,view,lock,form_id])
                connection.commit()
                cur.close()
                connection.close()
                return redirect("/casedetail")
           
                    
    else:
        user_id2 = request.args.get("id")
        status = session.get("status")
        role = session.get("role")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''insert into userid (user_id) values(%s);''',
        [user_id2])
        connection.commit()
        cur.close()
        connection.close()
        return render_template("rights.html",status=status,role=role)

@app.route("/user/rights/list", methods=["GET", "POST"])
def user_rights_list():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):

            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            message1 = request.args.get("message")
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = message1
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute('''SELECT user.user_name,rights.editt,rights.deletee,rights.addd,rights.vieww,rights.lockk,rights.sign,user.user_id 
            FROM user left JOIN rights ON user.user_id = rights.user_id
            order by user.user_name ;''')
            rights_list = cur.fetchall()
            print(rights_list,"mjhy dekho")
            username1 = session.get("username")
            event = "User Rights List Opened"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()

            cur.close()
            connection.close()
            headers = ["USER NAME", "EDIT", "DELETE","ADD", "VIEW","LOCK", "DIGITAL SIGNATURE","UPDATE"]
            return render_template("user-rights-list.html", rights_list=rights_list,headers=headers,status=status,role=role,username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        error = str(e)
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select user_id, name, user_name, contact_number, address, parent_id, role2 from user
                    where role=2 and status='active';''')
        users = cur.fetchall()
        cur.close()
        connection.close()
        headers = ["S.NO", "NAME", "USER NAME", "CONTACT NUMBER", "ADDRESS", "PROJECT I.D","ROLE", "EDIT", "DELETE"]
        return render_template("doctorlist.html", status=status, data=users, headers=headers, error=error,
                               role=users[6], username=username)


@app.route("/project-wise-userrights-list", methods=["GET", "POST"])
def projectwise_wise_userrights_list():
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        error = ""
        if session.get("error"):
            error = session.get("error")
            session.pop("error", None)

        connection = mysql.connect()
        cur = connection.cursor()
        if status == "admin":
            cur.execute('''select form_id, title from form;''')
            data = cur.fetchall()

        username1 = session.get("username")
        event = "Project User Rights List Opened"
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        connection.commit()

        header = ["S.NO", "Project" ]
        return render_template("projectwise-rights-list.html",header=header,data=data,status=status,role=role)



@app.route("/user-rights-detail", methods=["GET", "POST"])
def user_rights_detail():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
        user_id = request.args.get("id")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''SELECT user.user_name,rights.editt,rights.deletee,rights.addd,rights.vieww,rights.lockk,rights.data_download FROM rights INNER JOIN user ON user.user_id = rights.user_id where form_id=%s   ;''',[user_id])
        data = cur.fetchall()
        cur.execute('''select form_id, title from form;''')
        forms = cur.fetchall()
        username1 = session.get("username")
        event = "User Rights Details Opened"
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        connection.commit()
        cur.close()
        connection.close()
        header = ["USER NAME", "EDIT", "DELETE","ADD", "VIEW","LOCK","DATA DOWNLOAD"]
        return render_template("user-rights-detail.html",headers=header,data=data,forms=forms,status=status,role=role)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))


@app.route("/user/rights/update", methods=["GET", "POST"])
def user_rights_update():
    if request.method == "GET":
        id = request.cookies.get("formid")
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        connection = mysql.connect()
        cur = connection.cursor()
        event = "User Rights Opened"
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                    [username, event])
        connection.commit()
        cur.close()
        connection.close()
        print(id)
        return render_template("user-rights-update.html",role=role,status=status,username=username)

    if request.method == "POST":

        id = request.cookies.get("formid")
        print(id,"me hun id")

        delete = request.form.get("delete")
        edit = request.form.get("edit") 
        add = request.form.get("add")
        view = request.form.get("view")
        lock = request.form.get("lock")
        sign = request.form.get("sign")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''select * from rights where user_id=%s;''',[id])
        user_data = cur.fetchone()
        if user_data != None:
            username1 = session.get("username")
            event = "User Rights Updated"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.execute(''' update rights set editt=%s,deletee=%s,addd=%s,vieww=%s,lockk=%s,sign=%s where user_id=%s; ''',[edit,delete,add,view,lock,sign,id])
            connection.commit()
        else:
            username1 = session.get("username")
            event = "User Rights Added"
            cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
            connection.commit()
            cur.execute(''' insert into rights (user_id,editt,deletee,addd,vieww,lockk,sign,form_id)
            values(%s,%s,%s,%s,%s,%s,%s,%s); ''',
                        [id,edit, delete, add, view, lock,sign,12])
            connection.commit()

        username1 = session.get("username")
        event = "User Rights Update Opened"
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        connection.commit()
        
        cur.close()
        connection.close()
        return redirect('/user/rights/list') 

@app.route("/edit-patient", methods=["GET", "POST"])
def edit_patient():
    
    if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
        status = session.get("status")
        role = session.get("role")
        username = session.get("username")
        loginuserid = session.get("userid")
    if request.method == "POST":
        sno = request.form.get("sno")
        createdby = request.form.get("createdby")
        pname = request.form.get("pname")
        contact = request.form.get("contact")
        adress = request.form.get("adress")
        idd = request.form.get("idd")
       
        cnic = request.form.get("cnic")
        connection = mysql.connect()
        cur = connection.cursor()
        
        cur.execute(''' update patient set created_by=%s,patient_name=%s,contact=%s,address=%s,cnic=%s where patient_id=%s''',[createdby,pname,contact,adress,cnic,sno])
        connection.commit()
        username1 = session.get("username")
        event = "Patient Updated"
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
        connection.commit()
        cur.close()
        connection.close()
        session["message"] = "Data Has Been Updated"
        return redirect(f"/edit-patient?id={idd} ") 
    else:
        id = request.args.get("id")
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute(''' select * from patient where patient_id = %s ;''',[id])
        patient = cur.fetchone()

        cur.execute(''' select * from patient where patient_id = %s ;''',[id])
        patient = cur.fetchone()

        cur.execute(''' SELECT patient_id,created_by,patient_name,contact,patient.address,user.user_name FROM patient INNER JOIN user ON user.user_id = patient.created_by where patient_id=%s ;''',[id])
        patient2 = cur.fetchall()
      
        cur.close()
        connection.close()
        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        return render_template('edit-patient.html',patient=patient,data2 =patient2,id=id,status=status,role=role,message=message) 
            

@app.route("/delete-patient", methods=["GET", "POST"])
def delete_patient():
    id = request.args.get("id")
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute(''' delete from patient where patient_id=%s ;''',[id])
    cur.execute(''' delete from form_entry where patient_id=%s ;''',[id])
    connection.commit()
    username1 = session.get("username")
    event = "Patient Deleted"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()
    cur.close()
    connection.close()
    return redirect("/site-area")


@app.route("/lock-patient", methods=["GET", "POST"])
def lock_patient():
    id = request.args.get("id")
    status = "locked"
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute(''' update patient set status=%s where patient_id=%s ;''',[status,id])
    connection.commit()
    username1 = session.get("username")
    event = "Patient Record Locked"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()
    cur.close()
    connection.close()
    return redirect("/casedetail") 


@app.route("/unlock-patient", methods=["GET", "POST"])
def unlock_patient():
    id = request.cookies.get("patientid")
    status = "unlock"
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute(''' update patient set status=%s where patient_id=%s ;''',[status,id])
    connection.commit()
    username1 = session.get("username")
    event = "Patient Record Unlocked"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()
    cur.close()
    connection.close()
    return redirect("/locked-list") 


@app.route("/locked-list", methods=["GET", "POST"])
def locked_list():
    status = session.get("status")
    role = session.get("role")
    id = request.args.get("id")
    formid = request.cookies.get("formid")
    print(formid)
    print(id)
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute(""" select *, form_entry.form_id from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id WHERE patient.status = "locked" and form_entry.form_id=%s ;""",[formid])
    locked_patient = cur.fetchall()

    cur.execute(""" select form_entry.form_id, COUNT(form_entry.form_id) as count from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id where form_entry.form_id=%s ;""",[formid])
    total_patient_number = cur.fetchone()
    total_patient_number = total_patient_number[1]

    print(total_patient_number,"total")

    cur.execute("""  select form_entry.form_id, COUNT(form_entry.form_id) as "count" from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id WHERE patient.status = "locked" and form_entry.form_id=%s ;""",[formid])
    locked_patient_number = cur.fetchone()
    locked_patient_number = locked_patient_number[1]
    print(locked_patient_number,"locked")
    header = ["PATIENT NAME","CONTACT","CURRENT RESIDANCY","PATIENT ID","CNIC","CREAT AT","VIEW","UNLOCK"]
    connection.commit()
    username1 = session.get("username")
    event = "Locked Patients List Viewed"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()
    cur.close()
    connection.close()
    return render_template("locked-patient.html",locked_patient=locked_patient,header=header,total_patient_number=total_patient_number,locked_patient_number=locked_patient_number,formid=formid,status=status,role=role)


@app.route("/send-to-archive")
def sendToArchive():
    formid = request.cookies.get("formid")
    print(formid)
    conn = mysql.connect()
    cur = conn.cursor()

    cur.execute(""" select form_entry.form_id, COUNT(form_entry.form_id) as count from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id where form_entry.form_id=%s ;""",[formid])
    total_patient_number = cur.fetchone()
    total_patient_number = total_patient_number[1]
    print(total_patient_number,"total")

    cur.execute("""  select form_entry.form_id, COUNT(form_entry.form_id) as "count" from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id WHERE patient.status = "locked" and form_entry.form_id=%s ;""",[formid])
    locked_patient_number = cur.fetchone()
    locked_patient_number = locked_patient_number[1]
    print(locked_patient_number)

    zero = total_patient_number - locked_patient_number
    if zero == 0:
        cur.execute(""" UPDATE patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id SET patient.archive ="yes" WHERE form_entry.form_id = %s AND patient.status = "locked"  ;""",[formid]) 
        conn.commit()

        cur.execute(""" UPDATE form SET archive = "yes" WHERE form_id =%s;""",[formid]) 
        conn.commit()
        conn.close()
        cur.close()
        session["message"] = "Your Project Has Been Archived "
        return redirect("/CaseReport/list")
    else:
        session["error"] = "please all patient lock first"
        return redirect("/CaseReport/list")



@app.route("/archived-project-list")
def archiveProjectList():
    status = session.get("status")
    role = session.get("role")
    username = session.get("username")
    message1 = request.args.get("message")
    if message1 != None:
        connection = mysql.connect()
        cur = connection.cursor()
        event = message1
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
        connection.commit()

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(""" SELECT form_id,title FROM form WHERE archive = "yes"; """)
    project_list = cur.fetchall()
    username1 = session.get("username")
    event = "Archive Project List Viewed"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    conn.commit()

    conn.close()
    cur.close()
    header = ["S.NO","PROJECT NAME","View Patient"]
    return render_template("archive-project-list.html",project_list=project_list,header=header,status=status,role=role,
                           username=username)
        

@app.route("/archived-patient-list", methods=["GET", "POST"])
def archivedPatientList():
    formid = request.cookies.get("formid")
    print(formid)
    print(id)
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute(""" select *, form_entry.form_id from patient INNER JOIN form_entry ON form_entry.patient_id = patient.patient_id WHERE patient.status = "locked" and form_entry.form_id=%s ;""",[formid])
    locked_patient = cur.fetchall()
    username1 = session.get("username")
    event = "Archive Patient List Viewed"
    cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username1, event])
    connection.commit()

    cur.close()
    connection.close()
    header = ["PATIENT NAME","CONTACT","CURRENT RESIDANCY","PATIENT ID","CNIC","CREAT AT","VIEW","UNLOCK"]
    return render_template("archived-patient-list.html",locked_patient=locked_patient,header=header)




@app.route('/download/report/pdf')
def download_report():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select title,created_at,project_id,status from form limit 10")
        result = cursor.fetchall()
        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.set_font('Times','B',14.0) 
        pdf.cell(page_width, 0.0, 'Employee Data', align='C')
        pdf.ln(10)
        pdf.set_font('Courier', '', 12)
        col_width = page_width/4
        pdf.ln(1)
        th = pdf.font_size
        
        for row in result:
            pdf.cell(col_width, th, str(row['title']), border=1)
            pdf.cell(col_width, th, row['created_at'], border=1)
            pdf.cell(col_width, th, row['project_id'], border=1)
            pdf.cell(col_width, th, row['status'], border=1)
            pdf.ln(th)
        
        pdf.ln(10)
        
        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, '- end of report -', align='C')
        
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=employee_report.pdf'})
    except Exception as e:
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=employee_report.pdf'})
    finally:     
        cursor.close() 
        conn.close()


@app.route("/address-add", methods=["GET", "POST"])
def address_add():
    if request.method == "POST":
        address = request.form.get("address")
        print(address)
        connection = mysql.connect()
        cur = connection.cursor()

        cur.execute('''insert into address (address) values(%s);''',
        [address])
        connection.commit()
        username1 = session.get("username")
        event = "Address Added"
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                    [username1, event])
        connection.commit()

        cur.close()
        connection.close()

        session["message"] = "Address added successfully"
        return redirect("/address-add") 
    else:
        connection = mysql.connect()
        cur = connection.cursor()
        status = session.get("status")
        role = session.get("role")
        username1 = session.get("username")
        message = ""
        if session.get("message"):
            message = session.get("message")
            session.pop("message", None)
        event = "Add Address Opened"
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''',
                    [username1, event])
        connection.commit()
        return render_template('adress-add.html',message=message,status=status,role=role) 

@app.route('/patient-list2',methods=["POST","GET"])
def patient_list2():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            username = session.get("username")
            loginuserid = session.get("userid")
            message1 = request.args.get("message")
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = message1
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            if status == "admin":
                formid = request.args.get("formid")
                address = request.args.get("address")
                
                #formid = int(formid)
                print(type(formid))
                connection = mysql.connect()
                cur = connection.cursor()
           
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_entry.form_entry_id,patient.patient_id,user.user_id,user.name,patient.patient_name,patient.cnic,form_entry.created_at,form_id  FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where 
                form_entry.form_id=%s and user.address =%s;''', [formid,address])
                cur.close()
                data = cur.fetchall()
                print(data)
                header = ["S.NO","DR NAME","PATIENT NAME","CNIC", "CREATE AT","Edit","DELETE","VIEW"]
                return render_template("p2.html",data=data,header=header,loginuserid=loginuserid,username=username,status=status,role=role)

            else:
                formid = request.args.get("formid")
                address = request.args.get("address")
                print(address,"ADD")
                
                #formid = int(formid)
                print(type(formid))
                connection = mysql.connect()
                cur = connection.cursor()
                loginuserid = session.get("userid")
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_entry.form_entry_id,patient.patient_id,user.user_id,user.name,patient.patient_name,patient.cnic,form_entry.created_at,form_id  FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id INNER JOIN patient ON patient.patient_id = form_entry.patient_id where 
                form_entry.form_id=%s and user.address =%s and user.user_id=%s;''', [formid,address,loginuserid])
                cur.close()
                data = cur.fetchall()
                print(data)
                header = ["S.NO","DR NAME","PATIENT NAME","CNIC", "CREATE AT","Edit","DELETE","VIEW"]
                return render_template("p2.html",data=data,header=header,username=username,role=role,status=status)

            #return render_template("p2.html",data=data,header=header)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))



@app.route('/site-area',methods=["POST","GET"])
def site_area():
    try:
        if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
            status = session.get("status")
            role = session.get("role")
            role2 = session.get("role2")
            username = session.get("username")
            message1 = request.args.get("message")
            print(message1,"here i am")
            # print(username,"u name")
            loginuserid = session.get("userid")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            if message1 != None:
                connection = mysql.connect()
                cur = connection.cursor()
                event = message1
                cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
                connection.commit()

            if username == "admin":
                formid = request.cookies.get("formid")
                connection = mysql.connect()
                cur = connection.cursor()
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_entry.form_entry_id,patient.patient_id,user.user_id,address.address,form_id,user.address  
                FROM form_entry 
                INNER JOIN user ON user.user_id = form_entry.user_id 
                INNER JOIN patient ON patient.patient_id = form_entry.patient_id
                RIGHT JOIN address on
                address.sno = user.address 
                where 
                form_entry.form_id=%s group by user.address;''', [formid])
            else:
                formid = request.cookies.get("formid")
                print(formid,"formid")
                user = request.args.get("id")
                connection = mysql.connect()
                cur = connection.cursor()
                header = ["S.SO","DR NAME","PATIENT NAME","CREATED","View","DELETE"]
                cur.execute(''' SELECT form_entry.form_entry_id,patient.patient_id,user.user_id,address.address,form_id,user.address  
                FROM form_entry INNER JOIN user ON user.user_id = form_entry.user_id 
                INNER JOIN patient ON patient.patient_id = form_entry.patient_id 
                RIGHT JOIN address on
                address.sno = user.address
                where form_entry.form_id=%s and user.user_id=%s group by user.address;''', [formid,loginuserid])


            data = cur.fetchall()
            print(data)
            header = ["S.NO","Sites","VIEW"]
            return render_template("site-area.html",data=data,header=header,status=status,role=role,role2=role2,username=username)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("casereportlist"))

@app.route('/newtemp',methods=["POST","GET"])
def newtemp():
    formid = request.args.get("formid")
    patientid = request.args.get("patientid")
    doctorid = request.args.get("doctorid")
    return render_template("netemp.html", formid=formid, patientid=patientid,
    doctorid=doctorid)



###### query ######
@app.route("/query",methods=["GET","POST"])
def query():
    if request.method == "POST":
        form_id = request.form.get("formid")
        doctorid = request.form.get("doctorid")
        patientid = request.form.get("patientid")
        query = request.form.get("query")
        print(form_id,doctorid,patientid,query)
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" insert into query (form_idd,user_idd,patient_idd,query) values(%s,%s,%s,%s) ;""",[form_id,doctorid,patientid,query])
        con.commit()
        con.close()
        cur.close()
        return redirect("/casedetail")



@app.route("/query_done")
def queryDone():
    id = request.args.get("id")
    print(id)
    query_status = "yes"
    con = mysql.connect()
    cur = con.cursor()
    cur.execute(""" update query set query_status=%s where query_idd=%s ;""",[query_status,id])
    con.commit()
    cur.close()
    con.close()
    return redirect("/casedetail")


@app.route("/varified-query")
def varifiedQuery():
    username = session.get("username")
    role2 = session.get("role2")
    message1 = request.args.get("message")
    if message1 != None:
        connection = mysql.connect()
        cur = connection.cursor()
        event = message1
        cur.execute('''Insert into audittrail (username, event ) values (%s, %s)''', [username, event])
        connection.commit()

    con = mysql.connect()
    cur = con.cursor()
    cur.execute('''SELECT form.title,patient.patient_name,user.user_name,query,form_id,user_idd,patient_id,query_idd FROM query INNER JOIN form ON form.form_id = query.form_idd INNER JOIN patient ON patient.patient_id = query.patient_idd INNER JOIN user ON user_id = query.patient_idd WHERE  query_status="yes";''')
    data = cur.fetchall()
    con.close()
    cur.close()
    return render_template("varifiedquery.html",data=data,role2=role2,username=username)




@app.errorhandler(404)
def error404(error):
    status = session.get("status")
    role = session.get("role")
    username = session.get("username")
    return render_template('404.html', error=error, status=status, role=role, username=username), 404



@app.route("/checkqury")
def checkquery():
    connection = mysql.connect()
    cur = connection.cursor()
    cur.execute("""SET @sql = NULL;
SELECT
  GROUP_CONCAT(DISTINCT
    CONCAT(
      'max(case when label= ''',
      label,
      ''' then Value end) '
      
    )
  ) INTO @sql
FROM
  reportdata ;

SET @sql = CONCAT('SELECT  patient_id, ', @sql, ' 
                  FROM    reportdata 
                  GROUP   BY patient_id');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;""")

    data = cur.fetchall()
    print(data)

    return "true"

if __name__ == '__main__':
    app.run()

