from flask import Flask, request, render_template, redirect, url_for, session, flash
from init_db import app, init_db, get_db, modify_db, query_db
from config import SECRET_KEY, emailRegEx, pwRegEx
from os import path
import re

# Top page
@app.route("/")
def top():
    return render_template("top.html")

# Register (Sign-Up) page
@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in
    if 'userid' in session:
        flash(u"You're already logged in. Redirected to your profile page.", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("register.html", session=session)
        elif request.method == 'POST':
            # Store inputs (except password) in session to auto-fill the forms when redirected
            session['name']   = request.form.get("name")
            session['email']  = request.form.get("email")
            session['gender'] = request.form.get("gender")

            # Validate email (has to be unique, and has to contain @, followed by .)
            if re.fullmatch(emailRegEx, session['email']) == None:
                flash(u"Invalid email address. Please try again.", 'warning')
                return redirect(url_for("register"))
            else:
                if query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True) != None:
                    flash(u"Entered email address is already taken. Please try again with other email address.", 'warning')
                    return redirect(url_for("register"))

            # Validate password (has to be longer than 8 characters,
            # and has to contain at least one uppercase, lowercase, and digit, respectively)
            # Also, password is NOT stored in session for security purposes
            if re.fullmatch(pwRegEx, request.form.get("password")) == None:
                flash(u"Invalid password. Password has to be longer than or equal to 8 characters, \
                       and has to contain at least one uppercase, lowercase, and digit.", 'warning')
                return redirect(url_for("register"))

            # Store new user in DB only if passed all validations
            modify_db("INSERT INTO user (name, email, password, gender) VALUES(?, ?, ?, ?)", \
                      (session['name'], session['email'], request.form.get("password"), session['gender']))

            # Store user ID in session just for convenience
            user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)
            session['userid'] = user['id']

            flash(u"Signed up successfully.", 'info')
            return redirect(url_for('profile', userid=session['userid']))

# Log-In (Sign-In) page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in
    if 'userid' in session:
        flash(u"You're already logged in. Redirected to your profile page.", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("login.html", session=session)
        elif request.method == 'POST':
            # Store inputs (except password) in session to auto-fill the forms when redirected
            session['email'] = request.form.get("email")
            request.form.get("password")

            # Confirm user exists, and entered password matches the stored password
            user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)
            if user == None:
                flash(u"Invalid email or password. Please try again.", 'warning')
                return redirect(url_for("login"))
            elif request.form.get("password") != user['password']:
                flash(u"Invalid email or password. Please try again.", 'warning')
                return redirect(url_for("login"))

            # Store user info in session just for convenience
            session['userid'] = user['id']
            session['name']   = user['name']
            session['gender'] = user['gender']
            flash(u"Logged in successfully.", 'info')
            return redirect(url_for('profile', userid=session['userid']))

# Log-Out page
@app.route("/logout")
def logout():
    # If not logged in
    if 'userid' not in session:
        flash(u"You're not logged in. Please log in first to see the content.", 'warning')
        return redirect(url_for("login"))
    else:
        session.clear()
        flash(u"Logged out successfully. See you again!", 'info')
        return redirect(url_for('top'))

# User profile page
@app.route("/<int:userid>")
def profile(userid):
    # If not logged in
    if 'userid' not in session:
        flash(u"You're not logged in. Please log in first to see the content.", 'warning')
        return redirect(url_for("login"))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        user = query_db("SELECT * FROM user WHERE id = ?", (int(userid),), True)
        if user == None:
            flash(u"User doesn't exist. Redirected to your profile page.", 'warning')
            return redirect(url_for('profile', userid=session['userid']))
        else:
            return render_template("profile.html", session=session, user=user)
    else:
        return render_template("profile.html", session=session)

# Profile update page
@app.route("/<int:userid>/edit", methods=["GET", "POST"])
def update(userid):
    # If not logged in
    if 'userid' not in session:
        flash(u"You're not logged in. Please log in first to see the content.", 'warning')
        return redirect(url_for("login"))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        flash(u"You cannot edit other users' profile. Redirected to your profile page.", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("edit_profile.html", session=session)
        elif request.method == 'POST':
            # Validate email (has to be unique, and has to contain @, followed by .)
            if re.fullmatch(emailRegEx, request.form.get("email")) == None:
                flash(u"Invalid email address. Please try again.", 'warning')
                return redirect(url_for("update", userid=session['userid']))
            else:
                user = query_db("SELECT * FROM user WHERE email = ?", (request.form.get("email"),), True)
                if (user != None) and (user['id'] != session['userid']):
                    flash(u"Entered email address is already taken. Please try again with other email address.", 'warning')
                    return redirect(url_for("update", userid=session['userid']))

            # Validate password (has to be longer than 8 characters,
            # and has to contain at least one uppercase, lowercase, and digit, respectively)
            # Also, password is NOT stored in session for security purposes
            if re.fullmatch(pwRegEx, request.form.get("password")) == None:
                flash(u"Invalid password. Password has to be longer than or equal to 8 characters, \
                       and has to contain at least one uppercase, lowercase, and digit.", 'warning')
                return redirect(url_for("update", userid=session['userid']))

            # Store inputs (except password) in session for convenience
            session['name']   = request.form.get("name")
            session['email']  = request.form.get("email")
            session['gender'] = request.form.get("gender")

            # Update user info in DB only if passed all validations
            modify_db("UPDATE user \
                       SET name=?, email=?, password=?, gender=? \
                       WHERE id=?",
                       (session['name'], session['email'], request.form.get("password"), session['gender'], session['userid']))

            flash(u"Your profile has been updated successfully.", 'info')
            return redirect(url_for('profile', userid=session['userid']))

# User index page
@app.route("/users")
def index_users():
    # If not logged in
    if 'userid' not in session:
        flash(u"You're not logged in. Please log in first to see the content.", 'warning')
        return redirect(url_for("login"))
    else:
        users = query_db("SELECT * FROM user")
        return render_template("index_users.html", users=users)

# Function to be run before app starts running
@app.before_first_request
def init_app():
    if not path.exists("models/user.db"):
        init_db()

if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.run()
