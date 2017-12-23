from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import sqlite3 as sql

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login_employer', methods=["GET", "POST"])
def login_employer():
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
        # rows = c.execute("SELECT * FROM employee WHERE username = ?", (request.form.get("username"),)).fetchall()

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0][2]):
            return flash("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0][0]

        # redirect user to home page
        flash("logged in")
        return redirect(url_for("index"))
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
        # rows = c.execute("SELECT * FROM employee WHERE username = ?", (request.form.get("username"),)).fetchall()

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0][2]):
            return flash("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0][0]

        # redirect user to home page
        flash("logged in")
        return redirect(url_for("index"))
    else:
        return render_template('login_employee.html')


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        t=1
    else:
        return render_template("profile.html")


@app.route('/employer', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        t=1
    else:
        return render_template('employer-register.html')


app.run("0.0.0.0", "8080")
