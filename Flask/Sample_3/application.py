from flask import request, render_template, redirect, url_for, session
from init_db import app, get_db, insert_db, query_db

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route("/")
def top():
    return render_template("top.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
    errMsg = request.args.get('errMsg')
    # If already logged in
    if 'userid' in session:
        return redirect(url_for('profile', userid=session['userid'], errMsg="You're already logged in. Redirected to your profile page."))
    else:
        if request.method == 'GET':
            return render_template("register.html", session=session, errMsg=errMsg)
        elif request.method == 'POST':
            session['name']     = request.form.get("name")
            session['email']    = request.form.get("email")
            session['password'] = request.form.get("password")
            session['gender']   = request.form.get("gender")

            if len(request.form.get("password")) <= 3:
                return redirect(url_for("register", errMsg="Invalid password."))
            else:
                insert_db("INSERT INTO user (name, email, password, gender) VALUES(?, ?, ?, ?)", \
                          (session['name'], session['email'], session['password'], session['gender']))
                user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)

                session['userid'] = user['id']

                return redirect(url_for('profile', userid=session['userid'], errMsg=None))

@app.route("/login", methods=["GET", "POST"])
def login():
    errMsg = request.args.get('errMsg')
    # If already logged in
    if 'userid' in session:
        return redirect(url_for('profile', userid=session['userid'], errMsg="You're already logged in. Redirected to your profile page."))
    else:
        if request.method == 'GET':
            return render_template("login.html", session=session, errMsg=errMsg)
        elif request.method == 'POST':
            session['email']    = request.form.get("email")
            session['password'] = request.form.get("password")
            user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)

            if user and session['password'] == user['password']:
                session['userid'] = user['id']
                session['name']   = user['name']
                session['gender'] = user['gender']
                return redirect(url_for('profile', userid=session['userid'], errMsg=None))
            else:
                return redirect(url_for("login", errMsg="Invalid email or password. Please try again."))

@app.route("/logout")
def logout():
    errMsg = request.args.get('errMsg')
    # If not logged in
    if 'userid' not in session:
        return redirect(url_for("login", errMsg="You're not logged in. Please log in first to see the content."))
    else:
        session.clear()
        return redirect(url_for('top'))

@app.route("/<userid>")
def profile(userid):
    errMsg = request.args.get('errMsg')
    # If not logged in
    if 'userid' not in session:
        return redirect(url_for("login", errMsg="You're not logged in. Please log in first to see the content."))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        user = query_db("SELECT * FROM user WHERE id = ?", (int(userid),), True)
        if user == None:
            return redirect(url_for('profile', userid=session['userid'], errMsg="User doesn't exist. Redirected to your profile page."))
        else:
            return render_template("profile.html", session=session, user=user, errMsg=errMsg)
    else:
        return render_template("profile.html", session=session, errMsg=errMsg)

@app.route("/<userid>/edit", methods=["GET", "POST"])
def update(userid):
    errMsg = request.args.get('errMsg')
    # If not logged in
    if 'userid' not in session:
        return redirect(url_for("login", errMsg="You're not logged in. Please log in first to see the content."))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        return redirect(url_for('profile', userid=session['userid'], errMsg="You cannot edit other users' profile. Redirected to your profile page."))
    else:
        if request.method == 'GET':
            return render_template("edit_profile.html", session=session, errMsg=errMsg)
        elif request.method == 'POST':
            session['name']     = request.form.get("name")
            session['email']    = request.form.get("email")
            session['password'] = request.form.get("password")
            session['gender']   = request.form.get("gender")

            if len(request.form.get("password")) <= 3:
                return redirect(url_for("update", userid=session['userid'], errMsg="Invalid password."))
            else:
                insert_db("UPDATE user \
                           SET name=?, email=?, password=?, gender=? \
                           WHERE id=?", (session['name'], session['email'], session['password'], session['gender'], session['userid']))

                user = query_db("SELECT * FROM user WHERE id = ?", (session['userid'],), True)

                return redirect(url_for('profile', userid=session['userid'], errMsg=None))

@app.route("/users")
def index_users():
    errMsg = request.args.get('errMsg')
    # If not logged in
    if 'userid' not in session:
        return redirect(url_for("login", errMsg="You're not logged in. Please log in first to see the content."))
    else:
        users = query_db("SELECT * FROM user")
        return render_template("index_users.html", users=users)

if __name__ == '__main__':
    app.run()
