from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_mysqldb import MySQL
from flask_wtf import Form
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret123'

# config MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mytutor'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# index or home page
@app.route('/')
def index():
    return render_template("index.html")


# about section of the site
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/python')
def python():
    return render_template("python.html")


#
# class RegisterForm(Form):
#     name = StringField('Name', [validators.length(min=1, max=50)])
#     username = StringField('Username', [validators.length(min=4, max=25)])
#     email = StringField('Email', [validators.length(min=6, max=50)])
#     password = PasswordField('Password', [
#         validators.DataRequired(),
#         validators.EqualTo('confirm', message='Password do not match')
#     ])
#     confirm = PasswordField('Confirm Password')


# sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # form = RegisterForm(request.form)
    if request.method == 'POST':
        fname = request.form['firstname']
        lname = request.form['lastname']
        email = request.form['email']
        mobile = str(request.form['mobile'])
        password = sha256_crypt.encrypt(str(request.form['pwd']))

        # return type(fname)

        # create cursor
        cur = mysql.connection.cursor()
        # q="INSERT INTO users(fname,lname,email,mobile, password) VALUES ('"+fname+"', '"+lname+"', '"+email+"', '"+mobile+"', '"+password+"')"
        # cur.execute(q)
        cur.execute(
            "INSERT INTO users(fname,lname,email,mobile, password) VALUES ( %s, %s, %s, %s, %s)",
            (fname, lname, email, mobile, password)

        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    ip = request.remote_addr
    return render_template('signup.html', ip=ip)


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where email = %s", [email])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email

                flash('You are Successfully logged in', 'success')
                return redirect(url_for('index'))

            else:
                error = "Invalid Login"
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# html tutorial page
@app.route('/html')
@is_logged_in
def html():
    return render_template("HTML.html")


@app.route('/profile')
@is_logged_in
def profile():
    email = session['email']
    cur = mysql.connection.cursor()
    q = cur.execute("select fname  from users where email= %s", [email])

    fstnm = cur.fetchone()['fname']
    q = cur.execute("select lname from users where email= %s", [email])
    lstnm = cur.fetchone()['lname']
    username = fstnm + " " + lstnm
    cur.close()

    return render_template('profile.html', username=username)


@app.route('/edit_profile/<string:username>', methods=['GET', 'POST'])
@is_logged_in
def edit_profile(username=None):
    email = session['email']
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        passwrd = request.form['pass']
        newpass = request.form['newpass']
        newpass = sha256_crypt.encrypt(str(newpass))
        mob = request.form['mobile']
        cur = mysql.connection.cursor()
        if fname != '':
            p = cur.execute("update users set fname = %s where email = %s", [fname, email])
        if lname != '':
            r = cur.execute("update users set lname = %s where email = %s", [lname, email])
        pwd = cur.execute("select password from users where email = %s", [email])
        password = cur.fetchone()['password']
        if sha256_crypt.verify(passwrd, password):
            newp = cur.execute("update users set password = %s where email = %s", [newpass, email])
        if mob != '':
            m = cur.execute("update users set mobile = %s where email =%s", [mob, email])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("profile"))

    if request.method == 'GET':
        cur = mysql.connection.cursor()
        q = cur.execute("select fname  from users where email= %s", [email])

        fstnm = cur.fetchone()['fname']
        q = cur.execute("select lname from users where email= %s", [email])

        lstnm = cur.fetchone()['lname']

        username = fstnm + " " + lstnm
        cur.close()
        return render_template("edit.html", username=username)


# logout page
@app.route('/logout')
def logout():
    session.clear()
    flash('You Logged Out', 'danger')
    return redirect(url_for('index'))


# suggestion page
@app.route('/sug')
def sug():
    email = session['email']
    cur = mysql.connection.cursor()
    q = cur.execute("select fname  from users where email= %s", [email])

    fstnm = cur.fetchone()['fname']
    q = cur.execute("select lname from users where email= %s", [email])

    lstnm = cur.fetchone()['lname']

    username = fstnm + " " + lstnm

    cur.close()
    return render_template("sug.html", x=username)


@app.route('/message')
@is_logged_in
def message():
    message = 'abcdef'
    return render_template('message.html', message=message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
