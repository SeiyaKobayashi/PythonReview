from flask import request, render_template, redirect, url_for, session
from init_db import app, get_db, insert_db, query_db

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route("/")
def top():
    return render_template("top.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in
    if 'userid' in session:
        return redirect(url_for('mypage', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("register.html")
        elif request.method == 'POST':
            if not request.form.get("name") or not request.form.get("email") \
               or not request.form.get("password") or not request.form.get("gender"):
                return redirect("/register")
            elif len(request.form.get("password")) <= 3:
                return redirect("/register")
            else:
                session['name']     = request.form.get("name")
                session['email']    = request.form.get("email")
                session['password'] = request.form.get("password")
                session['gender']   = request.form.get("gender")

                insert_db("INSERT INTO user (name, email, password, gender) \
                           VALUES(?, ?, ?, ?)", (session['name'], session['email'], session['password'], session['gender']))
                user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)

                session['userid'] = user['id']

                return redirect(url_for('mypage', userid=session['userid']))

@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in
    if 'userid' in session:
        return redirect(url_for('mypage', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("login.html")
        elif request.method == 'POST':
            session['email']    = request.form.get("email")
            session['password'] = request.form.get("password")
            user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)

            if user and session['password'] == user['password']:
                session['userid'] = user['id']
                session['name']   = user['name']
                session['gender'] = user['gender']
                return redirect(url_for('mypage', userid=session['userid']))
            else:
                return redirect("/login")

@app.route("/logout")
def logout():
    # If not logged in
    if 'userid' not in session:
        return redirect("/login")
    else:
        session.clear()
        return redirect(url_for('top'))

@app.route("/<userid>")
def mypage(userid):
    # If not logged in
    if 'userid' not in session:
        return redirect("/login")
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        return redirect(url_for('mypage', userid=session['userid']))
    else:
        return render_template("mypage.html", session=session)

@app.route("/users")
def index_users():
    # If not logged in
    if 'userid' not in session:
        return redirect("/login")
    else:
        users = query_db("SELECT * FROM user")
        return render_template("index_users.html", users=users)

if __name__ == '__main__':
    app.run()
