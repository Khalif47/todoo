from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import sqlite3 as sql
from helper import *
from classification import *
import ast
from mail_send import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
connect = sql.connect('recruitment.db')
c = connect.cursor()


# c.execute("DROP TABLE post_employee")
# connect.commit()
#
# c.execute(
#     '''CREATE TABLE profiles (id INTEGER PRIMARY KEY, username STRING UNIQUE NOT NULL, hash TEXT NOT NULL, name STRING NOT NULL, suburb INTEGER NOT NULL, projects STRING NULL, industry STRING NOT NULL, description STRING NULL, skills STRING NULL, aspirations STRING NULL, years STRING NULL, positions STRING NULL, company STRING NULL, industries STRING NULL, email STRING NULL)''')
# connect.commit()


# c.execute(
#     '''CREATE TABLE employers (id INTEGER PRIMARY KEY, username STRING UNIQUE NOT NULL, hash STRING NOT NULL, company STRING UNIQUE NOT NULL, suburb STRING NOT NULL)''')
# connect.commit()

# c.execute(
#     '''CREATE TABLE posts (number_id INTEGER PRIMARY KEY, id INTEGER NOT NULL, industry STRING NOT NULL, title STRING NULL, role STRING NULL, skills STRING NULL, positions STRING NULL, years STRING NULL, candidates INTEGER NOT NULL)''')
# connect.commit()

# c.execute(
#     '''CREATE TABLE post_employee (id INTEGER NOT NULL, post_id INTEGER NOT NULL, name STRING NOT NULL, suburb INTEGER NOT NULL, industry STRING NOT NULL, description STRING NULL, skills STRING NULL, aspirations STRING NULL, years STRING NULL, positions STRING NULL, company STRING NULL, industries STRING NULL, email STRING NULL, points INTEGER NULL)''')
# connect.commit()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index_employee')
@login_required
def index_employee():
    return render_template('index_employee.html')


@app.route('/index_employer')
@login_required
def index_employer():
    # get posts and candidates
    job = c.execute("SELECT * FROM posts WHERE id = ?",
                    (session["user_id"],)).fetchall()

    candidates = c.execute("SELECT * FROM post_employee WHERE id = ?",
                           (session["user_id"],)).fetchall()
    print(job)
    print(candidates)
    return render_template('index_employer.html', posts=job, candidates=candidates)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/login_employer', methods=["GET", "POST"])
def login_employer():
    '''logs employer in.'''
    session.clear()
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("company"):
            return 'No username'

        # ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # query database for username
        rows = c.execute("SELECT * FROM employers WHERE company = ?", (request.form.get("company"),)).fetchone()

        # ensure username exists and password is correct
        if rows is None or not pwd_context.verify(request.form.get("password"), rows[2]):
            return "invalid username and/or password"

        # remember which user has logged in
        session["user_id"] = rows[0]

        # redirect user to home page
        flash("logged in")
        return redirect(url_for("index_employer"))
    else:
        return render_template('login_employer.html')


@app.route('/login_employee', methods=["GET", "POST"])
def login_employee():
    '''logs employer in.'''
    session.clear()
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return flash("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return flash("must provide password")

        # query database for username
        rows = c.execute("SELECT * FROM employee WHERE username = ?", (request.form.get("username"),)).fetchone()

        # ensure username exists and password is correct
        if rows is None or not pwd_context.verify(request.form.get("password"), rows[2]):
            return "invalid username and/or password"

        # remember which user has logged in
        session["user_id"] = rows[0]

        # redirect user to home page
        flash("logged in")
        return redirect(url_for("index_employee"))
    else:
        return render_template('login_employee.html')


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST" and request.form.get("number"):
        number = int(request.form.get("number"))
        list_a = []
        for i in range(number):
            list_a.append("a")
        password = pwd_context.encrypt(request.form.get("password"))
        c.execute(
            "INSERT INTO profiles (name, username, suburb, hash, industry, description, skills, aspirations, projects, email) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (request.form.get('name'), request.form.get('username'), request.form.get('suburb'), password,
             request.form.get('industry'), request.form.get('description'), request.form.get('skills'),
             request.form.get('aspirations'), request.form.get('projects'), request.form.get("email")))
        connect.commit()
        rows = c.execute("SELECT id FROM profiles WHERE username = ?", (request.form.get('username'),)).fetchone()
        session["user_id"] = rows[0]
        return render_template("employment.html", number=list_a)
    elif request.method == "POST":
        c.execute("UPDATE profiles SET company = ?, positions = ?, years = ?, industries = ? WHERE id = ?",
                  (str(request.form.getlist('company')), str(request.form.getlist('positions')),
                   str(request.form.getlist('years')), str(request.form.getlist('industries')),
                   session["user_id"]))
        connect.commit()
        return redirect(url_for("index_employee"))
    else:
        return render_template("profile.html")


@app.route("/posts", methods=["GET", "POST"])
@login_required
def posts():
    if request.method == "GET":
        return render_template('post.html')
    elif request.method == "POST" and request.form.get("number-c"):
        # insert into database
        c.execute('INSERT INTO posts (id, industry, title, role, candidates) VALUES (?,?,?,?,?)',
                  (session["user_id"], request.form.get("industry"), request.form.get("title"),
                   request.form.get("role"), int(request.form.get("number-c"))))
        connect.commit()
        id_n = c.execute("SELECT number_id FROM posts WHERE id = ? AND industry = ? AND title = ? AND role = ?",
                         (session["user_id"], request.form.get("industry"), request.form.get("title"),
                          request.form.get("role"))).fetchone()
        session["id"] = id_n[0]
        list_s = []
        list_e = []
        skills = int(request.form.get("number-s"))
        experiences = int(request.form.get("number-e"))
        for i in range(skills):
            list_s.append('a')
        for i in range(experiences):
            list_e.append('a')
        return render_template('post_positions.html', s=list_s, e=list_e)
    else:
        c.execute("UPDATE posts SET skills = ?, positions = ?, years = ? WHERE number_id = ?",
                  (str(request.form.getlist("skills")), str(request.form.getlist("positions")),
                   str(request.form.getlist("years")),
                   session["id"]))
        connect.commit()
        # We know call a function which will figure out how to rank profiles based on job post
        post = c.execute("SELECT * FROM posts WHERE number_id = ?", (session["id"],)).fetchone()
        profiles = c.execute("SELECT * FROM profiles").fetchall()
        profiles = rank_employers(post, profiles)
        # access database narrow number of candidates and insert it into table
        print(session["id"])
        candidates = c.execute('SELECT candidates FROM posts WHERE number_id = ? AND id = ?',
                               (session["id"], session["user_id"])).fetchone()
        profiles = profiles[0:int(candidates[0])]
        # c.execute(
        #     '''CREATE TABLE profiles (id INTEGER PRIMARY KEY, username STRING UNIQUE NOT NULL, hash TEXT NOT NULL, name STRING NOT NULL, suburb INTEGER NOT NULL, projects STRING NULL, industry STRING NOT NULL, description STRING NULL, skills STRING NULL, aspirations STRING NULL, years STRING NULL, positions STRING NULL, company STRING NULL, industries STRING NULL)''')
        # connect.commit()
        for item in profiles:
            c.execute(
                "INSERT INTO post_employee(id, post_id, name, suburb, industry, description, skills, aspirations, years, positions, company, industries, email, points) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (session["user_id"], session["id"], item[3], item[4], item[6], item[7], item[8], item[9], item[10],
                 item[11], item[12], item[13], item[14], int(item[15])))
            connect.commit()
            mail_send(profiles, post)
    return redirect(url_for("index_employer"))


@app.route('/employer', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if len(request.form.get("username")) == 0 or len(request.form.get("password")) == 0:
            return "No Username"
        if request.form.get("password1") != request.form.get("password"):
            return "Different passwords"
        password = pwd_context.encrypt(request.form.get("password"))
        c.execute("INSERT INTO employers (company, username, suburb, hash) VALUES (?,?,?,?)", (
            request.form.get("company"), request.form.get("username"), request.form.get("suburb"), password))
        connect.commit()
        rows = c.execute("SELECT * FROM employers WHERE company = ?", (request.form.get("company"),)).fetchall()
        # remember which user has logged in
        session["user_id"] = rows[0][0]
        # redirect user to home page
        return redirect(url_for("index_employer"))
    else:
        return render_template('employer-register.html')


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    if request.method == "POST":
        data = str(request.form.get("data"))
        data = ast.literal_eval(data)
        return render_template('review.html', data=data)


app.run("0.0.0.0", "8080")
