from flask import Flask, redirect, url_for,render_template, session, request, flash
import os
from os import path
import sqlite3
import db_stuff
import hashlib


app = Flask(__name__)
app.secret_key = 'some_secret'
DIR = path.dirname(__file__)


#console output will appear in /var/log/apache2/error.log

@app.route('/')
def root():
    if "username" in session:
        return redirect(url_for("homepage"))
    return render_template("index2.html")

###############################################################
###############login for student,teacher, admin ###############

@app.route('/studentlogin')
def student_login():
    if "username" in session:
        return redirect(url_for("homepage"))
    return render_template("login.html")

@app.route('/teacherlogin')
def teacher_login():
    if "username" in session:
        return redirect(url_for("teacherhomepage"))
    return render_template("teacherlogin.html")

@app.route('/adminlogin')
def admin_login():
    if "username" in session:
        return redirect(url_for("adminhomepage"))
    return render_template("adminlogin.html")

#############################################################
###################logout fxn ###############################
@app.route('/logout')
def logout():
    if "username" in session:
        session.pop("username")
        return redirect(url_for("root"))
    return render_template("login.html")

##############################################################
#################signup for student and teacher ##############

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if "username" not in session:
        return render_template("signup.html")
    else:
        flash("you are logged in")
        return redirect(url_for("homepage"))

@app.route('/teachersignup', methods=["GET", "POST"])
def teachersignup():
    if "username" not in session:
        return render_template("teachers/signup.html")
    else:
        flash("you are logged in")
        return redirect(url_for("teacherhomepage"))

###########################################################################
################## STUDENT PAGES #########################################
@app.route('/homepage', methods=["GET","POST"])
def homepage():
    if "username" in session:
        username = session["username"]
        name = db_stuff.get_name_from_student(username)
        stuid = db_stuff.get_id_from_student(username)
        osis = db_stuff.get_osis_from_student(username)
        email = name[0][0].lower() + name[1].lower() + "@stuy.edu"
        return render_template("home.html", username = session["username"], name = name, email = email, osis = osis, stuid = stuid)
    return redirect(url_for("auth"))

@app.route('/classes', methods=["GET","POST"])
def class_page():
    if "username" in session:
        username = session["username"]
        return render_template("classes.html", username = session["username"])
    return redirect(url_for("auth"))

@app.route('/calendar', methods=["GET","POST"])
def calendar_page():
    if "username" in session:
        username = session["username"]
        return render_template("calendar.html", username = session["username"])
    return redirect(url_for("auth"))

###########################################################################
##################### TEACHERPAGES #########################################
@app.route('/home', methods=["GET","POST"])
def teacherhomepage():
    if "username" in session:
        username = session["username"]
        # name = db_stuff.get_name_from_student(username)
        # stuid = db_stuff.get_id_from_student(username)
        # osis = db_stuff.get_osis_from_student(username)
        #email = name[0][0].lower() + name[1].lower() + "@stuy.edu"
        return render_template("teachers/home.html", username = session["username"])
    return redirect(url_for("teacherauth"))


###########################################################################
##################### ADMINPAGES #########################################
@app.route('/adminhome', methods=["GET","POST"])
def adminhomepage():
    if "username" in session:
        username = session["username"]
        # name = db_stuff.get_name_from_student(username)
        # stuid = db_stuff.get_id_from_student(username)
        # osis = db_stuff.get_osis_from_student(username)
        #email = name[0][0].lower() + name[1].lower() + "@stuy.edu"
        return render_template("admin/home.html", username = session["username"])
    return redirect(url_for("adminauth"))


############################################################################
################# STUDENT ACTIONS ##########################################
@app.route('/updatestudentpass', methods=["GET","POST"])
def updatepass():
    if "username" in session:
        username = session["username"]
        if request.method == "GET":
            return redirect("/")
        try:
            oldpass = request.form['currentpass']
            password0 = request.form['pass1']
            password1 = request.form['pass2']
        except KeyError:
            flash("Fill evrything in!")
            print "Fail0"
            return redirect(url_for("homepage", error = "Fill everything in!"))
        if db_stuff.get_pass_from_student(username) != hashlib.sha256(oldpass).hexdigest():
            flash("Old password is wrong!")
            print("wrong old")
            return redirect(url_for("homepage", error = "Old password is not correct."))
        if password0 != password1:
            flash("Passwords don't match!")
            print "Fail1"
            return redirect(url_for("homepage", error = "New passwords do not match!"))
        if not min_thres(password0):
            flash("Password must contain upper- and lowercase letters and at least one number")
            print "fail2"
            return redirect(url_for("homepage", error = "New password must contain both upper and lowercase letters, and at least one number."))
        if db_stuff.change_pass(username, password0):
            flash("successfully created!")
            print "success!"
            return redirect(url_for("logout"))
    return redirect(url_for("auth"))
############################################################################
##############LOGIN AUTHORIZATION ##########################################

@app.route('/auth', methods=["GET", "POST"])
def auth():
    if "username" in session:
        return redirect(url_for("homepage"))
    if request.method == "GET":
        return redirect("/")
    try:
        username = request.form['username']
        password = request.form['password']
        #osis = request.form['osis']
        #student_id = request.form['student_id']
    except KeyError:
        flash("Please fill everything in!")
        return render_template("login.html", error = "Please fill everything in!")
    '''
    db authentication
    '''
    if db_stuff.auth(username,password):
        session['username'] = username
        flash("You're logged in!")
        return redirect(url_for("homepage"))
    else:
        flash("oops! Login failed...")
        return render_template("login.html", error = "Wrong credentials. Please try again.")
    #redirect(url_for('root'))

@app.route('/teacherauth', methods=["GET", "POST"])
def teacherauth():
    if "username" in session:
        return redirect(url_for("homepage"))
    if request.method == "GET":
        return redirect("/")
    try:
        username = request.form['username']
        password = request.form['password']
        #osis = request.form['osis']
        #student_id = request.form['student_id']
    except KeyError:
        flash("Please fill everything in!")
        return render_template("teacherlogin.html", error = "Please fill everything in!")
    '''
    db authentication
    '''
    #print(username)
    #print(hashlib.sha256(password).hexdigest())
    if db_stuff.teacherauth(username,password):
        session['username'] = username
        flash("You're logged in!")
        return redirect(url_for("teacherhomepage"))
    else:
        flash("oops! Login failed...")
        return render_template("teacherlogin.html", error = "Wrong credentials. Please try again.")
    #redirect(url_for('root'))

@app.route('/adminauth', methods=["GET", "POST"])
def adminauth():
    if "username" in session:
        return redirect(url_for("adminhomepage"))
    if request.method == "GET":
        return redirect("/")
    try:
        username = request.form['username']
        password = request.form['password']
        #osis = request.form['osis']
        #student_id = request.form['student_id']
    except KeyError:
        flash("Please fill everything in!")
        return render_template("adminlogin.html", error = "Please fill everything in!")
    '''
    db authentication
    '''
    #print(username)
    #print(hashlib.sha256(password).hexdigest())
    if db_stuff.adminauth(username,password):
        session['username'] = username
        flash("You're logged in!")
        return redirect(url_for("adminhomepage"))
    else:
        flash("oops! Login failed...")
        return render_template("adminlogin.html", error = "Wrong credentials. Please try again.")
    #redirect(url_for('root'))



def min_thres(pswd):
    '''
    Returns whether a password meets minimum threshold:
    It contains a mixture of upper- and lowercase letters, and at least one number
    '''
    UC_LETTERS = "QWERTYUIOPASDFGHJKLZXCVBNM"
    LC_LETTERS = UC_LETTERS.lower()
    NUMBERS = "1234567890"
    U= [1 if x in UC_LETTERS else 0 for x in pswd]
    L= [1 if x in LC_LETTERS else 0 for x in pswd]
    N = [1 if x in NUMBERS else 0 for x in pswd]
    upper = 1 in U
    lower = 1 in L
    num = 1 in N
    return upper and lower and num

##################################################################################
########### Adding accounts for students and teachers ###########################
@app.route('/signauth', methods = ["GET", "POST"])
def signauth():
    if "username" in session:
        return redirect(url_for("homepage"))
    if request.method == "GET":
        return redirect("/")
    try:
        name = request.form['name']
        lastname = request.form['name2']
        username = request.form['username']
        password0 = request.form['password0']
        password1 = request.form['password1']
        osis = request.form['osis']
        sid = request.form['sid']
    except KeyError:
        flash("Fill evrything in!")
        print "Fail0"
        return render_template("signup.html", error = "Fill in all fields.")
    if password0 != password1:
        flash("Passwords don't match!")
        print "Fail1"
        return render_template("signup.html", error = "Passwords do not match.")
    if not min_thres(password0):
        flash("Password must contain upper- and lowercase letters and at least one number")
        print "fail2"
        return render_template("signup.html", error = "Passwords must contain both upper and lowercase letters, and at least one number.")
    if db_stuff.add_student(name, lastname, username, password0, osis, sid):
        flash("successfully created!")
        print "sucess!"
        return redirect(url_for("homepage"))
    else:
        flash("username exists")
        return render_template("signup.html", error = "Username already exists.")


@app.route('/teachersignauth', methods = ["GET", "POST"])
def teachersignauth():
    if "username" in session:
        return redirect(url_for("homepage"))
    if request.method == "GET":
        return redirect("/")
    try:
        name = request.form['name']
        lastname = request.form['name2']
        username = request.form['username']
        password0 = request.form['password0']
        password1 = request.form['password1']
    except KeyError:
        flash("Fill evrything in!")
        print "Fail0"
        return render_template("teachers/signup.html", error = "Fill in all fields.")
    if password0 != password1:
        flash("Passwords don't match!")
        print "Fail1"
        return render_template("teachers/signup.html", error = "Passwords do not match.")
    if not min_thres(password0):
        flash("Password must contain upper- and lowercase letters and at least one number")
        print "fail2"
        return render_template("teachers/signup.html", error = "Passwords must contain both upper and lowercase letters, and at least one number.")
    if db_stuff.add_teacher(name, lastname, username, password0):
        flash("successfully created!")
        print "sucess!"
        return redirect(url_for("homepage"))
    else:
        flash("username exists")
        return render_template("teachers/signup.html", error = "Username already exists.")

####################################################################################################

@app.route('/admin')
def admin():
    return render_template('admin/admin.html')

@app.route('/classes')
def classes():
    if "username" not in session:
        return redirect(url_for("auth"))
    username = session['username']
    classes = db_stuff.get_classes_from_student(username)
    headings = ['ID', "Name", "Description"]
    return render_template('info.html', table=classes, headings=headings)

'''
This entire section is just dealing with my lazily written admin code. Sorry whoever reads it.
'''
@app.route('/adminclass', methods=['POST'])
def adminclass():
    print str(db_stuff.add_class(request.form['name'], request.form['tid'], request.form['slist'],  request.form['desc']))
    return render_template('expression')

@app.route('/adminwork', methods=['POST'])
def adminwork():
    print str(db_stuff.add_work(request.form['CID'], request.form['Wdescr'], request.form['Type'], request.form['Date']))
    return render_template("home.html")

@app.route('/addwork', methods=['POST'])
def addclass():
    cl = int(request.form['class'])
    username = session['username']
    db_stuff.append_class(username,cl)
    return render_template('microsoftsucks.html')

app.secret_key = os.urandom(32)
if __name__ == '__main__':
    #app.secret_key = os.urandom(32)
    app.debug = True #DANGER DANGER! Set to FALSE before deployment!
    app.run()
